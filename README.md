# English Document Compliance Checker

## Overview
The **English Document Compliance Checker** is an AI-powered tool designed to evaluate uploaded PDF or DOCX files against standard English guidelines. It assesses key aspects such as grammar, clarity, structure, and adherence to writing conventions.

After the compliance check, the tool provides a detailed report highlighting any violations. Users can accept suggested modifications, ensuring their document meets the required standards. The updated file with corrected English structure can then be downloaded for further use.

## How It Works
1. **Upload a Document**: Users upload a PDF or DOCX file via the Streamlit interface.
2. **AI Analysis**: The system evaluates grammar, clarity, and structural accuracy, generating a compliance report.
3. **Review & Modify**: Users review the report and request AI-driven modifications.
4. **Download Final Document**: The refined document can be downloaded in the preferred format.

## Setup Instructions
### 1. Set Up a Virtual Environment
python -m venv venv

### 2. Activate virtual Environment
venv\Scripts\activate

### 3. Install Required Dependencies
pip install -r requirements.txt

### 4. Start the FastAPI Server
python upload_document.py

### 5.  Launch the Streamlit Interface
streamlit run streamlit_gui.py

## Launch the Deployed APP and upload your Docx/Pdf File...!!
[Link Text](https://english-compliance-checker-3gbhfk9sfckw9kb9a6fhh5.streamlit.app/)




