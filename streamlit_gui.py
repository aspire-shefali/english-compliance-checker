import streamlit as st
import requests
import os
import json
import time
from docx import Document
from agents import handle_file_processing
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph
import torch

torch.classes.__path__ = []

FASTAPI_URL = "https://english-compliance-checker.onrender.com/upload"
UPLOAD_FOLDER = "uploaded_files"
MODIFIED_FOLDER = "modified_documents"
os.makedirs(MODIFIED_FOLDER, exist_ok=True)

port = os.getenv("PORT", "8501")

st.set_page_config(
    page_title="English Compliance Checker", layout="centered", initial_sidebar_state="collapsed")

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = {}

# UI Styling
st.markdown(
    """
    <style>
        body {
            background-color: #add8e6;
            font-family: 'Arial', sans-serif;
        }
        div.stButton > button {
            width: 100%;
            border-radius: 10px;
            font-size: 18px;
            padding: 12px;
            background-color: #0077b6;
            color: white;
            font-weight: bold;
            border: none;
        }
        div.stButton > button:hover {
            background-color: #005fa3;
        }
        .custom-box {
            background-color: #ffffcc;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
            color: #000000;
            font-weight: bold;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("""<h1 style='text-align: center; color: green;'>English Compliance Checker</h1>""", unsafe_allow_html=True)

if "modify_clicked" not in st.session_state:
    st.session_state.modify_clicked = False

st.markdown("""<p style='text-align: center; font-size:18px;'>Upload a PDF or Word document for compliance checking.</p>""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx"], key="file_uploader")

if uploaded_file:
    st.session_state.modify_clicked = False
    st.session_state["uploaded_filename"] = uploaded_file.name
    st.session_state["uploaded_file"] = uploaded_file

    with st.container():
        st.info(f"Uploaded File: {uploaded_file.name}")

    st.markdown("""<p style='text-align: center;'>Processing file... Please wait.</p>""", unsafe_allow_html=True)
    
    files = {"uploaded_file": (uploaded_file.name, uploaded_file.getbuffer(), uploaded_file.type)}
    response = requests.post(FASTAPI_URL, files=files)
    
    if response.status_code == 200:
        st.success(f"File '{uploaded_file.name}' uploaded successfully!")
        with st.spinner("Analyzing document..."):
            try:
                time.sleep(3)
                report = handle_file_processing(uploaded_file.name, UPLOAD_FOLDER)
                compliance_dict = json.loads(report) if isinstance(report, str) else report
                compliance_text = compliance_dict.get(uploaded_file.name, "No compliance issues found.")
                
                subject = uploaded_file.name
                if subject not in st.session_state.chat_history:
                    st.session_state.chat_history[subject] = []
                st.session_state.chat_history[subject].append(compliance_text)
                
                with st.container():
                    st.markdown("""<h3 style='color: yellow;'>Compliance Report</h3>""", unsafe_allow_html=True)
                    st.markdown(f"""<div class='custom-box'>{compliance_text}</div>""", unsafe_allow_html=True)
                
                st.markdown("""<h3 style='color: darkgreen;'>Modify the Document?</h3>""", unsafe_allow_html=True)
                
                if st.button("Modify Document", key="modify_button", help="Click to modify document", 
                             use_container_width=True):
                    st.session_state.modify_clicked = True
                
                if st.session_state.modify_clicked:
                    with st.spinner("🔧 Modifying document..."):
                        modification_result = handle_file_processing(uploaded_file.name, UPLOAD_FOLDER)
                        modification_result_dict = json.loads(modification_result) if isinstance(modification_result, str) else modification_result
                        modified_doc = modification_result_dict.get(uploaded_file.name, None)
                        
                        if modified_doc:
                            st.subheader("Modified Document")
                            modified_filename = f"modified_{uploaded_file.name}"
                            modified_path = os.path.join(MODIFIED_FOLDER, modified_filename)
                            
                            file_extension = os.path.splitext(uploaded_file.name)[-1]
                            if file_extension.lower() == ".pdf":
                                doc = SimpleDocTemplate(modified_path, pagesize=letter)
                                styles = getSampleStyleSheet()
                                paragraph = Paragraph(modified_doc.replace("\n", "<br/>"), styles["Normal"])
                                doc.build([paragraph])
                                mime_type = "application/pdf"
                            elif file_extension.lower() == ".docx":
                                doc = Document()
                                for line in modified_doc.split("\n"):
                                    doc.add_paragraph(line)
                                doc.save(modified_path)
                                mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                            else:
                                st.error("Unsupported file format.")
                                st.stop()
                            
                            if os.path.exists(modified_path):
                                st.success("Modified document saved!")
                                with open(modified_path, "rb") as f:
                                    st.download_button("Download Modified Document", data=f, file_name=modified_filename, mime=mime_type)
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
    else:
        st.error(f"Upload failed: {response.json().get('detail', 'Unknown error')}")
