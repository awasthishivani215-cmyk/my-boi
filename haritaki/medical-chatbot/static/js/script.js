// static/js/script.js - Lightweight version
document.addEventListener('DOMContentLoaded', function() {
    // Initialize variables
    let sessionId = null;
    let patientData = {};
    let conversation = [];

    // DOM Elements
    const patientForm = document.getElementById('patient-form');
    const patientDisplay = document.getElementById('patient-display');
    const startConsultationBtn = document.getElementById('start-consultation');
    const editProfileBtn = document.getElementById('edit-profile');
    const messageInput = document.getElementById('message-input');
    const sendMessageBtn = document.getElementById('send-message');
    const chatMessages = document.getElementById('chat-messages');
    const typingIndicator = document.getElementById('typing-indicator');
    const clearChatBtn = document.getElementById('clear-chat');
    const generateReportBtn = document.getElementById('generate-report-btn');

    // API Base URL
    const API_BASE = 'http://localhost:5000/api';

    // Initialize the app
    function initApp() {
        // Show typing indicator initially
        showTypingIndicator();
        setTimeout(hideTypingIndicator, 1500);

        // Load sample symptoms for suggestions
        loadSampleSymptoms();
    }

    // Start Consultation
    startConsultationBtn.addEventListener('click', function() {
        const name = document.getElementById('patient-name').value;
        const age = document.getElementById('patient-age').value;
        const gender = document.getElementById('patient-gender').value;
        const contact = document.getElementById('patient-contact').value;
        const medicalHistory = document.getElementById('medical-history').value;

        if (!name || !age || !gender) {
            alert('Please fill in all required fields: Name, Age, and Gender');
            return;
        }

        patientData = {
            name: name,
            age: parseInt(age),
            gender: gender,
            contact: contact || 'Not provided',
            medical_history: medicalHistory || 'None provided'
        };

        // Switch to profile display
        updatePatientDisplay();
        patientForm.style.display = 'none';
        patientDisplay.style.display = 'block';

        // Send to backend to start session
        startSession(patientData);
    });

    // Edit Profile
    editProfileBtn.addEventListener('click', function() {
        patientDisplay.style.display = 'none';
        patientForm.style.display = 'block';
    });

    // Send Message
    sendMessageBtn.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Clear Chat
    clearChatBtn.addEventListener('click', function() {
        if (confirm('Are you sure you want to clear the chat?')) {
            chatMessages.innerHTML = '';
            conversation = [];
            addMessage('assistant', 'Chat cleared. How can I help you today?');
        }
    });

    // Generate Report
    generateReportBtn.addEventListener('click', function() {
        generateMedicalReport();
    });

    // Quick action buttons
    document.querySelectorAll('.suggestion-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            messageInput.value = this.textContent;
            messageInput.focus();
        });
    });

    // API Functions
    async function startSession(patientData) {
        try {
            showTypingIndicator();
            
            const response = await fetch(`${API_BASE}/start_session`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(patientData)
            });

            const data = await response.json();
            
            if (data.session_id) {
                sessionId = data.session_id;
                hideTypingIndicator();
                
                // Update UI with welcome message
                addMessage('assistant', data.message);
                
                // Enable report generation
                generateReportBtn.disabled = false;
                
                console.log('Session started:', sessionId);
            }
        } catch (error) {
            console.error('Error starting session:', error);
            hideTypingIndicator();
            addMessage('assistant', 'Sorry, I encountered an error. Please try again.');
        }
    }

    async function sendMessage() {
        const message = messageInput.value.trim();
        if (!message) return;
        
        if (!sessionId) {
            alert('Please start a consultation first by filling in your information.');
            return;
        }

        // Add user message to chat
        addMessage('user', message);
        messageInput.value = '';
        
        // Show typing indicator
        showTypingIndicator();

        try {
            const response = await fetch(`${API_BASE}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    session_id: sessionId
                })
            });

            const data = await response.json();
            hideTypingIndicator();

            if (data.response) {
                const aiResponse = data.response;
                
                // Add AI response to chat
                addMessage('assistant', aiResponse.message);
                
                // Update medical panels if data is available
                if (aiResponse.data) {
                    updateMedicalPanels(aiResponse.data);
                }
                
                // Store in conversation history
                conversation.push({
                    role: 'user',
                    message: message,
                    timestamp: new Date().toISOString()
                });
                
                conversation.push({
                    role: 'assistant',
                    message: aiResponse.message,
                    data: aiResponse.data,
                    timestamp: new Date().toISOString()
                });
            }
        } catch (error) {
            console.error('Error sending message:', error);
            hideTypingIndicator();
            addMessage('assistant', 'Sorry, I encountered an error. Please try again.');
        }
    }

    async function generateMedicalReport() {
        if (!sessionId) {
            alert('Please start a consultation first.');
            return;
        }

        try {
            showTypingIndicator();
            generateReportBtn.disabled = true;
            generateReportBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
            
            const response = await fetch(`${API_BASE}/generate_report`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    session_id: sessionId
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            if (data.report_url) {
                // Create a temporary link to download the PDF
                const downloadLink = document.createElement('a');
                const fullUrl = `${window.location.origin}${data.report_url}`;

downloadLink.href = fullUrl;
downloadLink.setAttribute('download', '');

                
                // Add to DOM, click, and remove
                document.body.appendChild(downloadLink);
                downloadLink.click();
                document.body.removeChild(downloadLink);
                
                // Success notification
                const successMsg = `Medical report for ${patientData.name} has been generated successfully.`;
                addMessage('assistant', successMsg);
                
                // Also show a user notification
                showNotification('Report generated successfully!', 'success');
            } else if (data.error) {
                throw new Error(data.error);
            } else if (data.pdf_base64) {
                // Handle base64 PDF data
                const pdfData = data.pdf_base64;
                const byteCharacters = atob(pdfData);
                const byteNumbers = new Array(byteCharacters.length);
                
                for (let i = 0; i < byteCharacters.length; i++) {
                    byteNumbers[i] = byteCharacters.charCodeAt(i);
                }
                
                const byteArray = new Uint8Array(byteNumbers);
                const blob = new Blob([byteArray], { type: 'application/pdf' });
                const url = URL.createObjectURL(blob);
                
                const downloadLink = document.createElement('a');
                downloadLink.href = url;
                downloadLink.download = `medical_report_${patientData.name || 'patient'}_${new Date().toISOString().split('T')[0]}.pdf`;
                downloadLink.target = '_blank';
                
                document.body.appendChild(downloadLink);
                downloadLink.click();
                document.body.removeChild(downloadLink);
                
                // Clean up URL object
                setTimeout(() => URL.revokeObjectURL(url), 100);
                
                const successMsg = `Medical report for ${patientData.name} has been generated successfully.`;
                addMessage('assistant', successMsg);
                showNotification('Report generated successfully!', 'success');
            }
            
        } catch (error) {
            console.error('Error generating report:', error);
            addMessage('assistant', `Sorry, I could not generate the report: ${error.message}`);
            showNotification('Failed to generate report. Please try again.', 'error');
        } finally {
            hideTypingIndicator();
            generateReportBtn.disabled = false;
            generateReportBtn.innerHTML = '<i class="fas fa-file-pdf"></i> Generate Report';
        }
    }

    // UI Helper Functions
    function addMessage(sender, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        messageDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-${sender === 'assistant' ? 'user-md' : 'user'}"></i>
            </div>
            <div class="message-content">
                <div class="message-header">
                    <span class="sender">${sender === 'assistant' ? 'Dr. HealthAI' : patientData.name || 'You'}</span>
                    <span class="time">${timestamp}</span>
                </div>
                <div class="message-text">
                    <p>${formatMessage(content)}</p>
                </div>
            </div>
        `;
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function formatMessage(content) {
        // Convert line breaks to <br> tags
        return content.replace(/\n/g, '<br>');
    }

    function updatePatientDisplay() {
        document.getElementById('display-name').textContent = patientData.name;
        document.getElementById('display-age-gender').textContent = 
            `${patientData.age} years, ${patientData.gender}`;
        document.getElementById('display-contact').textContent = patientData.contact;
        document.getElementById('display-history').textContent = 
            patientData.medical_history.substring(0, 50) + '...';
    }

    function updateMedicalPanels(data) {
        // Update Diagnosis Panel
        if (data.suggested_diagnosis) {
            const diagnosisContent = document.getElementById('diagnosis-content');
            diagnosisContent.innerHTML = `
                <div class="diagnosis-card">
                    <h5>${data.suggested_diagnosis}</h5>
                    <p>Confidence: ${Math.round(data.confidence * 100)}%</p>
                    <p>Urgency: <span class="${data.urgency}">${data.urgency}</span></p>
                </div>
            `;
        }

        // Update Treatment Panel
        if (data.treatment_recommendations) {
            const treatmentContent = document.getElementById('treatment-content');
            
            if (Array.isArray(data.treatment_recommendations)) {
                treatmentContent.innerHTML = data.treatment_recommendations.map(rec => {
                    if (typeof rec === 'string') {
                        return `
                            <div class="treatment-card">
                                <h5>Treatment</h5>
                                <p>${rec}</p>
                            </div>
                        `;
                    } else if (typeof rec === 'object') {
                        return `
                            <div class="treatment-card">
                                <h5>${rec.name || rec.title || 'Treatment'}</h5>
                                <p>${rec.description || rec.details || 'Treatment recommendation'}</p>
                                ${rec.dosage ? `<small>Dosage: ${rec.dosage}</small>` : ''}
                            </div>
                        `;
                    }
                }).join('');
            } else if (typeof data.treatment_recommendations === 'string') {
                treatmentContent.innerHTML = `
                    <div class="treatment-card">
                        <h5>Treatment Recommendation</h5>
                        <p>${data.treatment_recommendations}</p>
                    </div>
                `;
            }
        }

        // Update Tests Panel - FIXED VERSION
        if (data.recommended_tests) {
            const testsContent = document.getElementById('tests-content');
            
            // Check if recommended_tests is an array
            if (Array.isArray(data.recommended_tests)) {
                // Handle array of strings or objects
                testsContent.innerHTML = data.recommended_tests.map(test => {
                    // If test is a string, use it directly
                    if (typeof test === 'string') {
                        return `
                            <div class="test-card">
                                <h5>${test}</h5>
                                <p>Recommended diagnostic test</p>
                            </div>
                        `;
                    } 
                    // If test is an object, access its properties
                    else if (typeof test === 'object') {
                        return `
                            <div class="test-card">
                                <h5>${test.name || test.test_name || test.title || 'Diagnostic Test'}</h5>
                                <p>${test.description || 'Recommended diagnostic test'}</p>
                                ${test.code ? `<small>Code: ${test.code}</small>` : ''}
                            </div>
                        `;
                    }
                }).join('');
            } 
            // If it's a single object (not an array)
            else if (typeof data.recommended_tests === 'object') {
                testsContent.innerHTML = `
                    <div class="test-card">
                        <h5>${data.recommended_tests.name || data.recommended_tests.test_name || 'Diagnostic Test'}</h5>
                        <p>${data.recommended_tests.description || 'Recommended diagnostic test'}</p>
                        ${data.recommended_tests.code ? `<small>Code: ${data.recommended_tests.code}</small>` : ''}
                    </div>
                `;
            }
            // If it's a string
            else if (typeof data.recommended_tests === 'string') {
                testsContent.innerHTML = `
                    <div class="test-card">
                        <h5>${data.recommended_tests}</h5>
                        <p>Recommended diagnostic test</p>
                    </div>
                `;
            }
        }
    }

    function showTypingIndicator() {
        typingIndicator.style.display = 'flex';
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function hideTypingIndicator() {
        typingIndicator.style.display = 'none';
    }

    function loadSampleSymptoms() {
        const symptoms = [
            "Fever", "Headache", "Cough", "Fatigue", "Nausea",
            "Sore throat", "Shortness of breath", "Chest pain",
            "Dizziness", "Back pain", "Joint pain", "Rash"
        ];

        // Add symptoms to quick suggestions
        const container = document.querySelector('.input-suggestions');
        symptoms.forEach(symptom => {
            const btn = document.createElement('button');
            btn.className = 'suggestion-btn';
            btn.textContent = `I have ${symptom.toLowerCase()}`;
            btn.addEventListener('click', function() {
                messageInput.value = this.textContent;
                messageInput.focus();
            });
            container.appendChild(btn);
        });
    }

    // Notification system
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        `;
        
        document.body.appendChild(notification);
        
        // Add CSS animation if not already present
        if (!document.querySelector('#notification-styles')) {
            const style = document.createElement('style');
            style.id = 'notification-styles';
            style.textContent = `
                .notification {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    padding: 12px 20px;
                    border-radius: 8px;
                    background: white;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    z-index: 1000;
                    animation: slideIn 0.3s ease, fadeOut 0.3s ease 2.7s forwards;
                }
                .notification.success {
                    border-left: 4px solid #28a745;
                    color: #28a745;
                }
                .notification.error {
                    border-left: 4px solid #dc3545;
                    color: #dc3545;
                }
                .notification.info {
                    border-left: 4px solid #17a2b8;
                    color: #17a2b8;
                }
                @keyframes slideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
                @keyframes fadeOut {
                    from { opacity: 1; }
                    to { opacity: 0; }
                }
            `;
            document.head.appendChild(style);
        }
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 3000);
    }

    // Feature Notifications
    function showFeatureNotification(feature) {
        const notification = document.createElement('div');
        notification.className = 'feature-notification';
        notification.innerHTML = `
            <i class="fas fa-info-circle"></i>
            <span>${feature} feature will be implemented in the next version</span>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    // Quick action buttons event listeners
    document.getElementById('symptom-checker').addEventListener('click', function() {
        showFeatureNotification('Symptom Checker');
    });

    document.getElementById('medication-info').addEventListener('click', function() {
        showFeatureNotification('Medication Information');
    });

    document.getElementById('emergency-guide').addEventListener('click', function() {
        const emergencyModal = document.getElementById('emergency-modal');
        emergencyModal.classList.add('show');
        
        emergencyModal.addEventListener('click', function(e) {
            if (e.target === emergencyModal || e.target.closest('.close-modal')) {
                emergencyModal.classList.remove('show');
            }
        });
    });

    // Initialize the app
    initApp();
});