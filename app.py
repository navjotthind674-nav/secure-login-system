from flask import Flask, render_template, request, redirect, session
from flask_bcrypt import Bcrypt
import sqlite3

app = Flask(__name__)
app.secret_key = "thiranex_project_key"

bcrypt = Bcrypt(app)

# Home Page (Login)
@app.route("/")
def home():
    return render_template("login.html")

# Register
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users(username, email, password) VALUES (?, ?, ?)",
                (username, email, hashed_password)
            )
            conn.commit()

        except sqlite3.IntegrityError:
            conn.close()
            return "Email already exists!"

        conn.close()
        return redirect("/")

    return render_template("register.html")

# Login
@app.route("/login", methods=["POST"])
def login():

    email = request.form["email"]
    password = request.form["password"]

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT username, password FROM users WHERE email=?",
        (email,)
    )

    user = cursor.fetchone()
    conn.close()

    if user and bcrypt.check_password_hash(user[1], password):
        session["username"] = user[0]
        return redirect("/dashboard")

    return "Invalid Email or Password"

# Dashboard
@app.route("/dashboard")
def dashboard():

    if "username" not in session:
        return redirect("/")

    return render_template("dashboard.html", username=session["username"])

# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)