from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "secret123"

# ---------------- CONFIG ---------------- #
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# ---------------- DATABASE INIT ---------------- #
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            image TEXT
        )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------------- HOME ---------------- #
@app.route("/")
def home():
    return render_template("home.html")

# ---------------- ABOUT ---------------- #
@app.route("/about")
def about():
    return render_template("about.html")

# ---------------- PORTFOLIO ---------------- #
@app.route("/portfolio")
def portfolio():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM projects")
    projects = cursor.fetchall()
    conn.close()
    return render_template("portfolio.html", projects=projects)

# ---------------- CONTACT ---------------- #
@app.route("/contact", methods=["GET", "POST"])
def contact():
    message = ""
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO contacts (name, email) VALUES (?, ?)", (name, email))
        conn.commit()
        conn.close()

        message = f"Thanks {name}, we received your message!"

    return render_template("contact.html", message=message)

# ---------------- ADMIN LOGIN ---------------- #
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == "admin" and password == "1234":
            session["admin"] = True
            return redirect("/dashboard")

    return render_template("admin_login.html")

# ---------------- DASHBOARD ---------------- #
@app.route("/dashboard")
def dashboard():
    if not session.get("admin"):
        return redirect("/admin")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM projects")
    projects = cursor.fetchall()
    conn.close()

    return render_template("admin_dashboard.html", projects=projects)

# ---------------- ADD PROJECT ---------------- #
@app.route("/add", methods=["GET", "POST"])
def add_project():
    if not session.get("admin"):
        return redirect("/admin")

    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        image = request.files.get("image")

        filename = ""

        if image and image.filename != "":
            filename = image.filename
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            image.save(filepath)

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO projects (title, description, image) VALUES (?, ?, ?)",
            (title, description, filename)
        )
        conn.commit()
        conn.close()

        return redirect("/dashboard")

    return render_template("add_project.html")

# ---------------- LOGOUT ---------------- #
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------------- RUN ---------------- #
if __name__ == "__main__":
    app.run()
