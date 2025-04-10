import json
import random

# Base examples with labels (0 = Mild, 1 = Moderate, 2 = Severe, 3 = Critical)
base_examples = [
    {"text": "I have a slight headache and feel tired.", "label": 0},
    {"text": "I experience moderate fever and a sore throat.", "label": 1},
    {"text": "I have severe stomach pain and have been vomiting.", "label": 2},
    {"text": "I have critical chest pain and difficulty breathing.", "label": 3}
]

# Synonyms to augment the text (keys must be in lowercase)
synonyms = {
    "slight": ["mild", "light", "minor"],
    "headache": ["head pain", "migraine"],
    "tired": ["fatigued", "exhausted"],
    "moderate": ["medium", "average", "somewhat"],
    "fever": ["elevated temperature", "high temperature"],
    "sore": ["irritated", "raw"],
    "throat": ["pharynx"],
    "severe": ["intense", "extreme", "strong"],
    "stomach": ["abdominal", "belly"],
    "pain": ["ache"],
    "vomiting": ["throwing up", "emesis"],
    "critical": ["life-threatening", "urgent", "emergency"],
    "chest": ["thoracic"],
    "difficulty": ["trouble"],
    "breathing": ["respiration", "getting air"]
}

def augment_text(text):
    """Replace some words in the text with random synonyms to create variation."""
    words = text.split()
    new_words = []
    for word in words:
        # Remove punctuation for matching and keep punctuation for later
        clean_word = word.lower().strip(".,")
        if clean_word in synonyms and random.random() < 0.5:
            new_word = random.choice(synonyms[clean_word])
            # Keep the original capitalization if needed
            if word[0].isupper():
                new_word = new_word.capitalize()
            # Append punctuation if the original word ended with punctuation
            if word[-1] in ".,!?":
                new_word += word[-1]
            new_words.append(new_word)
        else:
            new_words.append(word)
    return " ".join(new_words)

# Generate a synthetic dataset
num_examples = 5000  # You can adjust this number to generate more examples
dataset = []

for _ in range(num_examples):
    # Pick a random base example
    base = random.choice(base_examples)
    text = base["text"]
    
    # With some probability, augment the text to create variation
    if random.random() < 0.8:
        text = augment_text(text)
    
    dataset.append({"text": text, "label": base["label"]})

# Save dataset to a JSON file
output_file = "symptom_data_large.json"
with open(output_file, "w") as f:
    json.dump(dataset, f, indent=2)

print(f"Generated {num_examples} synthetic examples in {output_file}")
