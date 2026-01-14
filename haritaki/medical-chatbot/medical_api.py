# medical_api.py
import openai
import json
import os
from datetime import datetime
from typing import Dict, List, Any
import random
import time
from config import Config
from symptom_checker import SymptomChecker
from treatment_db import TreatmentDatabase

class MedicalChatbot:
    def __init__(self):
        """Initialize the medical chatbot with enhanced personality"""
        # Set OpenAI API key
        openai.api_key = Config.OPENAI_API_KEY
        
        # Initialize symptom checker and treatment database
        self.symptom_checker = SymptomChecker()
        self.treatment_db = TreatmentDatabase()
        
        # Medical knowledge base - expanded
        self.medical_knowledge = self._load_medical_knowledge()
        
        # Human-like behavior configurations
        self.doctor_personalities = [
            {"name": "Dr. Smith", "style": "warm", "emoji": "👨‍⚕️", "greeting": "Hello there"},
            {"name": "Dr. Johnson", "style": "professional", "emoji": "👩‍⚕️", "greeting": "Good day"},
            {"name": "Dr. Patel", "style": "friendly", "emoji": "🩺", "greeting": "Hi there"}
        ]
        
        # Conversation memory for continuity
        self.conversation_memory = {}
        
        # Response cache for faster replies
        self.response_cache = {}
        
        # Current doctor personality
        self.current_doctor = random.choice(self.doctor_personalities)
        
    def _load_medical_knowledge(self) -> Dict:
        """Load enhanced medical knowledge base"""
        return {
            "common_diseases": {
                "common_cold": {
                    "symptoms": ["runny nose", "sneezing", "cough", "sore throat", "mild fever", "congestion"],
                    "description": "Viral infection of the upper respiratory tract",
                    "severity": "mild",
                    "urgency": "low",
                    "common_in": ["all ages", "seasonal"],
                    "recovery": "7-10 days"
                },
                "influenza": {
                    "symptoms": ["high fever", "body aches", "fatigue", "dry cough", "headache", "chills", "sweating"],
                    "description": "Viral infection affecting respiratory system",
                    "severity": "moderate",
                    "urgency": "medium",
                    "common_in": ["all ages", "winter season"],
                    "recovery": "1-2 weeks"
                },
                "migraine": {
                    "symptoms": ["severe headache", "nausea", "sensitivity to light", "sensitivity to sound", "aura"],
                    "description": "Neurological condition causing severe headaches",
                    "severity": "moderate",
                    "urgency": "medium",
                    "common_in": ["adults", "more common in women"],
                    "recovery": "4-72 hours"
                },
                "gastroenteritis": {
                    "symptoms": ["diarrhea", "vomiting", "stomach pain", "nausea", "fever", "loss of appetite"],
                    "description": "Inflammation of stomach and intestines (stomach flu)",
                    "severity": "moderate",
                    "urgency": "medium",
                    "common_in": ["all ages"],
                    "recovery": "2-5 days"
                },
                "sinusitis": {
                    "symptoms": ["facial pain", "nasal congestion", "headache", "cough", "post-nasal drip", "fatigue"],
                    "description": "Inflammation of the sinuses",
                    "severity": "mild",
                    "urgency": "low",
                    "common_in": ["adults"],
                    "recovery": "2-4 weeks"
                },
                "bronchitis": {
                    "symptoms": ["cough", "mucus production", "fatigue", "shortness of breath", "chest discomfort", "wheezing"],
                    "description": "Inflammation of the bronchial tubes",
                    "severity": "moderate",
                    "urgency": "medium",
                    "common_in": ["smokers", "elderly"],
                    "recovery": "3-4 weeks"
                },
                "strep_throat": {
                    "symptoms": ["sore throat", "fever", "swollen tonsils", "difficulty swallowing", "white patches"],
                    "description": "Bacterial infection of the throat",
                    "severity": "moderate",
                    "urgency": "medium",
                    "common_in": ["children", "young adults"],
                    "recovery": "3-7 days with antibiotics"
                },
                "urinary_tract_infection": {
                    "symptoms": ["burning sensation", "frequent urination", "cloudy urine", "pelvic pain", "fever"],
                    "description": "Infection in any part of urinary system",
                    "severity": "moderate",
                    "urgency": "medium",
                    "common_in": ["women"],
                    "recovery": "3-7 days with antibiotics"
                },
                "anxiety_disorder": {
                    "symptoms": ["anxiety", "restlessness", "panic attacks", "insomnia", "muscle tension"],
                    "description": "Mental health condition with excessive anxiety",
                    "severity": "moderate",
                    "urgency": "medium",
                    "common_in": ["all ages"],
                    "recovery": "Varies with treatment"
                }
            },
            "symptoms_db": [
                "fever", "cough", "headache", "fatigue", "nausea", "vomiting",
                "diarrhea", "constipation", "chest pain", "shortness of breath",
                "dizziness", "back pain", "joint pain", "rash", "sore throat",
                "runny nose", "sneezing", "abdominal pain", "loss of appetite",
                "weight loss", "insomnia", "anxiety", "depression", "palpitations",
                "chills", "sweating", "muscle pain", "blurred vision", "ear pain",
                "congestion", "wheezing", "heartburn", "indigestion", "bloating",
                "constipation", "burning sensation", "frequent urination", "swelling"
            ]
        }
    
    def get_welcome_message(self, patient_data: Dict) -> str:
        """Generate warm, personalized welcome message"""
        name = patient_data.get('name', 'Patient')
        age = patient_data.get('age', '')
        gender = patient_data.get('gender', '')
        
        doctor = self.current_doctor
        greeting = doctor["greeting"]
        emoji = doctor["emoji"]
        doctor_name = doctor["name"]
        
        # Personalized opening based on time of day
        current_hour = datetime.now().hour
        time_greeting = ""
        if current_hour < 12:
            time_greeting = "Good morning"
        elif current_hour < 17:
            time_greeting = "Good afternoon"
        else:
            time_greeting = "Good evening"
        
        return f"""{time_greeting} {name}! {emoji}

I'm {doctor_name}, your AI medical assistant. It's nice to meet you!

I see you're {age} years old, {gender.lower()}. First, I want you to know that I'm here to listen and help you feel better.

**How this works:**
1. You describe what you're feeling in your own words
2. I'll ask questions to understand better
3. We'll work together to figure out what might be going on
4. I'll suggest next steps that make sense for you

**Please tell me:**
• What symptoms you're experiencing right now
• When they started and how they've been changing
• How they're affecting your daily life
• Anything that makes them better or worse

Take your time - I'm here to listen carefully. What would you like to share first?"""
    
    def process_message(self, user_message: str, patient_data: Dict, conversation_history: List) -> Dict:
        """Process user message with human-like empathy and fast responses"""
        try:
            start_time = time.time()
            
            # Clean and analyze user message
            user_message_lower = user_message.lower().strip()
            
            # Check cache for similar messages
            cache_key = f"{user_message_lower[:50]}_{patient_data.get('name', '')}"
            if cache_key in self.response_cache:
                cached_response = self.response_cache[cache_key]
                cached_response['data']['processing_time'] = round(time.time() - start_time, 3)
                return cached_response
            
            # Human-like thinking simulation (brief pause for realism)
            thinking_time = random.uniform(0.1, 0.3)
            time.sleep(thinking_time)
            
            # Check for emergency keywords
            emergency_keywords = ['emergency', '911', 'heart attack', 'stroke', 'bleeding', 'unconscious', 'can\'t breathe']
            if any(keyword in user_message_lower for keyword in emergency_keywords):
                return self._handle_emergency_response(user_message, patient_data)
            
            # Extract symptoms with context
            symptoms = self._extract_symptoms_with_context(user_message, conversation_history)
            has_symptoms = len(symptoms) > 0
            
            # Get response based on message type with human-like flow
            if has_symptoms:
                response = self._handle_symptom_based_message_enhanced(user_message, symptoms, patient_data, conversation_history)
            elif any(keyword in user_message_lower for keyword in ['treatment', 'medicine', 'medication', 'prescription', 'drug']):
                response = self._handle_treatment_inquiry_enhanced(user_message, patient_data, conversation_history)
            elif any(keyword in user_message_lower for keyword in ['report', 'summary', 'record', 'download', 'document']):
                response = self._handle_report_request_enhanced(user_message, patient_data, conversation_history)
            elif any(keyword in user_message_lower for keyword in ['thank', 'thanks', 'appreciate', 'grateful']):
                response = self._handle_thankyou_message_enhanced(patient_data, conversation_history)
            elif any(keyword in user_message_lower for keyword in ['hi', 'hello', 'hey', 'greetings', 'morning', 'afternoon']):
                response = self._handle_greeting_enhanced(patient_data, conversation_history)
            elif any(keyword in user_message_lower for keyword in ['how are you', 'how do you do']):
                response = self._handle_personal_greeting(patient_data)
            elif any(keyword in user_message_lower for keyword in ['bye', 'goodbye', 'see you', 'farewell']):
                response = self._handle_goodbye_message(patient_data)
            elif any(keyword in user_message_lower for keyword in ['pain', 'hurt', 'ache', 'uncomfortable']):
                response = self._handle_pain_message(user_message, patient_data, conversation_history)
            else:
                response = self._handle_general_message_enhanced(user_message, patient_data, conversation_history)
            
            # Add human-like touches
            response = self._add_human_touches(response, conversation_history)
            
            # Add processing time
            processing_time = round(time.time() - start_time, 3)
            response['data']['processing_time'] = processing_time
            response['data']['doctor'] = self.current_doctor
            
            # Ensure response has proper structure for frontend
            response = self._ensure_response_structure(response)
            
            # Cache the response (except for emergencies)
            if response.get('type') != 'emergency':
                self.response_cache[cache_key] = response.copy()
                # Limit cache size
                if len(self.response_cache) > 100:
                    self.response_cache.pop(next(iter(self.response_cache)))
            
            return response
            
        except Exception as e:
            print(f"Error in process_message: {str(e)}")
            return self._get_error_response_enhanced(str(e), patient_data)
    
    def _handle_symptom_based_message_enhanced(self, user_message: str, symptoms: List[str], 
                                             patient_data: Dict, conversation_history: List) -> Dict:
        """Handle symptom descriptions with empathy and detailed analysis"""
        # Analyze symptoms
        analysis = self.symptom_checker.analyze_symptoms(symptoms, patient_data)
        
        # Get AI response with human-like empathy
        ai_response_text = self._get_ai_response_for_symptoms_enhanced(user_message, patient_data, symptoms, analysis)
        
        # Determine possible diseases with confidence
        possible_diseases = []
        for disease, info in self.medical_knowledge['common_diseases'].items():
            disease_symptoms = info['symptoms']
            matched_symptoms = set(symptoms) & set(disease_symptoms)
            if matched_symptoms:
                match_score = len(matched_symptoms) / len(disease_symptoms)
                if match_score > 0.2:  # Lower threshold for more possibilities
                    possible_diseases.append({
                        'name': disease.replace('_', ' ').title(),
                        'match_score': round(match_score, 2),
                        'description': info['description'],
                        'severity': info['severity'],
                        'urgency': info.get('urgency', 'medium'),
                        'common_in': info.get('common_in', 'Various ages'),
                        'recovery': info.get('recovery', 'Varies')
                    })
        
        # Sort by match score
        possible_diseases.sort(key=lambda x: x['match_score'], reverse=True)
        
        # Generate personalized treatment recommendations
        treatment_recommendations = self._get_personalized_treatment_recommendations(symptoms, possible_diseases, patient_data)
        
        # Prepare comprehensive response data for frontend
        response_data = {
            'symptoms': symptoms,
            'analysis': {
                'possible_conditions': possible_diseases[:5],  # Top 5
                'urgency_level': analysis.get('urgency_level', 'medium'),
                'severity': analysis.get('severity', 'moderate'),
                'recommended_actions': analysis.get('recommended_actions', [])
            },
            'suggested_diagnosis': possible_diseases[0]['name'] if possible_diseases else 'Requires further evaluation',
            'confidence': possible_diseases[0]['match_score'] if possible_diseases else 0.3,
            'urgency': analysis.get('urgency_level', 'medium'),
            'recommended_tests': self._suggest_comprehensive_tests(symptoms, patient_data),
            'treatment_recommendations': treatment_recommendations,
            'follow_up_advice': self._get_detailed_follow_up_advice(analysis.get('urgency_level', 'medium'), patient_data),
            'self_care_tips': self._get_self_care_tips(symptoms),
            'symptom_tracking': self._get_symptom_tracking_advice(symptoms)
        }
        
        return {
            'message': ai_response_text,
            'type': 'diagnosis',
            'data': response_data
        }
    
    def _handle_treatment_inquiry_enhanced(self, user_message: str, patient_data: Dict, 
                                         conversation_history: List) -> Dict:
        """Handle treatment inquiries with detailed, personalized information"""
        # Extract medication/disease from message with context
        medication_keywords = self._extract_medication_keywords_enhanced(user_message)
        disease_keywords = self._extract_disease_keywords(user_message)
        
        response_data = {}
        response_text = ""
        
        if medication_keywords:
            # Get detailed medication information
            medication_info = []
            for med in medication_keywords[:4]:  # Limit to 4 medications
                info = self.treatment_db.get_medication_info(med)
                if 'error' not in info:
                    # Enhance with additional info
                    info['common_side_effects'] = self._get_common_side_effects(med)
                    info['precautions'] = self._get_medication_precautions(med, patient_data)
                    info['interactions'] = self._get_potential_interactions(med)
                    medication_info.append(info)
            
            response_text = self._get_ai_response_for_medication_enhanced(user_message, medication_info, patient_data)
            
            response_data = {
                'medications': medication_info,
                'safety_notes': self._get_medication_safety_notes(),
                'when_to_consult': self._get_when_to_consult_doctor(medication_keywords),
                'alternative_options': self._get_alternative_treatments(medication_keywords, patient_data)
            }
        elif disease_keywords:
            # Get disease-specific treatment information
            treatment_info = self._get_disease_specific_treatments(disease_keywords, patient_data)
            response_text = self._get_ai_response_for_disease_treatment(user_message, treatment_info, patient_data)
            response_data = treatment_info
        else:
            # General treatment advice
            response_text = self._get_general_treatment_advice_enhanced(user_message, patient_data)
            response_data = {
                'general_advice': self._get_comprehensive_self_care_advice(),
                'when_to_seek_help': self._get_when_to_seek_medical_attention(),
                'home_remedies': self._get_home_remedies_based_on_context(conversation_history)
            }
        
        return {
            'message': response_text,
            'type': 'treatment_info',
            'data': response_data
        }
    
    def _handle_report_request_enhanced(self, user_message: str, patient_data: Dict, 
                                      conversation_history: List) -> Dict:
        """Handle report generation with detailed explanation"""
        name = patient_data.get('name', 'Patient')
        
        response_text = f"""I'd be happy to create a comprehensive medical report for you, {name}! 📋

**Here's what your personalized report will include:**

🔹 **Patient Summary**
• Your basic information and medical history
• Date and time of our consultation

🔹 **Symptom Analysis**
• Detailed list of symptoms you've described
• Timeline and severity assessment

🔹 **Medical Assessment**
• Possible conditions we've discussed
• Confidence levels for each possibility
• Urgency rating for follow-up

🔹 **Treatment Recommendations**
• Suggested medications (with proper disclaimers)
• Lifestyle modifications
• Self-care strategies

🔹 **Next Steps**
• Recommended medical tests
• Follow-up timeline
• Emergency warning signs to watch for

🔹 **Doctor's Notes**
• My personalized observations
• Important considerations for your healthcare provider

The report will be in PDF format, which you can:
• Save for your records
• Share with your doctor
• Use for insurance purposes
• Reference for future consultations

**Would you like me to generate this report now?** It typically takes about 15-30 seconds to create."""

        return {
            'message': response_text,
            'type': 'report_info',
            'data': {
                'can_generate': True,
                'includes': [
                    'Patient Information & History',
                    'Detailed Symptom Analysis',
                    'Possible Diagnoses with Confidence Levels',
                    'Personalized Treatment Plan',
                    'Recommended Medical Tests',
                    'Follow-up Instructions',
                    'Emergency Contact Information',
                    'Doctor\'s Summary Notes'
                ],
                'estimated_time': '15-30 seconds',
                'format': 'PDF (Printable & Shareable)'
            }
        }
    
    def _handle_emergency_response(self, user_message: str, patient_data: Dict) -> Dict:
        """Handle emergency situations with clear, urgent instructions"""
        name = patient_data.get('name', 'Patient')
        
        emergency_response = f"""🚨 **EMERGENCY MEDICAL ALERT** 🚨

{name}, I understand you're describing a serious situation. Based on your message, this appears to be a **MEDICAL EMERGENCY**.

**⚠️ IMMEDIATE ACTION REQUIRED ⚠️**

1. **STAY CALM** but act quickly
2. **CALL 911 or your local emergency number RIGHT NOW**
3. **DO NOT** try to drive yourself to the hospital
4. **STAY ON THE LINE** with emergency services
5. **FOLLOW THEIR INSTRUCTIONS** carefully

**If you're alone:**
• Call a neighbor or family member immediately
• Unlock your door so emergency personnel can enter
• If possible, sit or lie down while waiting for help

**Emergency Services Contact:**
• **Primary:** 911 (US) or your local emergency number
• **Poison Control:** 1-800-222-1222
• **Suicide Prevention:** 988 (US)
• **Crisis Text Line:** Text HOME to 741741

**What to tell the operator:**
• "I need an ambulance"
• Your exact location
• Your symptoms
• Your name and age
• Any medications you're taking

**Remember:**
• I'm an AI assistant and cannot provide emergency care
• Professional medical help is essential right now
• Every second counts in an emergency

**Please call for help immediately and then come back to let me know you're safe.** 🙏"""

        return {
            'message': emergency_response,
            'type': 'emergency',
            'data': {
                'is_emergency': True,
                'emergency_number': '911',
                'additional_contacts': [
                    {'name': 'Poison Control', 'number': '1-800-222-1222'},
                    {'name': 'Suicide Prevention Lifeline', 'number': '988'},
                    {'name': 'Crisis Text Line', 'number': 'Text HOME to 741741'}
                ],
                'immediate_actions': [
                    'Call emergency services',
                    'Do not drive yourself',
                    'Stay on the line with operator',
                    'Unlock door if alone',
                    'Sit or lie down if feeling faint'
                ]
            }
        }
    
    def _handle_thankyou_message_enhanced(self, patient_data: Dict, conversation_history: List) -> Dict:
        """Handle thank you messages with warmth and continuity"""
        name = patient_data.get('name', 'Patient')
        doctor = self.current_doctor
        
        # Check conversation context for personalized response
        last_diagnosis = None
        for msg in reversed(conversation_history):
            if msg.get('type') == 'diagnosis':
                last_diagnosis = msg.get('data', {}).get('suggested_diagnosis')
                break
        
        if last_diagnosis:
            response_text = f"""You're very welcome, {name}! {doctor['emoji']}

I'm genuinely glad I could help you understand more about {last_diagnosis.lower()}. It means a lot to me that you took the time to share your concerns.

**A few gentle reminders:**
• Be kind to yourself as you recover
• Follow the recommendations we discussed
• Don't hesitate to reach out if symptoms change
• Your health journey matters, and I'm here to support you

**Remember:** I'm available 24/7 if you have more questions or just need to check in about how you're feeling.

Is there anything else on your mind regarding your health today? I'm all ears! 👂"""
        else:
            response_text = f"""You're most welcome, {name}! {doctor['emoji']}

It's my pleasure to help. Taking care of your health shows real strength and self-care awareness.

**A little encouragement:**  
Remember that being proactive about your health is one of the best gifts you can give yourself. Whether it's following up on symptoms, asking questions, or just checking in - you're doing great!

**I'm here whenever you need:**
• To discuss new or changing symptoms
• To clarify any medical information
• Just to check in about how you're feeling
• Or if you have questions about treatments

Your well-being matters. What else can I assist you with today?"""

        return {
            'message': response_text,
            'type': 'general',
            'data': {
                'encouragement': True,
                'follow_up_available': True,
                'doctor': doctor
            }
        }
    
    def _handle_greeting_enhanced(self, patient_data: Dict, conversation_history: List) -> Dict:
        """Handle greeting messages with continuity awareness"""
        name = patient_data.get('name', 'Patient')
        doctor = self.current_doctor
        
        # Check if this is a return visit during same session
        if len(conversation_history) > 5:
            response_text = f"""Welcome back, {name}! {doctor['emoji']}

It's good to see you again. How are you feeling since we last spoke?

**Quick check-in:**
• Have your symptoms improved, stayed the same, or gotten worse?
• Did you have a chance to try any of the recommendations we discussed?
• Any new developments or concerns since our last conversation?

I'm here to continue supporting you on your health journey. What would you like to focus on today?"""
        else:
            response_text = f"""Hello again, {name}! {doctor['emoji']}

Nice to continue our conversation. How are you feeling right now?

**To help me understand better:**
• Are your symptoms the same as before, or have they changed?
• Is there anything specific you'd like to discuss or ask about?
• How has your day been in terms of how you're feeling?

I'm listening carefully and ready to help however I can. What's on your mind?"""

        return {
            'message': response_text,
            'type': 'general',
            'data': {
                'continuity_check': True,
                'personalized': True,
                'doctor': doctor
            }
        }
    
    def _handle_personal_greeting(self, patient_data: Dict) -> Dict:
        """Handle personal greetings like 'how are you'"""
        name = patient_data.get('name', 'Patient')
        doctor = self.current_doctor
        
        responses = [
            f"I'm doing well, thank you for asking! {doctor['emoji']} Just here ready to help you, {name}. How are you feeling today?",
            f"Thanks for asking! I'm here and fully operational, ready to assist you with your health concerns. How about you - how are you feeling right now, {name}?",
            f"I'm doing great, focused on helping you feel better! {doctor['emoji']} That's very kind of you to ask. How has your day been so far in terms of how you're feeling?"
        ]
        
        return {
            'message': random.choice(responses),
            'type': 'general',
            'data': {
                'friendly_exchange': True,
                'doctor': doctor
            }
        }
    
    def _handle_goodbye_message(self, patient_data: Dict) -> Dict:
        """Handle goodbye messages with care instructions"""
        name = patient_data.get('name', 'Patient')
        doctor = self.current_doctor
        
        response_text = f"""Goodbye, {name}! {doctor['emoji']}

It was a pleasure speaking with you today. Before you go:

**Final reminders:**
• Take good care of yourself
• Follow through with any recommendations we discussed
• Don't hesitate to return if symptoms change or new concerns arise
• Remember that your health is important

**Wishing you:**
🌿 Restful recovery  
💪 Strength and healing  
😊 Peace of mind

I'll be here whenever you need me - 24/7. Feel better soon!

**Take care and be well!** 🌟"""

        return {
            'message': response_text,
            'type': 'goodbye',
            'data': {
                'closing_remarks': True,
                'well_wishes': True,
                'doctor': doctor
            }
        }
    
    def _handle_pain_message(self, user_message: str, patient_data: Dict, conversation_history: List) -> Dict:
        """Special handling for pain-related messages with extra empathy"""
        name = patient_data.get('name', 'Patient')
        
        # Extract pain location and severity
        pain_keywords = self._extract_pain_details(user_message)
        
        response_text = f"""I hear you're experiencing pain, {name}. I'm sorry you're going through this. 😔

**First, let's acknowledge:** Pain is your body's way of telling you something needs attention. You're doing the right thing by addressing it.

**For immediate relief while we talk:**
• Try to find a comfortable position
• Take slow, deep breaths
• Apply a cold or warm compress if appropriate
• Avoid any movements that worsen the pain

**To help me understand better:**
1. **Location:** Where exactly is the pain?
2. **Type:** Is it sharp, dull, throbbing, burning, or aching?
3. **Scale:** On a scale of 
