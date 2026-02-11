from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json
import os
from database import init_db, get_or_create_user, save_resume, get_user_resumes, get_resume_by_id, save_cover_letter
from ai_helper import generate_resume, optimize_resume, check_ats, generate_cover_letter

app = Flask(__name__)
app.secret_key = 'hackathon-resume-builder-2024'

# Initialize database on startup
init_db()


# ─── LANDING PAGE (Name Entry) ───
@app.route('/', methods=['GET', 'POST'])
def landing():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if name:
            user = get_or_create_user(name)
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            return redirect(url_for('dashboard'))
    return render_template('landing.html')


# ─── DASHBOARD ───
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('landing'))
    resumes = get_user_resumes(session['user_id'])
    return render_template('dashboard.html', user_name=session['user_name'], resumes=resumes)


# ─── RESUME BUILDER (From Scratch) ───
@app.route('/builder', methods=['GET', 'POST'])
def builder():
    if 'user_id' not in session:
        return redirect(url_for('landing'))
    return render_template('builder.html', user_name=session['user_name'])


@app.route('/api/build-resume', methods=['POST'])
def api_build_resume():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    data = request.json
    result = generate_resume(data)
    resume_id, version = save_resume(
        user_id=session['user_id'],
        content=json.dumps(result),
        template=data.get('template', 'classic')
    )
    return jsonify({'resume': result, 'resume_id': resume_id, 'version': version})


# ─── RESUME OPTIMIZER ───
@app.route('/optimizer', methods=['GET', 'POST'])
def optimizer():
    if 'user_id' not in session:
        return redirect(url_for('landing'))
    return render_template('optimizer.html', user_name=session['user_name'])


@app.route('/api/optimize-resume', methods=['POST'])
def api_optimize_resume():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    data = request.json
    resume_text = data.get('resume_text', '')
    job_description = data.get('job_description', '')

    result = optimize_resume(resume_text, job_description)
    resume_id, version = save_resume(
        user_id=session['user_id'],
        content=json.dumps(result),
        job_description=job_description,
        ats_score=result.get('ats_score')
    )
    return jsonify({'result': result, 'resume_id': resume_id, 'version': version})


# ─── ATS CHECKER ───
@app.route('/api/ats-check', methods=['POST'])
def api_ats_check():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    data = request.json
    resume_text = data.get('resume_text', '')
    job_description = data.get('job_description', '')

    result = check_ats(resume_text, job_description)
    return jsonify(result)


# ─── COVER LETTER ───
@app.route('/cover-letter', methods=['GET'])
def cover_letter_page():
    if 'user_id' not in session:
        return redirect(url_for('landing'))
    return render_template('cover_letter.html', user_name=session['user_name'])


@app.route('/api/cover-letter', methods=['POST'])
def api_cover_letter():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    data = request.json
    resume_text = data.get('resume_text', '')
    job_description = data.get('job_description', '')

    result = generate_cover_letter(resume_text, job_description)
    save_cover_letter(session['user_id'], None, result, job_description)
    return jsonify({'cover_letter': result})


# ─── RESUME PREVIEW ───
@app.route('/preview/<int:resume_id>')
def preview(resume_id):
    resume = get_resume_by_id(resume_id)
    if not resume:
        return "Resume not found", 404
    content = json.loads(resume['content'])
    template = resume.get('template', 'classic')
    return render_template(f'resume_templates/{template}.html', resume=content)


# ─── PORTFOLIO (Shareable Link) ───
@app.route('/portfolio/<int:resume_id>')
def portfolio(resume_id):
    resume = get_resume_by_id(resume_id)
    if not resume:
        return "Portfolio not found", 404
    content = json.loads(resume['content'])
    return render_template('portfolio.html', resume=content)


# ─── PDF EXPORT (opens printable page → user hits Ctrl+P / Cmd+P) ───
@app.route('/export/<int:resume_id>')
def export_pdf(resume_id):
    resume = get_resume_by_id(resume_id)
    if not resume:
        return "Resume not found", 404
    content = json.loads(resume['content'])
    template = resume.get('template', 'classic')
    html = render_template(f'resume_templates/{template}.html', resume=content)
    # Add a print script so the browser auto-opens the print dialog
    print_script = '<script>window.onload = function() { window.print(); }</script>'
    return html + print_script


# ─── VERSION HISTORY ───
@app.route('/versions')
def versions():
    if 'user_id' not in session:
        return redirect(url_for('landing'))
    resumes = get_user_resumes(session['user_id'])
    return render_template('versions.html', user_name=session['user_name'], resumes=resumes)


# ─── LOGOUT ───
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('landing'))


if __name__ == '__main__':
    app.run(debug=True, port=5001)
