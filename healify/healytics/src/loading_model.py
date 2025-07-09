import PyPDF2
import torch
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel, PeftConfig
from time import time

def extract_pdf_text(pdf_file):
    """Extracts text content from a PDF file."""
    text = "hf_token"
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text() + "\n\n"
        return text
    except Exception as e:
        return f"Error reading PDF: {e}"

def analyze_text(text_to_analyze):
    #analysis="you can try later"
    model_id="Ihssane123/Llama-3.2-1B-Instruct-medical"
    token = "hf_token"
    # 1. Load the base Llama model (make sure this matches the base model the adapter was trained on)
    base_model_name = "meta-llama/Llama-3.2-1B-Instruct"  # Or the correct base model
    tokenizer = AutoTokenizer.from_pretrained(base_model_name, token=token)
    base_model = AutoModelForCausalLM.from_pretrained(base_model_name, token=token, torch_dtype=torch.float16, device_map="cpu")
    try:
        # 2. Load the LoRA adapter configuration
        peft_config = PeftConfig.from_pretrained(model_id)

        # 3. Load the LoRA adapter model
        model = PeftModel.from_pretrained(base_model, model_id, device_map="cpu")

        start_time = time()
        pipe = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            pad_token_id=128001,
            token=token,
            max_new_tokens = 500,
        )
        messages = [
            {"role": "system", "content": """you are a doctor that can
                                             analyse medical records and
                                             explain them to your patient
                                             in a simplified way, try to be concise and
                                             focus solely on important aspects,
                                             respond in professional way do not ask
                                             any further question just analyse it for him
                                             and use a direct tone when speaking to him
                                             try to complete sentence"""},
            {"role": "user", "content":text_to_analyze},
        ]
        outputs = pipe(
            messages,
        )
        analysis = outputs[0]["generated_text"][-1]['content']
        end_time = time()
        print(f"Time taken: {(end_time - start_time)/60} seconds")

    except Exception as e:
        print(f"Error loading LoRA adapter: {e}")
    """Placeholder function for your analysis script."""
    return analysis

def process_pdf_and_analyze(pdf_file):
    """Processes the PDF, extracts text, and performs analysis."""
    pdf_text = extract_pdf_text(pdf_file)
    analysis_result = analyze_text(pdf_text)
    return pdf_text, analysis_result

