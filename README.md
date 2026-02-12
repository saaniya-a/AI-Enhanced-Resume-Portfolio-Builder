# ResumeAI – AI-Enhanced Resume Portfolio Builder

> Build ATS-friendly resumes, optimize them for specific job descriptions, and manage multiple resume versions — all from a clean web interface.


## 📌 Overview

ResumeAI is a web-based resume builder designed to help users:
- Create structured, ATS-compliant resumes
- Improve resume content using AI
- Analyze resumes against job descriptions
- Maintain multiple resume versions
- Export resumes as PDFs or share them as portfolio links


## 🧩 Problem Statement

Many job applicants struggle with:
- Poor resume structure
- Low ATS compatibility
- Missing job-specific keywords
- Managing multiple resume versions for different roles

ResumeAI solves this by combining structured resume input, AI-powered optimization, ATS checking, and version control into a single application.

## 🚀 Features Implemented

- Section-wise resume builder (Education, Experience, Projects, Skills, Certifications)
- AI-powered resume generation
- Resume optimizer based on job descriptions
- ATS compatibility checker with keyword analysis
- Resume scoring system
- ATS-safe resume templates
- Resume version management
- Resume preview & browser-based PDF export
- Shareable portfolio-style resume page


## 🛠 Tech Stack

### Frontend
- HTML
- CSS

### Backend
- Python
- Flask

### Database
- SQLite (file-based, no setup required)

### AI Integration
- Grok AI API  

## Installation & Setup

1️⃣ Clone the Repository
```
git clone https://github.com/your-username/ResumeAI.git
cd ResumeAI
```

2️⃣ Create & Activate Virtual Environment
```
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

3️⃣ Install Dependencies
```
pip install -r requirements.txt
```

4️⃣ Environment Variables
Create a .env file in the root directory:
```
GEMINI_API_KEY=your_api_key_here
```

5️⃣ Run the Application
```
python app.py
```
Open in browser

## Application Flow
- User enters their name on the landing page
- User record is created or fetched from SQLite
- Resume data is entered section-wise
- AI generates a structured resume
- Resume is saved as a new version
- User can:
      Optimize resume
      Check ATS score
      Preview resume
      Export PDF
      Share portfolio link

## Screenshots

<img width="1770" height="2410" alt="image" src="https://github.com/user-attachments/assets/3010b7c4-75ed-4dfb-93e4-3e6fc0f52f0a" />

<img width="1770" height="3382" alt="127 0 0 1_5001_builder" src="https://github.com/user-attachments/assets/6d7e3519-15fa-4abd-9794-46242674719e" />

<img width="1440" height="932" alt="Screenshot 2026-02-12 at 9 13 05 AM" src="https://github.com/user-attachments/assets/f8a47d51-7564-41b5-aa72-54303a99efe2" />

<img width="1440" height="932" alt="Screenshot 2026-02-12 at 9 13 56 AM" src="https://github.com/user-attachments/assets/f901b641-5417-4d0d-8eba-394e1f126614" />


## Team
- Saaniya Ashraf
- Prathiyush Srinivasan

## Future Scope

- DOCX export support
- Paid AI tier integration
- Job-specific resume comparison
- Advanced ATS analytics
- In-line edit options
- User authentication

