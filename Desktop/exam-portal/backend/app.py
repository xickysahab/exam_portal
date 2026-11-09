
from flask import Flask, render_template, request , redirect,url_for,session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key="your_secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///exam_portal.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

#user database
class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False)

#complete profile database
class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)

    user = db.relationship("User", backref="profile")

#Index Page
@app.route("/")
def home():
    return render_template("index.html")

# Register Page
@app.route("/register", methods=["GET", "POST"])
def reg():
    return render_template("register.html")


# Register User in Database
@app.route("/register_db", methods=["POST"])
def register_db():

    username = request.form["username"]
    email = request.form["email"]
    password = request.form["password"]
    role = request.form["role"]
    old_user = User.query.filter_by(email=email).first()

    if old_user:
        return "User already exists"

    else:
        new_user = User(
            name=username,
            email=email,
            password=password,
            role=role
        )

        db.session.add(new_user)
        db.session.commit()

        return "User created successfully" 


#Login Page 
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        old_user = User.query.filter_by(email=email).first()

        if old_user and old_user.password == password:

            if old_user.role == "admin":
                return "Welcome Back Admin"

            elif old_user.role == "examiner":
                return "Welcome Back Examiner"

            elif old_user.role == "user":
                session["user_id"]=old_user.id
                return redirect(url_for("user_dashboard"))

        elif old_user:
            return "Wrong Password"

        else:
            return "User not found"

    return render_template("login.html")


#Complete Profile
@app.route("/complete_profile", methods=["GET", "POST"])
def complete_profile():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        age = request.form["age"]
        gender = request.form["gender"]
        address = request.form["address"]
        phone = request.form["phone"]

        if not phone.isdigit() or len(phone) != 10:
            return "Phone number must contain exactly 10 digits"

        user = User.query.get(session["user_id"])

        new_profile = UserProfile(
            user_id=user.id,
            name=user.name,
            age=int(age),
            gender=gender,
            address=address,
            phone=phone,
            email=user.email
        )

        db.session.add(new_profile)
        db.session.commit()

        return redirect(url_for("user_dashboard"))

    return render_template("complete_profile.html")


#User Dashboard
@app.route("/user_dashboard")
def user_dashboard():
    return render_template("user_dashboard.html")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True, port=5001)
