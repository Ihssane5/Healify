from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import pymongo
from dotenv import load_dotenv
import os
import certifi
import torch

load_dotenv()


class MedicalRagSystem:
    def __init__(self, medical_record, patient_id, med_rec_id, embedding_model_name="thenlper/gte-large", mongo_uri=None, llm_model_name="meta-llama/Llama-3.2-1B-Instruct", huggingface_token=None):
        self.medical_record = medical_record
        self.patient_id = patient_id
        self.med_rec_id = med_rec_id
        self.embedding_model = SentenceTransformer(embedding_model_name)
        if mongo_uri is None:
            mongo_uri = os.getenv("MONGO_URI")
        self.mongo_client = self.getMongoClient(mongo_uri)
        self.tokenizer = AutoTokenizer.from_pretrained(llm_model_name, token=huggingface_token)
        self.model = AutoModelForCausalLM.from_pretrained(llm_model_name, device_map="auto" if torch.cuda.is_available() else "cpu", token=huggingface_token, torch_dtype=torch.float16)
        self.pipe = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            pad_token_id=self.tokenizer.eos_token_id if self.tokenizer.pad_token_id is not None else self.tokenizer.unk_token_id,
            token=huggingface_token,
            max_new_tokens = 500,
        )

    def generateEmbedding(self, text):
        if not text.strip():
            print("Attempted to get embedding for empty text.")
            return []
        embedding = self.embedding_model.encode(text)
        return embedding.tolist()

    def getMongoClient(self, mongo_uri):
        """Establish connection to the MongoDB"""
        try:
            client = pymongo.MongoClient(mongo_uri, tlsCAFile = certifi.where())
            print("Connection to MongoDB successful")
            return client
        except pymongo.errors.ConnectionFailure as e:
            print(f"Connection failed: {e}")
            return None

    def storeEmbedding(self, db_name, col_name, patient_id, medical_record_id, medical_record, embedding):
        db = self.mongo_client[db_name]
        collection = db[col_name]
        my_object = {"patient_id": patient_id,
                     "medical_record_id": medical_record_id,
                     "medical_record" : medical_record,
                     "embedding": embedding
                     }
        inserted_result = collection.insert_one(my_object)
        print(f"Inserted document ID: {inserted_result.inserted_id}")
        # Consider creating the vector index if it doesn't exist
        # collection.create_index([("embedding", "vector")], name="vector_index", numVectorDimensions=len(embedding))
        # It's generally better to create the index beforehand in MongoDB Atlas or using MongoDB commands.
        return collection

    def similaritySearch(self, user_query, collection, patient_id, med_rec_id):
        # Generate embedding for the user query
        query_embedding = self.generateEmbedding(user_query)
        if not query_embedding:
            return "Invalid query or embedding generation failed."

        # Define the vector search pipeline with a $match stage for filtering
        pipeline = [
            {
                "$vectorSearch": {
                    "index": "vector_index",
                    "queryVector": query_embedding,
                    "path": "embedding",
                    "numCandidates": 150,  # Number of candidate matches to consider
                    "limit": 100,  # Increase limit to potentially find matches
                }
            },
            {
                "$match": {
                    "patient_id": patient_id,
                    "medical_record_id": med_rec_id
                }
            },
            {
                "$limit": 5  # Limit to the top 5 after filtering
            },
            {
                "$project": {
                    "_id": 0,
                    "patient_id": 1,
                    "medical_record_id": 1,
                    "medical_record": 1,
                    "score": {"$meta": "vectorSearchScore"}  # Include the score
                }}
        ]
        # Execute the search
        results = collection.aggregate(pipeline)
        return list(results)

    def get_search_result(self, query, collection, patient_id, med_rec_id):
        get_knowledge = self.similaritySearch(query, collection, patient_id, med_rec_id)
        search_result = ""
        for result in get_knowledge:
            search_result += f"patient_id: {result.get('patient_id', 'N/A')}, medical_record_id: {result.get('medical_record_id', 'N/A')}, medical_record : {result.get('medical_record', 'N/A')}\n"
        return search_result

    def generateFinalResponse(self, combined_informations, query):
        messages = [
            {"role": "system", "content": f"""you are a doctor that can
                                            use this information {combined_informations}
                                            to answer user  question try to answer the question
                                            directly don't get into too many details or explanation 
                                            just answer the question
                                         """},
            {"role": "user", "content": query},
        ]
        outputs = self.pipe(
            messages,
        )
        analysis = outputs[0]["generated_text"][2]["content"]
        return analysis


if __name__ == '__main__':
    medical_record = """
        Patient ID: 44154 Admission Date: 2178-05-15
        Admission Time: 02:47:00 Admission Type: EMERGENCY
        Diagnosis: ALTERED MENTAL STATUS Gender: M
        Age: 300.0 (Super Elderly) Insurance: Medicare
        Marital Status: MARRIED
        **Lab Results:**
        - Lactate: 2.6 mmol/L (abnormal)
        - pCO2: 34.0 mm Hg (abnormal)
        - pO2: 45.0 mm Hg (abnormal)
        """
    patient_id = 1
    med_rec_id = 1
    mongo_uri = os.getenv("MONGO_URI")
    token = os.getenv("HUGGINGFACE_API_KEY")

    medical_rag = MedicalRagSystem(medical_record, patient_id, med_rec_id, mongo_uri=mongo_uri, huggingface_token=token)
    embeddings = medical_rag.generateEmbedding(medical_record)
    if medical_rag.mongo_client:
        collections = medical_rag.storeEmbedding("Healify_db", "medical_records_collection", patient_id, med_rec_id, medical_record, embeddings)
        user_query = "what do you think about my lactate level"
        results = medical_rag.similaritySearch(user_query, collections, patient_id, med_rec_id)
        search_results = medical_rag.get_search_result(user_query, collections, patient_id, med_rec_id)
        print(search_results)
        combined_information = (
            f"Query: {user_query}\nContinue to answer the query by using the Search Results:\n{search_results}."
        )
        response = medical_rag.generateFinalResponse(combined_information,user_query)
        print(response)
    else:
        print("Failed to connect to MongoDB. Cannot proceed.")