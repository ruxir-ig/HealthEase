import os
from transformers import AutoModel, AutoTokenizer,AutoModelForSequenceClassification, PegasusForConditionalGeneration, PegasusTokenizer

# Create 'models' directory if it doesn't exist
os.makedirs("models", exist_ok=True)

# --- 1. Download and Save PubMedBERT ---
print("Downloading PubMedBERT...")
pubmedbert_model = AutoModel.from_pretrained("microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext")
pubmedbert_tokenizer = AutoTokenizer.from_pretrained("microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext")
pubmedbert_model.save_pretrained("models/PubMedBERT")
pubmedbert_tokenizer.save_pretrained("models/PubMedBERT_tokenizer")
print("✅ PubMedBERT model and tokenizer saved in 'models/PubMedBERT/' and 'models/PubMedBERT_tokenizer/'")


# --- 2. Download and Save PegasusXSum for Text Summarization ---
print("Downloading PegasusXSum...")
pegasus_model = PegasusForConditionalGeneration.from_pretrained("google/pegasus-xsum")
pegasus_tokenizer = PegasusTokenizer.from_pretrained("google/pegasus-xsum")
pegasus_model.save_pretrained("models/PegasusXSum")
pegasus_tokenizer.save_pretrained("models/PegasusXSum_tokenizer")
print("✅ PegasusXSum model and tokenizer saved in 'models/PegasusXSum/' and 'models/PegasusXSum_tokenizer/'")


print("Downloading Bio_ClinicalBERT...")
clinicalbert_model = "emilyalsentzer/Bio_ClinicalBERT"
clinicalbert_path = "./models/Bio_ClinicalBERT"

# Download tokenizer and model for classification (even if it’s base, we’ll fine-tune it)
tokenizer = AutoTokenizer.from_pretrained(clinicalbert_model)
model = AutoModelForSequenceClassification.from_pretrained(clinicalbert_model, num_labels=4)

tokenizer.save_pretrained(clinicalbert_path)
model.save_pretrained(clinicalbert_path)
print("✅ Bio_ClinicalBERT downloaded successfully.")

print("\n🎉 All models have been successfully downloaded and saved locally!")