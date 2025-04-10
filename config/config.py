# config/config.py
import os
from dotenv import load_dotenv  # type: ignore

# Load environment variables
load_dotenv()

class Config:
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    DB_NAME = os.getenv('DB_NAME', 'healthcare_platform')
    
   
    PUBMEDBERT_MODEL = "microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext"
    CLINICALBERT_MODEL = "emilyalsentzer/Bio_ClinicalBERT"
    MEDICAL_NER_MODEL = "samrawal/bert-base-uncased_clinical-ner"
    QA_MODEL = "deepset/roberta-base-squad2"
    ZERO_SHOT_MODEL = "facebook/bart-large-mnli"
    TEXT_GENERATION_MODEL = "./models/PegasusXSum"
    TEXT_GENERATION_TOKENIZER = "./models/PegasusXSum_tokenizer"
    
    SECRET_KEY = os.getenv('SECRET_KEY')
    
    EMERGENCY_PHONE = os.getenv('EMERGENCY_PHONE', '911')
    
    SESSION_LIFETIME = 24 * 60 * 60  # 24 hours in seconds
    
    COLLECTIONS = {
        'users': 'users',
        'health_records': 'health_records',
        'research_history': 'research_history',
        'wellness_data': 'wellness_data'
    }
    
    
    MAX_TEXT_LENGTH = 1024
    MIN_CONFIDENCE_THRESHOLD = 0.7