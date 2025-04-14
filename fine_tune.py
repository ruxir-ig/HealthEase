import os
import json
import torch # type: ignore
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from datasets import Dataset # type: ignore

# 1. Load your dataset from a JSON file
with open("symptom_data_large.json", "r") as f:
    data = json.load(f)

# Convert data to a Hugging Face Dataset
dataset = Dataset.from_dict({
    "text": [item["text"] for item in data],
    "labels": [item["label"] for item in data]
})

# Optional: Split into training and evaluation sets (80/20 split)
split_dataset = dataset.train_test_split(test_size=0.2)
train_dataset = split_dataset["train"]
eval_dataset = split_dataset["test"]

# 2. Define your model and tokenizer names or paths
# Here we use Bio_ClinicalBERT from Hugging Face hub.
model_name = "./models/Bio_ClinicalBERT"

# 3. Load the tokenizer and model with ignore_mismatched_sizes=True for classifier head
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(
    model_name,
    num_labels=4,  # Adjust the number of labels as per your mapping (e.g., 0: Mild, 1: Moderate, 2: Severe, 3: Critical)
    ignore_mismatched_sizes=True
)

# 4. Tokenize the dataset
def tokenize_function(examples):
    return tokenizer(examples["text"], padding="max_length", truncation=True, max_length=128)

tokenized_train = train_dataset.map(tokenize_function, batched=True)
tokenized_eval = eval_dataset.map(tokenize_function, batched=True)

# 5. Define training arguments
training_args = TrainingArguments(
    output_dir="./clinicalbert_finetuned",
    eval_strategy="epoch",
    save_strategy="epoch",
    num_train_epochs=3,              # Increase if needed
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    logging_dir="./logs",
    logging_steps=10,
    load_best_model_at_end=True,
    metric_for_best_model="accuracy"
)

# 6. Define compute_metrics function to calculate accuracy
def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = torch.argmax(torch.tensor(logits), dim=-1)
    accuracy = (predictions == torch.tensor(labels)).float().mean().item()
    return {"accuracy": accuracy}

# 7. Create the Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_train,
    eval_dataset=tokenized_eval,
    compute_metrics=compute_metrics
)

# 8. Fine-tune the model
trainer.train()

# 9. Save the fine-tuned model and tokenizer
model.save_pretrained("./clinicalbert_finetuned")
tokenizer.save_pretrained("./clinicalbert_finetuned")

print("Fine-tuning complete! Model saved at ./clinicalbert_finetuned")
