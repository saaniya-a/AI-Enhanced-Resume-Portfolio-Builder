import os
import json
import re

# ─── CONFIGURATION ───
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'YOUR_API_KEY_HERE')
DEMO_MODE = False  # Set to False when you want demo data instead of real AI


# ─── DEMO RESPONSES ───
def demo_generate_resume(data):
    name = data.get('name', 'John Doe')
    email = data.get('email', 'john@example.com')
    phone = data.get('phone', '')
    location = data.get('location', '')
    skills_raw = data.get('skills', 'Python, JavaScript')
    skills = [s.strip() for s in skills_raw.split(',') if s.strip()]

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "location": location,
        "summary": f"Results-driven professional with hands-on experience in {', '.join(skills[:3])}. Passionate about building impactful solutions and continuously learning new technologies.",
        "education": [
            {"degree": data.get('education', 'B.Tech Computer Science').split('\n')[0], "school": "University", "year": "2024", "details": ""}
        ],
        "experience": [
            {
                "title": "Software Developer Intern",
                "company": "Tech Company",
                "duration": "2023 - 2024",
                "bullets": [
                    "Developed and maintained web applications using modern frameworks",
                    "Collaborated with cross-functional teams to deliver features on schedule",
                    "Implemented automated testing, improving code reliability"
                ]
            }
        ],
        "projects": [
            {
                "name": "AI Resume Builder",
                "description": "Built a web application that uses AI to generate and optimize resumes for ATS compatibility",
                "tech": ", ".join(skills[:4]) if skills else "Python, Flask"
            }
        ],
        "skills": skills if skills else ["Python", "JavaScript", "SQL"],
        "certifications": [c.strip() for c in data.get('certifications', '').split(',') if c.strip()] or []
    }


def demo_optimize_resume(resume_text, job_description):
    return {
        "optimized_resume": resume_text,
        "changes": [
            {
                "original": "Worked on building web apps",
                "improved": "Developed and deployed 3 production web applications using React and Flask",
                "reason": "Added specificity and strong action verb 'Developed' instead of vague 'Worked on'"
            },
            {
                "original": "Helped the team with testing",
                "improved": "Implemented unit and integration tests, improving code coverage to 85%",
                "reason": "Replaced passive 'Helped' with active 'Implemented' and added measurable impact"
            },
            {
                "original": "Responsible for database management",
                "improved": "Designed and optimized PostgreSQL database schemas serving 10K+ daily queries",
                "reason": "Replaced 'Responsible for' with action verb and added scale context"
            }
        ],
        "ats_score": 78,
        "suggestions": [
            "Add more keywords from the job description like 'agile', 'CI/CD', 'REST API'",
            "Quantify your achievements where possible (e.g., reduced load time by 40%)",
            "Use standard section headings: 'Experience', 'Education', 'Skills'",
            "Move Skills section higher to improve keyword matching"
        ]
    }


def demo_check_ats(resume_text, job_description):
    return {
        "score": 72,
        "keyword_match": {
            "found": ["Python", "JavaScript", "SQL", "Git", "REST API", "problem solving"],
            "missing": ["Docker", "CI/CD", "Agile", "AWS", "TypeScript", "unit testing"]
        },
        "format_issues": [
            "Consider using standard heading 'Work Experience' instead of 'Jobs'",
            "Avoid tables or columns - use single-column layout for ATS",
            "Use standard bullet points instead of custom symbols"
        ],
        "content_feedback": [
            "Experience bullets should start with strong action verbs",
            "Add more quantifiable results (numbers, percentages, scale)",
            "Skills section should mirror the exact keywords from the job posting"
        ],
        "section_scores": {
            "keyword_match": 65,
            "formatting": 80,
            "content_clarity": 70
        },
        "overall_feedback": "Your resume covers many required skills but is missing key technical keywords. Rewrite bullets with action verbs and add measurable outcomes to improve your score."
    }


def demo_cover_letter(resume_text, job_description):
    return """Dear Hiring Manager,

I am writing to express my strong interest in the position advertised. With my background in software development and passion for building impactful solutions, I am confident I would be a valuable addition to your team.

Throughout my academic and professional journey, I have developed strong technical skills and a problem-solving mindset. My experience building web applications and working with modern development tools has prepared me to contribute effectively from day one. I am particularly drawn to your company's mission and the opportunity to work on challenging technical problems.

What sets me apart is my ability to combine technical expertise with clear communication and teamwork. I thrive in collaborative environments and am always eager to learn new technologies and approaches. I believe my skills and enthusiasm align well with the requirements of this role.

I would welcome the opportunity to discuss how my experience and skills can contribute to your team's success. Thank you for considering my application. I look forward to hearing from you.

Sincerely,
[Your Name]"""


