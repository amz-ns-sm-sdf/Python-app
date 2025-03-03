from flask import Flask, render_template, request, redirect
import mysql.connector

app = Flask(__name__)

# MySQL Database Configuration
db = mysql.connector.connect(
    host="localhost",
    user="root",        # Change if you have a different MySQL user
    password="admin",# Change to your MySQL password
    database="registration_db"
)

@app.route("/", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        address = request.form["address"]

        cursor = db.cursor()
        sql = "INSERT INTO users (name, email, phone, address) VALUES (%s, %s, %s, %s)"
        values = (name, email, phone, address)
        cursor.execute(sql, values)
        db.commit()
        cursor.close()

        return redirect("/success")

    return render_template("register.html")

@app.route("/success")
def success():
    return "Registration Successful!"

if __name__ == "__main__":
    app.run(debug=True)
