# main.py
SESSIONS = {}


from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime
from medical_api import MedicalChatbot
from report_generator import ReportGenerator
import uuid
from flask import send_from_directory

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)

app.secret_key = 'medical-chatbot-secret-key-2024'
CORS(app)

# Initialize chatbot
chatbot = MedicalChatbot()


@app.route('/reports/<path:filename>')
def download_report(filename):
    reports_dir = os.path.join(BASE_DIR, 'reports')
    return send_from_directory(reports_dir, filename, as_attachment=True)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/api/start_session', methods=['POST'])
def start_session():
    patient_data = request.json
    if not patient_data:
        return jsonify({'error': 'No patient data'}), 400

    session_id = str(uuid.uuid4())

    SESSIONS[session_id] = {
        "patient_data": patient_data,
        "conversation": []
    }

    welcome_msg = chatbot.get_welcome_message(patient_data)

    SESSIONS[session_id]["conversation"].append({
        "role": "assistant",
        "message": welcome_msg,
        "timestamp": datetime.now().isoformat()
    })

    return jsonify({
        "session_id": session_id,
        "message": welcome_msg
    })


@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    session_id = data.get('session_id')

    if not user_message or not session_id:
        return jsonify({'error': 'Missing message or session_id'}), 400

    session_data = SESSIONS.get(session_id)
    if not session_data:
        return jsonify({'error': 'Invalid session'}), 400

    patient_data = session_data['patient_data']
    conversation_history = session_data['conversation']

    conversation_history.append({
        'role': 'user',
        'message': user_message,
        'timestamp': datetime.now().isoformat()
    })

    ai_response = chatbot.process_message(
        user_message=user_message,
        patient_data=patient_data,
        conversation_history=conversation_history
    )

    conversation_history.append({
        'role': 'assistant',
        'message': ai_response['message'],
        'type': ai_response.get('type', 'text'),
        'data': ai_response.get('data', {}),
        'timestamp': datetime.now().isoformat()
    })

    SESSIONS[session_id]['conversation'] = conversation_history[-20:]

    return jsonify({
        'response': ai_response,
        'session_id': session_id
    })


@app.route('/api/diagnosis', methods=['POST'])
def get_diagnosis():
    data = request.json
    symptoms = data.get('symptoms', [])
    patient_data = data.get('patient_data', {})

    if not symptoms:
        return jsonify({'error': 'No symptoms provided'}), 400

    diagnosis = chatbot.get_diagnosis(symptoms, patient_data)
    return jsonify(diagnosis)


@app.route('/api/treatment', methods=['POST'])
def get_treatment():
    data = request.json
    diagnosis = data.get('diagnosis', {})
    patient_data = data.get('patient_data', {})

    if not diagnosis:
        return jsonify({'error': 'No diagnosis provided'}), 400

    treatment = chatbot.get_treatment_plan(diagnosis, patient_data)
    return jsonify(treatment)


@app.route('/api/generate_report', methods=['POST'])
def generate_report():
    data = request.json
    session_id = data.get('session_id')

    if not session_id:
        return jsonify({'error': 'Session ID missing'}), 400

    session_data = SESSIONS.get(session_id)
    if not session_data:
        return jsonify({'error': 'Invalid session'}), 400

    patient_data = session_data['patient_data']
    conversation = session_data['conversation']

    report_generator = ReportGenerator()
    report_data = chatbot.prepare_report_data(patient_data, conversation)

    pdf_path = report_generator.generate_pdf_report(report_data, session_id)

    return jsonify({
        'report_url': f'/reports/{os.path.basename(pdf_path)}',
        'message': 'Report generated successfully'
    })


@app.route('/api/save_patient_record', methods=['POST'])
def save_patient_record():
    data = request.json
    patient_data = data.get('patient_data', {})
    conversation = data.get('conversation', [])
    diagnosis = data.get('diagnosis', {})
    treatment = data.get('treatment', {})

    if not patient_data:
        return jsonify({'error': 'No patient data provided'}), 400

    record_id = chatbot.save_patient_record(
        patient_data=patient_data,
        conversation=conversation,
        diagnosis=diagnosis,
        treatment=treatment
    )

    return jsonify({
        'record_id': record_id,
        'message': 'Patient record saved successfully'
    })


if __name__ == '__main__':
    os.makedirs('patient_records', exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, 'reports'), exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)

    app.run(debug=True, port=5000)