# ─── REAL AI CALLS ───
def call_ai(prompt):
    """Call Google Gemini API and return the response text."""
    try:
        from google import genai
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model="gemini-1.0-pro",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"AI Error: {str(e)}"


def generate_resume(data):
    """Take section-wise input and generate a structured resume."""
    if DEMO_MODE:
        return demo_generate_resume(data)

    prompt = f"""You are a professional resume writer. Convert the following information into a clean, ATS-friendly resume.

RULES:
- Use strong action verbs (Led, Built, Designed, Implemented, etc.)
- Write concise bullet points
- Do NOT fabricate any information or metrics
- Keep formatting clean and professional
- Return the result as JSON

INPUT:
Name: {data.get('name', '')}
Email: {data.get('email', '')}
Phone: {data.get('phone', '')}
Location: {data.get('location', '')}

Education:
{data.get('education', '')}

Experience:
{data.get('experience', '')}

Projects:
{data.get('projects', '')}

Skills:
{data.get('skills', '')}

Certifications:
{data.get('certifications', '')}

Return ONLY a JSON object with this exact structure:
{{
    "name": "...",
    "email": "...",
    "phone": "...",
    "location": "...",
    "summary": "A 2-3 sentence professional summary",
    "education": [
        {{"degree": "...", "school": "...", "year": "...", "details": "..."}}
    ],
    "experience": [
        {{"title": "...", "company": "...", "duration": "...", "bullets": ["...", "..."]}}
    ],
    "projects": [
        {{"name": "...", "description": "...", "tech": "..."}}
    ],
    "skills": ["skill1", "skill2"],
    "certifications": ["cert1", "cert2"]
}}
"""
    response = call_ai(prompt)
    try:
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            return json.loads(json_match.group())
    except json.JSONDecodeError:
        pass
    return {"raw_text": response, "error": "Could not parse AI response"}


def optimize_resume(resume_text, job_description):
    """Optimize an existing resume against a job description."""
    if DEMO_MODE:
        return demo_optimize_resume(resume_text, job_description)

    prompt = f"""You are an expert resume optimizer. Analyze this resume against the job description and improve it.

RULES:
- Identify weak, vague, or passive bullet points
- Rewrite bullets to be clear and impactful
- Align phrasing with keywords from the job description
- Do NOT fabricate metrics or experience
- Explain WHAT you changed and WHY

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Return ONLY a JSON object:
{{
    "optimized_resume": "The full optimized resume text",
    "changes": [
        {{"original": "old bullet", "improved": "new bullet", "reason": "why this is better"}}
    ],
    "ats_score": 75,
    "suggestions": ["suggestion 1", "suggestion 2"]
}}
"""
    response = call_ai(prompt)
    try:
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            return json.loads(json_match.group())
    except json.JSONDecodeError:
        pass
    return {"raw_text": response, "error": "Could not parse AI response"}


def check_ats(resume_text, job_description):
    """Check ATS compatibility and extract keywords."""
    if DEMO_MODE:
        return demo_check_ats(resume_text, job_description)

    prompt = f"""You are an ATS (Applicant Tracking System) analyzer. Compare this resume against the job description.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Analyze and return ONLY a JSON object:
{{
    "score": 72,
    "keyword_match": {{
        "found": ["keyword1", "keyword2"],
        "missing": ["keyword3", "keyword4"]
    }},
    "format_issues": ["issue 1", "issue 2"],
    "content_feedback": ["feedback 1", "feedback 2"],
    "section_scores": {{
        "keyword_match": 70,
        "formatting": 80,
        "content_clarity": 65
    }},
    "overall_feedback": "Summary of what to improve"
}}
"""
    response = call_ai(prompt)
    try:
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            return json.loads(json_match.group())
    except json.JSONDecodeError:
        pass
    return {"raw_text": response, "error": "Could not parse AI response"}


def generate_cover_letter(resume_text, job_description):
    """Generate a role-specific cover letter."""
    if DEMO_MODE:
        return demo_cover_letter(resume_text, job_description)

    prompt = f"""Write a professional 1-page cover letter based on this resume and job description.

RULES:
- Be role-specific and mention the company/role
- Do NOT repeat resume bullet points word-for-word
- Show enthusiasm and fit for the role
- Keep it to 3-4 paragraphs
- Be professional but not robotic

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Return ONLY the cover letter text, no JSON.
"""
    return call_ai(prompt)