import os
import torch # type: ignore
import json
import random
from transformers import AutoTokenizer, AutoModelForSequenceClassification

class SymptomAnalyzer:
    def __init__(self, model_path="Krishna2908/clinicalbert_finetuned"):
        self.model_path = model_path

        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path)

        
        self.label_mapping = {
            0: "Mild",
            1: "Moderate",
            2: "Severe",
            3: "Critical"
        }

        
        self.recommendations_map = {
            "mild": [
                "Stay hydrated and get plenty of rest.",
                "Take over-the-counter pain relievers if necessary.",
                "Monitor your symptoms for the next 24 hours.",
                "Avoid strenuous activities.",
                "Get a good night's sleep.",
                "Eat light, balanced meals.",
                "Apply a cold compress if there's any inflammation.",
                "Maintain a calm and relaxed environment.",
                "Avoid caffeine and alcohol.",
                "Take a short walk if you feel up to it.",
                "Practice gentle stretching exercises.",
                "Keep your workspace stress-free.",
                "Try deep breathing exercises to relax.",
                "Maintain regular meal times.",
                "Keep a symptom diary to track any changes."
            ],
            "moderate": [
                "Consult a doctor if symptoms persist for more than 72 hours.",
                "Avoid heavy physical exertion until you feel better.",
                "Stay well-hydrated and consider electrolyte drinks.",
                "Monitor your temperature regularly.",
                "Follow any prescribed medication instructions carefully.",
                "Rest and minimize stress.",
                "Eat nutritious foods to help your recovery.",
                "Use a warm compress if you experience muscle pain.",
                "Reduce or avoid strenuous work or exercise.",
                "Keep a detailed record of your symptoms.",
                "Practice relaxation techniques like meditation.",
                "Avoid foods that could irritate your condition.",
                "Ensure you get adequate sleep.",
                "Consider a follow-up with your healthcare provider.",
                "Limit exposure to stressors and noisy environments."
            ],
            "severe": [
                "Seek immediate medical attention to evaluate your condition.",
                "Avoid self-medication without professional guidance.",
                "Have someone accompany you if you visit a hospital.",
                "Limit physical activities until assessed by a doctor.",
                "Follow your doctor’s instructions closely.",
                "Keep a list of current medications for review.",
                "Rest in a quiet, calm environment.",
                "Consult a specialist if symptoms do not improve.",
                "Record your symptoms and any changes for medical evaluation.",
                "Avoid heavy exertion and allow your body to recover.",
                "Be prepared to provide detailed symptom history to healthcare providers.",
                "Consider taking prescribed medication as advised.",
                "Avoid stressful activities and ensure proper rest.",
                "Monitor any additional symptoms carefully.",
                "Keep emergency contact numbers handy."
            ],
            "critical": [
                "🚨 CALL EMERGENCY SERVICES IMMEDIATELY! 🚨",
                "Do not delay seeking urgent medical care.",
                "Avoid driving yourself—ask someone to help you get to the hospital.",
                "Follow all emergency instructions from professionals.",
                "Prepare to provide a detailed account of your symptoms to emergency responders.",
                "Have a family member or friend accompany you, if possible.",
                "Do not self-medicate or try to treat severe symptoms alone.",
                "Stay as calm as possible while waiting for help.",
                "If available, take any prescribed emergency medication as directed.",
                "Keep all vital health information accessible for responders.",
                "Do not ignore severe warning signs.",
                "Immediately seek professional medical assistance.",
                "Ensure you have a way to quickly contact emergency services.",
                "Avoid any delay; your condition requires urgent attention.",
                "Follow the advice of emergency medical personnel without delay."
            ]
        }

    def analyze_symptoms(self, user_input):
        """
        Analyzes the symptom input and predicts:
        - Severity Level (Mild, Moderate, Severe, Critical)
        - Confidence Score
        - Provides recommendations based on the predicted severity
        """
        try:
            severity, confidence = self.get_severity_level(user_input)
            recommendations = self.generate_recommendations(severity)
            response = {
                "Analysis Results": {
                    "Severity": severity,
                    "Confidence": f"{confidence:.2f}%",
                    "Recommendations": recommendations,
                    "⚠️ Note": "This is an AI-assisted analysis. Always consult healthcare professionals for medical decisions."
                }
            }
            return json.dumps(response, indent=4)
        except Exception as e:
            return json.dumps({"error": str(e), "message": "Failed to analyze symptoms"})

    def get_severity_level(self, text):
        """
        Uses the fine-tuned ClinicalBERT model to determine the severity level.
        """
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=128)
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            predicted_label_id = torch.argmax(logits, dim=1).item()
        severity_level = self.label_mapping.get(predicted_label_id, "Unknown")
        confidence_score = torch.nn.functional.softmax(logits, dim=1)[0][predicted_label_id].item() * 100
        return severity_level, confidence_score

    def generate_recommendations(self, severity):
        """
        Provides a set of three recommendations randomly selected from a larger list based on the severity level.
        """
        
        severity_key = severity.lower()
        rec_list = self.recommendations_map.get(severity_key, ["Consult a healthcare professional."])
        selected_recommendations = random.sample(rec_list, k=min(3, len(rec_list)))
        return selected_recommendations

