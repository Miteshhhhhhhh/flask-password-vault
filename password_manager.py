from flask import Flask, g, request, redirect, render_template
import sqlite3
import string
import random

app = Flask(__name__)
Database = "password.db"

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect("password.db")
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    db.execute("CREATE TABLE IF NOT EXISTS passwords(id INTEGER PRIMARY KEY AUTOINCREMENT, website TEXT NOT NULL, username TEXT NOT NULL, password TEXT NOT NULL)")
    db.commit()

with app.app_context():
    init_db()

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        website = request.form["website"]
        username = request.form["username"]
        password = request.form[("password")]
        db = get_db()
        db.execute("INSERT INTO passwords(website, username, password) VALUES (?,?,?)",
                   (website, username, password))
        db.commit()
        return redirect("/")
    db = get_db()
    passwords = db.execute("SELECT * FROM passwords").fetchall()
    return render_template("home.html", passwords=passwords, generated_password=None)

def generate_password(length=12):
    password = "".join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=length))
    return password

@app.route("/generate")
def generate():
    new_password = generate_password()
    db = get_db()
    passwords = db.execute("SELECT * FROM passwords").fetchall()
    return render_template("home.html", passwords=passwords, generated_password=new_password)

@app.route("/delete/<int:id>")
def delete(id):
    db = get_db()
    db.execute("DELETE FROM passwords WHERE id = ?", (id,))
    db.commit()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=False)
