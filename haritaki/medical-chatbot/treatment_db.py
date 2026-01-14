# treatment_db.py
import json
import os
from typing import Dict, List, Any
from datetime import datetime

class TreatmentDatabase:
    def __init__(self):
        """Initialize treatment database"""
        self.treatments = self._load_treatments()
        self.medications = self._load_medications()
        self.tests = self._load_tests()
        
    def _load_treatments(self) -> Dict:
        """Load treatment database"""
        return {
            "common_cold": {
                "name": "Common Cold",
                "treatments": [
                    "Rest and hydration",
                    "Over-the-counter cold medication",
                    "Nasal decongestants",
                    "Throat lozenges",
                    "Steam inhalation"
                ],
                "medications": [
                    {"name": "Acetaminophen", "purpose": "Fever/pain relief", "dosage": "500mg every 6 hours"},
                    {"name": "Ibuprofen", "purpose": "Anti-inflammatory", "dosage": "400mg every 8 hours"},
                    {"name": "Pseudoephedrine", "purpose": "Decongestant", "dosage": "60mg every 6 hours"}
                ],
                "duration": "7-10 days",
                "follow_up": "If symptoms persist beyond 10 days"
            },
            "influenza": {
                "name": "Influenza (Flu)",
                "treatments": [
                    "Antiviral medication (if early)",
                    "Rest and fluids",
                    "Fever reducers",
                    "Symptom management",
                    "Isolation to prevent spread"
                ],
                "medications": [
                    {"name": "Oseltamivir", "purpose": "Antiviral", "dosage": "75mg twice daily for 5 days"},
                    {"name": "Acetaminophen", "purpose": "Fever/pain", "dosage": "650mg every 6 hours"}
                ],
                "duration": "1-2 weeks",
                "follow_up": "If breathing difficulties develop"
            },
            "migraine": {
                "name": "Migraine",
                "treatments": [
                    "Rest in dark, quiet room",
                    "Cold compress on forehead",
                    "Medication for acute attack",
                    "Preventive medication if frequent",
                    "Identify and avoid triggers"
                ],
                "medications": [
                    {"name": "Sumatriptan", "purpose": "Acute treatment", "dosage": "50-100mg at onset"},
                    {"name": "Naproxen", "purpose": "Pain relief", "dosage": "500mg initial, then 250mg every 8 hours"}
                ],
                "duration": "Varies",
                "follow_up": "If migraines become more frequent"
            },
            "gastroenteritis": {
                "name": "Gastroenteritis",
                "treatments": [
                    "Oral rehydration solution",
                    "BRAT diet (bananas, rice, applesauce, toast)",
                    "Avoid dairy and fatty foods",
                    "Rest",
                    "Gradual return to normal diet"
                ],
                "medications": [
                    {"name": "Loperamide", "purpose": "Anti-diarrheal", "dosage": "4mg initial, then 2mg after each loose stool"},
                    {"name": "Ondansetron", "purpose": "Anti-nausea", "dosage": "4-8mg every 8 hours as needed"}
                ],
                "duration": "2-5 days",
                "follow_up": "If symptoms worsen or blood in stool"
            }
        }
    
    def _load_medications(self) -> Dict:
        """Load medication database"""
        return {
            "analgesics": [
                {"name": "Acetaminophen", "type": "Pain reliever", "otc": True, "max_daily": "4000mg"},
                {"name": "Ibuprofen", "type": "NSAID", "otc": True, "max_daily": "3200mg"},
                {"name": "Naproxen", "type": "NSAID", "otc": True, "max_daily": "1375mg"}
            ],
            "antihistamines": [
                {"name": "Cetirizine", "type": "Antihistamine", "otc": True, "max_daily": "10mg"},
                {"name": "Loratadine", "type": "Antihistamine", "otc": True, "max_daily": "10mg"},
                {"name": "Fexofenadine", "type": "Antihistamine", "otc": True, "max_daily": "180mg"}
            ],
            "antibiotics": [
                {"name": "Amoxicillin", "type": "Antibiotic", "otc": False, "requires_prescription": True},
                {"name": "Azithromycin", "type": "Antibiotic", "otc": False, "requires_prescription": True},
                {"name": "Doxycycline", "type": "Antibiotic", "otc": False, "requires_prescription": True}
            ]
        }
    
    def _load_tests(self) -> Dict:
        """Load medical tests database"""
        return {
            "blood_tests": [
                "Complete Blood Count (CBC)",
                "Basic Metabolic Panel (BMP)",
                "Lipid Panel",
                "Liver Function Tests (LFT)",
                "Thyroid Function Tests",
                "C-reactive Protein (CRP)",
                "Erythrocyte Sedimentation Rate (ESR)"
            ],
            "imaging_tests": [
                "X-ray",
                "CT Scan",
                "MRI",
                "Ultrasound",
                "Echocardiogram"
            ],
            "other_tests": [
                "Electrocardiogram (ECG/EKG)",
                "Urinalysis",
                "Stool Test",
                "Pulmonary Function Test",
                "Allergy Testing"
            ]
        }
    
    def get_treatment(self, diagnosis: Dict, patient_data: Dict) -> Dict:
        """Get treatment plan for diagnosis"""
        diagnosis_name = diagnosis.get('primary_diagnosis', '').lower().replace(' ', '_')
        
        if diagnosis_name in self.treatments:
            treatment = self.treatments[diagnosis_name].copy()
        else:
            treatment = self._get_general_treatment(diagnosis, patient_data)
        
        # Add patient-specific adjustments
        treatment = self._adjust_for_patient(treatment, patient_data)
        
        # Add tests if needed
        if diagnosis.get('severity') == 'moderate' or diagnosis.get('severity') == 'severe':
            treatment['recommended_tests'] = self._get_recommended_tests(diagnosis)
        
        return treatment
    
    def _get_general_treatment(self, diagnosis: Dict, patient_data: Dict) -> Dict:
        """Get general treatment for unspecified diagnosis"""
        symptoms = diagnosis.get('symptoms', [])
        
        general_treatment = {
            "name": "General Symptom Management",
            "treatments": [
                "Rest and adequate hydration",
                "Symptom-specific over-the-counter medications",
                "Monitor for worsening symptoms",
                "Maintain comfortable environment"
            ],
            "medications": [],
            "duration": "Until symptoms improve",
            "follow_up": "If no improvement in 48 hours"
        }
        
        # Add symptom-specific recommendations
        if any(s in symptoms for s in ['fever', 'pain']):
            general_treatment['medications'].append({
                "name": "Acetaminophen",
                "purpose": "Fever and pain relief",
                "dosage": "500mg every 6 hours as needed"
            })
        
        if any(s in symptoms for s in ['cough', 'congestion']):
            general_treatment['medications'].append({
                "name": "Dextromethorphan",
                "purpose": "Cough suppression",
                "dosage": "30mg every 6-8 hours"
            })
        
        return general_treatment
    
    def _adjust_for_patient(self, treatment: Dict, patient_data: Dict) -> Dict:
        """Adjust treatment based on patient characteristics"""
        age = patient_data.get('age', 0)
        gender = patient_data.get('gender', '').lower()
        medical_history = patient_data.get('medical_history', '').lower()
        
        adjustments = []
        
        # Age-based adjustments
        if age < 12:
            adjustments.append("Pediatric dosing required")
            if 'ibuprofen' in str(treatment).lower():
                adjustments.append("Avoid ibuprofen in children under 6 months")
        
        if age > 65:
            adjustments.append("Consider reduced dosing for age")
            adjustments.append("Monitor for drug interactions")
        
        # Medical history adjustments
        if 'liver' in medical_history:
            adjustments.append("Use acetaminophen with caution")
        
        if 'kidney' in medical_history:
            adjustments.append("Avoid NSAIDs if possible")
        
        if 'pregnant' in medical_history or 'pregnancy' in medical_history:
            adjustments.append("Consult OB/GYN before any medication")
            adjustments.append("Avoid certain medications during pregnancy")
        
        # Add adjustments to treatment
        if adjustments:
            treatment['patient_specific_adjustments'] = adjustments
        
        return treatment
    
    def _get_recommended_tests(self, diagnosis: Dict) -> List[str]:
        """Get recommended tests based on diagnosis"""
        symptoms = diagnosis.get('symptoms', [])
        tests = []
        
        if any(s in symptoms for s in ['fever', 'fatigue', 'infection']):
            tests.append("Complete Blood Count (CBC)")
            tests.append("C-reactive Protein (CRP)")
        
        if any(s in symptoms for s in ['abdominal pain', 'nausea', 'vomiting']):
            tests.append("Basic Metabolic Panel (BMP)")
            tests.append("Liver Function Tests")
        
        if any(s in symptoms for s in ['chest pain', 'shortness of breath', 'palpitations']):
            tests.append("Electrocardiogram (ECG)")
            tests.append("Chest X-ray")
        
        if any(s in symptoms for s in ['headache', 'dizziness', 'neurological']):
            tests.append("Neurological examination")
        
        return tests[:5]  # Return max 5 tests
    
    def get_medication_info(self, medication_name: str) -> Dict:
        """Get detailed information about a medication"""
        for category, meds in self.medications.items():
            for med in meds:
                if med['name'].lower() == medication_name.lower():
                    info = med.copy()
                    info['category'] = category
                    info['common_side_effects'] = self._get_side_effects(medication_name)
                    info['precautions'] = self._get_precautions(medication_name)
                    return info
        
        return {"error": "Medication not found in database"}
    
    def _get_side_effects(self, medication: str) -> List[str]:
        """Get common side effects for medication"""
        side_effects = {
            "acetaminophen": ["Nausea", "Rash", "Liver damage (with overdose)"],
            "ibuprofen": ["Upset stomach", "Heartburn", "Dizziness", "Kidney issues (prolonged use)"],
            "amoxicillin": ["Diarrhea", "Nausea", "Rash", "Yeast infection"],
            "cetirizine": ["Drowsiness", "Dry mouth", "Headache", "Fatigue"]
        }
        
        return side_effects.get(medication.lower(), ["Consult medication guide for side effects"])
    
    def _get_precautions(self, medication: str) -> List[str]:
        """Get precautions for medication"""
        precautions = {
            "acetaminophen": ["Do not exceed 4000mg daily", "Avoid with alcohol", "Check other medications for acetaminophen"],
            "ibuprofen": ["Take with food", "Avoid if pregnant", "Caution with kidney disease"],
            "amoxicillin": ["Complete full course", "Take as prescribed", "Report allergic reactions immediately"]
        }
        
        return precautions.get(medication.lower(), ["Follow healthcare provider's instructions"])
    
    def get_all_tests_by_category(self) -> Dict:
        """Get all tests organized by category"""
        return self.tests
    
    def search_treatments(self, keyword: str) -> List[Dict]:
        """Search treatments by keyword"""
        results = []
        keyword_lower = keyword.lower()
        
        for disease, treatment in self.treatments.items():
            if (keyword_lower in disease or 
                keyword_lower in treatment['name'].lower() or
                any(keyword_lower in str(item).lower() for item in treatment['treatments'])):
                
                results.append({
                    'disease': disease,
                    'name': treatment['name'],
                    'treatments': treatment['treatments'][:3],  # First 3 treatments
                    'medications': treatment['medications'][:2]  # First 2 medications
                })
        
        return results