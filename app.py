from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'signup' in request.form:
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            email = request.form.get('email')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            
            if User.query.filter_by(email=email).first():
                flash('Email address already registered!', 'signup_error')
                return redirect(url_for('index') + '?signup=true')

            if password != confirm_password:
                flash('Passwords do not match!', 'signup_error')
                return redirect(url_for('index') + '?signup=true')

            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            new_user = User(first_name=first_name, last_name=last_name, email=email, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('thankyou'))
        
        elif 'signin' in request.form:
            email = request.form.get('email')
            password = request.form.get('password')
            user = User.query.filter_by(email=email).first()
            
            if user and check_password_hash(user.password, password):
                return redirect(url_for('secret_page'))
            else:
                flash('Invalid credentials', 'signin_error')
                return redirect(url_for('index'))
    
    return render_template('index.html')

@app.route('/secret')
def secret_page():
    return render_template('secretpage.html')

@app.route('/thankyou')
def thankyou():
    return render_template('thankyou.html')

if __name__ == '__main__':
    app.run(debug=True)
