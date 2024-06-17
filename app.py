import os
import cv2
from flask import Flask, render_template, request, flash, redirect, url_for
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'upload'
PROCESSED_FOLDER = 'static'
ALLOWED_EXTENSIONS = {'webp', 'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_img(filename, operation):
    print(f"The operation is {operation} and filename is {filename}.")
    img = cv2.imread(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    match operation:
        case "cgray":
            img_processed = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            new_filename = os.path.join(app.config['PROCESSED_FOLDER'], filename)
            cv2.imwrite(new_filename, img_processed)
            return new_filename
        case "cpng":
            new_filename = os.path.join(app.config['PROCESSED_FOLDER'], f"{filename.split('.')[0]}.png")
            cv2.imwrite(new_filename, img)
            return new_filename
        case "cwebp":
            new_filename = os.path.join(app.config['PROCESSED_FOLDER'], f"{filename.split('.')[0]}.webp")
            cv2.imwrite(new_filename, img)
            return new_filename
        case "cjpg":
            new_filename = os.path.join(app.config['PROCESSED_FOLDER'], f"{filename.split('.')[0]}.jpg")
            cv2.imwrite(new_filename, img)
            return new_filename
        case "cjpeg":
            new_filename = os.path.join(app.config['PROCESSED_FOLDER'], f"{filename.split('.')[0]}.jpeg")
            cv2.imwrite(new_filename, img)
            return new_filename

def cleanup_folders():
    folders = [app.config['UPLOAD_FOLDER'], app.config['PROCESSED_FOLDER']]
    for folder in folders:
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')

@app.route('/')
def hello_world():
    cleanup_folders()  # Clean folders when navigating away from '/edit'
    return render_template('index.html')

@app.route('/about')
def about():
    cleanup_folders()  # Clean folders when navigating away from '/edit'
    return render_template('about.html')

@app.route('/edit', methods=["GET", "POST"])
def edit():
    if request.method == "POST":
        operation = request.form.get("operation")
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            new = process_img(filename, operation)
            flash(f"{new}")
            return render_template('index.html')
    return render_template('index.html')
