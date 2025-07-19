from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
import re
import requests
import streamlit.components.v1 as components
from PyPDF2 import PdfReader
import inflect

# ----------- OPENROUTER CONFIG -----------
API_URL = "https://openrouter.ai/api/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
    "HTTP-Referer": "http://localhost:8501",
    "Content-Type": "application/json"
}

# ----------- HELPERS -----------
def get_openrouter_response(prompt, max_tokens=300):
    payload = {
        "model": "mistralai/mixtral-8x7b-instruct",
        "messages": [
            {"role": "system", "content": "You are an ATS (Applicant Tracking System) expert."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": 0.1
    }
    response = requests.post(API_URL, headers=HEADERS, json=payload)
    try:
        return response.json()['choices'][0]['message']['content']
    except Exception:
        return f"Error: {response.text}"

def add_bg_animation():
    st.markdown("""
        <style>
        body {
            background-color: #e6f0ff;  /* Light Blue Background */
        }

        .main {
            background-color: rgba(255,255,255,0.9);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
        }

        .stTextArea textarea, .stFileUploader {
            border-radius: 10px;
        }

        h1 {
            text-align: center;
            font-size: 2.5rem !important;
            font-weight: bold;
            background: -webkit-linear-gradient(45deg, #3a7bd5, #00d2ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        </style>
    """, unsafe_allow_html=True)



def gauge_chart(score):
    components.html(f"""
    <div style="text-align:center;">
      <svg width="200" height="200" viewBox="0 0 42 42">
        <circle cx="21" cy="21" r="15.9155" fill="none" stroke="#eee" stroke-width="3"></circle>
        <circle cx="21" cy="21" r="15.9155" fill="none" stroke="#4caf50"
                stroke-width="3" stroke-dasharray="{score}, 100" stroke-linecap="round"
                transform="rotate(-90 21 21)"></circle>
        <text x="50%" y="50%" text-anchor="middle" dy=".3em" font-size="8" fill="#333">{score}%</text>
      </svg>
    </div>
    """, height=220)

add_bg_animation()

# ----------- PDF UTILS -----------
def extract_text_from_pdf(uploaded_file):
    reader = PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text() + "\n"
    return text.strip()

# ----------- KEYWORD EXTRACTION -----------
p = inflect.engine()

def normalize_keyword(word):
    word = word.lower().strip()
    singular = p.singular_noun(word)
    return singular if singular else word

def extract_technical_keywords_ai(text, context):
    prompt = f"""
    Extract ONLY technical skills, tools, programming languages, cloud services, frameworks, or databases.
    ❌ Skip generic or soft skills.
    ✅ Return singular form only.
    ✅ Respond ONLY as a comma-separated list.

    {context.upper()}:
    {text}
    """
    response = get_openrouter_response(prompt)
    keywords = [normalize_keyword(kw) for kw in re.split(r",|\n", response) if kw.strip()]
    return set(keywords)

# ----------- SEMANTIC MATCHING -----------
def ai_semantic_match(keyword, resume_text):
    prompt = f"""
    Check if this resume shows strong actual experience with "{keyword}".
    Answer YES or NO.

    ✅ YES if actively used in experience/projects with context or achievements.
    ❌ NO if only listed in skills.

    RESUME:
    {resume_text}
    """
    response = get_openrouter_response(prompt, max_tokens=50).strip().lower()
    return "yes" in response

def calculate_semantic_match(resume_text, jd_keywords):
    matched, missing = [], []
    for kw in jd_keywords:
        if ai_semantic_match(kw, resume_text):
            matched.append(kw)
        else:
            missing.append(kw)
    total = len(jd_keywords)
    percentage = round((len(matched) / total) * 100, 2) if total else 0
    return percentage, matched, missing

# ----------- SMART IMPROVEMENTS -----------
def get_suggestions_ai(resume_text, jd_text, missing_keywords):
    prompt = f"""
    You are a senior technical recruiter improving resumes.

    ✅ Do NOT mention the candidate's name or refer to them directly.
    ✅ Do NOT suggest already strong skills or repeated action verbs if already well used.
    ✅ Focus only on real improvements.

    Give **4-6 actionable suggestions**, focusing on:
    - Stronger action verbs (replace weak/repetitive verbs if needed).
    - Quantifying achievements (add measurable impact if missing).
    - Leadership, scalability, or architectural impact (if relevant to the JD).
    - ONLY mention missing keywords if they are critical to this JD.

    Be concise and professional, like a real recruiter.

    RESUME:
    {resume_text}

    JOB DESCRIPTION:
    {jd_text}

    Missing technical keywords: {', '.join(missing_keywords)}
    """
    suggestions_text = get_openrouter_response(prompt, max_tokens=500)
    return [s.strip(" -•1234567890.*") for s in suggestions_text.split("\n") if s.strip()]


# ----------- BREVITY, STYLE, IMPACT, GRAMMAR -----------

def grammar_check(resume_text):
    prompt = f"""
    Check this resume for grammar, spelling, and sentence structure issues.
    ✅ Focus only on significant issues (no nitpicking).
    ✅ Suggest concise corrections in the format:
    - Original → Suggested Fix
    ✅ If there are no major issues, respond with "No major grammar issues found."

    {resume_text}
    """
    return get_openrouter_response(prompt, max_tokens=300)


def analyze_brevity(resume_text):
    prompt = f"""
    Identify long or wordy sentences in this resume and suggest concise rewrites.
    Respond in format: Original → Suggested Rewrite.
    {resume_text}
    """
    return get_openrouter_response(prompt, max_tokens=400)

def analyze_style(resume_text):
    prompt = f"""
    Check for repetitive action verbs and passive voice.
    Suggest stronger action verbs and active phrasing.
    {resume_text}
    """
    return get_openrouter_response(prompt, max_tokens=400)

# ----------- STREAMLIT APP -----------
st.set_page_config(page_title="ATS & Resume Optimizer", layout="wide")
st.title("📄 ATS & Resume Optimizer")
st.caption("AI-powered ATS scoring with actionable resume improvement suggestions")


jd_text = st.text_area("Paste Job Description here:", height=150)
uploaded_file = st.file_uploader("Upload your Resume (PDF)", type=["pdf"])

if uploaded_file:
    st.success("✅ Resume uploaded successfully!")

if st.button("🚀 Scan My Resume"):
    if uploaded_file and jd_text.strip():
        resume_text = extract_text_from_pdf(uploaded_file)

        with st.spinner("🔍 Analyzing..."):
            jd_keywords = extract_technical_keywords_ai(jd_text, "job description")
            percentage, matched_keywords, missing_keywords = calculate_semantic_match(resume_text, jd_keywords)
            suggestions = get_suggestions_ai(resume_text, jd_text, missing_keywords)
            brevity = analyze_brevity(resume_text)
            style = analyze_style(resume_text)
            grammar_issues = grammar_check(resume_text)

        # Display ATS Score
        col1, col2 = st.columns([1, 2])
        with col1:
            st.subheader("ATS Match Score")
            gauge_chart(percentage)
        with col2:
            st.subheader("Missing Keywords")
            if missing_keywords:
                for kw in missing_keywords:
                    st.markdown(f"❌ **{kw.title()}**")
            else:
                st.write("No critical keywords missing!")

            st.subheader("Improvement Suggestions")
            for i, suggestion in enumerate(suggestions, start=1):
                st.write(f"**{i}.** {suggestion}")

        # Additional Analysis
        st.markdown("### ✨ Additional Resume Insights")
        st.write("**Brevity Suggestions:**", brevity)
        st.write("**Style Suggestions:**", style)
        st.write("**Top Grammar/Spelling Issues:**", grammar_issues if grammar_issues else "✅ No major issues found")

        # Debugging
        with st.expander("🔍 Debugging Info"):
            st.write(f"Total JD Keywords: {len(jd_keywords)} → {', '.join(jd_keywords)}")
            st.write(f"Matched Keywords: {len(matched_keywords)} → {', '.join(matched_keywords)}")
            st.write(f"Missing Keywords: {len(missing_keywords)} → {', '.join(missing_keywords)}")

        # Download report
        report_text = f"""
        ATS Match Report
        ----------------
        Match Percentage: {percentage} %
        Matched Keywords: {', '.join(matched_keywords) if matched_keywords else 'None'}
        Missing Keywords: {', '.join(missing_keywords) if missing_keywords else 'None'}
        Suggestions:
        {chr(10).join([f"- {s}" for s in suggestions])}
        """
        st.download_button("📥 Download ATS Report", data=report_text, file_name="ATS_Report.txt")

    else:
        st.warning("⚠️ Please upload a resume and paste a job description.")
