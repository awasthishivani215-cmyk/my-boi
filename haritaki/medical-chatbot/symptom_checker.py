# symptom_checker.py
import json
from typing import Dict, List, Any
from datetime import datetime

class SymptomChecker:
    def __init__(self):
        """Initialize symptom checker with medical knowledge base"""
        self.symptom_database = self._load_symptom_database()
        self.disease_patterns = self._load_disease_patterns()
        
    def _load_symptom_database(self) -> Dict:
        """Load symptom database"""
        return {
            "respiratory": ["cough", "shortness of breath", "chest pain", "sore throat", "runny nose"],
            "gastrointestinal": ["nausea", "vomiting", "diarrhea", "abdominal pain", "constipation"],
            "neurological": ["headache", "dizziness", "blurred vision", "numbness", "seizures"],
            "musculoskeletal": ["joint pain", "back pain", "muscle pain", "swelling", "stiffness"],
            "general": ["fever", "fatigue", "weight loss", "sweating", "chills"]
        }
    
    def _load_disease_patterns(self) -> Dict:
        """Load disease patterns"""
        return {
            "common_cold": {
                "symptoms": ["runny nose", "sneezing", "cough", "sore throat"],
                "severity": "mild",
                "urgency": "low"
            },
            "influenza": {
                "symptoms": ["fever", "body aches", "fatigue", "cough", "headache"],
                "severity": "moderate",
                "urgency": "medium"
            },
            "covid_19": {
                "symptoms": ["fever", "cough", "shortness of breath", "fatigue", "loss of taste/smell"],
                "severity": "variable",
                "urgency": "high"
            },
            "migraine": {
                "symptoms": ["severe headache", "nausea", "sensitivity to light", "sensitivity to sound"],
                "severity": "moderate",
                "urgency": "medium"
            },
            "appendicitis": {
                "symptoms": ["abdominal pain", "nausea", "vomiting", "fever"],
                "severity": "severe",
                "urgency": "high"
            }
        }
    
    def analyze_symptoms(self, symptoms: List[str], patient_data: Dict) -> Dict:
        """Analyze symptoms and provide preliminary assessment"""
        if not symptoms:
            return {
                "error": "No symptoms provided",
                "urgency_level": "unknown"
            }
        
        # Categorize symptoms
        categories = {}
        for symptom in symptoms:
            for category, symptom_list in self.symptom_database.items():
                if symptom in symptom_list:
                    categories.setdefault(category, []).append(symptom)
        
        # Match against disease patterns
        possible_conditions = []
        for disease, pattern in self.disease_patterns.items():
            match_score = self._calculate_match_score(symptoms, pattern["symptoms"])
            if match_score > 0.3:  # Threshold for possible match
                possible_conditions.append({
                    "disease": disease.replace("_", " ").title(),
                    "match_score": match_score,
                    "severity": pattern["severity"],
                    "urgency": pattern["urgency"]
                })
        
        # Sort by match score
        possible_conditions.sort(key=lambda x: x["match_score"], reverse=True)
        
        # Determine urgency level
        urgency_level = self._determine_urgency_level(symptoms, possible_conditions)
        
        # Generate severity assessment
        severity = self._assess_severity(symptoms, patient_data)
        
        return {
            "symptoms": symptoms,
            "symptom_categories": categories,
            "possible_conditions": possible_conditions[:5],  # Top 5
            "urgency_level": urgency_level,
            "severity": severity,
            "recommended_actions": self._get_recommended_actions(urgency_level),
            "timestamp": datetime.now().isoformat()
        }
    
    def _calculate_match_score(self, user_symptoms: List[str], disease_symptoms: List[str]) -> float:
        """Calculate how well user symptoms match disease pattern"""
        if not user_symptoms or not disease_symptoms:
            return 0.0
        
        matched = len(set(user_symptoms) & set(disease_symptoms))
        return matched / len(disease_symptoms)
    
    def _determine_urgency_level(self, symptoms: List[str], possible_conditions: List[Dict]) -> str:
        """Determine urgency level based on symptoms and possible conditions"""
        # Check for emergency symptoms
        emergency_symptoms = ["chest pain", "shortness of breath", "severe headache", 
                            "uncontrolled bleeding", "loss of consciousness"]
        
        if any(symptom in symptoms for symptom in emergency_symptoms):
            return "high"
        
        # Check if any possible condition has high urgency
        for condition in possible_conditions:
            if condition.get("urgency") == "high":
                return "high"
        
        # Check for moderate symptoms
        moderate_symptoms = ["fever", "vomiting", "severe pain", "dizziness"]
        if any(symptom in symptoms for symptom in moderate_symptoms):
            return "medium"
        
        return "low"
    
    def _assess_severity(self, symptoms: List[str], patient_data: Dict) -> str:
        """Assess severity of symptoms"""
        age = patient_data.get("age", 0)
        
        # Consider age in severity assessment
        if age > 60 or age < 5:
            age_factor = 1.5
        else:
            age_factor = 1.0
        
        # Count symptoms
        symptom_count = len(symptoms)
        
        if symptom_count >= 5:
            return "severe"
        elif symptom_count >= 3:
            return "moderate"
        else:
            return "mild"
    
    def _get_recommended_actions(self, urgency_level: str) -> List[str]:
        """Get recommended actions based on urgency"""
        actions = {
            "high": [
                "Seek emergency medical attention immediately",
                "Call emergency services or go to nearest ER",
                "Do not delay treatment"
            ],
            "medium": [
                "Schedule appointment with healthcare provider within 24-48 hours",
                "Monitor symptoms closely",
                "Rest and stay hydrated"
            ],
            "low": [
                "Self-care and monitoring",
                "Consider over-the-counter remedies if appropriate",
                "Consult doctor if symptoms persist beyond 48 hours"
            ]
        }
        
        return actions.get(urgency_level, ["Consult healthcare provider"])
    
    def get_symptom_severity(self, symptom: str, description: str) -> int:
        """Get severity score for a symptom based on description"""
        severity_keywords = {
            "mild": ["slight", "minor", "tolerable", "manageable"],
            "moderate": ["uncomfortable", "bothersome", "interferes"],
            "severe": ["unbearable", "excruciating", "debilitating", "worst ever"]
        }
        
        description_lower = description.lower()
        
        for level, keywords in severity_keywords.items():
            if any(keyword in description_lower for keyword in keywords):
                if level == "mild":
                    return 3
                elif level == "moderate":
                    return 6
                elif level == "severe":
                    return 9
        
        return 5  # Default moderate
    
    def validate_symptoms(self, symptoms: List[str]) -> Dict:
        """Validate if symptoms are recognized medical terms"""
        valid_symptoms = []
        unrecognized = []
        
        # Flatten all known symptoms
        all_known_symptoms = []
        for category in self.symptom_database.values():
            all_known_symptoms.extend(category)
        
        for symptom in symptoms:
            if symptom in all_known_symptoms:
                valid_symptoms.append(symptom)
            else:
                unrecognized.append(symptom)
        
        return {
            "valid_symptoms": valid_symptoms,
            "unrecognized_symptoms": unrecognized,
            "suggestions": self._suggest_similar_symptoms(unrecognized)
        }
    
    def _suggest_similar_symptoms(self, symptoms: List[str]) -> Dict[str, List[str]]:
        """Suggest similar known symptoms for unrecognized ones"""
        suggestions = {}
        
        for symptom in symptoms:
            symptom_lower = symptom.lower()
            similar = []
            
            # Check for similar symptoms in database
            for known_symptom in self._get_all_known_symptoms():
                if symptom_lower in known_symptom or known_symptom in symptom_lower:
                    similar.append(known_symptom)
            
            if similar:
                suggestions[symptom] = similar[:3]  # Top 3 suggestions
        
        return suggestions
    
    def _get_all_known_symptoms(self) -> List[str]:
        """Get all known symptoms from database"""
        all_symptoms = []
        for category_symptoms in self.symptom_database.values():
            all_symptoms.extend(category_symptoms)
        return list(set(all_symptoms))