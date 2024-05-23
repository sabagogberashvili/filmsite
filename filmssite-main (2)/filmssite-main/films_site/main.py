from flask import Flask, request, render_template, redirect, url_for, flash, session
import os
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'
Base = declarative_base()
currentlocation = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = 'static/images/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif',"webp"}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(30), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)

class Film(Base):
    __tablename__ = 'films'
    id = Column(Integer, primary_key=True)
    title = Column(String(30), nullable=False)
    years = Column(String(4), nullable=False)
    budget = Column(Float, nullable=False)
    url = Column(String(200), nullable=True)  
    filename = Column(String(100), nullable=True)

engine = create_engine('sqlite:///database.db', echo=True)
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)
db_session = Session()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    films = db_session.query(Film).all()
    return render_template('index.html', films=films)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        if db_session.query(User).filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('register'))
        
        new_user = User(username=username, email=email, password=password)
        db_session.add(new_user)
        db_session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = db_session.query(User).filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            session['email'] = user.email
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
            return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/home')
def homepage():
    films = db_session.query(Film).all()
    return render_template('home.html', films=films)

@app.route('/films', methods=['GET', 'POST'])
def films():
    if request.method == 'POST':
        title = request.form['title']
        years = request.form['years']
        budget = request.form['budget']
        url = request.form['url']  

        file = request.files['file']

        if title and years and budget and file and allowed_file(file.filename):
            try:
                years = int(years)
                budget = float(budget)

                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                new_film = Film(title=title, years=str(years), budget=budget, url=url, filename=filename)  
                db_session.add(new_film)
                db_session.commit()
                flash('Film added successfully')
                return redirect(url_for('homepage'))
            except ValueError:
                flash('Invalid input for years or budget')
        else:
            flash('Please fill out all fields and ensure the file is an allowed type')
    films = db_session.query(Film).all()
    return render_template('films.html', films=films)

@app.route('/dashboard')
def dashboard():
    if 'email' in session:
        user = db_session.query(User).filter_by(email=session['email']).first()
        return render_template('user.html', user=user)
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('index'))

@app.route('/delete_film/<int:film_id>', methods=['POST'])
def delete_film(film_id):
    film = db_session.query(Film).filter_by(id=film_id).first()
    if film:
        db_session.delete(film)
        db_session.commit()
        flash('Film deleted successfully')
    else:
        flash('Film not found')
    return redirect(url_for('homepage'))

if __name__ == "__main__":
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)

app = Flask(__name__)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return redirect(url_for('login'))
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)