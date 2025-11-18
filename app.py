from flask import Flask, render_template, request, redirect, url_for,session
from flask_sqlalchemy import SQLAlchemy
from datetime import date   
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash

# setting up the flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///smarthealth.db'  # database setup
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'faycel_habchi123456789'  # pour les sessions

db = SQLAlchemy(app)  # database link
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    number = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False)




class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specialty = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(50), nullable=False)
    image = db.Column(db.String(100))  # path for image file in static
    description = db.Column(db.String(300))  # small text about doctor

    # link to appointments (so admin can see which patients booked)
    appointments = db.relationship('Appointment', backref='doctor', lazy=True)


# appointment table (patients fill this in form)
class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    symptoms = db.Column(db.String(300), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    hour = db.Column(db.String(5), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        action = request.form.get("action")  # "login" ou "register"
        error = None

        # Si l'utilisateur veut se CONNECTER
        if action == "login":
            email = request.form.get("login_email")
            password = request.form.get("login_password")

            user = User.query.filter_by(email=email).first()

            if user is None:
                error = "No account found with this email."
            elif not check_password_hash(user.password, password):
                error = "Incorrect password."

            if error is None:
                # on sauvegarde l'utilisateur dans la session
                session["user_id"] = user.id
                session["user_role"] = user.role
                session["user_email"] = user.email
                

                flash("Login successful! Welcome back!", "success")

                # Si admin → redirige vers /admin, sinon vers /search
                if user.role == "admin":
                    return redirect(url_for("admin"))
                else:
                    next_page = request.args.get("next")
                    if next_page:
                        return redirect(next_page)
                    return redirect(url_for("search"))
            else:
                flash(error, "danger")

        # Si l'utilisateur veut s'INSCRIRE
        elif action == "register":
            firstname = request.form.get("firstname")
            lastname = request.form.get("lastname")
            email = request.form.get("email")
            password = request.form.get("password")
            address = request.form.get("address")
            number = request.form.get("number")
            role = "patient"  # par défaut

            # Vérifier que tout est rempli
            if not all([firstname, lastname, email, password, address, number]):
                error = "Please fill in all fields."

            # Vérifier si email déjà utilisé
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                error = "Email already exists! Please use another one."

            if error is None:
                hashed_pw = generate_password_hash(password)

                new_user = User(
                    firstname=firstname,
                    lastname=lastname,
                    email=email,
                    password=hashed_pw,
                    address=address,
                    number=int(number),
                    role=role
                )
                db.session.add(new_user)
                db.session.commit()

                # connexion direct après inscription
                session["user_id"] = new_user.id
                session["user_role"] = new_user.role
                session["user_email"] = new_user.email
                session["user_avatar"] = "img/default-avatar.png"

                flash("Registration successful! You are now logged in.", "success")

                next_page = request.args.get("next")
                if next_page:
                    return redirect(next_page)
                return redirect(url_for("search"))
            else:
                flash(error, "danger")

    # GET → on affiche juste le template login/register
    return render_template("login.html")


@app.route("/doctor_login")
def doctor_login():
    # no password for now just direct route to admin
    return redirect(url_for("admin"))

@app.route("/admin")
def admin():
    doctors = Doctor.query.all()  
    appointments = Appointment.query.all()  
    return render_template("admin.html", doctors=doctors, appointments=appointments)


@app.route("/search")
def search():
    # 1️⃣ Si pas connecté → redirige vers login
    if "user_id" not in session:
        # on garde en mémoire où il voulait aller (ici /search)
        return redirect(url_for("login", next=request.path))

    # 2️⃣ Si connecté → comportement normal
    query = request.args.get("query", "")
    if query:
        doctors = Doctor.query.filter(
            (Doctor.name.like(f"%{query}%")) |
            (Doctor.specialty.like(f"%{query}%")) |
            (Doctor.location.like(f"%{query}%"))
        ).all()
    else:
        doctors = Doctor.query.all()
    return render_template("search.html", doctors=doctors, query=query)


# this is the booking route (for patient)
@app.route("/book/<int:doctor_id>", methods=["GET", "POST"])
def book_appointment(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    message = None
    success = None

    if request.method == "POST":
        name = request.form.get("name")
        age = request.form.get("age")
        gender = request.form.get("gender")
        symptoms = request.form.get("symptoms")
        appointment_date = request.form.get("date")   # ⬅️ correspond à name="date"
        time_str = request.form.get("time")           # ⬅️ correspond à name="time"

        # check if fields are empty
        if not name or not age or not gender or not symptoms or not appointment_date or not time_str:
            message = "Please fill in all fields properly."
        else:
            new_appt = Appointment(
                patient_name=name,
                age=age,
                gender=gender,
                symptoms=symptoms,
                date=appointment_date,
                hour=time_str,          # ⬅️ on utilise la valeur du select
                doctor_id=doctor.id
            )
            db.session.add(new_appt)
            db.session.commit()
            return redirect(url_for("appointment_confirmed", doctor_id=doctor.id))

    # ⬅️ ici, pas de conflit : on utilise dt_date (la classe), pas une variable
    today = date.today().isoformat()  # 'YYYY-MM-DD'

    return render_template(
        "book_appointment.html",
        doctor=doctor,
        message=message,
        success=success,
        today=today      # ⬅️ envoyé au template pour min="{{ today }}"
    )


# confirmation page route
@app.route("/appointment_confirmed/<int:doctor_id>")
def appointment_confirmed(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    # this just shows a page saying booked successfully
    return render_template("appointment_confirmed.html", doctor=doctor)



if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # makes db if not exists

        # only adds demo data once (so it doesn't repeat)
        if not Doctor.query.first():
            doctors = [
                Doctor(name="Dr. John Smith", specialty="Cardiology", location="Sheffield",
                       image="img/doctor1.jpg", description="Expert in cardiovascular health and patient care."),
                Doctor(name="Dr. Emma Lee", specialty="Dermatology", location="Leeds",
                       image="img/doctor2.jpg", description="Specialist in skincare, acne treatment, and laser therapy."),
                Doctor(name="Dr. James Patel", specialty="Orthopedic Surgery", location="Birmingham",
                       image="img/doctor3.jpg", description="Experienced orthopedic surgeon focusing on joint and spine health."),
                Doctor(name="Dr. Olivia Wright", specialty="Neurology", location="Nottingham",
                       image="img/doctor4.jpg", description="Neurology expert specializing in migraines and cognitive disorders."),
                Doctor(name="Dr. Noah Khan", specialty="Pediatrics", location="Manchester",
                       image="img/doctor5.jpg", description="Pediatrician dedicated to child development and family care."),
                Doctor(name="Dr. Sarah Benali", specialty="Psychiatry", location="London",
                       image="img/doctor6.jpg", description="Compassionate psychiatrist supporting mental wellness.")
            ]
            db.session.add_all(doctors)
            db.session.commit()  # save demo doctors
            # just to make sure there’s data for the search page

    # running on debug so can see errors
    app.run(debug=True)