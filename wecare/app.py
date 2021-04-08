from flask import Flask,render_template,request,session,redirect
from flask_sqlalchemy import SQLAlchemy
import os
app=Flask(__name__)
app.secret_key=os.urandom(24)

ENV='dev'

if ENV=='dev':
    app.debug=True
    app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:55555@localhost/answers'
else:    
    app.debug=False
    app.config['SQLALCHEMY_DATABASE_URI']=''

app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

db=SQLAlchemy(app)


@app.route('/',methods=['GET','POST'])
def index():
    if request.method=='GET':
        return render_template('login.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='GET':
        return render_template('login.html')
    if request.method=='POST':
        email=request.form.get("email")
        password=request.form.get("password")

        try:
            mycursor=db.session.execute("SELECT * FROM wecare WHERE email = :email AND password = :password", {'email': email,'password':password})
            userrow = mycursor.fetchone()

            if (userrow[0]==email and userrow[1]==password):
                session['username']=email
                return render_template('book.html',email=email)
            else:
                return render_template('login.html') 
        except:
            return render_template('register.html') 
         


@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=='POST':
        email=str(request.form.get("email"))
        mobile=str(request.form.get("mobile"))
        password=str(request.form.get("password"))
        cpassword=request.form.get("cpassword")
        if(password!=cpassword):
            return render_template('register.html') 

        try:
            mycursor=db.session.execute("SELECT * FROM wecare WHERE email = :id",{'id': email})
            if (mycursor is None):
                return render_template('/')
            else:
                session['username']=email
                db.session.execute("INSERT INTO wecare(email,password,mobile) VALUES(:email,:password,:mobile)",{'email':email,'password':password,'mobile':mobile})
                db.session.commit()
                return render_template('login.html') 
        except:
            return render_template('register.html') 

    if request.method=='GET':
        return render_template('register.html')


@app.route('/book',methods=['GET','POST'])
def book():
    if request.method=='GET':
        return render_template('book.html')
    if request.method=='POST':
        email=session['username']
        date=request.form.get("bookdate")
        remove=request.form.get("cancel")
        logout=request.form.get("logout")
        if(remove):
            db.session.execute("delete from booking WHERE email=:email",{'email': email})
            db.session.commit()
            message="Your Booking Is Canceled"  
            return render_template('book.html',message=message,email=email)
        if(logout):
            session.pop('username',None)
            return redirect('/')


        try:
            mycursor=db.session.execute("SELECT * FROM booking  WHERE email = :email",{'email': email})
            userrow = mycursor.fetchone()
            if (userrow[0]==email):
                db.session.execute("UPDATE booking set date=:date WHERE email=:email",{'date':date,'email': email})
                db.session.commit() 
                message="Successfully Updated Booking Date"  
                return render_template('book.html',message=message,email=email)

        except:
            db.session.execute("INSERT INTO booking(email,date) VALUES(:email,:date)",{'email':email,'date':date})
            db.session.commit() 
            message="Successfully Booked"  
            return render_template('book.html',message=message,email=email)   

@app.route('/adminlogin',methods=['GET','POST'])
def admin():
    email=str(request.form.get("email"))
    password=str(request.form.get("password"))
    try:
        mycursor=db.session.execute("SELECT * FROM admins WHERE email = :email AND password = :password", {'email': email,'password':password})
        userrow = mycursor.fetchone()
        if (userrow[0]==email and userrow[1]==password):
            session['username']=email
            return redirect('/admins') 
        else:
            return render_template('adminlogin.html') 
    except:
        return render_template('adminlogin.html') 

@app.route('/admins',methods=['GET','POST'])
def admins():
    mycursor=db.session.execute("SELECT * FROM wecare")
    data = mycursor.fetchall()
    mybook=db.session.execute("SELECT * FROM booking")
    booked=mybook.fetchall()
    return render_template('admin.html',data=data,booked=booked) 


if __name__=='__main__':
    app.run(debug=True)
