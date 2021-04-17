from datetime import datetime
from flask_restful import Resource, Api

import requests
from flask import Flask, render_template, request, redirect, session, make_response, send_file, jsonify
from mysql.connector import connect
from flask_mail import Mail, Message
import random
import string
app = Flask(__name__)
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME='saranshpareek12@gmail.com',
    MAIL_PASSWORD='9784290149'
)
app.secret_key='ghjhjhq/213763fbf'

mail=Mail(app)

@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/<url>')
def dynamicUrl(url):
    connection = connect(host="localhost", database="student", user="root", password="admin123")
    cur = connection.cursor()
    query1 = "select * from urlinfo where encryptedUrl='{}'".format(url)
    cur.execute(query1)
    orignalurl = cur.fetchone()
    if orignalurl==None:
        return render_template('index.html')
    else:
        print(orignalurl[1])
        return redirect(orignalurl[1])


@app.route('/urlshortner')
def urlshortner():
    # letter='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    url = request.args.get('link')
    custom = request.args.get('customurl')
    print(custom)
    print("planettech")
    connection = connect(host="localhost", database="student", user="root", password="admin123")
    cur = connection.cursor()
    encryptedurl=''
    if custom=='':
        while True:
            encryptedurl=createEncrytedUrl()
            query1="select * from urlinfo where encryptedUrl='{}'".format(encryptedurl)
            cur.execute(query1)
            xyz=cur.fetchone()
            if xyz==None:
                break
        print(encryptedurl)
        if 'userid' in session:
            id=session['userid']
            query = "insert into urlinfo(orignalUrl,encryptedUrl,is_Active,created_by) values('{}','{}',1,{})".format(url, encryptedurl,id)
        else:
            query = "insert into urlinfo(orignalUrl,encryptedUrl,is_Active) values('{}','{}',1)".format(url,encryptedurl)
        cur = connection.cursor()
        cur.execute(query)
        connection.commit()
        finalencryptedurl = 'sd.in/' + encryptedurl
    else:
        query1 = "select * from urlinfo where encryptedUrl='{}'".format(custom)
        cur.execute(query1)
        xyz = cur.fetchone()
        if xyz==None:
            if 'userid' in session:
                id = session['userid']
                query = "insert into urlinfo(orignalUrl,encryptedUrl,is_Active,created_by) values('{}','{}',1,{})".format(url,custom,id)
            else:
                query = "insert into urlinfo(orignalUrl,encryptedUrl,is_Active) values('{}','{}',1)".format(url, custom, 1)
            cur = connection.cursor()
            cur.execute(query)
            connection.commit()
            finalencryptedurl = 'srt.in/' +custom
        else:
            return "url already exist"
    if 'userid' in session:
        return redirect('/home')
    else:
        return render_template('index.html',finalencryptedurl=finalencryptedurl,url=url)

def createEncrytedUrl():
    letter = string.ascii_letters + string.digits
    encryptedurl = ''
    for i in range(6):
        encryptedurl = encryptedurl + ''.join(random.choice(letter))
    print(encryptedurl)
    return encryptedurl

@app.route('/signup')
def signup():
    return render_template('SignUp.html')


@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/checkLoginIn')
def checkLogIn():
    email=request.args.get('email')
    password=request.args.get('pwd')
    connection = connect(host="localhost", database="student", user="root", password="admin123")
    cur = connection.cursor()
    query1 = "select * from userdetails where emailId='{}'".format(email)
    cur.execute(query1)
    xyz = cur.fetchone()
    print(xyz)
    if xyz == None:
        return render_template('Login.html', xyz='you are not registered')
    else:
        if password==xyz[3]:
            session['email']=email
            session['userid']=xyz[0]
            #return render_template('UserHome.html')
            return redirect('/home')
        else:
            return render_template('Login.html', xyz='your password is not correct')


