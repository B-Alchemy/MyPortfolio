from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
import os
import json
from werkzeug.utils import secure_filename
from auth.auth import check_login
from utils.file_handler import save_file
from utils.json_handler import load_json, save_json
from config import SECRET_KEY, UPLOAD_FOLDER_IMAGES, UPLOAD_FOLDER_PDFS, ALLOWED_IMAGE_EXTENSIONS, ALLOWED_PDF_EXTENSIONS

app = Flask(__name__)
app.secret_key = SECRET_KEY

# Ensure upload folders exist
os.makedirs(UPLOAD_FOLDER_IMAGES, exist_ok=True)
os.makedirs(UPLOAD_FOLDER_PDFS, exist_ok=True)

# ---------------------- AUTH ----------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if check_login(request.form['username'], request.form['password']):
            session['logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# ---------------------- ADMIN DASHBOARD ----------------------
@app.route('/admin')
def admin_dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('admin/admin_dashboard.html')

@app.route('/admin/<section>', methods=['GET', 'POST'])
def edit_section(section):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    json_path = os.path.join('data', f'{section}.json')
    data = load_json(json_path)

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        image_file = request.files.get('image')
        pdf_file = request.files.get('pdf')

        entry = {
            'title': title,
            'description': description,
            'image': save_file(image_file, UPLOAD_FOLDER_IMAGES, ALLOWED_IMAGE_EXTENSIONS) if image_file else '',
            'pdf': save_file(pdf_file, UPLOAD_FOLDER_PDFS, ALLOWED_PDF_EXTENSIONS) if pdf_file else ''
        }

        data.append(entry)
        save_json(json_path, data)
        flash('Content added successfully')
        return redirect(url_for('edit_section', section=section))

    return render_template('admin/admin_about.html', section=section, data=data)

@app.route('/admin/<section>/delete/<int:index>', methods=['POST'])
def delete_entry(section, index):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    json_path = os.path.join('data', f'{section}.json')
    data = load_json(json_path)

    if 0 <= index < len(data):
        data.pop(index)
        save_json(json_path, data)

    return redirect(url_for('edit_section', section=section))

# ---------------------- PUBLIC ROUTES ----------------------
@app.route('/')
def index():
    content = {
        section.replace('.json', ''): load_json(os.path.join('data', section))
        for section in os.listdir('data') if section.endswith('.json')
    }
    return render_template('index.html', content=content)

@app.route('/resume')
def resume():
    return render_template('resume.html')

# ---------------------- STATIC FILE SERVE ----------------------
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    directory = UPLOAD_FOLDER_IMAGES if 'images/' in filename else UPLOAD_FOLDER_PDFS
    return send_from_directory(directory, filename.split('/')[-1])

# ---------------------- ERROR HANDLING ----------------------
@app.errorhandler(404)
def not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('errors/500.html'), 500

# ---------------------- RUN APP ----------------------
if __name__ == '__main__':
    app.run(debug=True)
