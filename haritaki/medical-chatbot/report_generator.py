# report_generator.py
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime
import os
from typing import Dict, List, Any
import json

class ReportGenerator:
    def __init__(self):
        """Initialize report generator"""
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.report_path = os.path.join(BASE_DIR, "reports")

        
        # Create reports directory if it doesn't exist
        os.makedirs(self.report_path, exist_ok=True)
    
    def _create_custom_styles(self):
        """Create custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='MedicalTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=30,
            alignment=1  # Center
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='MedicalSubtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#34495E'),
            spaceAfter=20
        ))
        
        # Normal text style
        self.styles.add(ParagraphStyle(
            name='MedicalText',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=12
        ))
        
        # Bold style for labels
        self.styles.add(ParagraphStyle(
            name='MedicalBold',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#2C3E50'),
            fontName='Helvetica-Bold',
            spaceAfter=6
        ))
        
        # Footer style
        self.styles.add(ParagraphStyle(
            name='MedicalFooter',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.gray,
            alignment=1  # Center
        ))
    
    def generate_pdf_report(self, report_data: Dict, session_id: str) -> str:
        """Generate PDF medical report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"medical_report_{session_id}_{timestamp}.pdf"
        filepath = os.path.join(self.report_path, filename)
        
        # Create document
        doc = SimpleDocTemplate(
            filepath,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Create story (content)
        story = []
        
        # Add header
        story.extend(self._create_header(report_data))
        
        # Add patient information
        story.extend(self._create_patient_info_section(report_data))
        
        # Add symptoms
        story.extend(self._create_symptoms_section(report_data))
        
        # Add diagnosis
        story.extend(self._create_diagnosis_section(report_data))
        
        # Add treatment plan
        story.extend(self._create_treatment_section(report_data))
        
        # Add recommendations
        story.extend(self._create_recommendations_section(report_data))
        
        # Add summary
        story.extend(self._create_summary_section(report_data))
        
        # Add footer
        story.extend(self._create_footer())
        
        # Build PDF
        doc.build(story)
        
        return filepath
    
    def _create_header(self, report_data: Dict) -> List:
        """Create report header"""
        elements = []
        
        # Title
        title = Paragraph("MEDICAL CONSULTATION REPORT", self.styles['MedicalTitle'])
        elements.append(title)
        
        # Subtitle
        subtitle = Paragraph("AI-Powered Medical Assessment", self.styles['MedicalSubtitle'])
        elements.append(subtitle)
        
        # Date
        date_str = report_data.get('consultation_date', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        date_para = Paragraph(f"Date: {date_str}", self.styles['MedicalText'])
        elements.append(date_para)
        
        elements.append(Spacer(1, 20))
        
        # Separator line
        elements.append(self._create_separator())
        
        return elements
    
    def _create_patient_info_section(self, report_data: Dict) -> List:
        """Create patient information section"""
        elements = []
        
        patient = report_data.get('patient', {})
        
        # Section title
        section_title = Paragraph("PATIENT INFORMATION", self.styles['MedicalSubtitle'])
        elements.append(section_title)
        
        # Create patient info table
        patient_data = [
            ["Name:", patient.get('name', 'Not provided')],
            ["Age:", str(patient.get('age', 'Not provided'))],
            ["Gender:", patient.get('gender', 'Not provided')],
            ["Contact:", patient.get('contact', 'Not provided')],
            ["Medical History:", patient.get('medical_history', 'None provided')]
        ]
        
        patient_table = Table(patient_data, colWidths=[1.5*inch, 4*inch])
        patient_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ECF0F1')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2C3E50')),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        
        elements.append(patient_table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_symptoms_section(self, report_data: Dict) -> List:
        """Create symptoms section"""
        elements = []
        
        symptoms = report_data.get('symptoms', [])
        
        # Section title
        section_title = Paragraph("SYMPTOMS REPORTED", self.styles['MedicalSubtitle'])
        elements.append(section_title)
        
        if symptoms:
            # Create symptoms list
            for i, symptom in enumerate(symptoms, 1):
                symptom_text = Paragraph(f"{i}. {symptom.title()}", self.styles['MedicalText'])
                elements.append(symptom_text)
        else:
            no_symptoms = Paragraph("No specific symptoms reported.", self.styles['MedicalText'])
            elements.append(no_symptoms)
        
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_diagnosis_section(self, report_data: Dict) -> List:
        """Create diagnosis section"""
        elements = []
        
        diagnosis = report_data.get('diagnosis', [])
        
        # Section title
        section_title = Paragraph("DIAGNOSIS", self.styles['MedicalSubtitle'])
        elements.append(section_title)
        
        if diagnosis:
            for i, diag in enumerate(diagnosis, 1):
                if isinstance(diag, dict):
                    diag_text = diag.get('name', 'Unknown diagnosis')
                    confidence = diag.get('confidence', '')
                    if confidence:
                        diag_text += f" (Confidence: {confidence})"
                else:
                    diag_text = str(diag)
                
                diagnosis_para = Paragraph(f"{i}. {diag_text}", self.styles['MedicalText'])
                elements.append(diagnosis_para)
        else:
            no_diagnosis = Paragraph("No specific diagnosis reached. Further evaluation recommended.", 
                                   self.styles['MedicalText'])
            elements.append(no_diagnosis)
        
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_treatment_section(self, report_data: Dict) -> List:
        """Create treatment plan section"""
        elements = []
        
        treatment_plan = report_data.get('treatment_plan', [])
        
        # Section title
        section_title = Paragraph("TREATMENT PLAN", self.styles['MedicalSubtitle'])
        elements.append(section_title)
        
        if treatment_plan:
            # Create a structured treatment table
            treatment_data = [["Treatment", "Details"]]
            
            for i, treatment in enumerate(treatment_plan, 1):
                if isinstance(treatment, dict):
                    # Extract treatment information
                    treatment_type = treatment.get('type', 'General')
                    details = treatment.get('description', 'No details provided')
                    
                    treatment_data.append([treatment_type, details])
                else:
                    treatment_data.append([f"Recommendation {i}", str(treatment)])
            
            treatment_table = Table(treatment_data, colWidths=[2*inch, 3.5*inch])
            treatment_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8F9F9')),
            ]))
            
            elements.append(treatment_table)
        else:
            no_treatment = Paragraph("No specific treatment plan generated. Please consult a healthcare provider for personalized treatment.", 
                                   self.styles['MedicalText'])
            elements.append(no_treatment)
        
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_recommendations_section(self, report_data: Dict) -> List:
        """Create recommendations section"""
        elements = []
        
        recommendations = report_data.get('recommendations', [])
        
        # Section title
        section_title = Paragraph("RECOMMENDATIONS", self.styles['MedicalSubtitle'])
        elements.append(section_title)
        
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                rec_para = Paragraph(f"• {rec}", self.styles['MedicalText'])
                elements.append(rec_para)
        else:
            default_recs = [
                "Follow up with your healthcare provider",
                "Monitor your symptoms regularly",
                "Seek emergency care if symptoms worsen suddenly",
                "Complete any prescribed treatments as directed"
            ]
            
            for i, rec in enumerate(default_recs, 1):
                rec_para = Paragraph(f"• {rec}", self.styles['MedicalText'])
                elements.append(rec_para)
        
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_summary_section(self, report_data: Dict) -> List:
        """Create summary section"""
        elements = []
        
        summary = report_data.get('summary', '')
        
        # Section title
        section_title = Paragraph("CONSULTATION SUMMARY", self.styles['MedicalSubtitle'])
        elements.append(section_title)
        
        if summary:
            summary_para = Paragraph(summary, self.styles['MedicalText'])
            elements.append(summary_para)
        else:
            default_summary = "This report summarizes the AI-powered medical consultation. The recommendations provided are based on the information shared during the consultation and are not a substitute for professional medical advice."
            summary_para = Paragraph(default_summary, self.styles['MedicalText'])
            elements.append(summary_para)
        
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_footer(self) -> List:
        """Create report footer"""
        elements = []
        
        elements.append(self._create_separator())
        elements.append(Spacer(1, 10))
        
        # Disclaimer
        disclaimer_text = """
        <b>IMPORTANT DISCLAIMER:</b><br/>
        This report is generated by an AI medical assistant and is for informational purposes only. 
        It is not a substitute for professional medical advice, diagnosis, or treatment. 
        Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition. 
        Never disregard professional medical advice or delay in seeking it because of something you have read in this report.<br/><br/>
        
        In case of emergency, call your local emergency number or go to the nearest emergency room immediately.
        """
        
        disclaimer = Paragraph(disclaimer_text, self.styles['MedicalFooter'])
        elements.append(disclaimer)
        
        elements.append(Spacer(1, 10))
        
        # Generated by
        generated_by = Paragraph("Generated by Dr. HealthAI - AI Medical Assistant", self.styles['MedicalFooter'])
        elements.append(generated_by)
        
        # Timestamp
        timestamp = Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                            self.styles['MedicalFooter'])
        elements.append(timestamp)
        
        return elements
    
    def _create_separator(self):
        """Create a horizontal separator line"""
        return Spacer(1, 0.5)
    
    def generate_text_report(self, report_data: Dict) -> str:
        """Generate a plain text version of the report"""
        patient = report_data.get('patient', {})
        
        report_text = "=" * 60 + "\n"
        report_text += "MEDICAL CONSULTATION REPORT\n"
        report_text += "=" * 60 + "\n\n"
        
        # Patient Information
        report_text += "PATIENT INFORMATION:\n"
        report_text += "-" * 40 + "\n"
        report_text += f"Name: {patient.get('name', 'Not provided')}\n"
        report_text += f"Age: {patient.get('age', 'Not provided')}\n"
        report_text += f"Gender: {patient.get('gender', 'Not provided')}\n"
        report_text += f"Contact: {patient.get('contact', 'Not provided')}\n"
        report_text += f"Medical History: {patient.get('medical_history', 'None provided')}\n\n"
        
        # Symptoms
        symptoms = report_data.get('symptoms', [])
        report_text += "SYMPTOMS REPORTED:\n"
        report_text += "-" * 40 + "\n"
        if symptoms:
            for i, symptom in enumerate(symptoms, 1):
                report_text += f"{i}. {symptom}\n"
        else:
            report_text += "No specific symptoms reported.\n"
        report_text += "\n"
        
        # Diagnosis
        diagnosis = report_data.get('diagnosis', [])
        report_text += "DIAGNOSIS:\n"
        report_text += "-" * 40 + "\n"
        if diagnosis:
            for i, diag in enumerate(diagnosis, 1):
                report_text += f"{i}. {diag}\n"
        else:
            report_text += "No specific diagnosis reached.\n"
        report_text += "\n"
        
        # Recommendations
        recommendations = report_data.get('recommendations', [])
        report_text += "RECOMMENDATIONS:\n"
        report_text += "-" * 40 + "\n"
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                report_text += f"{i}. {rec}\n"
        else:
            report_text += "1. Follow up with healthcare provider\n"
            report_text += "2. Monitor symptoms regularly\n"
            report_text += "3. Seek emergency care if symptoms worsen\n"
        report_text += "\n"
        
        # Summary
        summary = report_data.get('summary', '')
        report_text += "SUMMARY:\n"
        report_text += "-" * 40 + "\n"
        report_text += f"{summary}\n\n" if summary else "Consultation summary not available.\n\n"
        
        # Disclaimer
        report_text += "=" * 60 + "\n"
        report_text += "DISCLAIMER:\n"
        report_text += "=" * 60 + "\n"
        report_text += "This report is generated by an AI medical assistant and is for informational purposes only.\n"
        report_text += "It is not a substitute for professional medical advice, diagnosis, or treatment.\n"
        report_text += "Always consult with a qualified healthcare provider for medical concerns.\n"
        report_text += "In emergencies, call your local emergency number immediately.\n\n"
        
        report_text += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report_text += "By: Dr. HealthAI - AI Medical Assistant\n"
        
        return report_text