@app.route('/register',methods=['post'])
def register():
    email=request.form.get('email')
    username=request.form.get('uname')
    password=request.form.get('pwd')
    connection = connect(host="localhost", database="student", user="root", password="admin123")
    cur = connection.cursor()
    query1 = "select * from userdetails where emailId='{}'".format(email)
    cur.execute(query1)
    xyz = cur.fetchone()
    if xyz==None:
        file=request.files['file']
        print(type(file))
        file.save('F:/files/'+file.filename)
        query = "insert into userdetails(emailId,userName,password,is_Active,created_Date) values('{}','{}','{}',1,now())".format(email, username, password)
        cur = connection.cursor()
        cur.execute(query)
        connection.commit()
        return 'you are successfully registered'

    else:
        return 'already registered'
@app.route('/google')
def google():
    path='F:/files/as.jpg'
    return send_file(path,mimetype='image/jpg',as_attachment=True)

@app.route('/home')
def home():
    if 'userid' in session:
        email=session['email']
        id=session['userid']
        print(id)
        connection = connect(host="localhost", database="student", user="root", password="admin123")
        cur = connection.cursor()
        query1 = "select * from urlinfo where created_by={}".format(id)
        cur.execute(query1)
        data=cur.fetchall()
        print(data)
        return render_template('updateUrl.html',data=data)
    return render_template('login.html')
@app.route('/editUrl',methods=['post'])
def editUrl():
    if 'userid' in session:
        email = session['email']
        print(email)
        id=request.form.get('id')
        url=request.form.get('orignalurl')
        encrypted=request.form.get('encrypted')
        return render_template("editUrl.html",url=url,encrypted=encrypted,id=id)
    return render_template('login.html')

@app.route('/updateUrl',methods=['post'])
def updateUrl():
    if 'userid' in session:
        id=request.form.get('id')
        url=request.form.get('orignalurl')
        encrypted=request.form.get('encrypted')
        connection = connect(host="localhost", database="student", user="root", password="admin123")
        cur = connection.cursor()
        query = "select * from urlinfo where encryptedurl='{}'and pk_urlId!={}".format(encrypted,id)
        cur.execute(query)
        data = cur.fetchone()
        if data==None:
            query1 = "update urlinfo set orignalUrl='{}', encryptedUrl='{}' where pk_urlId={}".format(url,encrypted,id)
            cur.execute(query1)
            connection.commit()
            return redirect('/home')
        else:
            return render_template("editUrl.html", url=url, encrypted=encrypted, id=id,error='short url already exist')
    return render_template("login.html")

@app.route('/deleteUrl',methods=['post'])
def deleteUrl():
    if 'userid' in session:
        id = request.form.get('id')
        connection = connect(host="localhost", database="student", user="root", password="admin123")
        cur = connection.cursor()
        query1 = "delete from urlinfo where pk_urlId="+id
        cur.execute(query1)
        connection.commit()
        return redirect('/home')
    return render_template('login.html')

@app.route('/mailbhejo')
def mailbhejo():
    msg= Message(subject='mail sender', sender='saranshpareek12@gmail.com', recipients=['saransh.pareek24@gmail.com'],body=
            "This is my first email through python")
    msg.cc=['yadavsmriti705']
    msg.html=render_template('index.html')
    with app.open_resource("F:/files/merge/1.png") as f:
        msg.attach("1.png","image/png",f.read())
    mail.send(msg)
    return "mail sent!!"

@app.route('/logout')
def logout():
    list = []
    print("hello")
    dict["name"] = "Saransh"
    list.append(dict)
    return jsonify(list)


@app.route('/xyzlogin',methods=['post'])
def testapi():
    abc=request.get_json()
    print(abc)
    list=[]
    da={}
    connection = connect(host="localhost", database="student", user="root", password="admin123")
    cur = connection.cursor()
    query = "select * from urlinfo"
    cur.execute(query)
    data = cur.fetchall()
    for i in data:
        da["name"]=i[0]
        da["email"]=i[1]
        list.append(da)
    return jsonify(list)

if __name__ == "__main__":
    app.run()
