from functools import wraps
from flask_login import current_user
from app import app, db, csrf
from flask import flash, render_template, redirect, url_for, session, request, current_app
from app.forms import RegisterForm,LoginForm, PaymentForm
from app.models import User
import os
from werkzeug.utils import secure_filename
from app.extractText import render_pdf_to_images, load_symspell, load_domain_vocab, preprocess_image, ocr_image, correct_spelling_symspell, filter_domain
from app.docNotes import count_tokens, extract_chapter_number, ai_summarise, points_extractor, getFinalNotes
from langchain.schema import Document
import pypandoc
from docx2pdf import convert
from datetime import datetime

WORKDIR = os.getcwd()
md_file = os.path.join(WORKDIR, "notes.md")
docx_file = os.path.join(WORKDIR, "Physics_Notes.docx")
pdf_file  = os.path.join(WORKDIR, "Physics_Notes.pdf")

ALLOWED_EXTENSIONS = {'pdf', 'mp4', 'mov', 'avi'}
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_current_user():
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None

@app.context_processor
def inject_current_accounts():
    return {
        'current_user': get_current_user()
    }

def login_required_user(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            print("Please log in to access this page!!!")
            return redirect(url_for('signin'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/home')
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/dashboard')
@login_required_user
def dashboard():
    user_data=User.query.filter_by(id=get_current_user().id).first()
    if not user_data.is_premium:
        return render_template('dashboardfree.html', user_data=user_data)
    else:
        return render_template('dashboard.html', user_data=user_data)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'user_id' in session: 
        return redirect(url_for('dashboard'))
        
    form = RegisterForm()
    if form.validate_on_submit():
        print(form.username.data)
        print(form.email.data)
        print(form.password.data)
        with app.app_context():
            user_data = User(
                username=form.username.data,
                email=form.email.data,
                password=form.password.data 
            )
            db.session.add(user_data)
            db.session.commit()
            session['user_id'] = user_data.id
        return redirect(url_for('dashboard'))

    return render_template('signup.html', form=form)

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if 'user_id' in session: 
        return redirect(url_for('dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(form.password.data):
            session['user_id'] = attempted_user.id
            return redirect(url_for('dashboard'))
        else:
            flash("Username and Password do not match! Please try again", "danger")

    return render_template('signin.html', form=form)

@app.route('/payments', methods=['GET', 'POST'])
@login_required_user
def payments():
    form = PaymentForm()
    if form.validate_on_submit():
        user = User.query.get(get_current_user().id)
        user.is_premium = True
        db.session.commit()

        return redirect(url_for('dashboard'))
    else:
        print("CSRF token valid?" , form.csrf_token.validate(form))

    return render_template('payment.html', form=form)

@app.route('/notes', methods=['GET', 'POST'])
@login_required_user
@csrf.exempt
def upload_pdf():
    uploaded_filename = None

    if request.method == 'POST':
        # `pdf_file` matches the <input name="pdf_file" …>
        upload = request.files.get('pdf_file')

        if not upload or upload.filename == '':
            flash('No file selected', 'warning')
            return redirect(request.url)

        if not allowed_file(upload.filename):
            flash('Only PDF uploads are allowed.', 'error')
            return redirect(request.url)

        # secure the filename, prepend user or timestamp if you like
        filename = secure_filename(f"{get_current_user().id}_{upload.filename}")
        save_path = os.path.join(UPLOAD_FOLDER, filename)

        # save to disk
        upload.save(save_path)
        flash(f'Uploaded {filename} successfully!', 'success')

        uploaded_filename = filename

    # Render your notes page, passing the filename for the “Uploaded:” message
    return render_template(
        'notes.html',
        uploaded_filename=uploaded_filename
    )

@app.route('/generate_notes', methods=['POST'])
@login_required_user
@csrf.exempt
def generate_notes():
    card_type = request.form.get('card_type')  
    tone     = request.form.get('tone')
    language = request.form.get('language')
    audio    = bool(request.form.get('audio'))

    pdf = request.files.get('pdf_file')  
    if not pdf or pdf.filename == '':
        flash('Please upload a PDF file.', 'warning')
        return redirect(request.referrer)

    if not allowed_file(pdf.filename):
        flash('Only PDF files are allowed.', 'error')
        return redirect(request.referrer)

    filename = secure_filename(f"{get_current_user().id}_{pdf.filename}")
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    pdf.save(save_path)

    current_app.logger.info(
        f"User {get_current_user().id} generated {card_type} notes "
        f"(tone={tone}, lang={language}, audio={audio}), file saved as {filename}"
    )
    notes_type=""
    if card_type=="descriptive":
        notes_type="Descriptive"

    path="HexaFalls\\app\\uploads\\"+filename
    print(path)
    pages=render_pdf_to_images(path, zoom=3.0)
    sym=load_symspell()
    vocab=load_domain_vocab()

    all_texts=[]
    for i, pg in enumerate(pages, 1):
        proc=preprocess_image(pg, method='minimal', deskew=False)
        raw=ocr_image(proc, psm=3)
        corrected=correct_spelling_symspell(raw, sym)
        filtered=filter_domain(corrected, vocab)

        all_texts.append(f"---Page {i} ---")
        all_texts.append(filtered)

        print(f"Processed page {i}, chars: {len(filtered)}")

    with open('text_chapters\\chapter03.txt', 'w', encoding='utf-8') as out:
        out.write(''.join(all_texts))

    print("All pages saved to combined_output.txt")

    docs=[]
    for fname in os.listdir("text_chapters"):
        chapter_number=extract_chapter_number(fname)
        if chapter_number is None:
            continue
        with open(os.path.join("text_chapters", fname), "r", encoding="utf-8") as f:
            text = f.read()
        
        
        summary = ai_summarise(text, subject="Physics")
        key_points=points_extractor(text)
        
        doc=Document(
            page_content=text,
            metadata={
                "chapter": chapter_number,
                "summary": summary,
                "key_points": key_points,
                "file_name": fname
            }
        )
        docs.append(doc)

    final_notes=getFinalNotes(docs, notes_type, tone, language=language)
    print(final_notes)

    with open(md_file, "w", encoding="utf-8") as f:
        f.write(final_notes.strip())
    print(f"[{datetime.now()}] Wrote Markdown → {md_file}")

    pypandoc.convert_file(
        source_file=md_file,
        to="docx",
        outputfile=docx_file,
        extra_args=[
            "--toc",            
            "--toc-depth=2",    
        ]
    )
    print(f"[{datetime.now()}] Converted → {docx_file}")

    convert(docx_file, pdf_file)
    print(f"[{datetime.now()}] Converted → {pdf_file}")

    
    
    return redirect(url_for('upload_pdf'))

@app.route('/logout')
@login_required_user
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))