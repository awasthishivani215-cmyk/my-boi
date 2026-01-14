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
3. **Scale:** On a scale of 1-10, with 10 being the worst pain imaginable, where is it?
4. **Duration:** How long have you had this pain?
5. **Triggers:** What makes it better or worse?

**Important:** If the pain is severe (8-10/10), sudden, or accompanied by chest pain, difficulty breathing, or weakness on one side, please seek emergency care immediately.

Take your time describing it to me. I'm here to listen and help. 💙"""

        return {
            'message': response_text,
            'type': 'pain_assessment',
            'data': {
                'pain_keywords': pain_keywords,
                'immediate_relief_tips': self._get_immediate_pain_relief_tips(pain_keywords),
                'assessment_questions': self._get_pain_assessment_questions()
            }
        }
    
    def _handle_general_message_enhanced(self, user_message: str, patient_data: Dict, 
                                       conversation_history: List) -> Dict:
        """Handle general medical conversations with enhanced understanding"""
        try:
            # Create a more empathetic system prompt
            system_prompt = f"""You are {self.current_doctor['name']}, a compassionate and highly knowledgeable AI medical assistant with a {self.current_doctor['style']} bedside manner.

**Patient Context:**
- Name: {patient_data.get('name', 'Patient')}
- Age: {patient_data.get('age', 'Not specified')}
- Gender: {patient_data.get('gender', 'Not specified')}
- Medical History: {patient_data.get('medical_history', 'None provided')}

**Your Communication Style:**
1. **Be empathetic and human-like** - Show genuine care and concern
2. **Use natural conversation flow** - Don't sound robotic or scripted
3. **Acknowledge emotions** - Validate how they might be feeling
4. **Be encouraging** - Offer hope and positive reinforcement
5. **Use appropriate emojis occasionally** - To add warmth (👂, 💙, 🤔, etc.)
6. **Ask clarifying questions** - When you need more information
7. **Provide clear explanations** - In simple, understandable language
8. **End with an open question** - To continue the conversation naturally

**Important Medical Guidelines:**
- Always prioritize safety
- Suggest seeing a real doctor for serious concerns
- Don't prescribe controlled substances
- Provide evidence-based information
- Consider their age and medical history

**Current conversation context:** {self._summarize_recent_conversation(conversation_history[-3:])}

Respond in a warm, professional, and helpful manner."""

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # Using 3.5 for faster response
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.8,  # Slightly higher for more varied responses
                max_tokens=350,
                presence_penalty=0.3,  # Encourage varied responses
                frequency_penalty=0.2   # Reduce repetition
            )
            
            ai_response = response.choices[0].message.content
            
            return {
                'message': ai_response,
                'type': 'general',
                'data': {
                    'ai_generated': True,
                    'doctor': self.current_doctor,
                    'tone': self.current_doctor['style']
                }
            }
            
        except Exception as e:
            # More empathetic fallback response
            return {
                'message': f"I understand you're reaching out about something important. I want to make sure I give you the best possible response. Could you tell me a bit more about what's on your mind? I'm here to listen and help in any way I can. 💭",
                'type': 'general',
                'data': {
                    'fallback': True,
                    'encouraging': True
                }
            }
    
    # ========== ENHANCED HELPER METHODS ==========
    
    def _extract_symptoms_with_context(self, text: str, conversation_history: List) -> List[str]:
        """Extract symptoms with context from conversation history"""
        symptoms = []
        text_lower = text.lower()
        
        # Check against known symptoms
        for symptom in self.medical_knowledge['symptoms_db']:
            if symptom in text_lower:
                symptoms.append(symptom)
        
        # Also check for symptom variations
        symptom_variations = {
            'headache': ['head pain', 'head ache', 'migraine', 'head pounding'],
            'stomach pain': ['abdominal pain', 'belly pain', 'tummy ache', 'stomach ache', 'cramps'],
            'fever': ['temperature', 'hot', 'chills', 'sweating', 'feverish'],
            'cough': ['coughing', 'hacking', 'clearing throat'],
            'fatigue': ['tired', 'exhausted', 'weak', 'low energy', 'lethargic'],
            'nausea': ['queasy', 'sick to stomach', 'feeling sick'],
            'anxiety': ['nervous', 'worried', 'panic', 'stressed', 'uneasy']
        }
        
        for symptom, variations in symptom_variations.items():
            if any(variation in text_lower for variation in variations):
                if symptom not in symptoms:
                    symptoms.append(symptom)
        
        # Check conversation history for mentioned symptoms
        for msg in conversation_history[-5:]:  # Last 5 messages
            if msg['role'] == 'user':
                msg_lower = msg['message'].lower()
                for symptom in self.medical_knowledge['symptoms_db']:
                    if symptom in msg_lower and symptom not in symptoms:
                        symptoms.append(symptom)
        
        return list(set(symptoms))[:15]  # Return unique, max 15
    
    def _extract_medication_keywords_enhanced(self, text: str) -> List[str]:
        """Extract medication keywords with brand names"""
        common_medications = [
            'aspirin', 'ibuprofen', 'acetaminophen', 'paracetamol', 'amoxicillin',
            'penicillin', 'omeprazole', 'atorvastatin', 'metformin', 'lisinopril',
            'levothyroxine', 'albuterol', 'prednisone', 'tramadol', 'codeine',
            'advil', 'tylenol', 'motrin', 'aleve', 'nexium', 'prilosec',
            'zoloft', 'prozac', 'lexapro', 'xanax', 'ambien', 'vicodin',
            'hydrocodone', 'oxycodone', 'morphine', 'insulin', 'warfarin'
        ]
        
        text_lower = text.lower()
        found_medications = []
        
        for med in common_medications:
            if med in text_lower:
                found_medications.append(med)
        
        return found_medications
    
    def _extract_disease_keywords(self, text: str) -> List[str]:
        """Extract disease keywords from text"""
        diseases = list(self.medical_knowledge['common_diseases'].keys())
        text_lower = text.lower()
        found_diseases = []
        
        for disease in diseases:
            disease_name = disease.replace('_', ' ')
            if disease_name in text_lower:
                found_diseases.append(disease)
        
        return found_diseases
    
    def _extract_pain_details(self, text: str) -> Dict:
        """Extract pain details from message"""
        pain_details = {
            'locations': [],
            'types': [],
            'severity': None,
            'duration': None
        }
        
        text_lower = text.lower()
        
        # Pain locations
        locations = ['head', 'neck', 'back', 'chest', 'stomach', 'abdomen', 'arm', 'leg', 
                    'joint', 'muscle', 'throat', 'ear', 'eye', 'tooth', 'pelvic']
        for location in locations:
            if location in text_lower:
                pain_details['locations'].append(location)
        
        # Pain types
        types = ['sharp', 'dull', 'throbbing', 'burning', 'aching', 'stabbing', 'cramping']
        for pain_type in types:
            if pain_type in text_lower:
                pain_details['types'].append(pain_type)
        
        # Extract severity (1-10 scale)
        import re
        severity_match = re.search(r'(\d+)/10|pain level.*?(\d+)|scale.*?(\d+)', text_lower)
        if severity_match:
            for group in severity_match.groups():
                if group and group.isdigit():
                    pain_details['severity'] = int(group)
                    break
        
        return pain_details
    
    def _get_ai_response_for_symptoms_enhanced(self, user_message: str, patient_data: Dict, 
                                             symptoms: List[str], analysis: Dict) -> str:
        """Get AI response for symptom descriptions with enhanced empathy"""
        try:
            doctor = self.current_doctor
            
            system_prompt = f"""You are {doctor['name']}, a {doctor['style']} and empathetic AI medical assistant.

**Patient Context:**
- Name: {patient_data.get('name', 'Patient')}
- Age: {patient_data.get('age', 'Not specified')}
- Gender: {patient_data.get('gender', 'Not specified')}
- Symptoms: {', '.join(symptoms)}
- Severity Assessment: {analysis.get('severity', 'unknown')}
- Urgency Level: {analysis.get('urgency_level', 'medium')}

**Your Response Should:**
1. Start with empathy and validation of their experience
2. Show genuine concern for their well-being
3. Provide clear, understandable medical assessment
4. Offer specific, actionable recommendations
5. Explain when to seek emergency care
6. End with an encouraging, hopeful note
7. Use occasional appropriate emojis for warmth
8. Sound natural and conversational, not robotic

**Medical Guidelines:**
- Be honest about limitations
- Never guarantee a specific diagnosis
- Always recommend professional follow-up for serious symptoms
- Provide evidence-based information
- Consider their specific circumstances

**Tone:** Warm, professional, reassuring, and human-like
**Length:** 250-300 words maximum
**Style:** Conversational with appropriate medical terminology explained simply"""

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.75,
                max_tokens=400,
                presence_penalty=0.2
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            # Enhanced fallback response
            symptom_text = ', '.join(symptoms) if symptoms else "what you're experiencing"
            
            fallback_responses = [
                f"""Thank you for sharing that you're experiencing {symptom_text}. I want you to know I'm taking this seriously and I'm here to help you understand what might be going on.

Based on the symptoms you've described, here's what I'm thinking:

**Initial Assessment:**
It sounds like you might be dealing with a common health issue that many people experience. The good news is that most of these conditions are manageable with proper care.

**What I Recommend:**
1. **Monitor closely:** Keep track of how your symptoms change over the next 24 hours
2. **Rest and hydrate:** Your body needs energy to heal
3. **Consider OTC options:** Over-the-counter medications might help with symptom relief
4. **Watch for red flags:** If symptoms worsen suddenly, seek medical attention

**Next Steps:**
Could you tell me a bit more about when these symptoms started and how they've been affecting your daily activities? This will help me provide more personalized guidance.

Remember, I'm here to support you through this. 💙""",
                
                f"""I hear you're dealing with {symptom_text}, and I want you to know I understand how concerning that can be. Let's work through this together.

**First, take a deep breath.** You're doing the right thing by addressing your symptoms.

**Based on what you've shared:**
Your symptoms suggest a condition that typically responds well to proper care. Many people experience similar issues and recover fully.

**My suggestions for now:**
• Give your body the rest it needs
• Stay well-hydrated with water and electrolyte drinks if needed
• Consider gentle symptom relief if appropriate
• Keep a simple symptom diary

**Important:**
If you experience severe pain, difficulty breathing, or sudden worsening of symptoms, please seek immediate medical attention.

**To help me help you better:**
Could you describe how these symptoms started and what makes them better or worse? The more context I have, the better I can assist you.

You're not alone in this - I'm here to guide you. 🌿"""
            ]
            
            return random.choice(fallback_responses)
    
    def _get_personalized_treatment_recommendations(self, symptoms: List[str], 
                                                  possible_diseases: List[Dict], 
                                                  patient_data: Dict) -> List[Dict]:
        """Get personalized treatment recommendations"""
        treatments = []
        
        # Add disease-specific treatments
        if possible_diseases:
            primary_disease = possible_diseases[0]['name'].lower().replace(' ', '_')
            if primary_disease in self.medical_knowledge['common_diseases']:
                disease_info = self.medical_knowledge['common_diseases'][primary_disease]
                treatments.extend(self._get_disease_specific_treatments_list(disease_info))
        
        # Add symptom-specific treatments
        treatments.extend(self._get_symptom_specific_treatments(symptoms))
        
        # Add general wellness recommendations
        treatments.extend([
            {
                'name': 'Adequate Rest',
                'description': '7-9 hours of quality sleep to support immune function',
                'type': 'lifestyle',
                'priority': 'high',
                'duration': 'Daily'
            },
            {
                'name': 'Proper Hydration',
                'description': '8-10 glasses of water daily, more if feverish',
                'type': 'nutrition',
                'priority': 'high',
                'duration': 'Daily'
            },
            {
                'name': 'Balanced Nutrition',
                'description': 'Focus on fruits, vegetables, and lean proteins',
                'type': 'nutrition',
                'priority': 'medium',
                'duration': 'Daily'
            }
        ])
        
        # Add age-specific recommendations
        age = patient_data.get('age', 0)
        if age > 60:
            treatments.append({
                'name': 'Gentle Movement',
                'description': 'Light walking or stretching as tolerated',
                'type': 'exercise',
                'priority': 'medium',
                'duration': 'Daily, as able'
            })
        elif age < 18:
            treatments.append({
                'name': 'Parental Monitoring',
                'description': 'Close observation by caregiver',
                'type': 'care',
                'priority': 'high',
                'duration': 'Until recovered'
            })
        
        return treatments[:8]  # Return max 8 recommendations
    
    def _get_disease_specific_treatments_list(self, disease_info: Dict) -> List[Dict]:
        """Get treatments for specific diseases"""
        disease_name = disease_info.get('description', '').lower()
        
        treatments_map = {
            'common cold': [
                {'name': 'Nasal Saline Spray', 'description': 'For congestion relief without medication', 'type': 'self_care', 'priority': 'medium'},
                {'name': 'Steam Inhalation', 'description': 'Warm steam to loosen mucus', 'type': 'self_care', 'priority': 'low'},
                {'name': 'Throat Lozenges', 'description': 'For sore throat relief', 'type': 'medication', 'priority': 'medium'}
            ],
            'influenza': [
                {'name': 'Antiviral Medication', 'description': 'If prescribed within 48 hours of symptoms', 'type': 'medication', 'priority': 'high'},
                {'name': 'Fever Management', 'description': 'Regular monitoring and medication as needed', 'type': 'monitoring', 'priority': 'high'},
                {'name': 'Isolation', 'description': 'Rest at home to prevent spread', 'type': 'prevention', 'priority': 'high'}
            ],
            'migraine': [
                {'name': 'Dark, Quiet Environment', 'description': 'Reduce sensory stimulation', 'type': 'environment', 'priority': 'high'},
                {'name': 'Hydration with Electrolytes', 'description': 'Prevent dehydration headache', 'type': 'nutrition', 'priority': 'medium'},
                {'name': 'Trigger Avoidance', 'description': 'Identify and avoid personal triggers', 'type': 'prevention', 'priority': 'medium'}
            ],
            'gastroenteritis': [
                {'name': 'Oral Rehydration Solution', 'description': 'Restore electrolyte balance', 'type': 'nutrition', 'priority': 'high'},
                {'name': 'BRAT Diet', 'description': 'Bananas, Rice, Applesauce, Toast - easy to digest', 'type': 'diet', 'priority': 'high'},
                {'name': 'Probiotics', 'description': 'Restore gut flora after symptoms subside', 'type': 'supplement', 'priority': 'low'}
            ]
        }
        
        for key, treatments in treatments_map.items():
            if key in disease_name:
                return treatments
        
        # Default treatments if no specific match
        return [
            {'name': 'Symptom Management', 'description': 'Address specific symptoms as they arise', 'type': 'general', 'priority': 'medium'},
            {'name': 'Medical Follow-up', 'description': 'Consult healthcare provider for proper diagnosis', 'type': 'medical', 'priority': 'high'}
        ]
    
    def _get_symptom_specific_treatments(self, symptoms: List[str]) -> List[Dict]:
        """Get treatments for specific symptoms"""
        treatments = []
        
        symptom_treatments = {
            'fever': {'name': 'Fever Reducers', 'description': 'Acetaminophen or ibuprofen as directed', 'type': 'medication', 'priority': 'medium'},
            'headache': {'name': 'Headache Relief', 'description': 'Rest in quiet environment, consider OTC pain relief', 'type': 'medication', 'priority': 'medium'},
            'cough': {'name': 'Cough Management', 'description': 'Honey (adults), cough drops, humidifier', 'type': 'self_care', 'priority': 'low'},
            'sore throat': {'name': 'Throat Soothers', 'description': 'Warm salt water gargle, throat lozenges', 'type': 'self_care', 'priority': 'medium'},
            'nausea': {'name': 'Nausea Control', 'description': 'Ginger tea, small bland meals, avoid strong smells', 'type': 'diet', 'priority': 'medium'},
            'fatigue': {'name': 'Energy Conservation', 'description': 'Pace activities, prioritize rest', 'type': 'lifestyle', 'priority': 'medium'}
        }
        
        for symptom in symptoms:
            if symptom in symptom_treatments:
                treatments.append(symptom_treatments[symptom])
        
        return list({t['name']: t for t in treatments}.values())  # Remove duplicates
    
    def _suggest_comprehensive_tests(self, symptoms: List[str], patient_data: Dict) -> List[Dict]:
        """Suggest comprehensive diagnostic tests"""
        tests = []
        
        # Basic tests for most situations
        basic_tests = [
            {'name': 'Complete Blood Count (CBC)', 'purpose': 'General health screening', 'urgency': 'medium'},
            {'name': 'Vital Signs Check', 'purpose': 'Blood pressure, heart rate, temperature', 'urgency': 'low'}
        ]
        
        # Symptom-specific tests
        if any(s in symptoms for s in ['fever', 'infection']):
            tests.append({'name': 'Inflammatory Markers (CRP, ESR)', 'purpose': 'Check for inflammation', 'urgency': 'medium'})
        
        if any(s in symptoms for s in ['cough', 'shortness of breath', 'chest pain']):
            tests.extend([
                {'name': 'Chest X-ray', 'purpose': 'Check lung health', 'urgency': 'medium'},
                {'name': 'Pulse Oximetry', 'purpose': 'Measure oxygen levels', 'urgency': 'low'}
            ])
        
        if any(s in symptoms for s in ['abdominal pain', 'nausea', 'vomiting', 'diarrhea']):
            tests.extend([
                {'name': 'Basic Metabolic Panel', 'purpose': 'Check organ function and electrolytes', 'urgency': 'medium'},
                {'name': 'Stool Test (if indicated)', 'purpose': 'Check for infections', 'urgency': 'low'}
            ])
        
        if any(s in symptoms for s in ['headache', 'dizziness', 'neurological symptoms']):
            tests.append({'name': 'Neurological Examination', 'purpose': 'Comprehensive neurological assessment', 'urgency': 'medium'})
        
        # Age-specific tests
        age = patient_data.get('age', 0)
        if age > 40:
            tests.append({'name': 'Blood Glucose Test', 'purpose': 'Check for diabetes', 'urgency': 'low'})
        
        # Combine and prioritize
        all_tests = basic_tests + tests
        unique_tests = []
        seen = set()
        for test in all_tests:
            if test['name'] not in seen:
                seen.add(test['name'])
                unique_tests.append(test)
        
        # Sort by urgency
        urgency_order = {'high': 0, 'medium': 1, 'low': 2}
        unique_tests.sort(key=lambda x: urgency_order.get(x['urgency'], 3))
        
        return unique_tests[:6]  # Return max 6 tests
    
    def _get_detailed_follow_up_advice(self, urgency_level: str, patient_data: Dict) -> Dict:
        """Get detailed follow-up advice"""
        name = patient_data.get('name', 'Patient')
        
        advice_map = {
            'high': {
                'timeline': 'IMMEDIATELY',
                'action': 'Go to Emergency Room or Call 911',
                'monitoring': 'Continuous, do not leave alone',
                'preparation': 'Bring ID, insurance card, medication list',
                'message': f"{name}, this requires urgent medical attention. Please don't delay."
            },
            'medium': {
                'timeline': 'Within 24-48 hours',
                'action': 'Schedule appointment with Primary Care Physician',
                'monitoring': 'Twice daily symptom check',
                'preparation': 'Note symptom changes, prepare questions for doctor',
                'message': f"{name}, it's important to follow up with your doctor soon to get proper evaluation."
            },
            'low': {
                'timeline': 'Within 1 week if symptoms persist',
                'action': 'Monitor and follow up if no improvement',
                'monitoring': 'Daily symptom log',
                'preparation': 'Track symptom patterns and triggers',
                'message': f"{name}, most likely this will resolve on its own, but keep an eye on it."
            }
        }
        
        advice = advice_map.get(urgency_level, {
            'timeline': 'Within 2-3 days',
            'action': 'Consult healthcare provider',
            'monitoring': 'Monitor symptoms',
            'preparation': 'Keep notes on symptoms',
            'message': f"{name}, it's always good to check with a professional if you're concerned."
        })
        
        # Add specific instructions
        advice['specific_instructions'] = [
            'Keep a symptom diary with times and severity',
            'Note any triggers or relieving factors',
            'Track temperature if fever is present',
            'Record medication use and effects'
        ]
        
        return advice
    
    def _get_self_care_tips(self, symptoms: List[str]) -> List[str]:
        """Get self-care tips for symptoms"""
        tips = []
        
        # General wellness tips
        general_tips = [
            "Stay hydrated with water and herbal teas",
            "Get plenty of rest - your body heals during sleep",
            "Eat nutritious, easily digestible foods",
            "Practice gentle breathing exercises for relaxation",
            "Maintain a comfortable room temperature"
        ]
        
        # Symptom-specific tips
        symptom_tips = {
            'fever': ["Use lukewarm sponge baths to reduce fever", "Dress in light, breathable clothing"],
            'cough': ["Use a humidifier in your room", "Prop yourself up with pillows at night"],
            'headache': ["Apply cold compress to forehead", "Reduce screen time and bright lights"],
            'nausea': ["Sip ginger tea or ginger ale", "Eat small, frequent meals"],
            'fatigue': ["Pace your activities throughout the day", "Take short, frequent rests"]
        }
        
        tips.extend(general_tips)
        
        for symptom in symptoms:
            if symptom in symptom_tips:
                tips.extend(symptom_tips[symptom])
        
        return list(set(tips))[:8]  # Return unique, max 8 tips
    
    def _get_symptom_tracking_advice(self, symptoms: List[str]) -> Dict:
        """Get advice for tracking symptoms"""
        return {
            'what_to_track': [
                'Symptom severity (1-10 scale)',
                'Time of day when worst/best',
                'Activities before symptoms change',
                'Food and drink consumption',
                'Medication timing and effects',
                'Sleep quality and duration'
            ],
            'tracking_methods': [
                'Use a notebook or smartphone app',
                'Take photos if visual symptoms (rash, swelling)',
                'Record temperature if fever present',
                'Note emotional state alongside physical symptoms'
            ],
            'when_to_review': [
                'Daily for acute symptoms',
                'Weekly for chronic issues',
                'Before doctor appointments',
                'When trying new treatments'
            ]
        }
    
    # ========== ADDITIONAL ENHANCED METHODS ==========
    
    def _add_human_touches(self, response: Dict, conversation_history: List) -> Dict:
        """Add human-like touches to responses"""
        # Add occasional thinking indicators
        thinking_indicators = ["Let me think about that...", "Hmm, that's an important point...", 
                              "I want to make sure I understand correctly...", "That's a good question..."]
        
        # Only add thinking indicator occasionally (20% chance)
        if random.random() < 0.2 and len(response['message']) > 100:
            indicator = random.choice(thinking_indicators)
            response['message'] = f"{indicator}\n\n{response['message']}"
        
        # Add occasional empathy statements based on conversation
        if response['type'] in ['diagnosis', 'pain_assessment']:
            empathy_statements = [
                "\n\nI know this can be worrying, but you're taking the right steps by addressing it. 💙",
                "\n\nRemember to be kind to yourself while you're not feeling well. Healing takes time. 🌿",
                "\n\nIt's completely normal to feel concerned about health symptoms. You're not alone in this. 🤝"
            ]
            
            if random.random() < 0.3:
                response['message'] += random.choice(empathy_statements)
        
        # Occasionally add a follow-up question to continue conversation
        if response['type'] == 'general' and random.random() < 0.25:
            follow_ups = [
                "\n\nHow does that sound to you?",
                "\n\nDoes that make sense based on what you're experiencing?",
                "\n\nWhat are your thoughts on this approach?",
                "\n\nIs there anything about this that you'd like me to clarify?"
            ]
            response['message'] += random.choice(follow_ups)
        
        return response
    
    def _summarize_recent_conversation(self, recent_messages: List) -> str:
        """Summarize recent conversation for context"""
        if not recent_messages:
            return "First interaction with patient."
        
        summary = "Recent discussion: "
        points = []
        
        for msg in recent_messages[-3:]:  # Last 3 messages
            role = "Patient" if msg['role'] == 'user' else "Doctor"
            content = msg['message'][:100] + "..." if len(msg['message']) > 100 else msg['message']
            points.append(f"{role}: {content}")
        
        return summary + " | ".join(points)
    
    def _get_error_response_enhanced(self, error_msg: str = "", patient_data: Dict = None) -> Dict:
        """Get enhanced error response with empathy"""
        name = patient_data.get('name', 'Patient') if patient_data else "Patient"
        
        error_responses = [
            f"I apologize, {name}. I'm having a bit of technical difficulty right now. Could you please rephrase your question or try again in a moment? I want to make sure I give you the best possible response. 🔧",
            f"Thank you for your patience, {name}. I'm experiencing a temporary issue. Could you please ask your question again? I'm here and ready to help you. 💭",
            f"I'm sorry, {name}. There seems to be a technical glitch on my end. Please try asking your question again, and I'll do my best to provide a helpful response. Your health questions are important to me. 🌟"
        ]
        
        return {
            'message': random.choice(error_responses),
            'type': 'error',
            'data': {
                'error': error_msg[:100] if error_msg else 'Technical issue',
                'suggested_action': 'Please rephrase or try again',
                'empathy_level': 'high'
            }
        }
    
    def _ensure_response_structure(self, response: Dict) -> Dict:
        """Ensure response has proper structure for frontend"""
        required_keys = ['message', 'type']
        for key in required_keys:
            if key not in response:
                response[key] = ''
        
        # Ensure data exists with timestamp
        if 'data' not in response:
            response['data'] = {}
        
        # Add timestamp
        response['data']['timestamp'] = datetime.now().isoformat()
        
        # Clean up message text
        if response['message']:
            response['message'] = response['message'].strip()
        
        return response
    
    # ========== EXISTING METHODS WITH MINIMAL CHANGES ==========
    
    def get_diagnosis(self, symptoms: List[str], patient_data: Dict) -> Dict:
        """Get diagnosis based on symptoms - Frontend optimized"""
        try:
            analysis = self.symptom_checker.analyze_symptoms(symptoms, patient_data)
            
            # Get possible diseases
            possible_diseases = []
            for disease, info in self.medical_knowledge['common_diseases'].items():
                disease_symptoms = info['symptoms']
                matched_symptoms = set(symptoms) & set(disease_symptoms)
                if matched_symptoms:
                    match_score = len(matched_symptoms) / len(disease_symptoms)
                    if match_score > 0.3:
                        possible_diseases.append({
                            'name': disease.replace('_', ' ').title(),
                            'match_score': round(match_score, 2),
                            'description': info['description'],
                            'severity': info['severity'],
                            'urgency': info.get('urgency', 'medium')
                        })
            
            # Sort by match score
            possible_diseases.sort(key=lambda x: x['match_score'], reverse=True)
            
            # Generate AI summary
            ai_summary = self._generate_diagnosis_summary(symptoms, possible_diseases, patient_data)
            
            return {
                'status': 'success',
                'symptoms': symptoms,
                'analysis': analysis,
                'possible_diseases': possible_diseases[:5],
                'ai_summary': ai_summary,
                'recommended_tests': self._suggest_comprehensive_tests(symptoms, patient_data),
                'urgency_level': analysis.get('urgency_level', 'medium')
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'symptoms': symptoms,
                'analysis': {'urgency_level': 'unknown'},
                'possible_diseases': []
            }
    
    def _generate_diagnosis_summary(self, symptoms: List[str], possible_diseases: List[Dict], 
                                   patient_data: Dict) -> str:
        """Generate AI summary of diagnosis"""
        try:
            symptom_text = ', '.join(symptoms)
            disease_text = ', '.join([d['name'] for d in possible_diseases[:3]])
            
            prompt = f"""Based on symptoms: {symptom_text}
Possible conditions: {disease_text}
Patient: {patient_data.get('name')}, {patient_data.get('age')}

Provide a warm, empathetic 3-4 sentence summary of the likely diagnosis and next steps. Use a comforting tone."""

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6,
                max_tokens=200
            )
            
            return response.choices[0].message.content
            
        except:
            return "Based on the symptoms described, I recommend further evaluation by a healthcare provider for proper diagnosis and treatment."
    
    def get_treatment_plan(self, diagnosis: Dict, patient_data: Dict) -> Dict:
        """Generate treatment plan for diagnosis"""
        try:
            # Extract primary diagnosis
            primary_diagnosis = diagnosis.get('primary_diagnosis', '')
            symptoms = diagnosis.get('symptoms', [])
            
            # Get treatment from database
            if primary_diagnosis:
                treatment_info = self.treatment_db.get_treatment(diagnosis, patient_data)
            else:
                treatment_info = self.treatment_db._get_general_treatment(diagnosis, patient_data)
            
            # Add patient-specific information
            treatment_info['patient_name'] = patient_data.get('name', 'Patient')
            treatment_info['consultation_date'] = datetime.now().strftime('%Y-%m-%d')
            
            # Generate prescription if appropriate
            if symptoms and len(symptoms) > 0:
                treatment_info['sample_prescription'] = self._generate_sample_prescription(symptoms, patient_data)
            
            return {
                'status': 'success',
                'treatment_plan': treatment_info
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'basic_recommendations': [
                    "Rest and hydrate",
                    "Monitor symptoms",
                    "Consult healthcare provider"
                ]
            }
    
    def _generate_sample_prescription(self, symptoms: List[str], patient_data: Dict) -> Dict:
        """Generate sample prescription information"""
        prescription = {
            'patient': patient_data.get('name', 'Patient'),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'medications': [],
            'instructions': 'Take as directed with food. Discontinue if adverse reactions occur.',
            'provider': f"{self.current_doctor['name']} (AI Medical Assistant)",
            'disclaimer': 'SAMPLE PRESCRIPTION ONLY. Actual medications must be prescribed by a licensed healthcare provider after proper evaluation.',
            'follow_up': 'Schedule follow-up appointment in 1-2 weeks if symptoms persist.'
        }
        
        # Add medications based on symptoms
        if any(s in symptoms for s in ['fever', 'pain', 'headache']):
            prescription['medications'].append({
                'name': 'Acetaminophen',
                'dosage': '500mg',
                'frequency': 'Every 6 hours as needed for pain/fever',
                'duration': '3-5 days',
                'max_daily': '4000mg',
                'notes': 'Take with food, avoid alcohol'
            })
        
        if any(s in symptoms for s in ['cough', 'congestion']):
            prescription['medications'].append({
                'name': 'Dextromethorphan',
                'dosage': '30mg',
                'frequency': 'Every 6-8 hours',
                'duration': '7 days',
                'max_daily': '120mg',
                'notes': 'Do not use with MAO inhibitors'
            })
        
        if any(s in symptoms for s in ['allergy', 'itch', 'rash']):
            prescription['medications'].append({
                'name': 'Cetirizine',
                'dosage': '10mg',
                'frequency': 'Once daily',
                'duration': 'As needed',
                'max_daily': '10mg',
                'notes': 'May cause drowsiness, avoid driving'
            })
        
        return prescription
    
    def prepare_report_data(self, patient_data: Dict, conversation_history: List) -> Dict:
        """Prepare data for report generation"""
        # Extract information from conversation
        symptoms = []
        diagnoses = []
        treatments = []
        
        for msg in conversation_history:
            if msg.get('type') == 'diagnosis':
                data = msg.get('data', {})
                if 'symptoms' in data:
                    symptoms.extend(data['symptoms'])
                if 'suggested_diagnosis' in data:
                    diagnoses.append(data['suggested_diagnosis'])
            
            elif msg.get('type') in ['treatment_info', 'treatment_advice']:
                data = msg.get('data', {})
                if 'treatment_recommendations' in data:
                    treatments.extend(data['treatment_recommendations'])
        
        # Create unique lists
        unique_symptoms = list(set(symptoms))
        unique_diagnoses = list(set(diagnoses))
        
        # Prepare summary
        summary = f"""Medical Consultation Summary
Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Patient: {patient_data.get('name')}
Age: {patient_data.get('age')}
Gender: {patient_data.get('gender')}

Symptoms Discussed: {', '.join(unique_symptoms) if unique_symptoms else 'None specified'}
Possible Diagnoses: {', '.join(unique_diagnoses) if unique_diagnoses else 'Requires further evaluation'}

Consultation Summary: AI-assisted medical consultation completed with {self.current_doctor['name']}.
Overall assessment based on symptoms described and patient history."""

        return {
            'patient': patient_data,
            'consultation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'symptoms': unique_symptoms,
            'diagnosis': unique_diagnoses,
            'treatment_plan': treatments[:5],  # Limit to 5 treatments
            'summary': summary,
            'doctor': self.current_doctor,
            'recommendations': [
                "Follow up with healthcare provider for proper evaluation",
                "Monitor symptoms as discussed during consultation",
                "Complete any recommended treatments as appropriate",
                "Seek emergency care if symptoms worsen suddenly",
                "Maintain open communication with healthcare providers"
            ]
        }
    
    def save_patient_record(self, patient_data: Dict, conversation: List, 
                           diagnosis: Dict, treatment: Dict) -> str:
        """Save patient record to file"""
        import uuid
        from datetime import datetime
        
        record_id = str(uuid.uuid4())
        filename = f"patient_records/record_{record_id}.json"
        
        record = {
            'record_id': record_id,
            'timestamp': datetime.now().isoformat(),
            'patient_data': patient_data,
            'conversation_summary': self._summarize_conversation(conversation),
            'diagnosis': diagnosis,
            'treatment': treatment,
            'doctor': self.current_doctor,
            'metadata': {
                'version': '2.0',
                'system': 'Enhanced Medical Chatbot',
                'created_by': 'Dr. HealthAI Pro'
            }
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(record, f, indent=2)
            return record_id
        except Exception as e:
            return f"Error saving record: {str(e)}"
    
    # Additional helper methods would be defined here...