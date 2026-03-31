from dotenv import load_dotenv
import os
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
db_name = os.getenv('DB_NAME')

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{user}:{password}@localhost:3306/{db_name}'
db = SQLAlchemy(app)

class Users(db.Model):
    __tablename__ = 'users'

    uid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    full_name = db.Column(db.String(100), unique=False, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(15), nullable=True)
    created_at = db.Column(db.TIMESTAMP, nullable=True, default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.uid} - {self.full_name}>'
    
    # Password helpers
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    # Common queries
    @classmethod
    def get_by_id(cls, uid):
        return cls.query.get(uid)
    
    @classmethod
    def get_by_email(cls, email):
        return cls.query.filter_by(email=email).first()
    
    @classmethod
    def get_all(cls):
        return cls.query.all()
    
    # Serialize
    def to_dict(self):
        return{
            'uid': self.uid,
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if(request.method == 'POST'):
        email = request.form.get('email')
        password = request.form.get('password')

        # Look up user by email
        user = Users.get_by_email(email)

        # Validate user and password
        if user and user.check_password(password):
            session['uid'] = user.uid
            session['full_name'] = user.full_name
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password', 'error')

    return render_template('login.html')

if __name__=='__main__':
    app.run(host='0.0.0.0', debug=True)