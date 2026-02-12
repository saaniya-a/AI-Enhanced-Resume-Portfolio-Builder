// Helpers
function show(id) { document.getElementById(id).classList.remove('hidden'); }
function hide(id) { document.getElementById(id).classList.add('hidden'); }
function $(id) { return document.getElementById(id); }

async function apiCall(url, data) {
    var res = await fetch(url, { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data) });
    return res.json();
}

// Format resume JSON as HTML preview
function formatResumeHTML(r) {
    var h = '<div class="preview-header"><h2>' + (r.name||'') + '</h2>';
    var c = [r.email, r.phone, r.location].filter(Boolean).join(' | ');
    if (c) h += '<p class="preview-contact">' + c + '</p>';
    h += '</div>';
    if (r.summary) h += '<div class="preview-section"><h3>Summary</h3><p>' + r.summary + '</p></div>';
    if (r.experience && r.experience.length) {
        h += '<div class="preview-section"><h3>Experience</h3>';
        r.experience.forEach(function(e) {
            h += '<div class="preview-entry"><div class="preview-entry-header"><strong>'+e.title+'</strong><span>'+(e.duration||'')+'</span></div>';
            if (e.company) h += '<div class="preview-entry-sub">'+e.company+'</div>';
            if (e.bullets) { h += '<ul>'; e.bullets.forEach(function(b){h+='<li>'+b+'</li>';}); h += '</ul>'; }
            h += '</div>';
        }); h += '</div>';
    }
    if (r.education && r.education.length) {
        h += '<div class="preview-section"><h3>Education</h3>';
        r.education.forEach(function(e) {
            h += '<div class="preview-entry"><div class="preview-entry-header"><strong>'+e.degree+'</strong><span>'+(e.year||'')+'</span></div>';
            if (e.school) h += '<div class="preview-entry-sub">'+e.school+'</div>';
            h += '</div>';
        }); h += '</div>';
    }
    if (r.projects && r.projects.length) {
        h += '<div class="preview-section"><h3>Projects</h3>';
        r.projects.forEach(function(p) {
            h += '<div class="preview-entry"><strong>'+p.name+'</strong>';
            if (p.tech) h += ' <span class="preview-tech">('+p.tech+')</span>';
            h += '<p>'+(p.description||'')+'</p></div>';
        }); h += '</div>';
    }
    if (r.skills && r.skills.length) {
        h += '<div class="preview-section"><h3>Skills</h3><div class="preview-skills">';
        r.skills.forEach(function(s){h+='<span class="skill-pill">'+s+'</span>';}); h += '</div></div>';
    }
    if (r.certifications && r.certifications.length) {
        h += '<div class="preview-section"><h3>Certifications</h3><ul>';
        r.certifications.forEach(function(c){h+='<li>'+c+'</li>';}); h += '</ul></div>';
    }
    return h;
}

// Animate SVG score gauge
function setGauge(fillId, numberId, score) {
    var fill = $(fillId), num = $(numberId);
    if (!fill || !num) return;
    var circ = 2 * Math.PI * 50;
    fill.style.strokeDasharray = circ;
    fill.style.strokeDashoffset = circ;
    var color = score >= 70 ? '#27ae60' : score >= 50 ? '#f39c12' : '#e74c3c';
    fill.style.stroke = color; num.style.fill = color;
    setTimeout(function(){ fill.style.strokeDashoffset = circ - (score/100)*circ; }, 100);
    num.textContent = score;
}

// Resume Builder
var resumeForm = $('resume-form');
if (resumeForm) {
    resumeForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        var fields = ['name','email','phone','location','education','experience','projects','skills','certifications','job_description'];
        var data = {}; fields.forEach(function(f){ var el = $(f); if (el) data[f] = el.value; });
        data.template = document.querySelector('input[name="template"]:checked').value;
        hide('result'); show('loading');
        try {
            var res = await apiCall('/api/build-resume', data);
            hide('loading');
            if (res.resume) {
                $('resume-preview').innerHTML = formatResumeHTML(res.resume);
                $('preview-link').href = '/preview/' + res.resume_id;
                $('pdf-link').href = '/export/' + res.resume_id;
                $('portfolio-link').href = '/portfolio/' + res.resume_id;
                show('result');
            }
        } catch(err) { hide('loading'); alert('Error: '+err.message); }
    });
}

