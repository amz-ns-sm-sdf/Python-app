from flask import Flask, render_template, request, redirect, session
import mysql.connector
import bcrypt
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")  # Flask secret key

# MySQL Configuration
db = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)

# ---------------- User Registration ----------------
@app.route("/", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        address = request.form["address"]
        password = request.form["password"]

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        cursor = db.cursor()
        sql = "INSERT INTO users (name, email, phone, address, password) VALUES (%s, %s, %s, %s, %s)"
        values = (name, email, phone, address, hashed_password)
        cursor.execute(sql, values)
        db.commit()
        cursor.close()

        return redirect("/login")

    return render_template("register.html")

# ---------------- User Login ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"].encode('utf-8')

        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()
        cursor.close()

        if user and bcrypt.checkpw(password, user["password"].encode('utf-8')):
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            return redirect("/dashboard")
        else:
            return "Invalid Credentials! Try again."

    return render_template("login.html")

# ---------------- User Dashboard ----------------
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, name, email, phone, address FROM users WHERE id = %s", (session["user_id"],))
    user = cursor.fetchone()
    cursor.close()

    if not user:
        return "User not found!", 404

    return render_template("dashboard.html", user=user)


# ---------------- Admin Page (List of Users) ----------------
@app.route("/admin")
@app.route("/admin")
def admin():
    if "user_id" not in session:
        return redirect("/login")

    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT is_admin FROM users WHERE id = %s", (session["user_id"],))
    user = cursor.fetchone()

    if not user or user["is_admin"] == 0:
        return "Access Denied! Only admins can view this page.", 403

    cursor.execute("SELECT id, name, email, phone, address FROM users")
    users = cursor.fetchall()
    cursor.close()

    print(users)  # Debugging: Check if users are fetched

    return render_template("admin.html", users=users)


# ---------------- Logout ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")



if __name__ == "__main__":
    app.run(debug=True)
