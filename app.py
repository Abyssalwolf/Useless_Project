from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from summary import extract_text_from_pdf, generate_summary_with_groq
from watermark import add_watermark

app = Flask(__name__)
app.secret_key = 'sebinthomas'

# Setup upload folder
UPLOAD_FOLDER = 'F:/Useless_Project/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///documents.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

migrate = Migrate(app, db)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)

# Simple user model
class User(UserMixin):
    def __init__(self, id, role):
        self.id = id
        self.role = role

# Sample users dictionary (for hackathon purposes, replace with real database if needed)
users = {
    "pattipani": User("pattipani", "person_1"),
    "averagemanager": User("averagemanager", "person_2"),
    "bossman": User("bossman", "person_3")
}

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return users.get(user_id)

@app.route('/')
def index():
    return redirect(url_for('login'))

# Route for logging in users
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':    
        user_id = request.form['user_id']
        if user_id in users:
            login_user(users[user_id])
            print("yes")
            return redirect(url_for('dashboard'))
        else:
            print(f"Failed login attempt for user: {user_id}")
    return render_template('login.html')

# Route for uploading documents
@app.route('/upload', methods=['POST'])
@login_required
def upload():
    print(f"Current user: {current_user.id}, Role: {current_user.role}")
    if current_user.role == "person_1":
        file = request.files['document']
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            full_text = extract_text_from_pdf(file_path)
            summary = generate_summary_with_groq(full_text)

            new_document=Document(filename=filename,file_path=file_path, status='Pending',user_id=current_user.id,summary=summary)
            db.session.add(new_document)
            db.session.commit()
            # Here, save the document metadata (file path, status, etc.) to a database
            return redirect(url_for('dashboard'))
    return "Not authorized", 403

# Route for downloading documents
@app.route('/download/<filename>')
@login_required
def download(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/approve/<int:document_id>', methods=['POST'])
@login_required
def approve(document_id):
    document = Document.query.get_or_404(document_id)
    if current_user.role == "person_2" and not document.approved_by_user_2:
        document.approved_by_user_2 = True
        document.approver_id = current_user.id
        db.session.commit()

        # Add watermark indicating approval by User 2
        input_pdf = os.path.join(app.config['UPLOAD_FOLDER'], document.filename)
        output_pdf = os.path.join(app.config['UPLOAD_FOLDER'], f"user2_approved_{document.filename}")
        add_watermark(input_pdf, output_pdf, "Approved by User 2", position="bottom_left")
        document.filename = f"user2_approved_{document.filename}"
        db.session.commit()
            # Pass the document to `person_3` view by changing roles/access

    elif current_user.role == "person_3" and not document.approved_by_user_3:
        document.approved_by_user_3 = True
        document.approver_id = current_user.id
        document.status = "Final Approval"
        db.session.commit()

        # Add final watermark indicating approval by User 3
        input_pdf = os.path.join(app.config['UPLOAD_FOLDER'], document.filename)
        output_pdf = os.path.join(app.config['UPLOAD_FOLDER'], f"user3_final_approved_{document.filename}")
        add_watermark(input_pdf, output_pdf, "Approved by User 3 - Final Approval", position="bottom_right")
        document.filename = f"user3_final_approved_{document.filename}"
        db.session.commit()
    
    else:
        return "Unauthorized", 403

    return redirect(url_for('dashboard'))

@app.route('/reject/<int:document_id>', methods=['POST'])
@login_required
def reject(document_id):
    document = Document.query.get_or_404(document_id)
    if current_user.role in ['person_2', 'person_3']:  # Assuming person_2 and person_3 can reject
        document.status = 'Rejected'
        document.approver_id = current_user.id
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
        db.session.delete(document)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return "Not authorized", 403

# Dashboard route where users see the document and actions
@app.route('/dashboard')
@login_required
def dashboard():
    # You could load the uploaded files and status from a database here
    documents = Document.query.all()
    return render_template('dashboard.html', documents=documents, role=current_user.role)

@app.route('/delete/<int:doc_id>', methods=['POST'])
@login_required
def delete_document(doc_id):
    if current_user.role == "person_1":
        doc = Document.query.get(doc_id)
        if doc and doc.status == "Final Approval":
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], doc.filename))  # Delete file
            db.session.delete(doc)  # Delete from database
            db.session.commit()
            return redirect(url_for('dashboard'))
    return "Not authorized", 403

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(150), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), default='Pending')  # Default status is 'Pending'
    user_id = db.Column(db.String(150), nullable=False)  # To track which user uploaded it
    approver_id = db.Column(db.String(150))
    approved_by_user_2 = db.Column(db.Boolean, default=False)
    approved_by_user_3 = db.Column(db.Boolean, default=False)
    summary = db.Column(db.Text)

    def __repr__(self):
        return f'<Document {self.filename} - {self.status}>'

if __name__ == '__main__':
    app.run(debug=True)