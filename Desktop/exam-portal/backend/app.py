
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
    status = db.Column(db.String(50), default="pending")
    

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




# Course Database
class Course(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(100), nullable=False)
    course_code = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(200))



#Index Page
@app.route("/")
def home():
    return render_template("index.html")

# Register Page
@app.route("/register", methods=["GET", "POST"])
def reg():
    return render_template("register.html")


# Register User in Database
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

    if role == "examiner":
        status = "pending"
    else:
        status = "approved"

    new_user = User(
        name=username,
        email=email,
        password=password,
        role=role,
        status=status
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
                session["user_id"] = old_user.id
                return redirect(url_for("admin_dashboard"))

            elif old_user.role == "examiner":

                if old_user.status == "pending":
                    return "Your account is waiting for Admin approval"

                elif old_user.status == "approved":
                    return "Welcome Back Examiner"

                else:
                    return "Your account has been rejected"

            elif old_user.role == "user":
                session["user_id"] = old_user.id
                return redirect(url_for("user_dashboard"))

        elif old_user:
            return "Wrong Password"

        else:
            return "User not found"

    return render_template("login.html")


# Admin Dashboard
@app.route("/admin_dashboard")
def admin_dashboard():

    view = request.args.get("view")
    status = request.args.get("status")

    examiners = []

    if view == "examiners":

        if status:
            examiners = User.query.filter_by(role="examiner", status=status).all()
        else:
            examiners = User.query.filter_by(role="examiner").all()

    return render_template("admin_dashboard.html", examiners=examiners, view=view)


# Approve Examiner
@app.route("/approve/<int:id>", methods=["POST"])
def approve(id):

    examiner = User.query.get(id)

    examiner.status = "approved"

    db.session.commit()

    return redirect(url_for("admin_dashboard", view="examiners"))


# Reject Examiner
@app.route("/reject/<int:id>", methods=["POST"])
def reject(id):

    examiner = User.query.get(id)

    examiner.status = "rejected"

    db.session.commit()

    return redirect(url_for("admin_dashboard", view="examiners"))

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


# Add Course
@app.route("/add_course", methods=["GET", "POST"])
def add_course():

    if request.method == "POST":

        course_name = request.form["course_name"]
        course_code = request.form["course_code"]
        description = request.form["description"]

        new_course = Course(
            course_name=course_name,
            course_code=course_code,
            description=description
        )

        db.session.add(new_course)
        db.session.commit()

        return redirect(url_for("admin_dashboard", view="courses"))

    return render_template("add_course.html")

#User Dashboard
@app.route("/user_dashboard")
def user_dashboard():
    return render_template("user_dashboard.html")

if __name__ == "__main__":

    with app.app_context():
        db.create_all()

        admin = User.query.filter_by(role="admin").first()

        if not admin:
            new_admin = User(
                name="Admin",
                email="admin@gmail.com",
                password="admin123",
                role="admin",
                status="approved"
            )

            db.session.add(new_admin)
            db.session.commit()

    app.run(debug=True, port=5001)
