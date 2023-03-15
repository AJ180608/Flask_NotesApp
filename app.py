from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session
import sqlite3
import json

db = sqlite3.connect('database.db')
print("Opened database successfully")

db.execute(
    'CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE, password TEXT)')
db.execute('CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, data TEXT, user_id TEXT)')

print("Tables created successfully")
db.close()


app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route('/')
def index():
    if not session.get('name'):
        return render_template('login.html')
    else:
        with sqlite3.connect("database.db") as con:
            cur = con.cursor()
            con.row_factory = sqlite3.Row
            notesDB = cur.execute(
                "SELECT * FROM notes WHERE user_id = (?) ", [session['name']]).fetchall()
            con.commit()
        return render_template('home.html', notes=notesDB, )


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        try:
            with sqlite3.connect("database.db") as con:
                cur = con.cursor()
                con.row_factory = sqlite3.Row
                usernameDB = cur.execute(
                    "SELECT * FROM users WHERE email = (?) ", [email]).fetchall()
                username = usernameDB[0]
                con.commit()
                if password == username[2]:
                    session["name"] = username[1]
                    return redirect("/")
                else:
                    return render_template('login.html', error="Password is incorrect")
        except:
            return render_template('login.html', error="Username does not exist")
    else:
        return render_template('login.html')


@app.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signUp.html")
    else:
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if not email or not password or not confirm_password:
            return render_template('signUp.html', error="No blank fields")
        if confirm_password != password:
            return render_template('signUp.html', error="Passwords do no match")

         # password_hash = generate_password_hash(password)
        try:
            with sqlite3.connect("database.db") as con:
                cur = con.cursor()
                cur.execute(
                    "INSERT INTO users (email,password) VALUES (?,?)", (email, password))
                con.commit()
            print("Account Created")
            return render_template('login.html')
        except:
            return render_template('signUp.html', error="Username already taken")


@app.route('/logout', methods=["POST", "GET"])
def logout():
    session['name'] = None
    return redirect('/login')


@app.route('/new-note', methods=["GET", "POST"])
def new_note():
    if request.method == "GET":
        return render_template("new_note.html")
    else:
        title = request.form.get('title')
        data = request.form.get('content')

        if not title or not data:
            return render_template("new_note.html", error="No blank fields")

        with sqlite3.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO notes (title,data,user_id) VALUES (?,?,?)",
                        (title, data, session['name']))
            con.commit()
        print("Note Created")
        return redirect('/')


@app.route('/delete/<int:id>/', methods=["GET", "POST"])
def delete_note(id):
    with sqlite3.connect("database.db") as con:
        cur = con.cursor()
        cur.execute("DELETE from notes where id=?", [id])
        con.commit()
        return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
