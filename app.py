from flask import Flask, render_template, send_from_directory
import os
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DATA_FOLDER = 'data'
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Define all 12 sections: id, title, filename
SECTIONS = [
    ('home', 'Home', 'home.json'),
    ('about', 'About Me', 'about.json'),
    ('projects', 'Projects', 'projects.json'),
    ('skills', 'Skills', 'skills.json'),
    ('timeline', 'Timeline', 'timeline.json'),
    ('resume', 'Resume', 'resume.json'),
    ('education', 'Education', 'education.json'),
    ('experience', 'Work Experience', 'experience.json'),
    ('certifications', 'Certifications', 'certifications.json'),
    ('languages', 'Languages', 'languages.json'),
    ('contact', 'Contact', 'contact.json'),
    ('tools', 'Tools & Technologies', 'tools.json')
]

def load_data(file):
    path = os.path.join(DATA_FOLDER, file)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

@app.route('/')
def index():
    sections = []
    for sec_id, sec_title, filename in SECTIONS:
        items = load_data(filename)
        sections.append({
            'id': sec_id,
            'title': sec_title,
            'items': items
        })
    return render_template('index.html', sections=sections)

@app.route('/static/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)
