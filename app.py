from flask import Flask, render_template, request, redirect, flash, session
from pymongo import MongoClient
import hashlib
import random

app = Flask(__name__)
app.secret_key = "#12345#"
client = MongoClient('localhost', 27017)
db = client.student_forum

def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

@app.route("/")
def index():
    session['attempts'] = 0
    session['random'] = random.randint(3, 10)
    return render_template('index.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
            user_login_col = db['user_login']
            email = request.form.get("email")
            password = hash_password(request.form.get("password"))
            query = {"email":email, "password":password}
            result = user_login_col.find_one(query)
            if result:
                session['username'] = result['username']
                session['id'] = str(result['_id'])
                return redirect('user_home')
            else:
                session['attempts'] += 1
                if session['attempts'] == session['random']:
                    session['attempts'] = 0
                    session['random'] = random.randint(3, 10)
                    return redirect('security')
                flash('** Check Your Email and Password', 'error')
                return redirect('login')   
    return render_template('login.html')

@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        admin_login_col = db['admin_login']
        email = request.form.get("email")
        password = hash_password(request.form.get("password"))
        query = {"email":email, "password":password}
        result = admin_login_col.find_one(query)
        if result:
            session['admin_username'] = result['username']
            session['admin_id'] = str(result['_id'])
            return redirect('admin_home')
        else:
            session['attempts'] += 1
            if session['attempts'] == session['random']:
                session['attempts'] = 0
                session['random'] = random.randint(3, 10)
                return redirect('security')
            flash('** Check Your Email and Password', 'error')
            return redirect('admin_login')
    return render_template('admin_login.html')

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        user_login_col = db['user_login']
        firstname = request.form.get('firstname').title()
        lastname = request.form.get('lastname').title()
        username = request.form.get('username')
        email = request.form.get('email')
        dob = request.form.get('dob')
        password = hash_password(request.form.get('password'))
        cpassword = hash_password(request.form.get('cpassword'))
        security_question = request.form.get('security_question')
        security_answer = hash_password(request.form.get('security_answer').lower())
        if password != cpassword:
            flash('** Passwords does not match')
            return redirect('signup')
        data = {"firstname":firstname, "lastname":lastname, "username":username, "email":email, "dob":dob, "password":password, "security_question":security_question, "security_answer":security_answer}
        result = user_login_col.insert_one(data)
        if not result:
            flash('** Database Error. Please Try Again')
            return redirect('signup')
        else:
            return redirect('login')
    return render_template('signup.html')

@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        user_login_col = db['user_login']
        email = request.form.get("email")
        security_question = request.form.get("security_question")
        security_answer = hash_password(request.form.get("security_answer").lower())
        password = hash_password(request.form.get("password"))
        cpassword = hash_password(request.form.get("cpassword"))
        if password != cpassword:
            flash('** Passwords does not match')
            return redirect('forgot_password')
        update_condition = {"email": email, "security_question": security_question, "security_answer": security_answer}
        update_query = {"$set": {"password": password}}
        try:
            print(update_condition)
            result = user_login_col.update_one(update_condition, update_query)
            if result.matched_count > 0:
                flash('Password Updated Successfully')
                return redirect('login')
            else:
                flash('Incorrect Security Question/Answer')
                return redirect('login')
        except:
            flash('Incorrect Security Question/Answer')
            return redirect('login')
    return render_template('forgot_password.html')

@app.route('/user_home')
def user_home():
    events_col = db['events']
    result = events_col.find()
    return render_template('user_home.html', events=result)

@app.route('/logout')
def logout():
    session.pop('username')
    session.pop('userid')
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)