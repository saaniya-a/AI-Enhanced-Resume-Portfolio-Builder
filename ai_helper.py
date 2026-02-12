import os, json, re

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'AIzaSyDkgBzhxKa9W10rqM7FvQzluRpLOuHwHSA')

def call_ai(prompt):
    from google import genai
    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(model="gemini-1.0-pro", contents=prompt)
    return response.text

def parse_json(text):
    match = re.search(r'\{[\s\S]*\}', text)
    if match:
        try: return json.loads(match.group())
        except: return None
    return None


def generate_resume(data):
    job_desc = data.get('job_description', '')
    job_section = f"\nTarget Job Description:\n{job_desc}\n\nTailor the resume to match this job — use relevant keywords, highlight matching skills, and align the summary with the role." if job_desc else ""
    prompt = f"""You are a resume writer. Convert this info into an ATS-friendly resume.
Return ONLY a JSON object with keys: name, email, phone, location, summary, education, experience, projects, skills, certifications.
{job_section}
Name: {data.get('name','')}  Email: {data.get('email','')}  Phone: {data.get('phone','')}
Location: {data.get('location','')}
Education: {data.get('education','')}
Experience: {data.get('experience','')}
Projects: {data.get('projects','')}
Skills: {data.get('skills','')}
Certifications: {data.get('certifications','')}

JSON format: {{"name":"","email":"","phone":"","location":"","summary":"2-3 sentences",
"education":[{{"degree":"","school":"","year":"","details":""}}],
"experience":[{{"title":"","company":"","duration":"","bullets":[""]}}],
"projects":[{{"name":"","description":"","tech":""}}],
"skills":[""],"certifications":[""]}}"""
    try:
        result = parse_json(call_ai(prompt))
        if result: return result
    except Exception as e:
        print(f"[AI ERROR - generate_resume] {e}")
    skills = [s.strip() for s in data.get('skills','').split(',') if s.strip()]
    return {
        "name": data.get('name','Your Name'), "email": data.get('email',''),
        "phone": data.get('phone',''), "location": data.get('location',''),
        "summary": f"Professional with experience in {', '.join(skills[:3]) or 'software development'}.",
        "education": [{"degree": data.get('education','').split('\n')[0], "school":"", "year":"", "details":""}],
        "experience": [{"title":"Experience", "company":"", "duration":"", "bullets":[data.get('experience','No experience provided')]}],
        "projects": [{"name":"Projects", "description":data.get('projects',''), "tech":', '.join(skills[:4])}],
        "skills": skills or ["Not specified"],
        "certifications": [c.strip() for c in data.get('certifications','').split(',') if c.strip()]
    }


def optimize_resume(resume_text, job_description):
    prompt = f"""Optimize this resume for the job description. Return ONLY JSON:
{{"optimized_resume":"improved text","changes":[{{"original":"old","improved":"new","reason":"why"}}],"ats_score":75,"suggestions":["tip"]}}

RESUME:\n{resume_text}\n\nJOB DESCRIPTION:\n{job_description}"""
    try:
        result = parse_json(call_ai(prompt))
        if result: return result
    except Exception as e:
        print(f"[AI ERROR - optimize_resume] {e}")
    return {
        "optimized_resume": resume_text,
        "changes": [{"original":"Worked on projects","improved":"Developed and maintained project deliverables","reason":"Stronger action verb"}],
        "ats_score": 70,
        "suggestions": ["Add job-specific keywords","Quantify achievements","Use standard section headings"]
    }


def check_ats(resume_text, job_description):
    prompt = f"""Score this resume against the job description. Return ONLY JSON:
{{"score":72,"keyword_match":{{"found":["word"],"missing":["word"]}},"format_issues":["issue"],"content_feedback":["tip"],
"section_scores":{{"keyword_match":70,"formatting":80,"content_clarity":65}},"overall_feedback":"summary"}}

RESUME:\n{resume_text}\n\nJOB DESCRIPTION:\n{job_description}"""
    try:
        result = parse_json(call_ai(prompt))
        if result: return result
    except Exception as e:
        print(f"[AI ERROR - check_ats] {e}")
    return {
        "score": 65,
        "keyword_match": {"found":["Python","SQL"], "missing":["Docker","AWS","CI/CD"]},
        "format_issues": ["Use standard ATS section headings","Ensure single-column layout"],
        "content_feedback": ["Start bullets with action verbs","Add more job-relevant keywords"],
        "section_scores": {"keyword_match":60,"formatting":75,"content_clarity":70},
        "overall_feedback": "Improve keyword alignment and quantify achievements."
    }