// Optimizer
var optForm = $('optimizer-form');
if (optForm) {
    optForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        var data = { resume_text: $('resume_text').value, job_description: $('job_description').value };
        hide('optimize-result'); hide('ats-result'); show('loading');
        try {
            var res = await apiCall('/api/optimize-resume', data);
            hide('loading');
            if (res.result) {
                var r = res.result;
                setGauge('opt-gauge-fill','opt-gauge-number', r.ats_score||0);
                var cd = $('changes-list'); cd.innerHTML = '';
                window._changes = r.changes || [];
                (r.changes||[]).forEach(function(c,i) {
                    cd.innerHTML += '<div class="change-card">' +
                        '<label class="change-checkbox"><input type="checkbox" checked data-index="'+i+'"> Accept</label>' +
                        '<div class="change-side change-before"><div class="change-label">Before</div><p>'+c.original+'</p></div>' +
                        '<div class="change-side change-after"><div class="change-label">After</div><p>'+c.improved+'</p></div>' +
                        '<div class="change-reason">'+c.reason+'</div></div>';
                });
                var sd = $('suggestions-list'); sd.innerHTML = '';
                (r.suggestions||[]).forEach(function(s){ sd.innerHTML += '<div class="suggestion-item">'+s+'</div>'; });
                hide('final-result'); show('optimize-result');
            }
        } catch(err) { hide('loading'); alert('Error: '+err.message); }
    });
}

// Apply selected changes
var applyBtn = $('apply-changes-btn');
if (applyBtn) {
    applyBtn.addEventListener('click', async function() {
        var accepted = [];
        document.querySelectorAll('#changes-list input[type="checkbox"]').forEach(function(cb) {
            if (cb.checked) accepted.push(window._changes[parseInt(cb.dataset.index)]);
        });
        if (!accepted.length) { alert('Select at least one change.'); return; }
        show('apply-loading'); hide('final-result');
        try {
            var res = await apiCall('/api/apply-changes', { resume_text: $('resume_text').value, changes: accepted });
            hide('apply-loading');
            $('final-preview-link').href = '/preview/' + res.resume_id;
            $('final-pdf-link').href = '/export/' + res.resume_id;
            show('final-result');
        } catch(err) { hide('apply-loading'); alert('Error: '+err.message); }
    });
}

// ATS Check
var atsBtn = $('ats-check-btn');
if (atsBtn) {
    atsBtn.addEventListener('click', async function() {
        var data = { resume_text: $('resume_text').value, job_description: $('job_description').value };
        if (!data.resume_text || !data.job_description) { alert('Fill in both fields.'); return; }
        hide('optimize-result'); hide('ats-result'); show('loading');
        try {
            var r = await apiCall('/api/ats-check', data);
            hide('loading');
            setGauge('ats-gauge-fill','ats-gauge-number', r.score||0);
            // Keywords
            function renderTags(id, title, items, cls) {
                var d = $(id); d.innerHTML = '<h4>'+title+'</h4><div class="keyword-tags">';
                (items||[]).forEach(function(k){ d.innerHTML += '<span class="keyword-tag '+cls+'">'+k+'</span>'; });
                d.innerHTML += '</div>';
            }
            renderTags('keywords-found','Keywords Found', r.keyword_match&&r.keyword_match.found, 'keyword-found');
            renderTags('keywords-missing','Missing Keywords', r.keyword_match&&r.keyword_match.missing, 'keyword-missing');
            // Issues & feedback
            function renderList(id, title, items) {
                var d = $(id); d.innerHTML = '<h4>'+title+'</h4>';
                (items||[]).forEach(function(x){ d.innerHTML += '<div class="suggestion-item">'+x+'</div>'; });
            }
            renderList('format-issues','Format Issues', r.format_issues);
            renderList('content-feedback','Content Feedback', r.content_feedback);
            show('ats-result');
        } catch(err) { hide('loading'); alert('Error: '+err.message); }
    });
}

// PDF Upload
document.querySelectorAll('.upload-pdf-btn').forEach(function(btn) {
    btn.addEventListener('click', async function() {
        var input = btn.parentElement.querySelector('.file-input');
        var status = btn.parentElement.querySelector('.upload-status-text');
        if (!input.files.length) { alert('Select a PDF file first.'); return; }
        var fd = new FormData(); fd.append('file', input.files[0]);
        status.textContent = 'Extracting...'; btn.disabled = true;
        try {
            var res = await (await fetch('/api/upload-resume', {method:'POST', body:fd})).json();
            if (res.error) status.textContent = 'Error: '+res.error;
            else { $(btn.dataset.target).value = res.text; status.textContent = 'Done!'; }
        } catch(err) { status.textContent = 'Upload failed.'; }
        btn.disabled = false;
    });
});
