from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json
from database import (init_db, get_or_create_user, save_resume, get_user_resumes,
                      get_resume_by_id, delete_resume, rename_resume)
from ai_helper import generate_resume, optimize_resume, check_ats

app = Flask(__name__)
app.secret_key = 'hackathon-resume-builder-2024'
init_db()

def logged_in():
    return 'user_id' in session

def render_resume(resume_id):
    resume = get_resume_by_id(resume_id)
    if not resume: return None, None
    content = json.loads(resume['content'])
    t = resume.get('template', 'classic')
    tpl = 'resume_templates/text.html' if (t == 'text' or 'text' in content) else f'resume_templates/{t}.html'
    return content, tpl

# ─── PAGE ROUTES ───

@app.route('/', methods=['GET', 'POST'])
def landing():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        if name and email:
            user = get_or_create_user(name, email)
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            return redirect(url_for('landing'))
    user_name = session.get('user_name') if logged_in() else None
    return render_template('landing.html', user_name=user_name)

@app.route('/dashboard')
def dashboard():
    return redirect(url_for('landing'))

@app.route('/builder')
def builder():
    if not logged_in(): return redirect(url_for('landing'))
    return render_template('builder.html', user_name=session['user_name'])

@app.route('/optimizer')
def optimizer():
    if not logged_in(): return redirect(url_for('landing'))
    return render_template('optimizer.html', user_name=session['user_name'])

@app.route('/versions')
def versions():
    if not logged_in(): return redirect(url_for('landing'))
    return render_template('versions.html', user_name=session['user_name'], resumes=get_user_resumes(session['user_id']))

@app.route('/preview/<int:resume_id>')
def preview(resume_id):
    content, tpl = render_resume(resume_id)
    if not content: return "Resume not found", 404
    return render_template(tpl, resume=content)

@app.route('/portfolio/<int:resume_id>')
def portfolio(resume_id):
    resume = get_resume_by_id(resume_id)
    if not resume: return "Not found", 404
    return render_template('portfolio.html', resume=json.loads(resume['content']))

@app.route('/export/<int:resume_id>')
def export_pdf(resume_id):
    content, tpl = render_resume(resume_id)
    if not content: return "Resume not found", 404
    return render_template(tpl, resume=content) + '<script>window.onload=function(){window.print()}</script>'

@app.route('/admin')
def admin():
    from database import get_db
    db = get_db()
    users = [dict(r) for r in db.execute(
        'SELECT users.id, users.name, users.created_at, COUNT(resumes.id) as resume_count '
        'FROM users LEFT JOIN resumes ON users.id = resumes.user_id '
        'GROUP BY users.id ORDER BY users.created_at DESC').fetchall()]
    db.close()
    return render_template('admin.html', users=users)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('landing'))

# ─── API ROUTES ───

@app.route('/api/build-resume', methods=['POST'])
def api_build_resume():
    if not logged_in(): return jsonify({'error': 'Not logged in'}), 401
    data = request.json
    result = generate_resume(data)
    rid, ver = save_resume(session['user_id'], json.dumps(result), template=data.get('template', 'classic'))
    return jsonify({'resume': result, 'resume_id': rid, 'version': ver})

@app.route('/api/optimize-resume', methods=['POST'])
def api_optimize_resume():
    if not logged_in(): return jsonify({'error': 'Not logged in'}), 401
    data = request.json
    result = optimize_resume(data.get('resume_text', ''), data.get('job_description', ''))
    rid, ver = save_resume(session['user_id'], json.dumps(result), job_description=data.get('job_description', ''), ats_score=result.get('ats_score'))
    return jsonify({'result': result, 'resume_id': rid, 'version': ver})

@app.route('/api/ats-check', methods=['POST'])
def api_ats_check():
    if not logged_in(): return jsonify({'error': 'Not logged in'}), 401
    data = request.json
    return jsonify(check_ats(data.get('resume_text', ''), data.get('job_description', '')))

@app.route('/api/upload-resume', methods=['POST'])
def api_upload_resume():
    if not logged_in(): return jsonify({'error': 'Not logged in'}), 401
    file = request.files.get('file')
    if not file: return jsonify({'error': 'No file'}), 400
    try:
        from PyPDF2 import PdfReader
        text = '\n'.join(page.extract_text() for page in PdfReader(file).pages)
        return jsonify({'text': text.strip()})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/apply-changes', methods=['POST'])
def api_apply_changes():
    if not logged_in(): return jsonify({'error': 'Not logged in'}), 401
    data = request.json
    text = data.get('resume_text', '')
    for change in data.get('changes', []):
        text = text.replace(change['original'], change['improved'])
    rid, ver = save_resume(session['user_id'], json.dumps({"text": text}), template='text', label='Optimized')
    return jsonify({'resume_id': rid, 'version': ver})

@app.route('/api/delete-resume/<int:resume_id>', methods=['POST'])
def api_delete_resume(resume_id):
    if not logged_in(): return jsonify({'error': 'Not logged in'}), 401
    delete_resume(resume_id, session['user_id'])
    return jsonify({'success': True})

@app.route('/api/rename-resume/<int:resume_id>', methods=['POST'])
def api_rename_resume(resume_id):
    if not logged_in(): return jsonify({'error': 'Not logged in'}), 401
    rename_resume(resume_id, session['user_id'], request.json.get('label', ''))
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True, port=5001)