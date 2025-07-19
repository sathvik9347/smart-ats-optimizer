AI-powered ATS scoring tool that analyzes resumes against job descriptions using semantic matching and style analysis.
It provides:
✅ ATS Match Score (with semantic keyword matching)
✅ Missing Keywords (only if not strongly covered in resume)
✅ Actionable Resume Suggestions (stronger action verbs, quantifying impact, leadership emphasis)
✅ Brevity & Style Analysis (wordy sentences, passive voice improvements)
✅ Grammar & Spelling Insights

🚀 Features
Semantic Keyword Matching: Checks if keywords are truly demonstrated in experience/projects (not just listed in skills).

Smart Suggestions: Avoids redundant suggestions, focuses on real improvements.

Style & Brevity Analysis: Suggests concise rewrites and stronger action verbs.

Interactive UI: Built with Streamlit, includes animated gauges and clean UI.


🛠️ Tech Stack
Python 3.10+

Streamlit (Frontend UI)

OpenRouter API (Mixtral Model) for AI-powered analysis

PyPDF2 for resume text extraction

Inflect for keyword normalization



⚙️ Installation
1. Clone Repository
bash
Copy
Edit
git clone https://github.com/your-username/ats-resume-optimizer.git
cd ats-resume-optimizer
2. Install Dependencies
bash
Copy
Edit
pip install -r requirements.txt
(Create a requirements.txt if you haven’t already; I can generate it for you.)

3. Set Environment Variables
Create a .env file:

ini
Copy
Edit
OPENROUTER_API_KEY=your_openrouter_api_key
▶️ Running Locally
bash
Copy
Edit
streamlit run app.py
Then open: http://localhost:8501 in your browser.

🌐 Deployment
You can deploy using:
✅ Hugging Face Spaces (recommended)
✅ Streamlit Cloud
✅ Vercel (requires FastAPI wrapper)

📌 Roadmap
 Multi-language resume support

 Export as PDF with formatted ATS report

 Integration with LinkedIn job postings