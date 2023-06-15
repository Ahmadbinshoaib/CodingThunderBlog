from datetime import datetime
import json
from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail


with open("config.json", 'r') as c:
    params = json.load(c) ["params"]

local_server= True



app = Flask(__name__)
app.secret_key = 'super-secret-key'

app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['gmail-user'],
    MAIL_PASSWORD = params['gmail-password']

)
mail = Mail(app)

if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

db = SQLAlchemy(app)

class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone_num = db.Column(db.String(12), nullable=False)
    msg = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    email = db.Column(db.String(20), nullable=False)

class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(21), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    img_file = db.Column(db.String(20), nullable=True)

@app.route("/")
def index():
    posts= Posts.query.filter_by().all() [0:params['no_of_posts']]
    return render_template('index.html', params=params, posts=posts)

@app.route("/dashboard", methods=['POST', 'GET'])
def dashboard():

    if 'user' in session and session['user'] == params['admin_user']:
        post=Posts.query.all()
        return render_template('dashboard.html', params=params, post=post)

    if request.method == 'POST':
        email = request.form['emailf']
        password = request.form['password']
        if(email== params['admin_user'] and password== params['admin_password']):
            #session variable
            session['user']= email
            post=Posts.query.all()
            return render_template('dashboard.html', params=params, post=post)



    return render_template('login.html', params=params)


@app.route('/logout')
def logout():
    session.pop('user')
    return redirect('/dashboard')


@app.route("/delete/<string:sno>", methods = ['POST', 'GET'])
def delete(sno):
    if 'user' in session and session['user'] == params['admin_user']:
        post = Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect("/dashboard")




@app.route("/about")
def about():
    return render_template('about.html', params=params)

@app.route("/contact", methods = ['POST', 'GET'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        message = request.form['message']
        entry = Contacts(name=name, phone_num=phone, msg=message, date=datetime.now(), email=email)
        db.session.add(entry)
        db.session.commit()

        # mail.send_message("New message from Ahmad Blogs",
        #                   sender="email",
        #                   recipients = [params['gmail-user']],
        #                   body= message + "\n" + phone)



    return render_template('contact.html', params=params)

@app.route("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    post= Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html', params=params, post=post)

@app.route("/edit/<string:sno>", methods = ['POST', 'GET'])
def edit(sno):
    if 'user' in session and session['user'] == params['admin_user']:
        if request.method == 'POST':
            title= request.form.get('title')
            slug = request.form.get('slug')
            content = request.form.get('content')
            img = request.form.get('img_file')
            date= datetime.now()

            if sno=='0':
                post = Posts(title=title, slug=slug, content=content, img_file=img, date=date)
                db.session.add(post)
                db.session.commit()
            else:
                post = Posts.query.filter_by(sno=sno).first()
                post.title = title
                post.slug = slug
                post.content = content
                post.img_file = img
                post.date = date
                db.session.commit()
                return redirect('/edit/' + sno)

        post = Posts.query.filter_by(sno=sno).first()
        return render_template('edit.html', params=params, post=post, sno=sno)








app.run(debug=True)