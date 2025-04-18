import os
import re
import PyPDF2  # type: ignore
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline  # type: ignore
from config.config import Config

def chunk_text(text, max_length=1024):
    chunks = []
    start = 0
    while start < len(text):
        chunks.append(text[start:start + max_length])
        start += max_length
    return chunks

def remove_duplicate_sentences(summary):
    sentences = re.split(r'(?<=[.!?])\s+', summary)
    seen = set()
    unique_sentences = []
    for sent in sentences:
        s = sent.strip()
        if s and s.lower() not in seen:
            unique_sentences.append(s)
            seen.add(s.lower())
    return ' '.join(unique_sentences).strip()

def remove_boilerplate(text):
    pattern = re.compile(r"(References|REFERENCES).*$", re.DOTALL)
    text = pattern.sub("", text)
    return text

class ResearchAnalyzer:
    def __init__(self, models_dir="models"):
        self.models_dir = models_dir
        
        self.tokenizer = AutoTokenizer.from_pretrained("microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract")
        self.model = AutoModelForSequenceClassification.from_pretrained("microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract")

        
        self.summarizer = pipeline(
            "summarization",
            model="google/pegasus-xsum",
            tokenizer="google/pegasus-xsum"
        )


    @staticmethod
    def clean_text(text):
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def multi_chunk_summarize(self, text, chunk_size=1024, default_summary_len=250, min_length=120, max_chunks=2):
        chunks = chunk_text(text, max_length=chunk_size)
        chunk_summaries = []
        for i, chunk in enumerate(chunks[:max_chunks]):
            try:
                summary_output = self.summarizer(
                    chunk,
                    max_length=default_summary_len,
                    min_length=min_length,
                    truncation=True,
                    num_beams=6,
                    no_repeat_ngram_size=3,
                    repetition_penalty=2.0,
                    early_stopping=True
                )
                chunk_summaries.append(summary_output[0]['summary_text'])
            except Exception as e:
                print(f"Error summarizing chunk {i}: {e}")
        combined_text = " ".join(chunk_summaries)
        return remove_duplicate_sentences(combined_text)

    def extract_text_from_pdf(self, pdf_file):
        reader = PyPDF2.PdfReader(pdf_file)
        text = " ".join([page.extract_text() or "" for page in reader.pages])
        return text

    def extract_key_points(self, text, num_points=8):
        sentences = re.split(r'(?<=[.!?])\s+', text)
        filtered = [s.strip() for s in sentences if 8 < len(s.split()) < 30]  # Limiting size of key points
        seen = set()
        unique = []
        for s in filtered:
            if s.lower() not in seen:
                unique.append(s)
                seen.add(s.lower())
        sorted_sentences = sorted(unique, key=lambda s: len(s.split()), reverse=True)[:num_points]
        final_key_points = [" ".join(re.split(r'(?<=[.!?])\s+', kp)[:2]) for kp in sorted_sentences]  # Strictly 2 sentences
        return final_key_points

    def analyze_research_paper(self, pdf_file):
        try:
            text = self.extract_text_from_pdf(pdf_file)
            text = remove_boilerplate(text)
            text = self.clean_text(text)
            summary = self.multi_chunk_summarize(text)
            key_points = self.extract_key_points(text)
            return {"summary": summary, "key_points": key_points}
        except Exception as e:
            return {"error": str(e), "message": "Failed to analyze paper"}
