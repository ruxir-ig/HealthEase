from transformers import AutoModelForSequenceClassification, AutoTokenizer
import os

# Define model name and local directory
model_name = "emilyalsentzer/Bio_ClinicalBERT"
save_directory = "./models/Bio_ClinicalBERT"

# Create directory if it doesn't exist
os.makedirs(save_directory, exist_ok=True)

# Download and save the tokenizer
print(f"Downloading tokenizer for {model_name}...")
tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.save_pretrained(save_directory)

# Download and save the model
print(f"Downloading model for {model_name}...")
model = AutoModelForSequenceClassification.from_pretrained(model_name)
model.save_pretrained(save_directory)

print(f"✅ Model saved successfully at {save_directory}")
