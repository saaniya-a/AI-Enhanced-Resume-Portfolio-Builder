// ─── HELPER: Show/Hide elements ───
function show(id) { document.getElementById(id).classList.remove('hidden'); }
function hide(id) { document.getElementById(id).classList.add('hidden'); }

// ─── HELPER: API Call ───
async function apiCall(url, data) {
    const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    return response.json();
}

// ─── RESUME BUILDER FORM ───
const resumeForm = document.getElementById('resume-form');
if (resumeForm) {
    resumeForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const data = {
            name: document.getElementById('name').value,
            email: document.getElementById('email').value,
            phone: document.getElementById('phone').value,
            location: document.getElementById('location').value,
            education: document.getElementById('education').value,
            experience: document.getElementById('experience').value,
            projects: document.getElementById('projects').value,
            skills: document.getElementById('skills').value,
            certifications: document.getElementById('certifications').value,
            template: document.querySelector('input[name="template"]:checked').value
        };

        hide('result');
        show('loading');

        try {
            const result = await apiCall('/api/build-resume', data);
            hide('loading');

            if (result.resume) {
                // Show preview
                const preview = document.getElementById('resume-preview');
                preview.textContent = JSON.stringify(result.resume, null, 2);

                // Set action links
                document.getElementById('preview-link').href = '/preview/' + result.resume_id;
                document.getElementById('pdf-link').href = '/export/' + result.resume_id;
                document.getElementById('portfolio-link').href = '/portfolio/' + result.resume_id;

                show('result');
            }
        } catch (err) {
            hide('loading');
            alert('Error: ' + err.message);
        }
    });
}

// ─── OPTIMIZER FORM ───
const optimizerForm = document.getElementById('optimizer-form');
if (optimizerForm) {
    optimizerForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const data = {
            resume_text: document.getElementById('resume_text').value,
            job_description: document.getElementById('job_description').value
        };

        hide('optimize-result');
        hide('ats-result');
        show('loading');

        try {
            const result = await apiCall('/api/optimize-resume', data);
            hide('loading');

            if (result.result) {
                const r = result.result;

                // Score
                document.querySelector('#optimize-result .score-number').textContent = r.ats_score || '--';

                // Changes
                const changesDiv = document.getElementById('changes-list');
                changesDiv.innerHTML = '<h4>Changes Made:</h4>';
                if (r.changes) {
                    r.changes.forEach(change => {
                        changesDiv.innerHTML += `
                            <div class="change-item">
                                <div class="change-original">${change.original}</div>
                                <div class="change-improved">${change.improved}</div>
                                <div class="change-reason">${change.reason}</div>
                            </div>
                        `;
                    });
                }

                // Suggestions
                const sugDiv = document.getElementById('suggestions-list');
                sugDiv.innerHTML = '<h4>Suggestions:</h4>';
                if (r.suggestions) {
                    r.suggestions.forEach(s => {
                        sugDiv.innerHTML += `<div class="suggestion-item">${s}</div>`;
                    });
                }

                // Links
                document.getElementById('preview-link').href = '/preview/' + result.resume_id;
                document.getElementById('pdf-link').href = '/export/' + result.resume_id;

                show('optimize-result');
            }
        } catch (err) {
            hide('loading');
            alert('Error: ' + err.message);
        }
    });
}

// ─── ATS CHECK BUTTON ───
const atsBtn = document.getElementById('ats-check-btn');
if (atsBtn) {
    atsBtn.addEventListener('click', async () => {
        const data = {
            resume_text: document.getElementById('resume_text').value,
            job_description: document.getElementById('job_description').value
        };

        if (!data.resume_text || !data.job_description) {
            alert('Please fill in both fields.');
            return;
        }

        hide('optimize-result');
        hide('ats-result');
        show('loading');

        try {
            const result = await apiCall('/api/ats-check', data);
            hide('loading');

            // Score
            document.querySelector('#ats-result .score-number').textContent = result.score || '--';

            // Keywords found
            const foundDiv = document.getElementById('keywords-found');
            foundDiv.innerHTML = '<h4>Keywords Found:</h4><div class="keyword-tags">';
            if (result.keyword_match && result.keyword_match.found) {
                result.keyword_match.found.forEach(k => {
                    foundDiv.innerHTML += `<span class="keyword-tag keyword-found">${k}</span>`;
                });
            }
            foundDiv.innerHTML += '</div>';

            // Keywords missing
            const missingDiv = document.getElementById('keywords-missing');
            missingDiv.innerHTML = '<h4>Missing Keywords:</h4><div class="keyword-tags">';
            if (result.keyword_match && result.keyword_match.missing) {
                result.keyword_match.missing.forEach(k => {
                    missingDiv.innerHTML += `<span class="keyword-tag keyword-missing">${k}</span>`;
                });
            }
            missingDiv.innerHTML += '</div>';

            // Format issues
            const formatDiv = document.getElementById('format-issues');
            formatDiv.innerHTML = '<h4>Format Issues:</h4>';
            if (result.format_issues) {
                result.format_issues.forEach(i => {
                    formatDiv.innerHTML += `<div class="suggestion-item">${i}</div>`;
                });
            }

            // Content feedback
            const feedbackDiv = document.getElementById('content-feedback');
            feedbackDiv.innerHTML = '<h4>Content Feedback:</h4>';
            if (result.content_feedback) {
                result.content_feedback.forEach(f => {
                    feedbackDiv.innerHTML += `<div class="suggestion-item">${f}</div>`;
                });
            }

            show('ats-result');
        } catch (err) {
            hide('loading');
            alert('Error: ' + err.message);
        }
    });
}

// ─── COVER LETTER FORM ───
const clForm = document.getElementById('cover-letter-form');
if (clForm) {
    clForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const data = {
            resume_text: document.getElementById('cl_resume_text').value,
            job_description: document.getElementById('cl_job_description').value
        };

        hide('cover-letter-result');
        show('loading');

        try {
            const result = await apiCall('/api/cover-letter', data);
            hide('loading');

            if (result.cover_letter) {
                document.getElementById('cover-letter-text').textContent = result.cover_letter;
                show('cover-letter-result');
            }
        } catch (err) {
            hide('loading');
            alert('Error: ' + err.message);
        }
    });
}

// ─── COPY TO CLIPBOARD ───
function copyToClipboard() {
    const text = document.getElementById('cover-letter-text').textContent;
    navigator.clipboard.writeText(text).then(() => {
        alert('Copied to clipboard!');
    });
}