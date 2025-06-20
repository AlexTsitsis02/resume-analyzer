import streamlit as st
from PyPDF2 import PdfReader
import requests
import json
import re

# Replace with your Groq API key
GROQ_API_KEY = "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"

# Set page config
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="🧠",
    layout="centered",
)

# Minimal styling using Streamlit native options
st.markdown(
    """
    <style>
    .stApp {
        background-color: #black;
        font-family: 'Segoe UI', sans-serif;
    }
    .title {
        font-size: 2.2rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        color: #2c3e50;
    }
    .subtitle {
        font-size: 1.2rem;
        margin-bottom: 2rem;
        color: #7f8c8d;
    }
    .score {
        font-size: 2rem;
        font-weight: bold;
        color: #27ae60;
        background-color: #ecf0f1;
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
    }
    .skill {
        background-color: #;
        padding: 0.75rem 1rem;
        margin-bottom: 0.5rem;
        border-left: 5px solid #e74c3c;
        border-radius: 8px;
        font-size: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# UI Header
st.markdown('<div class="title">🧠 AI Resume Analyzer</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Compare your resume to a job description using LLaMA 3 on Groq</div>', unsafe_allow_html=True)

# Upload and Input
uploaded_file = st.file_uploader("📄 Upload your resume (PDF)", type=["pdf"])
job_description = st.text_area("💼 Paste the job description", height=200)

# Extract PDF text
def extract_text_from_pdf(pdf_file):
    pdf_reader = PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text
    return text

# Groq + LLaMA 3 call
def analyze_resume(text, job_description):
    prompt = f"""
You are a career coach AI. Analyze the resume below and compare it to the job description.
Give a score out of 100 for how well the resume matches the job description.
List missing key skills or experience from the resume compared to the job description.

Respond ONLY in JSON format like this:
{{
  "score": 85,
  "missing_skills": ["Skill A", "Skill B"]
}}

Resume:
{text}

Job Description:
{job_description}
"""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": "You are a helpful career coach AI."},
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)

    if response.status_code != 200:
        return {"score": "N/A", "missing_skills": [f"Error: {response.text}"]}

    try:
        reply = response.json()["choices"][0]["message"]["content"]
        json_match = re.search(r"\{.*\}", reply, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        else:
            return {"score": "N/A", "missing_skills": ["Could not extract valid JSON from response."]}
    except Exception as e:
        return {"score": "N/A", "missing_skills": [f"Parsing error", str(e)]}

# Run if inputs present
if uploaded_file and job_description:
    with st.spinner("🔍 Analyzing resume..."):
        resume_text = extract_text_from_pdf(uploaded_file)
        result = analyze_resume(resume_text, job_description)

    st.markdown('<div class="score">✅ Match Score: ' + str(result.get("score", "N/A")) + '</div>', unsafe_allow_html=True)

    st.subheader("❌ Missing Skills / Experience")
    for skill in result.get("missing_skills", []):
        st.markdown(f'<div class="skill">- {skill}</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(
    "<center><small>Made with ❤️ using Streamlit + Groq + LLaMA 3</small></center>",
    unsafe_allow_html=True,
)
