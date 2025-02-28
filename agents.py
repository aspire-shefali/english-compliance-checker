import os
import autogen
import docx
import easyocr
from pdf2image import convert_from_path
from pypdf import PdfReader
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Retrieve API key from environment
GROQ_API_TOKEN = os.getenv("GROQ_API_KEY")

# Configuration for Autogen's LLM
llm_settings = {
    "model": "llama-3.3-70b-versatile",
    "api_key": GROQ_API_TOKEN,
    "base_url": "https://api.groq.com/openai/v1",
}

def extract_pdf_text(file_path):
    """Extracts text from a PDF. Uses OCR for scanned documents if necessary."""
    with open(file_path, "rb") as f:
        pdf_reader = PdfReader(f)
        extracted_text = "\n".join(
            [page.extract_text() for page in pdf_reader.pages if page.extract_text()]
        )
    
    if not extracted_text.strip():
        images = convert_from_path(file_path)
        ocr_reader = easyocr.Reader(["en"], gpu=False)
        extracted_text = "\n".join(["\n".join(ocr_reader.readtext(img, detail=0)) for img in images])
    
    return extracted_text

def extract_docx_text(file_path):
    """Retrieves text from a .docx file."""
    document = docx.Document(file_path)
    return "\n".join([para.text for para in document.paragraphs])

def read_document(file_path):
    """Determines file type and extracts text accordingly."""
    if file_path.endswith(".pdf"):
        return extract_pdf_text(file_path)
    if file_path.endswith(".docx"):
        return extract_docx_text(file_path)
    
    raise ValueError("Unsupported file format")

def initialize_agents():
    """Initializes Autogen agents configured with the Groq API."""
    text_parser = autogen.AssistantAgent(
        name="TextExtractor",
        system_message="Extract and format text from uploaded documents.",
        llm_config=llm_settings,
    )
    
    compliance_checker = autogen.AssistantAgent(
        name="ComplianceEvaluator",
        system_message="Review document compliance with grammatical and professional standards.",
        llm_config=llm_settings,
    )
    
    report_creator = autogen.AssistantAgent(
        name="ComplianceReporter",
        system_message="Generate a structured compliance report highlighting areas for improvement.",
        llm_config=llm_settings,
    )
    
    text_rewriter = autogen.AssistantAgent(
        name="ContentRewriter",
        system_message="Revise documents to meet compliance standards while maintaining clarity.",
        llm_config=llm_settings,
    )
    
    return text_parser, compliance_checker, report_creator, text_rewriter

def analyze_document(file_path, apply_rewrite=False):
    """Processes a document with Autogen agents and generates compliance feedback."""
    _, compliance_checker, report_creator, text_rewriter = initialize_agents()
    
    document_content = read_document(file_path)
    
    compliance_query = f"""
    Evaluate the following document for compliance:
    - Identify grammar and structural issues.
    - Provide an explanation for each issue.
    - Format response as:
      **Sentence:** "<original sentence>"
      - **Issue:** <description>
    ---
    Document Content:
    {document_content}
    """
    compliance_result = compliance_checker.generate_reply(
        messages=[{"role": "user", "content": compliance_query}]
    )
    
    report_query = f"""
    Create a structured compliance report with:
    1. Summary of key issues.
    2. Detailed line-by-line analysis.
    3. Suggested improvements.
    4. Compliance rating (1-10 scale).
    Compliance Details:
    {compliance_result}
    """
    compliance_report = report_creator.generate_reply(
        messages=[{"role": "user", "content": report_query}]
    )
    
    if apply_rewrite:
        rewrite_query = f"""
        Rewrite the following document while addressing all compliance concerns:
        {document_content}
        """
        revised_document = text_rewriter.generate_reply(
            messages=[{"role": "user", "content": rewrite_query}]
        )
        return revised_document
    
    return compliance_report

def handle_file_processing(filename, directory="uploads", apply_rewrite=False):
    """Handles document processing workflow."""
    full_path = os.path.join(directory, filename)
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"File '{filename}' not found in '{directory}'.")
    
    if filename.endswith(".pdf") or filename.endswith(".docx"):
        return {filename: analyze_document(full_path, apply_rewrite)}
    raise ValueError("Invalid file type")
