from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from utils import parse_and_update
from models import db, User, ParsingResult
import hashlib
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///dbase.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Please log in to access this page."

@app.template_filter('sha256')
def sha256_filter(value):
    return hashlib.sha256(value.encode()).hexdigest()    

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.context_processor
def inject_user():
    return dict(user=current_user)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/parse", methods=["GET", "POST"])
@login_required
def parse():
    if request.method == "POST":
        try:
            data = request.get_json()
            url = data.get("url")
            xpath = data.get("xpath")

            if not url or not xpath:
                return jsonify({"error": "Missing URL or XPath"}), 400

            print(f"Parsing URL: {url}, XPath: {xpath}")  # Debugging print

            result = parse_and_update(current_user.email, url.strip(), xpath.strip())
            return jsonify(result)

        except Exception as e:
            print(f"Error during parsing: {str(e)}")  # Debugging print
            return jsonify({"error": str(e)}), 500

    return render_template("parse.html")



@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        if User.query.filter_by(email=email).first():
            flash("Email is already registered.", "error")
            return redirect(url_for("register"))
        
        email_hash = sha256_filter(email) 

        # Перевірка: чи такий хеш вже існує
        if User.query.filter_by(email_sha256=email_hash).first():
            flash("This email hash already exists in the system.", "error")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful. Please log in.", "success")
        return redirect(url_for('login'))

    return render_template("register.html")    

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('parse'))
    
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember')
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user, remember=bool(remember))
            flash("Login successful!", "success")
            return redirect(url_for('parse'))
        
        else:
            flash("Invalid email or password.", "error")

    return render_template("login.html") 

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for('login'))

@app.route("/results", methods=["GET"])
@login_required
def results():
    # Отримуємо всі результати для поточного користувача
    user_results = ParsingResult.query.filter_by(user_email=current_user.email).all()
    
    # Переконайтеся, що на сторінці завжди актуальні результати
    return jsonify([{
        "url": result.url,
        "xpath": result.xpath,
        "result": result.result,
        "timestamp": result.timestamp.strftime("%Y-%m-%d %H:%M:%S")
    } for result in user_results])

@app.route('/delete_result', methods=['DELETE'])
@login_required
def delete_result():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "URL is missing."}), 400

    result = db.session.query(ParsingResult).filter_by(url=url).first()
    if result:
        db.session.delete(result)
        db.session.commit()
        return jsonify({"message": "Record deleted successfully."}), 200

    return jsonify({"error": "Record not found."}), 404

@app.route('/delete_profile', methods=["POST"])
@login_required
def delete_profile():
    try:
        ParsingResult.query.filter_by(user_email=current_user.email).delete()
        User.query.filter_by(email=current_user.email).delete()
        db.session.commit()
        logout()
        flash("Your profile has been deleted successfully.", "success")
        return redirect(url_for("register"))
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while deleting your profile.", "error")
        return redirect(url_for("parse"))

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)