import datetime
from unittest import loader
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
from .src.loading_model import *
from .src.rag import *
from dotenv import load_dotenv
from healytics.models import History
from accounts.models import Patient
from healytics.models import MedicalRecord
import PyPDF2
import os
import json


### Global Variables
PDF_UPLOAD_DIR = 'uploads'
Discussions = []

###Load 
load_dotenv()

# Create your views here.

### View for the home page
def index(request):
    return render(request,"index.html")


def about(request):
    return render(request,"about.html")

def contact(request):
    return render(request,"contact-page.html")


## View for healytics page

def healytics(request):
    return render(request,"healytics.html")

## View for uploading pdf/ extracting text


def uploadPdf(request):
    if request.method == 'POST' and request.FILES['medicalRecord']:
        medical_record_file = request.FILES['medicalRecord']
        if medical_record_file.content_type == 'application/pdf':
            # Ensure the upload directory exists
            if not os.path.exists(PDF_UPLOAD_DIR):
                os.makedirs(PDF_UPLOAD_DIR)

            # Create a FileSystemStorage instance with the custom location
            fs = FileSystemStorage(location=PDF_UPLOAD_DIR)
            filename = fs.save(medical_record_file.name, medical_record_file)
            uploaded_file_url = fs.url(filename)

            # At this point, the PDF is saved in your specified 'uploaded_pdfs/' directory.
            # You can now perform further analysis on the file using the 'file_path'.
            file_path = fs.path(filename)
            print(f"PDF saved at: {file_path}")
            ### we can do further analysis on the pdf uploaded
            ### extract text from the pdf
            medical_record =  extract_pdf_text(file_path)
            print(medical_record)
            medical_analysis = analyze_text(medical_record)
            #medical_analysis = medical_record
            parts = medical_analysis.split("**Lab Results:**")
            print(parts)
            if len(parts) > 1:
                analysis_recommendations = parts[1].strip() # Take the part after "Lab Results:" and remove leading/trailing whitespace
                print(analysis_recommendations)
            else:
                analysis_recommendations = medical_analysis
            context = {"medical_analysis": analysis_recommendations}
            request.session["medical_record"] = medical_record
            request.session["medical_analysis"] = medical_analysis
            return render(request, "healytics.html", context)
    

### Healychat
def chatPdf(request):
    print(Discussions)
    ## retrieve the infos from the session
    patient_id = request.session.get('current_patient_id')
    medical_record = request.session.get("medical_record")
    patient_medical_analysis = request.session.get("medical_analysis")
    patient_diagnosis = "sick till now"
    patient_instance = get_object_or_404(Patient, pk=patient_id)
    print(patient_instance)
    ### generate the actual date and time ---> create instance ---> save the history
    today_date = str(datetime.date.today())
    now_time = str(datetime.datetime.now().time())
    patient_history = History (
        date = today_date,
        time = now_time,
    )
    patient_history.save()
    history_instance = History.objects.latest('history_id') 
    ### save the medical records informations 
    patient_medical_records = MedicalRecord (
        diagnosis = patient_diagnosis,
        medical_analysis = patient_medical_analysis, 
        patient = patient_instance,
        history = history_instance
    )
    patient_medical_records.save()
    ### last inserted medical records id
    medical_record_instance =  MedicalRecord.objects.latest('med_rec_id') 
    med_rec_id = medical_record_instance.med_rec_id
    print(med_rec_id)
    request.session["med_rec_id"] = med_rec_id
    ### create a mongodb database: patient_id, medical_record_id, medical_analysis, embeddings
    mongo_uri = os.getenv("MONGO_URI")
    token = os.getenv("HUGGINGFACE_API_KEY")
    global medical_rag
    medical_rag = MedicalRagSystem(medical_record, patient_id, med_rec_id, mongo_uri=mongo_uri, huggingface_token=token)
    embeddings = medical_rag.generateEmbedding(medical_record)
    if medical_rag.mongo_client:
        global collections
        collections = medical_rag.storeEmbedding("Healify_db", "medical_records_collection", patient_id, med_rec_id, medical_record, embeddings)
        return render(request, "healytics-chat.html")


def answerQuery(request):
    discussion = {}
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            user_query = data.get('query', '')
            discussion["query"] = user_query
            if user_query:
                patient_id = request.session.get("patient_id")
                patient_medical_record = request.session.get("medical_record")
                med_rec_id = request.session.get("med_rec_id")
                results = medical_rag.similaritySearch(user_query, collections, patient_id, med_rec_id)
                search_results = medical_rag.get_search_result(user_query, collections, patient_id, med_rec_id)
                print(f"Search result: {search_results}")
                combined_information = (
                    f"Query: {user_query}\nContinue to answer the query by using the Search Results:\n{search_results}."
                )
                response = medical_rag.generateFinalResponse(combined_information, user_query)
                discussion["answer"] = response
                Discussions.append(discussion)
                print(Discussions)
                return JsonResponse({'response': response})
            else:
                return JsonResponse({'error': 'No query provided'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
