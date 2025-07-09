from transformers import pipeline
from dotenv import load_dotenv
import os

load_dotenv()

token = os.getenv("HUGGINGFACE_API_KEY")
summarizer = pipeline("summarization", model="facebook/bart-large-cnn", token=token)

from transformers import pipeline
from dotenv import load_dotenv
import os

load_dotenv()

token = os.getenv("HUGGINGFACE_API_KEY")
summarizer = pipeline("summarization", model="facebook/bart-large-cnn", token=token)

CONVERSATION_DATA = [
    {'query': 'what do you think about my medical records', 'answer': 'I think your medical records are incomplete and require further investigation.'}
    ]

# Format the conversation data into a play-like format
play_format_text = ""
for i, turn in enumerate(CONVERSATION_DATA):
    play_format_text += f"Turn {i+1}:\n"
    play_format_text += f"  Question: {turn['query']}\n"
    play_format_text += f"  Answer: {turn['answer']}\n\n"

# Now you can pass this formatted text to the summarizer
summary = summarizer(play_format_text, max_length=130, min_length=30, do_sample=False)
print(summary)