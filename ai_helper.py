import os, json, re
from dotenv import load_dotenv
load_dotenv()

# Demo mode toggle: set DEMO_MODE=1 in your environment to enable canned fallbacks.
DEMO_MODE = os.environ.get('DEMO_MODE', '0').lower() in ('1', 'true', 'yes', 'on')

# Groq API key (free, no credit card needed). Set GROQ_API_KEY in your environment or .env.
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
GROQ_MODEL = os.environ.get('GROQ_MODEL', 'llama-3.3-70b-versatile')

if not GROQ_API_KEY and not DEMO_MODE:
    raise RuntimeError(
        "GROQ_API_KEY environment variable not set. "
        "Get a free key at https://console.groq.com/keys and add it to your .env file. "
        "To allow demo fallbacks set DEMO_MODE=1"
    )

from groq import Groq
client = Groq(api_key=GROQ_API_KEY)


def run_chat(prompt, max_tokens=1000, temperature=0.2):
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful resume-writing assistant."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return response.choices[0].message.content


def parse_json(text):
    match = re.search(r'\{[\s\S]*\}', text)
    if match:
        try:
            return json.loads(match.group())
        except Exception:
            return None
    return None


def generate_resume(data):
    job_desc = data.get('job_description', '')
    job_section = (
        f"\nTarget Job Description:\n{job_desc}\n\n"
        "Tailor the resume to match this job — use relevant keywords, "
        "highlight matching skills, and align the summary with the role."
    ) if job_desc else ""

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
        text = run_chat(prompt)
        result = parse_json(text)
        if result:
            return result
    except Exception as e:
        print(f"[AI ERROR - generate_resume] {e}")

    if DEMO_MODE:
        skills = [s.strip() for s in data.get('skills', '').split(',') if s.strip()]
        return {
            "name": data.get('name', 'Your Name'), "email": data.get('email', ''),
            "phone": data.get('phone', ''), "location": data.get('location', ''),
            "summary": f"Professional with experience in {', '.join(skills[:3]) or 'software development'}.",
            "education": [{"degree": data.get('education', '').split('\n')[0], "school": "", "year": "", "details": ""}],
            "experience": [{"title": "Experience", "company": "", "duration": "", "bullets": [data.get('experience', 'No experience provided')]}],
            "projects": [{"name": "Projects", "description": data.get('projects', ''), "tech": ', '.join(skills[:4])}],
            "skills": skills or ["Not specified"],
            "certifications": [c.strip() for c in data.get('certifications', '').split(',') if c.strip()]
        }
    raise RuntimeError('AI generate_resume failed and DEMO_MODE is disabled')


def optimize_resume(resume_text, job_description):
    prompt = (
        "Optimize this resume for the job description. Return ONLY JSON:\n"
        '{"optimized_resume":"improved text","changes":[{"original":"old","improved":"new","reason":"why"}],"ats_score":75,"suggestions":["tip"]}\n\n'
        "RESUME:\n" + resume_text + "\n\nJOB DESCRIPTION:\n" + job_description
    )

    try:
        text = run_chat(prompt)
        result = parse_json(text)
        if result:
            return result
    except Exception as e:
        print(f"[AI ERROR - optimize_resume] {e}")

    if DEMO_MODE:
        return {
            "optimized_resume": resume_text,
            "changes": [{"original": "Worked on projects", "improved": "Developed and maintained project deliverables", "reason": "Stronger action verb"}],
            "ats_score": 70,
            "suggestions": ["Add job-specific keywords", "Quantify achievements", "Use standard section headings"]
        }
    raise RuntimeError('AI optimize_resume failed and DEMO_MODE is disabled')


def check_ats(resume_text, job_description):
    prompt = (
        "Score this resume against the job description. Return ONLY JSON:\n"
        '{"score":72,"keyword_match":{"found":["word"],"missing":["word"]},"format_issues":["issue"],"content_feedback":["tip"],'
        '"section_scores":{"keyword_match":70,"formatting":80,"content_clarity":65},"overall_feedback":"summary"}\n\n'
        "RESUME:\n" + resume_text + "\n\nJOB DESCRIPTION:\n" + job_description
    )
    try:
        text = run_chat(prompt)
        result = parse_json(text)
        if result:
            return result
    except Exception as e:
        print(f"[AI ERROR - check_ats] {e}")

    if DEMO_MODE:
        return {
            "score": 65,
            "keyword_match": {"found": ["Python", "SQL"], "missing": ["Docker", "AWS", "CI/CD"]},
            "format_issues": ["Use standard ATS section headings", "Ensure single-column layout"],
            "content_feedback": ["Start bullets with action verbs", "Add more job-relevant keywords"],
            "section_scores": {"keyword_match": 60, "formatting": 75, "content_clarity": 70},
            "overall_feedback": "Improve keyword alignment and quantify achievements."
        }
    raise RuntimeError('AI check_ats failed and DEMO_MODE is disabled')
