from flask import Flask, render_template,request,flash,redirect,url_for,session,make_response,send_file
from werkzeug.utils import secure_filename
import os
import pathlib
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import pdfkit
import time
from io import BytesIO
import zipfile
from zipfile import ZipFile, ZIP_DEFLATED
from flask import send_file
import shutil
from datetime import datetime
import pandas as pd
import mysql.connector
time_format = '%H:%M:%S'


app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'Flask_Upload/static'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'user'
app.config['MYSQL_PASSWORD'] = 'secret'
app.config['MYSQL_DB'] = 'tt_data'

mysql = MySQL(app)

def weekoff(f):
    if f in ['EDR','PV','BB','ACJ','CTJ','KN','RML','ES','LS','BT','DMV','JPM','AKR','GBC','MM']:
        wo=['mon','tue']
    elif f in ['SV','RGK','NC']:
        wo=['sun','mon']
    else:
        wo=['sat','sun']
        
    return wo
    

@app.route('/input', methods=['GET',"POST"])
def upload():
    if request.method=='POST':
            if request.files['Key'].filename.split('.')[-1] == 'xlsx' and request.files['ans'].filename.split('.')[-1] == 'xlsx':
                batch=request.form['day']
                r1=request.form['day1']
                r2=request.form['day2']
                file1 = request.files['Key']
                file2=request.files['ans']
                file1.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'],secure_filename(file1.filename)))
                file2.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'],secure_filename(file2.filename)))
                
                return calc(batch,file1,file2,r1,r2)
            else:
                flash("Please upload '.xlsx' files only")
                render_template('indx1.html')
    return render_template('indx1.html')






@app.route('/', methods=['GET',"POST"])
@app.route('/pythonlogin/', methods=['GET', 'POST'])
def login():
    print("in login")
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        global jjj
        jjj=username
        password = request.form['password']
        global cursor
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            return redirect('/home/entr')
        else:
            msg = 'Incorrect username/password!'
    return render_template('index.html', msg=msg)


@app.route('/pythonlogin/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   return redirect(url_for('login'))

@app.route('/pythonlogin/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('register.html', msg=msg)



@app.route('/home/profile', methods=['GET',"POST"])
def prof():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM accounts WHERE username = %s', (jjj,))
    account = cursor.fetchone()

    username = account['username']
    password = account['password']
    email = account['email']
    return render_template('prof.html',username=username,password=password,email=email)


@app.route('/home/entr', methods=['GET',"POST"])
def entr():
    return render_template('entr.html')

@app.route('/entr1', methods=['GET',"POST"])
def entr1():
    return render_template('entr1.html')


@app.route('/home/enter', methods=['GET',"POST"])
def enter():
    return render_template('enter.html')

@app.route('/get_vals', methods=['GET',"POST"])
def get_vals():
    return render_template('get_vals.html')


@app.route('/pythonlogin/profile')
def profile():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        return render_template('profile.html', account=account)
    return redirect(url_for('login'))






























@app.route('/h1', methods=['GET', 'POST'])
def enter_tt():
    if request.method == 'POST':
            day = request.form['day']
            s1 = request.form['s1']
            s2 = request.form['s2']
            try:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('INSERT INTO subject VALUES(%s);', (s2))
                cursor.execute('INSERT INTO faculty VALUES (%s, %s, %s);', (day,s1,s2))
                mysql.connection.commit()
            except:
                pass
    return render_template('index1.html')


@app.route('/h2', methods=['GET', 'POST'])
def enter_tt1():
    if request.method == 'POST':
            day = request.form['day']
            try:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('INSERT INTO subject VALUES(%s);', (day))
                mysql.connection.commit()
            except:
                pass
    return render_template('index11.html')

@app.route('/h3', methods=['GET', 'POST'])
def enter_tt2():
    if request.method == 'POST':
            day = request.form['day']
            try:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('INSERT INTO class_room VALUES(%s);', (day))
                mysql.connection.commit()
            except:
                pass
    return render_template('index12.html')

@app.route('/h4', methods=['GET', 'POST'])
def enter_tt3():
    if request.method == 'POST':
            day = request.form['day']
            s1 = request.form['s1']
            s2 = request.form['s2']
            try:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('INSERT INTO set_batc VALUES (%s, %s, %s);', (day,s1,s2))
                mysql.connection.commit()
            except:
                pass
    return render_template('index13.html')

@app.route('/h5', methods=['GET', 'POST'])
def enter_tt4():
    if request.method == 'POST':
            day = request.form['day']
            s1 = request.form['s1']
            s2 = request.form['s2']
            s3 = request.form['s3']
            s4 = request.form['s4']
            s5 = request.form['s5']
            s6 = request.form['s6']
            try:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('INSERT INTO classes VALUES (%s,%s,%s,%s,%s,%s,%s);', (day,s1,s2,s3,s4,s5,s6))
                mysql.connection.commit()
            except:
                pass
    return render_template('index14.html')




@app.route('/home/second', methods=['GET', 'POST'])
def edit_tt():
    if request.method == 'POST':
            field = request.form['field']
            value = request.form['value']
            daye = request.form['daye']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

            a='UPDATE time_table SET '+str(field)+"="+"\'"+str(value)+"\'"+" WHERE day1="+"\'"+str(daye)+"\'"
            #cursor.execute('UPDATE time_table SET %s=%s WHERE day1=%s;', (field,value,daye))
            cursor.execute(a)
            mysql.connection.commit()
    return render_template('index2.html')




@app.route('/ht1', methods=['GET', 'POST'])
def delete_tt():
    if request.method == 'POST':
            day = request.form['day']
            s1 = request.form['s1']
            try:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('Delete from faculty where facultyid=%s and subject_subjectid=%s ;', (day,s1))
                mysql.connection.commit()
            except:
                pass            
    return render_template('index3.html')

@app.route('/ht2', methods=['GET', 'POST'])
def delete_tt1():
    if request.method == 'POST':
            day = request.form['day']
            try:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('Delete from subject where subjectid=%s;', (day))
                mysql.connection.commit()
            except:
                pass            
    return render_template('index31.html')

@app.route('/ht3', methods=['GET', 'POST'])
def delete_tt2():
    if request.method == 'POST':
            day = request.form['day']
            try:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('Delete from class_room where roomid=%s;', (day))
                mysql.connection.commit()
            except:
                pass            
    return render_template('index32.html')

@app.route('/ht4', methods=['GET', 'POST'])
def delete_tt3():
    if request.method == 'POST':
            day = request.form['day']
            try:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('Delete from set_batc where batchid=%s', (day))
                mysql.connection.commit()
            except:
                pass            
    return render_template('index33.html')

@app.route('/ht5', methods=['GET', 'POST'])
def delete_tt4():
    if request.method == 'POST':
            day = request.form['day']
            s1 = request.form['s1']
            try:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('Delete from classes where days=%s and set_batc_batchid=%s;', (day,s1))
                mysql.connection.commit()
            except:
                pass            
    return render_template('index34.html')


@app.route('/ht6', methods=['GET', 'POST'])
def delete_tt5():
    if request.method == 'POST':
            try:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('Delete from classes;')
                mysql.connection.commit()
                cursor.execute('Delete from set_batc;')
                mysql.connection.commit()
                cursor.execute('Delete from class_room;')
                mysql.connection.commit()
                cursor.execute('Delete from faculty;')
                mysql.connection.commit()
                cursor.execute('Delete from subject;')
                mysql.connection.commit()
                
                
                
            except:
                pass            
    return render_template('index35.html')


'''@app.route('/home/third1', methods=['GET', 'POST'])
def delete_tt1():
    if request.method == 'POST':
            dday = request.form['dday']
            l=['CSE S1','CSE S2','CSE S3','CSE S4','CYS S1','CYS S2','CYS S3','CYS S4','ECE S1','ECE S2','ECE S3','ECE S4']
            dday=str(dday)[2:]+" "
            for i in range(len(l)):
                l[i]=dday+l[i]

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            for i in range(len(l)):
                a='DELETE FROM classes WHERE set_batc_batchid='+"\'"+str(l[i])+"\'"
                cursor.execute(a)
            #cursor.execute('DELETE FROM time_table WHERE day1=%s;', (dday))
            mysql.connection.commit()
    return render_template('index3.html')'''


@app.route('/home1', methods=['GET', 'POST'])
def show_tt():
#    if request.method == 'POST':
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM time_table')
            result=cursor.fetchall()
#            print(result)
            global l
            global length
            l = []
            for x in result:
                x = list(x.values())
                l.append(x)
            length=len(l)
            return redirect('/result1')

@app.route('/result1')
def result1():
#    print(l)
    return render_template('basic.html',data=l,length=length)






'''
@app.route('/home/second', methods=['GET',"POST"])
def upload1():
    if request.method=='POST':
        if request.files and 'Answers' in request.files and 'Key' in request.files :
            if request.files['Key'].filename.split('.')[1] == 'txt' and request.files['Answers'].filename.split('.')[1] == 'txt':
                file1 = request.files['Key']
                file1.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'],secure_filename(file1.filename)))
                file2=request.files['Answers']
                file2.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'],secure_filename(file2.filename)))
                return calc1()
            else:
                flash("Please upload '.txt' files only")
                render_template('index2.html') 
        else:
            flash("Please upload both files")
            render_template('index2.html') 
    return render_template('index2.html')'''









########
@app.route('/log1', methods=['GET',"POST"])
def logout1():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   return redirect('/pythonlogin1')
@app.route('/pythonlogin1', methods=['GET', 'POST'])
def login1():
    print("in login 1")
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        print("inside login 1")
        username = request.form['username']
        global jjj
        jjj=username
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts1 WHERE username = %s AND password = %s', (username, password,))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            print('going to /input')
            return redirect('/entr1')
        else:
            msg = 'Incorrect username/password!'
    return render_template('indexx.html', msg=msg)


'''@app.route('/pythonlogin1/logout')
def logout1():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   return redirect(url_for('login'))'''
######











@app.route('/ind1', methods=['GET', 'POST'])
def ind1():
    if request.method == 'POST':
            dday = request.form['dday']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            a="select days,tim_from,tim_to,faculty_subject_subjectid,faculty_facultyid,class_room_roomid from classes where set_batc_batchid="+"\'"+str(dday)+"\'"+" order by days,tim_from;"
            
            cursor.execute(a)
            result=cursor.fetchall()
            t=[]
            for x in result:
                x = list(x.values())
                t.append(x)
            
            
            sort_order = ['Mon','Tue','Wed','Thu','Fri']
            t = [tu for x in sort_order for tu in t if tu[0] == x]
            l=[]
            for x in t:
                x = list(x)
                l.append(x)


            for i in range(len(l)):
                if str(l[i][0])=='Mon':
                    l[i].append(0)
                elif str(l[i][0])=='Tue':
                    l[i].append(1)
                elif str(l[i][0])=='Wed':
                    l[i].append(2)
                elif str(l[i][0])=='Thu':
                    l[i].append(3)
                elif str(l[i][0])=='Fri':
                    l[i].append(4)

            for i in range(len(l)):
                if str(l[i][1])=='8:00:00':
                    l[i].append(0)
                elif str(l[i][1])=='9:00:00':
                    l[i].append(1)
                elif str(l[i][1])=='10:00:00' or str(l[i][1])=='10:05:00':
                    l[i].append(2)
                elif str(l[i][1])=='11:05:00' and str(l[i][2])=='12:00:00':
                    l[i].append(3)
                elif str(l[i][1])=='11:05:00' and str(l[i][2])=='13:00:00':
                    l[i].append(34)
                elif str(l[i][1])=='12:05:00':
                    l[i].append(4)
                elif str(l[i][1])=='13:00:00'and str(l[i][2])=='15:55:00':
                    l[i].append(567)
                elif str(l[i][1])=='13:00:00' and str(l[i][2])=='13:55:00':
                    l[i].append(5)
                elif str(l[i][1])=='14:00:00' and str(l[i][2])=='14:55:00':
                    l[i].append(6)
                elif str(l[i][1])=='14:00:00' and str(l[i][2])=='15:55:00':
                    l[i].append(67)
                elif str(l[i][1])=='15:00:00' and str(l[i][2])=='15:55:00':
                    l[i].append(7)
                elif str(l[i][1])=='15:00:00' and str(l[i][2])=='16:55:00':
                    l[i].append(78)
                elif str(l[i][1])=='16:00:00' and str(l[i][2])=='16:55:00':
                    l[i].append(8)


            global ls
            global length

            ls=[]
            for i in range(5):
                lists = [[] for i in range(9)]
                ls.append(lists)
                
                
            for i in range(len(l)):
                a=l[i][-2]
                b=l[i][-1]
                if b<10:
                    if len(ls[a][b])==0:
                        ls[a][b]=[l[i][3],l[i][4],l[i][5]]
                    else:
                        ls[a][b].append(l[i][5])
                        
                        
                else:
                    b1=b//10
                    b2=b%10
                    
                    if len(ls[a][b1])==0:
                        ls[a][b1]=[l[i][3],l[i][4],l[i][5]]
                    else:
                        ls[a][b1].append(l[i][5])

                    if len(ls[a][b2])==0:
                        ls[a][b2]=[l[i][3],l[i][4],l[i][5]]
                    else:
                        ls[a][b2].append(l[i][5])

            for i in range(len(ls)):
                for j in range(9):
                    ls[i][j]="\n".join(ls[i][j])

            ls[0].insert(0, 'Mon')
            ls[1].insert(0, 'Tue')
            ls[2].insert(0, 'Wed')
            ls[3].insert(0, 'Thu')
            ls[4].insert(0, 'Fri')



            length=len(ls)
            #print(l)
            return redirect('/res1')
    return render_template('ind1.html')
@app.route('/res1')
def res1():
#    print(l)
    return render_template('res1.html',data=ls,length=length)








@app.route('/ind11', methods=['GET', 'POST'])
def ind11():
    if request.method == 'POST':
            dday = request.form['dday']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            d1,d2=dday.split(",")
            a='''select a.days,a.tim_from,a.tim_to,a.faculty_subject_subjectid,a.faculty_facultyid,a.class_room_roomid from (select days,tim_from,tim_to,faculty_subject_subjectid,faculty_facultyid,class_room_roomid from classes where set_batc_batchid='''+"\'"+str(d1)+"\'"+''' order by days,tim_from) a
UNION ALL 
select b.days,b.tim_from,b.tim_to,b.faculty_subject_subjectid,b.faculty_facultyid,b.class_room_roomid from  (select days,tim_from,tim_to,faculty_subject_subjectid,faculty_facultyid,class_room_roomid from classes where set_batc_batchid='''+"\'"+str(d2)+"\'"+''' order by days,tim_from) b
group by(class_room_roomid) ;'''
            
            cursor.execute(a)
            result=cursor.fetchall()
            #print(result)
            t=[]
            for x in result:
                x = list(x.values())
                t.append(x)
            
            
            sort_order = ['Mon','Tue','Wed','Thu','Fri']
            t = [tu for x in sort_order for tu in t if tu[0] == x]
            l=[]
            for x in t:
                x = list(x)
                l.append(x)


            for i in range(len(l)):
                if str(l[i][0])=='Mon':
                    l[i].append(0)
                elif str(l[i][0])=='Tue':
                    l[i].append(1)
                elif str(l[i][0])=='Wed':
                    l[i].append(2)
                elif str(l[i][0])=='Thu':
                    l[i].append(3)
                elif str(l[i][0])=='Fri':
                    l[i].append(4)

            for i in range(len(l)):
                if str(l[i][1])=='8:00:00':
                    l[i].append(0)
                elif str(l[i][1])=='9:00:00':
                    l[i].append(1)
                elif str(l[i][1])=='10:00:00' or str(l[i][1])=='10:05:00':
                    l[i].append(2)
                elif str(l[i][1])=='11:05:00' and str(l[i][2])=='12:00:00':
                    l[i].append(3)
                elif str(l[i][1])=='11:05:00' and str(l[i][2])=='13:00:00':
                    l[i].append(34)
                elif str(l[i][1])=='12:05:00':
                    l[i].append(4)
                elif str(l[i][1])=='13:00:00'and str(l[i][2])=='15:55:00':
                    l[i].append(567)
                elif str(l[i][1])=='13:00:00' and str(l[i][2])=='13:55:00':
                    l[i].append(5)
                elif str(l[i][1])=='14:00:00' and str(l[i][2])=='14:55:00':
                    l[i].append(6)
                elif str(l[i][1])=='14:00:00' and str(l[i][2])=='15:55:00':
                    l[i].append(67)
                elif str(l[i][1])=='15:00:00' and str(l[i][2])=='15:55:00':
                    l[i].append(7)
                elif str(l[i][1])=='15:00:00' and str(l[i][2])=='16:55:00':
                    l[i].append(78)
                elif str(l[i][1])=='16:00:00' and str(l[i][2])=='16:55:00':
                    l[i].append(8)


            global ls
            global length

            ls=[]
            for i in range(5):
                lists = [[] for i in range(9)]
                ls.append(lists)
                
                
            for i in range(len(l)):
                a=l[i][-2]
                b=l[i][-1]
                if b<10:
                    if len(ls[a][b])==0:
                        ls[a][b]=[l[i][3],l[i][4],l[i][5]]
                    else:
                        ls[a][b].append(l[i][5])
                        
                        
                else:
                    b1=b//10
                    b2=b%10
                    
                    if len(ls[a][b1])==0:
                        ls[a][b1]=[l[i][3],l[i][4],l[i][5]]
                    else:
                        ls[a][b1].append(l[i][5])

                    if len(ls[a][b2])==0:
                        ls[a][b2]=[l[i][3],l[i][4],l[i][5]]
                    else:
                        ls[a][b2].append(l[i][5])

            for i in range(len(ls)):
                for j in range(9):
                    ls[i][j]="\n".join(ls[i][j])
            
            ls[0].insert(0, 'Mon')
            ls[1].insert(0, 'Tue')
            ls[2].insert(0, 'Wed')
            ls[3].insert(0, 'Thu')
            ls[4].insert(0, 'Fri')



            length=len(ls)
            #print(l)
            return redirect('/res1')
    return render_template('ind1.html')
'''@app.route('/res1')
def res1():
#    print(l)
    return render_template('res1.html',data=l,length=length)'''






@app.route('/ind2', methods=['GET', 'POST'])
def ind2():
    if request.method == 'POST':
            global name
            dday = request.form['dday']
            name=str(dday)
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            a="select days,tim_from,tim_to,faculty_subject_subjectid,class_room_roomid,set_batc_batchid from classes where faculty_facultyid="+"\'"+str(dday)+"\'"+" order by days,tim_from;"
            cursor.execute(a)
            result=cursor.fetchall()
            #print(result)

            b="select fname from faculty where facultyid="+"\'"+str(dday)+"\'"+";"
            cursor.execute(b)
            rn=cursor.fetchall()
            print(rn)
            rn=list(rn[0].values())[0]
            print(rn)
            name=rn



            global satsun
            global length2
            t=[]
            t2=[]
            for x in result:
                x = list(x.values())
                if('Sat' not in x and 'Sun' not in x):
                    t.append(x)
                else:
                    t2.append(x)
                
            s_o2=['Sat','Sun']
            t2 = [tu for x in s_o2 for tu in t2 if tu[0] == x]

            
            #print(t)
            sat=['Sat']
            sun=['Sun']
            for i in range(len(t2)):
                if 'Sat' in t2[i]:
                    sat.append(t2[i][1:])
                else:
                    sun.append(t2[i][1:])

            satsun=[sat]+[sun]

            length2=len(satsun)
            for i in range(len(satsun)):
                for j in range(1,len(satsun[i])):
                    satsun[i][j][0]=str(satsun[i][j][0])
                    satsun[i][j][1]=str(satsun[i][j][1])
            global ls1
            ls1=[]
            for i in range(2):
                lists = [[" "] for i in range(8)]
                ls1.append(lists)

            for i in range(1,len(satsun[0])):
                if datetime.strptime(satsun[0][i][0],time_format)<=datetime.strptime('10:00:00',time_format) and datetime.strptime(satsun[0][i][1],time_format)>=datetime.strptime('9:00:00',time_format):
                    ls1[0][0]=satsun[0][i]
                if datetime.strptime(satsun[0][i][0],time_format)<=datetime.strptime('11:00:00',time_format) and datetime.strptime(satsun[0][i][1],time_format)>=datetime.strptime('10:00:00',time_format) and ((datetime.strptime(satsun[0][i][0],time_format)<=datetime.strptime('10:00:00',time_format) and datetime.strptime(satsun[0][i][1],time_format)>=datetime.strptime('9:00:00',time_format))!=True):
                    ls1[0][1]=satsun[0][i]
                if datetime.strptime(satsun[0][i][0],time_format)<=datetime.strptime('12:00:00',time_format) and datetime.strptime(satsun[0][i][1],time_format)>=datetime.strptime('11:00:00',time_format) and ((datetime.strptime(satsun[0][i][0],time_format)<=datetime.strptime('11:00:00',time_format) and datetime.strptime(satsun[0][i][1],time_format)>=datetime.strptime('10:00:00',time_format))!=True):
                    ls1[0][2]=satsun[0][i]
                if datetime.strptime(satsun[0][i][0],time_format)<=datetime.strptime('13:00:00',time_format) and datetime.strptime(satsun[0][i][1],time_format)>=datetime.strptime('12:00:00',time_format) and ((datetime.strptime(satsun[0][i][0],time_format)<=datetime.strptime('12:00:00',time_format) and datetime.strptime(satsun[0][i][1],time_format)>=datetime.strptime('11:00:00',time_format))!=True):
                    ls1[0][3]=satsun[0][i]
                if datetime.strptime(satsun[0][i][0],time_format)<=datetime.strptime('14:00:00',time_format) and datetime.strptime(satsun[0][i][1],time_format)>=datetime.strptime('13:00:00',time_format) and ((datetime.strptime(satsun[0][i][0],time_format)<=datetime.strptime('13:00:00',time_format) and datetime.strptime(satsun[0][i][1],time_format)>=datetime.strptime('12:00:00',time_format))!=True):
                    ls1[0][4]=satsun[0][i]
                if datetime.strptime(satsun[0][i][0],time_format)<=datetime.strptime('15:00:00',time_format) and datetime.strptime(satsun[0][i][1],time_format)>=datetime.strptime('14:00:00',time_format) and ((datetime.strptime(satsun[0][i][0],time_format)<=datetime.strptime('14:00:00',time_format) and datetime.strptime(satsun[0][i][1],time_format)>=datetime.strptime('13:00:00',time_format))!=True):
                    ls1[0][5]=satsun[0][i]
                if datetime.strptime(satsun[0][i][0],time_format)<=datetime.strptime('16:00:00',time_format) and datetime.strptime(satsun[0][i][1],time_format)>=datetime.strptime('15:00:00',time_format) and ((datetime.strptime(satsun[0][i][0],time_format)<=datetime.strptime('15:00:00',time_format) and datetime.strptime(satsun[0][i][1],time_format)>=datetime.strptime('14:00:00',time_format))!=True):
                    ls1[0][6]=satsun[0][i]
                if datetime.strptime(satsun[0][i][0],time_format)<=datetime.strptime('17:00:00',time_format) and datetime.strptime(satsun[0][i][1],time_format)>=datetime.strptime('16:00:00',time_format) and ((datetime.strptime(satsun[0][i][0],time_format)<=datetime.strptime('16:00:00',time_format) and datetime.strptime(satsun[0][i][1],time_format)>=datetime.strptime('15:00:00',time_format))!=True):
                    ls1[0][7]=satsun[0][i]




            


                    

            for i in range(1,len(satsun[1])):
                if datetime.strptime(satsun[1][i][0],time_format)<=datetime.strptime('10:00:00',time_format) and datetime.strptime(satsun[1][i][1],time_format)>=datetime.strptime('9:00:00',time_format):
                    ls1[1][0]=satsun[1][i]
                if datetime.strptime(satsun[1][i][0],time_format)<=datetime.strptime('11:00:00',time_format) and datetime.strptime(satsun[1][i][1],time_format)>=datetime.strptime('10:00:00',time_format) and ((datetime.strptime(satsun[1][i][0],time_format)<=datetime.strptime('10:00:00',time_format) and datetime.strptime(satsun[1][i][1],time_format)>=datetime.strptime('9:00:00',time_format))!=True):
                    ls1[1][1]=satsun[1][i]
                if datetime.strptime(satsun[1][i][0],time_format)<=datetime.strptime('12:00:00',time_format) and datetime.strptime(satsun[1][i][1],time_format)>=datetime.strptime('11:00:00',time_format) and ((datetime.strptime(satsun[1][i][0],time_format)<=datetime.strptime('11:00:00',time_format) and datetime.strptime(satsun[1][i][1],time_format)>=datetime.strptime('10:00:00',time_format))!=True):
                    ls1[1][2]=satsun[1][i]
                if datetime.strptime(satsun[1][i][0],time_format)<=datetime.strptime('13:00:00',time_format) and datetime.strptime(satsun[1][i][1],time_format)>=datetime.strptime('12:00:00',time_format) and ((datetime.strptime(satsun[1][i][0],time_format)<=datetime.strptime('12:00:00',time_format) and datetime.strptime(satsun[1][i][1],time_format)>=datetime.strptime('11:00:00',time_format))!=True):
                    ls1[1][3]=satsun[1][i]
                if datetime.strptime(satsun[1][i][0],time_format)<=datetime.strptime('14:00:00',time_format) and datetime.strptime(satsun[1][i][1],time_format)>=datetime.strptime('13:00:00',time_format) and ((datetime.strptime(satsun[1][i][0],time_format)<=datetime.strptime('13:00:00',time_format) and datetime.strptime(satsun[1][i][1],time_format)>=datetime.strptime('12:00:00',time_format))!=True):
                    ls1[1][4]=satsun[1][i]
                if datetime.strptime(satsun[1][i][0],time_format)<=datetime.strptime('15:00:00',time_format) and datetime.strptime(satsun[1][i][1],time_format)>=datetime.strptime('14:00:00',time_format) and ((datetime.strptime(satsun[1][i][0],time_format)<=datetime.strptime('14:00:00',time_format) and datetime.strptime(satsun[1][i][1],time_format)>=datetime.strptime('13:00:00',time_format))!=True):
                    ls1[1][5]=satsun[1][i]
                if datetime.strptime(satsun[1][i][0],time_format)<=datetime.strptime('16:00:00',time_format) and datetime.strptime(satsun[1][i][1],time_format)>=datetime.strptime('15:00:00',time_format) and ((datetime.strptime(satsun[1][i][0],time_format)<=datetime.strptime('15:00:00',time_format) and datetime.strptime(satsun[1][i][1],time_format)>=datetime.strptime('14:00:00',time_format))!=True):
                    ls1[1][6]=satsun[1][i]
                if datetime.strptime(satsun[1][i][0],time_format)<=datetime.strptime('17:00:00',time_format) and datetime.strptime(satsun[1][i][1],time_format)>=datetime.strptime('16:00:00',time_format) and ((datetime.strptime(satsun[1][i][0],time_format)<=datetime.strptime('16:00:00',time_format) and datetime.strptime(satsun[1][i][1],time_format)>=datetime.strptime('15:00:00',time_format))!=True):
                    ls1[1][7]=satsun[1][i]


            for i in range(len(ls1)):
                for j in range(8):
                    ls1[i][j]="\n".join(ls1[i][j])

            ls1[0].insert(0, 'Sat')
            ls1[1].insert(0, 'Sun')

            length2=len(ls1)



            for i in range(len(satsun)):
                for j in range(1,len(satsun[i])):
                    satsun[i][j][0]=str(satsun[i][j][0])
                    satsun[i][j][1]=str(satsun[i][j][1])
                    satsun[i][j]=' ||||  '.join(satsun[i][j])

            
            

            





            sort_order = ['Mon','Tue','Wed','Thu','Fri']
            t = [tu for x in sort_order for tu in t if tu[0] == x]
            l=[]
            for x in t:
                x = list(x)
                l.append(x)


            for i in range(len(l)):
                if str(l[i][0])=='Mon':
                    l[i].append(0)
                elif str(l[i][0])=='Tue':
                    l[i].append(1)
                elif str(l[i][0])=='Wed':
                    l[i].append(2)
                elif str(l[i][0])=='Thu':
                    l[i].append(3)
                elif str(l[i][0])=='Fri':
                    l[i].append(4)

            for i in range(len(l)):
                if str(l[i][1])=='8:00:00':
                    l[i].append(0)
                elif str(l[i][1])=='9:00:00':
                    l[i].append(1)
                elif str(l[i][1])=='10:00:00' or str(l[i][1])=='10:05:00':
                    l[i].append(2)
                elif str(l[i][1])=='11:05:00' and str(l[i][2])=='12:00:00':
                    l[i].append(3)
                elif str(l[i][1])=='11:05:00' and str(l[i][2])=='13:00:00':
                    l[i].append(34)
                elif str(l[i][1])=='12:05:00':
                    l[i].append(4)
                elif str(l[i][1])=='13:00:00'and str(l[i][2])=='15:55:00':
                    l[i].append(567)
                elif str(l[i][1])=='13:00:00' and str(l[i][2])=='13:55:00':
                    l[i].append(5)
                elif str(l[i][1])=='14:00:00' and str(l[i][2])=='14:55:00':
                    l[i].append(6)
                elif str(l[i][1])=='14:00:00' and str(l[i][2])=='15:55:00':
                    l[i].append(67)
                elif str(l[i][1])=='15:00:00' and str(l[i][2])=='15:55:00':
                    l[i].append(7)
                elif str(l[i][1])=='15:00:00' and str(l[i][2])=='16:55:00':
                    l[i].append(78)
                elif str(l[i][1])=='16:00:00' and str(l[i][2])=='16:55:00':
                    l[i].append(8)
                elif str(l[i][1])=='17:00:00' and str(l[i][2])=='17:55:00':
                    l[i].append(9)


            global ls
            global length

            ls=[]
            for i in range(5):
                lists = [[] for i in range(10)]
                ls.append(lists)


            print('.....\n')
            print('.....\n')
            print('.....\n')
            print('.....\n')
            print('.....\n')
            print('.....\n')
            print('.....\n')
            print(l)
            print('.....\n')
            print('.....\n')
            print('.....\n')
            print('.....\n')
            print('.....\n')
            print('.....\n')
            print('.....\n')
                
                
            for i in range(len(l)):
                a=l[i][-2]
                b=l[i][-1]
                #print(i,a,b)
                print(l[i],'\n\n')
                if b<10:
                    if len(ls[a][b])==0:
                        ls[a][b]=[l[i][3],l[i][4],l[i][5]]
                    else:
                        ls[a][b].append(l[i][5])
                        
                        
                else:
                    b1=b//10
                    b2=b%10
                    
                    if len(ls[a][b1])==0:
                        ls[a][b1]=[l[i][3],l[i][4],l[i][5]]
                    else:
                        ls[a][b1].append(l[i][5])

                    if len(ls[a][b2])==0:
                        ls[a][b2]=[l[i][3],l[i][4],l[i][5]]
                    else:
                        ls[a][b2].append(l[i][5])




                        

            b23_b1=['23 CSE S1','23 CSE S2','23 CYS S1','23 CYS S2','23 ECE S1','23 ECE S2','23 CDS S1','23 CDS S2']
            b23_b2=['23 CSE S3','23 CSE S4','23 CYS S3','23 CYS S4','23 ECE S3','23 ECE S4','23 CDS S3','23 CDS S4']
            b23_b3=['23 CSE S5','23 CSE S6','23 CYS S5','23 CYS S6','23 ECE S5','23 ECE S6','23 CDS S5','23 CDS S6']

            b22_b1=['22 CSE S1','22 CSE S2','22 CYS S1','22 CYS S2','22 ECE S1','22 ECE S2','22 CDS S1','22 CDS S2']
            b22_b2=['22 CSE S3','22 CSE S4','22 CYS S3','22 CYS S4','22 ECE S3','22 ECE S4','22 CDS S3','22 CDS S4']
            b22_b3=['22 CSE S5','22 CSE S6','22 CYS S5','22 CYS S6','22 ECE S5','22 ECE S6','22 CDS S5','22 CDS S6']

            b21_b1=['21 CSE S1','21 CSE S2','21 CYS S1','21 CYS S2','21 ECE S1','21 ECE S2']
            b21_b2=['21 CSE S3','21 CSE S4','21 CYS S3','21 CYS S4','21 ECE S3','21 ECE S4']

            b20_b1=['20 CSE S1','20 CSE S2','20 ECE S1','20 ECE S2']
            b20_b2=['20 CSE S3','20 CSE S4','20 ECE S3','20 ECE S4']




            b22_b1_cs=['22 CSE S1','22 CSE S2']
            b22_b2_cs=['22 CSE S3','22 CSE S4']
            b22_b3_cs=['22 CSE S5','22 CSE S6']

            b22_b1_ec=['22 ECE S1','22 ECE S2']
            b22_b2_ec=['22 ECE S3','22 ECE S4']
            b22_b3_ec=['22 ECE S5','22 ECE S6']

            b22_b1_cy=['22 CYS S1','22 CYS S2']
            b22_b2_cy=['22 CYS S3','22 CYS S4']
            b22_b3_cy=['22 CYS S5','22 CYS S6']

            b22_b1_cd=['22 CDS S1','22 CDS S2']
            b22_b2_cd=['22 CDS S3','22 CDS S4']
            b22_b3_cd=['22 CDS S5','22 CDS S6']


            b22_b1_s1=['22 CSE S1','22 ECE S1','22 CYS S1','22 CDS S1']
            b22_b1_s2=['22 CSE S2','22 ECE S2','22 CYS S2','22 CDS S2']
            b22_b2_s3=['22 CSE S3','22 ECE S3','22 CYS S3','22 CDS S3']
            b22_b2_s4=['22 CSE S4','22 ECE S4','22 CYS S4','22 CDS S4']
            b22_b3_s5=['22 CSE S5','22 ECE S5','22 CYS S5','22 CDS S5']
            b22_b3_s6=['22 CSE S6','22 ECE S6','22 CYS S6','22 CDS S6']



            b23_b1_cs=['23 CSE S1','23 CSE S2']
            b23_b2_cs=['23 CSE S3','23 CSE S4']
            b23_b3_cs=['23 CSE S5','23 CSE S6']

            b23_b1_ec=['23 ECE S1','23 ECE S2']
            b23_b2_ec=['23 ECE S3','23 ECE S4']
            b23_b3_ec=['23 ECE S5','23 ECE S6']

            b23_b1_cy=['23 CYS S1','23 CYS S2']
            b23_b2_cy=['23 CYS S3','23 CYS S4']
            b23_b3_cy=['23 CYS S5','23 CYS S6']

            b23_b1_cd=['23 CDS S1','23 CDS S2']
            b23_b2_cd=['23 CDS S3','23 CDS S4']
            b23_b3_cd=['23 CDS S5','23 CDS S6']

            b23_b1_s1=['23 CSE S1','23 ECE S1','23 CYS S1','23 CDS S1']
            b23_b1_s2=['23 CSE S2','23 ECE S2','23 CYS S2','23 CDS S2']
            b23_b2_s3=['23 CSE S3','23 ECE S3','23 CYS S3','23 CDS S3']
            b23_b2_s4=['23 CSE S4','23 ECE S4','23 CYS S4','23 CDS S4']
            b23_b3_s5=['23 CSE S5','23 ECE S5','23 CYS S5','23 CDS S5']
            b23_b3_s6=['23 CSE S6','23 ECE S6','23 CYS S6','23 CDS S6']




            b21_b1_cs=['21 CSE S1','21 CSE S2']
            b21_b2_cs=['21 CSE S3','21 CSE S4']

            b21_b1_ec=['21 ECE S1','21 ECE S2']
            b21_b2_ec=['21 ECE S3','21 ECE S4']

            b21_b1_cy=['21 CYS S1','21 CYS S2']
            b21_b2_cy=['21 CYS S3','21 CYS S4']


            b21_b1_s1=['21 CSE S1','21 ECE S1','21 CYS S1']
            b21_b1_s2=['21 CSE S2','21 ECE S2','21 CYS S2']
            b21_b2_s3=['21 CSE S3','21 ECE S3','21 CYS S3']
            b21_b2_s4=['21 CSE S4','21 ECE S4','21 CYS S4']




            b20_b1_cs=['20 CSE S1','20 CSE S2']
            b20_b2_cs=['20 CSE S3','20 CSE S4']

            b20_b1_ec=['20 ECE S1','20 ECE S2']
            b20_b2_ec=['20 ECE S3','20 ECE S4']





            for i in range(len(ls)):
                for j in range(len(ls[i])):

            	    








                    if (all(item in ls[i][j] for item in b22_b1)):
                        lly = [x for x in ls[i][j] if x not in b22_b1]
                        ls[i][j] = lly
                        ls[i][j].append('22 Batch 1')
                        
                        
                    if (all(item in ls[i][j] for item in b22_b2)):
                        lly = [x for x in ls[i][j] if x not in b22_b2]
                        ls[i][j] = lly
                        ls[i][j].append('22 Batch 2')
                        
                        
                    if (all(item in ls[i][j] for item in b22_b3)):
                        lly = [x for x in ls[i][j] if x not in b22_b3]
                        ls[i][j] = lly
                        ls[i][j].append('22 Batch 3')
                        
                        
                    if (all(item in ls[i][j] for item in b22_b1_cs)):
                        lly = [x for x in ls[i][j] if x not in b22_b1_cs]
                        ls[i][j] = lly
                        ls[i][j].append('22 Batch 1 CSE')
                    
                    
                    if (all(item in ls[i][j] for item in b22_b2_cs)):
                        lly = [x for x in ls[i][j] if x not in b22_b2_cs]
                        ls[i][j] = lly
                        ls[i][j].append('22 Batch 2 CSE')
                    
                    if (all(item in ls[i][j] for item in b22_b3_cs)):
                        lly = [x for x in ls[i][j] if x not in b22_b3_cs]
                        ls[i][j] = lly
                        ls[i][j].append('22 Batch 3 CSE')
                        
                
                        
                    if (all(item in ls[i][j] for item in b22_b1_ec)):
                        lly = [x for x in ls[i][j] if x not in b22_b1_ec]
                        ls[i][j] = lly
                        ls[i][j].append('22 Batch 1 ECE')
                    
                    
                    if (all(item in ls[i][j] for item in b22_b2_ec)):
                        lly = [x for x in ls[i][j] if x not in b22_b2_ec]
                        ls[i][j] = lly
                        ls[i][j].append('22 Batch 2 ECE')
                    
                    if (all(item in ls[i][j] for item in b22_b3_ec)):
                        lly = [x for x in ls[i][j] if x not in b22_b3_ec]
                        ls[i][j] = lly
                        ls[i][j].append('22 Batch 3 ECE')
                        
                        
                        
                    if (all(item in ls[i][j] for item in b22_b1_cy)):
                        lly = [x for x in ls[i][j] if x not in b22_b1_cy]
                        ls[i][j] = lly
                        ls[i][j].append('22 Batch 1 CYS')
                    
                    
                    if (all(item in ls[i][j] for item in b22_b2_cy)):
                        lly = [x for x in ls[i][j] if x not in b22_b2_cy]
                        ls[i][j] = lly
                        ls[i][j].append('22 Batch 2 CYS')
                    
                    if (all(item in ls[i][j] for item in b22_b3_cy)):
                        lly = [x for x in ls[i][j] if x not in b22_b3_cy]
                        ls[i][j] = lly
                        ls[i][j].append('22 Batch 3 CYS')
                        
                        
                        
                    if (all(item in ls[i][j] for item in b22_b1_cd)):
                        lly = [x for x in ls[i][j] if x not in b22_b1_cd]
                        ls[i][j] = lly
                        ls[i][j].append('22 Batch 1 CDS')
                    
                    
                    if (all(item in ls[i][j] for item in b22_b2_cd)):
                        lly = [x for x in ls[i][j] if x not in b22_b2_cd]
                        ls[i][j] = lly
                        ls[i][j].append('22 Batch 2 CDS')
                    
                    if (all(item in ls[i][j] for item in b22_b3_cd)):
                        lly = [x for x in ls[i][j] if x not in b22_b3_cd]
                        ls[i][j] = lly
                        ls[i][j].append('22 Batch 3 CDS')



                    if (all(item in ls[i][j] for item in b22_b1_s1)):
                        lly = [x for x in ls[i][j] if x not in b22_b1_s1]
                        ls[i][j] = lly
                        ls[i][j].append('22 Batch 1 set 1')
                        
                    if (all(item in ls[i][j] for item in b22_b1_s2)):
                        lly = [x for x in ls[i][j] if x not in b22_b1_s2]
                        ls[i][j] = lly
                        ls[i][j].append('22 Batch 1 set 2')
                    
                    if (all(item in ls[i][j] for item in b22_b2_s3)):
                        lly = [x for x in ls[i][j] if x not in b22_b2_s3]
                        ls[i][j] = lly
                        ls[i][j].append('22 Batch 2 set 3')
                    
                    if (all(item in ls[i][j] for item in b22_b2_s4)):
                        lly = [x for x in ls[i][j] if x not in b22_b2_s4]
                        ls[i][j] = lly
                        ls[i][j].append('22 Batch 2 set 4')     
                        
                    if (all(item in ls[i][j] for item in b22_b3_s5)):
                        lly = [x for x in ls[i][j] if x not in b22_b3_s5]
                        ls[i][j] = lly
                        ls[i][j].append('22 Batch 3 set 5')
                    
                    if (all(item in ls[i][j] for item in b22_b3_s6)):
                        lly = [x for x in ls[i][j] if x not in b22_b3_s6]
                        ls[i][j] = lly
                        ls[i][j].append('22 Batch 3 set 6')









                    if (all(item in ls[i][j] for item in b23_b1)):
                        lly = [x for x in ls[i][j] if x not in b23_b1]
                        ls[i][j] = lly
                        ls[i][j].append('23 Batch 1')
                        
                        
                    if (all(item in ls[i][j] for item in b23_b2)):
                        lly = [x for x in ls[i][j] if x not in b23_b2]
                        ls[i][j] = lly
                        ls[i][j].append('23 Batch 2')
                        
                        
                    if (all(item in ls[i][j] for item in b23_b3)):
                        lly = [x for x in ls[i][j] if x not in b23_b3]
                        ls[i][j] = lly
                        ls[i][j].append('23 Batch 3')
                        
                        
                    if (all(item in ls[i][j] for item in b23_b1_cs)):
                        lly = [x for x in ls[i][j] if x not in b23_b1_cs]
                        ls[i][j] = lly
                        ls[i][j].append('23 Batch 1 CSE')
                    
                    
                    if (all(item in ls[i][j] for item in b23_b2_cs)):
                        lly = [x for x in ls[i][j] if x not in b23_b2_cs]
                        ls[i][j] = lly
                        ls[i][j].append('23 Batch 2 CSE')
                    
                    if (all(item in ls[i][j] for item in b23_b3_cs)):
                        lly = [x for x in ls[i][j] if x not in b23_b3_cs]
                        ls[i][j] = lly
                        ls[i][j].append('23 Batch 3 CSE')
                        
                
                        
                    if (all(item in ls[i][j] for item in b23_b1_ec)):
                        lly = [x for x in ls[i][j] if x not in b23_b1_ec]
                        ls[i][j] = lly
                        ls[i][j].append('23 Batch 1 ECE')
                    
                    
                    if (all(item in ls[i][j] for item in b23_b2_ec)):
                        lly = [x for x in ls[i][j] if x not in b23_b2_ec]
                        ls[i][j] = lly
                        ls[i][j].append('23 Batch 2 ECE')
                    
                    if (all(item in ls[i][j] for item in b23_b3_ec)):
                        lly = [x for x in ls[i][j] if x not in b23_b3_ec]
                        ls[i][j] = lly
                        ls[i][j].append('23 Batch 3 ECE')
                        
                        
                        
                    if (all(item in ls[i][j] for item in b23_b1_cy)):
                        lly = [x for x in ls[i][j] if x not in b23_b1_cy]
                        ls[i][j] = lly
                        ls[i][j].append('23 Batch 1 CYS')
                    
                    
                    if (all(item in ls[i][j] for item in b23_b2_cy)):
                        lly = [x for x in ls[i][j] if x not in b23_b2_cy]
                        ls[i][j] = lly
                        ls[i][j].append('23 Batch 2 CYS')
                    
                    if (all(item in ls[i][j] for item in b23_b3_cy)):
                        lly = [x for x in ls[i][j] if x not in b23_b3_cy]
                        ls[i][j] = lly
                        ls[i][j].append('23 Batch 3 CYS')
                        
                        
                        
                    if (all(item in ls[i][j] for item in b23_b1_cd)):
                        lly = [x for x in ls[i][j] if x not in b23_b1_cd]
                        ls[i][j] = lly
                        ls[i][j].append('23 Batch 1 CDS')
                    
                    
                    if (all(item in ls[i][j] for item in b23_b2_cd)):
                        lly = [x for x in ls[i][j] if x not in b23_b2_cd]
                        ls[i][j] = lly
                        ls[i][j].append('23 Batch 2 CDS')
                    
                    if (all(item in ls[i][j] for item in b23_b3_cd)):
                        lly = [x for x in ls[i][j] if x not in b23_b3_cd]
                        ls[i][j] = lly
                        ls[i][j].append('23 Batch 3 CDS')



                    if (all(item in ls[i][j] for item in b23_b1_s1)):
                        lly = [x for x in ls[i][j] if x not in b23_b1_s1]
                        ls[i][j] = lly
                        ls[i][j].append('23 Batch 1 set 1')
                        
                    if (all(item in ls[i][j] for item in b23_b1_s2)):
                        lly = [x for x in ls[i][j] if x not in b23_b1_s2]
                        ls[i][j] = lly
                        ls[i][j].append('23 Batch 1 set 2')
                    
                    if (all(item in ls[i][j] for item in b23_b2_s3)):
                        lly = [x for x in ls[i][j] if x not in b23_b2_s3]
                        ls[i][j] = lly
                        ls[i][j].append('23 Batch 2 set 3')
                    
                    if (all(item in ls[i][j] for item in b23_b2_s4)):
                        lly = [x for x in ls[i][j] if x not in b23_b2_s4]
                        ls[i][j] = lly
                        ls[i][j].append('23 Batch 2 set 4')     
                        
                    if (all(item in ls[i][j] for item in b23_b3_s5)):
                        lly = [x for x in ls[i][j] if x not in b23_b3_s5]
                        ls[i][j] = lly
                        ls[i][j].append('23 Batch 3 set 5')
                    
                    if (all(item in ls[i][j] for item in b23_b3_s6)):
                        lly = [x for x in ls[i][j] if x not in b23_b3_s6]
                        ls[i][j] = lly
                        ls[i][j].append('23 Batch 3 set 6')


                        
                    




                    
                        
                        
                    
                    
                    if (all(item in ls[i][j] for item in b21_b1)):
                        lly = [x for x in ls[i][j] if x not in b21_b1]
                        ls[i][j] = lly
                        ls[i][j].append('21 Batch 1')
                        
                    if (all(item in ls[i][j] for item in b21_b2)):
                        lly = [x for x in ls[i][j] if x not in b21_b2]
                        ls[i][j] = lly
                        ls[i][j].append('21 Batch 2')
                        
                        
                    if (all(item in ls[i][j] for item in b21_b1_cs)):
                        lly = [x for x in ls[i][j] if x not in b21_b1_cs]
                        ls[i][j] = lly
                        ls[i][j].append('21 Batch 1 CSE')
                        
                    if (all(item in ls[i][j] for item in b21_b2_cs)):
                        lly = [x for x in ls[i][j] if x not in b21_b2_cs]
                        ls[i][j] = lly
                        ls[i][j].append('21 Batch 2 CSE')
                        
                        
                    if (all(item in ls[i][j] for item in b21_b1_ec)):
                        lly = [x for x in ls[i][j] if x not in b21_b1_ec]
                        ls[i][j] = lly
                        ls[i][j].append('21 Batch 1 ECE')
                        
                    if (all(item in ls[i][j] for item in b21_b2_ec)):
                        lly = [x for x in ls[i][j] if x not in b21_b2_ec]
                        ls[i][j] = lly
                        ls[i][j].append('21 Batch 2 ECE')
                        
                        
                    if (all(item in ls[i][j] for item in b21_b1_cy)):
                        lly = [x for x in ls[i][j] if x not in b21_b1_cy]
                        ls[i][j] = lly
                        ls[i][j].append('21 Batch 1 CYS')
                        
                    if (all(item in ls[i][j] for item in b21_b2_cy)):
                        lly = [x for x in ls[i][j] if x not in b21_b2_cy]
                        ls[i][j] = lly
                        ls[i][j].append('21 Batch 2 CYS')
                        

                    if (all(item in ls[i][j] for item in b21_b1_s1)):
                        lly = [x for x in ls[i][j] if x not in b21_b1_s1]
                        ls[i][j] = lly
                        ls[i][j].append('21 Batch 1 set 1')
                        
                    if (all(item in ls[i][j] for item in b21_b1_s2)):
                        lly = [x for x in ls[i][j] if x not in b21_b1_s2]
                        ls[i][j] = lly
                        ls[i][j].append('21 Batch 1 set 2')
                    
                    if (all(item in ls[i][j] for item in b21_b2_s3)):
                        lly = [x for x in ls[i][j] if x not in b21_b2_s3]
                        ls[i][j] = lly
                        ls[i][j].append('21 Batch 2 set 3')
                    
                    if (all(item in ls[i][j] for item in b21_b2_s4)):
                        lly = [x for x in ls[i][j] if x not in b21_b2_s4]
                        ls[i][j] = lly
                        ls[i][j].append('21 Batch 2 set 4')   
                    
                    
                    
                        
                        
                    
                    
                    if (all(item in ls[i][j] for item in b20_b1)):
                        lly = [x for x in ls[i][j] if x not in b20_b1]
                        ls[i][j] = lly
                        ls[i][j].append('20 Batch 1')
                        
                    if (all(item in ls[i][j] for item in b20_b2)):
                        lly = [x for x in ls[i][j] if x not in b20_b2]
                        ls[i][j] = lly
                        ls[i][j].append('20 Batch 2')
                        
                        
                    if (all(item in ls[i][j] for item in b20_b1_cs)):
                        lly = [x for x in ls[i][j] if x not in b20_b1_cs]
                        ls[i][j] = lly
                        ls[i][j].append('20 Batch 1 CSE')
                        
                    if (all(item in ls[i][j] for item in b20_b2_cs)):
                        lly = [x for x in ls[i][j] if x not in b20_b2_cs]
                        ls[i][j] = lly
                        ls[i][j].append('20 Batch 2 CSE')
                        
                        
                    if (all(item in ls[i][j] for item in b20_b1_ec)):
                        lly = [x for x in ls[i][j] if x not in b20_b1_ec]
                        ls[i][j] = lly
                        ls[i][j].append('20 Batch 1 ECE')
                        
                    if (all(item in ls[i][j] for item in b20_b2_ec)):
                        lly = [x for x in ls[i][j] if x not in b20_b2_ec]
                        ls[i][j] = lly
                        ls[i][j].append('20 Batch 2 ECE')





            for i in range(len(ls)):
                for j in range(10):
                    ls[i][j]="\n".join(ls[i][j])

            
            ls[0].insert(0, 'Mon')
            ls[1].insert(0, 'Tue')
            ls[2].insert(0, 'Wed')
            ls[3].insert(0, 'Thu')
            ls[4].insert(0, 'Fri')





            name=name
            '''l = []
            for x in result:
                x = list(x.values())
                l.append(x)'''
            length=len(ls)
            return redirect('/res2')
    return render_template('ind2.html')
@app.route('/res2')
def res2():
#    print(l)
    html = render_template('res2.html',data=ls,length=length,name=name,length2=length2,t2=ls1)
    pdf = pdfkit.from_string(html, False)
    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = "inline; filename="+name+"_TT.pdf"
    return response
    #return render_template('res2.html',data=ls,length=length)










def ind22(fid):
    #if request.method == 'POST':
            
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            global name
            name=str(fid)
            a="select days,tim_from,tim_to,faculty_subject_subjectid,class_room_roomid,set_batc_batchid from classes where faculty_facultyid="+"\'"+str(fid)+"\'"+" order by days,tim_from;"
            cursor.execute(a)
            result=cursor.fetchall()
            #print(result)
            t=[]
            for x in result:
                x = list(x.values())
                t.append(x)

            #print(t)
            b="select fname from faculty where facultyid="+"\'"+str(fid)+"\'"+";"
            cursor.execute(b)
            rn=cursor.fetchall()
            print(rn)
            rn=list(rn[0].values())[0]
            print(rn)
            name=rn



            global satsun
            global length2
            t=[]
            t2=[]
            for x in result:
                x = list(x.values())
                if('Sat' not in x and 'Sun' not in x):
                    t.append(x)
                else:
                    t2.append(x)
                
            s_o2=['Sat','Sun']
            t2 = [tu for x in s_o2 for tu in t2 if tu[0] == x]

            
            #print(t)
            sat=['Sat']
            sun=['Sun']
            for i in range(len(t2)):
                if 'Sat' in t2[i]:
                    sat.append(t2[i][1:])
                else:
                    sun.append(t2[i][1:])

            satsun=[sat]+[sun]

            length2=len(satsun)

            for i in range(len(satsun)):
                for j in range(1,len(satsun[i])):
                    satsun[i][j][0]=str(satsun[i][j][0])
                    satsun[i][j][1]=str(satsun[i][j][1])
                    satsun[i][j]=' ||||  '.join(satsun[i][j])






            sort_order = ['Mon','Tue','Wed','Thu','Fri']
            t = [tu for x in sort_order for tu in t if tu[0] == x]
            l=[]
            for x in t:
                x = list(x)
                l.append(x)


            for i in range(len(l)):
                if str(l[i][0])=='Mon':
                    l[i].append(0)
                elif str(l[i][0])=='Tue':
                    l[i].append(1)
                elif str(l[i][0])=='Wed':
                    l[i].append(2)
                elif str(l[i][0])=='Thu':
                    l[i].append(3)
                elif str(l[i][0])=='Fri':
                    l[i].append(4)

            for i in range(len(l)):
                if str(l[i][1])=='8:00:00':
                    l[i].append(0)
                elif str(l[i][1])=='9:00:00':
                    l[i].append(1)
                elif str(l[i][1])=='10:00:00' or str(l[i][1])=='10:05:00':
                    l[i].append(2)
                elif str(l[i][1])=='11:05:00' and str(l[i][2])=='12:00:00':
                    l[i].append(3)
                elif str(l[i][1])=='11:05:00' and str(l[i][2])=='13:00:00':
                    l[i].append(34)
                elif str(l[i][1])=='12:05:00':
                    l[i].append(4)
                elif str(l[i][1])=='13:00:00'and str(l[i][2])=='15:55:00':
                    l[i].append(567)
                elif str(l[i][1])=='13:00:00' and str(l[i][2])=='13:55:00':
                    l[i].append(5)
                elif str(l[i][1])=='14:00:00' and str(l[i][2])=='14:55:00':
                    l[i].append(6)
                elif str(l[i][1])=='14:00:00' and str(l[i][2])=='15:55:00':
                    l[i].append(67)
                elif str(l[i][1])=='15:00:00' and str(l[i][2])=='15:55:00':
                    l[i].append(7)
                elif str(l[i][1])=='15:00:00' and str(l[i][2])=='16:55:00':
                    l[i].append(78)
                elif str(l[i][1])=='16:00:00' and str(l[i][2])=='16:55:00':
                    l[i].append(8)


            global ls
            global length

            ls=[]
            for i in range(5):
                lists = [[] for i in range(9)]
                ls.append(lists)
                
                
            for i in range(len(l)):
                a=l[i][-2]
                b=l[i][-1]
                #print(i,a,b)
                print(l[i],'\n\n')
                if b<10:
                    if len(ls[a][b])==0:
                        ls[a][b]=[l[i][3],l[i][4],l[i][5]]
                    else:
                        ls[a][b].append(l[i][5])
                        
                        
                else:
                    b1=b//10
                    b2=b%10
                    
                    if len(ls[a][b1])==0:
                        ls[a][b1]=[l[i][3],l[i][4],l[i][5]]
                    else:
                        ls[a][b1].append(l[i][5])

                    if len(ls[a][b2])==0:
                        ls[a][b2]=[l[i][3],l[i][4],l[i][5]]
                    else:
                        ls[a][b2].append(l[i][5])



            b23_b1=['23 CSE S1','23 CSE S2','23 CYS S1','23 CYS S2','23 ECE S1','23 ECE S2','23 CDS S1','23 CDS S2']
            b23_b2=['23 CSE S3','23 CSE S4','23 CYS S3','23 CYS S4','23 ECE S3','23 ECE S4','23 CDS S3','23 CDS S4']
            b23_b3=['23 CSE S5','23 CSE S6','23 CYS S5','23 CYS S6','23 ECE S5','23 ECE S6','23 CDS S5','23 CDS S6']

            b22_b1=['22 CSE S1','22 CSE S2','22 CYS S1','22 CYS S2','22 ECE S1','22 ECE S2','22 CDS S1','22 CDS S2']
            b22_b2=['22 CSE S3','22 CSE S4','22 CYS S3','22 CYS S4','22 ECE S3','22 ECE S4','22 CDS S3','22 CDS S4']
            b22_b3=['22 CSE S5','22 CSE S6','22 CYS S5','22 CYS S6','22 ECE S5','22 ECE S6','22 CDS S5','22 CDS S6']

            b21_b1=['21 CSE S1','21 CSE S2','21 CYS S1','21 CYS S2','21 ECE S1','21 ECE S2']
            b21_b2=['21 CSE S3','21 CSE S4','21 CYS S3','21 CYS S4','21 ECE S3','21 ECE S4']

            b20_b1=['20 CSE S1','20 CSE S2','20 ECE S1','20 ECE S2']
            b20_b2=['20 CSE S3','20 CSE S4','20 ECE S3','20 ECE S4']




            b22_b1_cs=['22 CSE S1','22 CSE S2']
            b22_b2_cs=['22 CSE S3','22 CSE S4']
            b22_b3_cs=['22 CSE S5','22 CSE S6']

            b22_b1_ec=['22 ECE S1','22 ECE S2']
            b22_b2_ec=['22 ECE S3','22 ECE S4']
            b22_b3_ec=['22 ECE S5','22 ECE S6']

            b22_b1_cy=['22 CYS S1','22 CYS S2']
            b22_b2_cy=['22 CYS S3','22 CYS S4']
            b22_b3_cy=['22 CYS S5','22 CYS S6']

            b22_b1_cd=['22 CDS S1','22 CDS S2']
            b22_b2_cd=['22 CDS S3','22 CDS S4']
            b22_b3_cd=['22 CDS S5','22 CDS S6']


            b22_b1_s1=['22 CSE S1','22 ECE S1','22 CYS S1','22 CDS S1']
            b22_b1_s2=['22 CSE S2','22 ECE S2','22 CYS S2','22 CDS S2']
            b22_b2_s3=['22 CSE S3','22 ECE S3','22 CYS S3','22 CDS S3']
            b22_b2_s4=['22 CSE S4','22 ECE S4','22 CYS S4','22 CDS S4']
            b22_b3_s5=['22 CSE S5','22 ECE S5','22 CYS S5','22 CDS S5']
            b22_b3_s6=['22 CSE S6','22 ECE S6','22 CYS S6','22 CDS S6']




            b23_b1_cs=['23 CSE S1','23 CSE S2']
            b23_b2_cs=['23 CSE S3','23 CSE S4']
            b23_b3_cs=['23 CSE S5','23 CSE S6']

            b23_b1_ec=['23 ECE S1','23 ECE S2']
            b23_b2_ec=['23 ECE S3','23 ECE S4']
            b23_b3_ec=['23 ECE S5','23 ECE S6']

            b23_b1_cy=['23 CYS S1','23 CYS S2']
            b23_b2_cy=['23 CYS S3','23 CYS S4']
            b23_b3_cy=['23 CYS S5','23 CYS S6']

            b23_b1_cd=['23 CDS S1','23 CDS S2']
            b23_b2_cd=['23 CDS S3','23 CDS S4']
            b23_b3_cd=['23 CDS S5','23 CDS S6']

            b23_b1_s1=['23 CSE S1','23 ECE S1','23 CYS S1','23 CDS S1']
            b23_b1_s2=['23 CSE S2','23 ECE S2','23 CYS S2','23 CDS S2']
            b23_b2_s3=['23 CSE S3','23 ECE S3','23 CYS S3','23 CDS S3']
            b23_b2_s4=['23 CSE S4','23 ECE S4','23 CYS S4','23 CDS S4']
            b23_b3_s5=['23 CSE S5','23 ECE S5','23 CYS S5','23 CDS S5']
            b23_b3_s6=['23 CSE S6','23 ECE S6','23 CYS S6','23 CDS S6']



            b21_b1_cs=['21 CSE S1','21 CSE S2']
            b21_b2_cs=['21 CSE S3','21 CSE S4']

            b21_b1_ec=['21 ECE S1','21 ECE S2']
            b21_b2_ec=['21 ECE S3','21 ECE S4']

            b21_b1_cy=['21 CYS S1','21 CYS S2']
            b21_b2_cy=['21 CYS S3','21 CYS S4']


            b21_b1_s1=['21 CSE S1','21 ECE S1','21 CYS S1']
            b21_b1_s2=['21 CSE S2','21 ECE S2','21 CYS S2']
            b21_b2_s3=['21 CSE S3','21 ECE S3','21 CYS S3']
            b21_b2_s4=['21 CSE S4','21 ECE S4','21 CYS S4']




            b20_b1_cs=['20 CSE S1','20 CSE S2']
            b20_b2_cs=['20 CSE S3','20 CSE S4']

            b20_b1_ec=['20 ECE S1','20 ECE S2']
            b20_b2_ec=['20 ECE S3','20 ECE S4']





            for i in range(len(ls)):
                for j in range(len(ls[i])):
                    if (all(item in ls[i][j] for item in b22_b1)):
                        lly = [x for x in ls[i][j] if x not in b22_b1]
                        ls[i][j] = lly
                        ls[i][j].append('22 Batch 1')
                        
                        
                    if (all(item in ls[i][j] for item in b22_b2)):
                        lly = [x for x in ls[i][j] if x not in b22_b2]
                        ls[i][j] = lly
                        ls[i][j].append('22 Batch 2')
                        
                        
                    if (all(item in ls[i][j] for item in b22_b3)):
                        lly = [x for x in ls[i][j] if x not in b22_b3]
                        ls[i][j] = lly
                        ls[i][j].append('22 Batch 3')
                        
                        
                    if (all(item in ls[i][j] for item in b22_b1_cs)):
                        lly = [x for x in ls[i][j] if x not in b22_b1_cs]
                        ls[i][j] = lly
                        ls[i][j].append('22 Batch 1 CSE')
                    
                    
                    if (all(item in ls[i][j] for item in b22_b2_cs)):
                        lly = [x for x in ls[i][j] if x not in b22_b2_cs]
                        ls[i][j] = lly
                        ls[i][j].append('22 Batch 2 CSE')
                    
                    if (all(item in ls[i][j] for item in b22_b3_cs)):
                        lly = [x for x in ls[i][j] if x not in b22_b3_cs]
                        ls[i][j] = lly
                        ls[i][j].append('22 Batch 3 CSE')
                        
                
                        
                    if (all(item in ls[i][j] for item in b22_b1_ec)):
                        lly = [x for x in ls[i][j] if x not in b22_b1_ec]
                        ls[i][j] = lly
                        ls[i][j].append('22 Batch 1 ECE')
                    
                    
                    if (all(item in ls[i][j] for item in b22_b2_ec)):
                        lly = [x for x in ls[i][j] if x not in b22_b2_ec]
                        ls[i][j] = lly
                        ls[i][j].append('22 Batch 2 ECE')
                    
                    if (all(item in ls[i][j] for item in b22_b3_ec)):
                        lly = [x for x in ls[i][j] if x not in b22_b3_ec]
                        ls[i][j] = lly
                        ls[i][j].append('22 Batch 3 ECE')
                        
                        
                        
                    if (all(item in ls[i][j] for item in b22_b1_cy)):
                        lly = [x for x in ls[i][j] if x not in b22_b1_cy]
                        ls[i][j] = lly
                        ls[i][j].append('22 Batch 1 CYS')
                    
                    
                    if (all(item in ls[i][j] for item in b22_b2_cy)):
                        lly = [x for x in ls[i][j] if x not in b22_b2_cy]
                        ls[i][j] = lly
                        ls[i][j].append('22 Batch 2 CYS')
                    
                    if (all(item in ls[i][j] for item in b22_b3_cy)):
                        lly = [x for x in ls[i][j] if x not in b22_b3_cy]
                        ls[i][j] = lly
                        ls[i][j].append('22 Batch 3 CYS')
                        
                        
                        
                    if (all(item in ls[i][j] for item in b22_b1_cd)):
                        lly = [x for x in ls[i][j] if x not in b22_b1_cd]
                        ls[i][j] = lly
                        ls[i][j].append('22 Batch 1 CDS')
                    
                    
                    if (all(item in ls[i][j] for item in b22_b2_cd)):
                        lly = [x for x in ls[i][j] if x not in b22_b2_cd]
                        ls[i][j] = lly
                        ls[i][j].append('22 Batch 2 CDS')
                    
                    if (all(item in ls[i][j] for item in b22_b3_cd)):
                        lly = [x for x in ls[i][j] if x not in b22_b3_cd]
                        ls[i][j] = lly
                        ls[i][j].append('22 Batch 3 CDS')
                        
                    
                        
                    if (all(item in ls[i][j] for item in b22_b1_s1)):
                        lly = [x for x in ls[i][j] if x not in b22_b1_s1]
                        ls[i][j] = lly
                        ls[i][j].append('22 Batch 1 set 1')
                        
                    if (all(item in ls[i][j] for item in b22_b1_s2)):
                        lly = [x for x in ls[i][j] if x not in b22_b1_s2]
                        ls[i][j] = lly
                        ls[i][j].append('22 Batch 1 set 2')
                    
                    if (all(item in ls[i][j] for item in b22_b2_s3)):
                        lly = [x for x in ls[i][j] if x not in b22_b2_s3]
                        ls[i][j] = lly
                        ls[i][j].append('22 Batch 2 set 3')
                    
                    if (all(item in ls[i][j] for item in b22_b2_s4)):
                        lly = [x for x in ls[i][j] if x not in b22_b2_s4]
                        ls[i][j] = lly
                        ls[i][j].append('22 Batch 2 set 4')     
                        
                    if (all(item in ls[i][j] for item in b22_b3_s5)):
                        lly = [x for x in ls[i][j] if x not in b22_b3_s5]
                        ls[i][j] = lly
                        ls[i][j].append('22 Batch 3 set 5')
                    
                    if (all(item in ls[i][j] for item in b22_b3_s6)):
                        lly = [x for x in ls[i][j] if x not in b22_b3_s6]
                        ls[i][j] = lly
                        ls[i][j].append('22 Batch 3 set 6')






                    if (all(item in ls[i][j] for item in b23_b1)):
                        lly = [x for x in ls[i][j] if x not in b23_b1]
                        ls[i][j] = lly
                        ls[i][j].append('23 Batch 1')
                        
                        
                    if (all(item in ls[i][j] for item in b23_b2)):
                        lly = [x for x in ls[i][j] if x not in b23_b2]
                        ls[i][j] = lly
                        ls[i][j].append('23 Batch 2')
                        
                        
                    if (all(item in ls[i][j] for item in b23_b3)):
                        lly = [x for x in ls[i][j] if x not in b23_b3]
                        ls[i][j] = lly
                        ls[i][j].append('23 Batch 3')
                        
                        
                    if (all(item in ls[i][j] for item in b23_b1_cs)):
                        lly = [x for x in ls[i][j] if x not in b23_b1_cs]
                        ls[i][j] = lly
                        ls[i][j].append('23 Batch 1 CSE')
                    
                    
                    if (all(item in ls[i][j] for item in b23_b2_cs)):
                        lly = [x for x in ls[i][j] if x not in b23_b2_cs]
                        ls[i][j] = lly
                        ls[i][j].append('23 Batch 2 CSE')
                    
                    if (all(item in ls[i][j] for item in b23_b3_cs)):
                        lly = [x for x in ls[i][j] if x not in b23_b3_cs]
                        ls[i][j] = lly
                        ls[i][j].append('23 Batch 3 CSE')
                        
                
                        
                    if (all(item in ls[i][j] for item in b23_b1_ec)):
                        lly = [x for x in ls[i][j] if x not in b23_b1_ec]
                        ls[i][j] = lly
                        ls[i][j].append('23 Batch 1 ECE')
                    
                    
                    if (all(item in ls[i][j] for item in b23_b2_ec)):
                        lly = [x for x in ls[i][j] if x not in b23_b2_ec]
                        ls[i][j] = lly
                        ls[i][j].append('23 Batch 2 ECE')
                    
                    if (all(item in ls[i][j] for item in b23_b3_ec)):
                        lly = [x for x in ls[i][j] if x not in b23_b3_ec]
                        ls[i][j] = lly
                        ls[i][j].append('23 Batch 3 ECE')
                        
                        
                        
                    if (all(item in ls[i][j] for item in b23_b1_cy)):
                        lly = [x for x in ls[i][j] if x not in b23_b1_cy]
                        ls[i][j] = lly
                        ls[i][j].append('23 Batch 1 CYS')
                    
                    
                    if (all(item in ls[i][j] for item in b23_b2_cy)):
                        lly = [x for x in ls[i][j] if x not in b23_b2_cy]
                        ls[i][j] = lly
                        ls[i][j].append('23 Batch 2 CYS')
                    
                    if (all(item in ls[i][j] for item in b23_b3_cy)):
                        lly = [x for x in ls[i][j] if x not in b23_b3_cy]
                        ls[i][j] = lly
                        ls[i][j].append('23 Batch 3 CYS')
                        
                        
                        
                    if (all(item in ls[i][j] for item in b23_b1_cd)):
                        lly = [x for x in ls[i][j] if x not in b23_b1_cd]
                        ls[i][j] = lly
                        ls[i][j].append('23 Batch 1 CDS')
                    
                    
                    if (all(item in ls[i][j] for item in b23_b2_cd)):
                        lly = [x for x in ls[i][j] if x not in b23_b2_cd]
                        ls[i][j] = lly
                        ls[i][j].append('23 Batch 2 CDS')
                    
                    if (all(item in ls[i][j] for item in b23_b3_cd)):
                        lly = [x for x in ls[i][j] if x not in b23_b3_cd]
                        ls[i][j] = lly
                        ls[i][j].append('23 Batch 3 CDS')



                    if (all(item in ls[i][j] for item in b23_b1_s1)):
                        lly = [x for x in ls[i][j] if x not in b23_b1_s1]
                        ls[i][j] = lly
                        ls[i][j].append('23 Batch 1 set 1')
                        
                    if (all(item in ls[i][j] for item in b23_b1_s2)):
                        lly = [x for x in ls[i][j] if x not in b23_b1_s2]
                        ls[i][j] = lly
                        ls[i][j].append('23 Batch 1 set 2')
                    
                    if (all(item in ls[i][j] for item in b23_b2_s3)):
                        lly = [x for x in ls[i][j] if x not in b23_b2_s3]
                        ls[i][j] = lly
                        ls[i][j].append('23 Batch 2 set 3')
                    
                    if (all(item in ls[i][j] for item in b23_b2_s4)):
                        lly = [x for x in ls[i][j] if x not in b23_b2_s4]
                        ls[i][j] = lly
                        ls[i][j].append('23 Batch 2 set 4')     
                        
                    if (all(item in ls[i][j] for item in b23_b3_s5)):
                        lly = [x for x in ls[i][j] if x not in b23_b3_s5]
                        ls[i][j] = lly
                        ls[i][j].append('23 Batch 3 set 5')
                    
                    if (all(item in ls[i][j] for item in b23_b3_s6)):
                        lly = [x for x in ls[i][j] if x not in b23_b3_s6]
                        ls[i][j] = lly
                        ls[i][j].append('23 Batch 3 set 6')





                    
                        
                        
                    
                    
                    if (all(item in ls[i][j] for item in b21_b1)):
                        lly = [x for x in ls[i][j] if x not in b21_b1]
                        ls[i][j] = lly
                        ls[i][j].append('21 Batch 1')
                        
                    if (all(item in ls[i][j] for item in b21_b2)):
                        lly = [x for x in ls[i][j] if x not in b21_b2]
                        ls[i][j] = lly
                        ls[i][j].append('21 Batch 2')
                        
                        
                    if (all(item in ls[i][j] for item in b21_b1_cs)):
                        lly = [x for x in ls[i][j] if x not in b21_b1_cs]
                        ls[i][j] = lly
                        ls[i][j].append('21 Batch 1 CSE')
                        
                    if (all(item in ls[i][j] for item in b21_b2_cs)):
                        lly = [x for x in ls[i][j] if x not in b21_b2_cs]
                        ls[i][j] = lly
                        ls[i][j].append('21 Batch 2 CSE')
                        
                        
                    if (all(item in ls[i][j] for item in b21_b1_ec)):
                        lly = [x for x in ls[i][j] if x not in b21_b1_ec]
                        ls[i][j] = lly
                        ls[i][j].append('21 Batch 1 ECE')
                        
                    if (all(item in ls[i][j] for item in b21_b2_ec)):
                        lly = [x for x in ls[i][j] if x not in b21_b2_ec]
                        ls[i][j] = lly
                        ls[i][j].append('21 Batch 2 ECE')
                        
                        
                    if (all(item in ls[i][j] for item in b21_b1_cy)):
                        lly = [x for x in ls[i][j] if x not in b21_b1_cy]
                        ls[i][j] = lly
                        ls[i][j].append('21 Batch 1 CYS')
                        
                    if (all(item in ls[i][j] for item in b21_b2_cy)):
                        lly = [x for x in ls[i][j] if x not in b21_b2_cy]
                        ls[i][j] = lly
                        ls[i][j].append('21 Batch 2 CYS')
                        

                    if (all(item in ls[i][j] for item in b21_b1_s1)):
                        lly = [x for x in ls[i][j] if x not in b21_b1_s1]
                        ls[i][j] = lly
                        ls[i][j].append('21 Batch 1 set 1')
                        
                    if (all(item in ls[i][j] for item in b21_b1_s2)):
                        lly = [x for x in ls[i][j] if x not in b21_b1_s2]
                        ls[i][j] = lly
                        ls[i][j].append('21 Batch 1 set 2')
                    
                    if (all(item in ls[i][j] for item in b21_b2_s3)):
                        lly = [x for x in ls[i][j] if x not in b21_b2_s3]
                        ls[i][j] = lly
                        ls[i][j].append('21 Batch 2 set 3')
                    
                    if (all(item in ls[i][j] for item in b21_b2_s4)):
                        lly = [x for x in ls[i][j] if x not in b21_b2_s4]
                        ls[i][j] = lly
                        ls[i][j].append('21 Batch 2 set 4')
                        
                    
                    
                    
                        
                        
                    
                    
                    if (all(item in ls[i][j] for item in b20_b1)):
                        lly = [x for x in ls[i][j] if x not in b20_b1]
                        ls[i][j] = lly
                        ls[i][j].append('20 Batch 1')
                        
                    if (all(item in ls[i][j] for item in b20_b2)):
                        lly = [x for x in ls[i][j] if x not in b20_b2]
                        ls[i][j] = lly
                        ls[i][j].append('20 Batch 2')
                        
                        
                    if (all(item in ls[i][j] for item in b20_b1_cs)):
                        lly = [x for x in ls[i][j] if x not in b20_b1_cs]
                        ls[i][j] = lly
                        ls[i][j].append('20 Batch 1 CSE')
                        
                    if (all(item in ls[i][j] for item in b20_b2_cs)):
                        lly = [x for x in ls[i][j] if x not in b20_b2_cs]
                        ls[i][j] = lly
                        ls[i][j].append('20 Batch 2 CSE')
                        
                        
                    if (all(item in ls[i][j] for item in b20_b1_ec)):
                        lly = [x for x in ls[i][j] if x not in b20_b1_ec]
                        ls[i][j] = lly
                        ls[i][j].append('20 Batch 1 ECE')
                        
                    if (all(item in ls[i][j] for item in b20_b2_ec)):
                        lly = [x for x in ls[i][j] if x not in b20_b2_ec]
                        ls[i][j] = lly
                        ls[i][j].append('20 Batch 2 ECE')









            for i in range(len(ls)):
                for j in range(10):
                    ls[i][j]="\n".join(ls[i][j])

            
            ls[0].insert(0, 'Mon')
            ls[1].insert(0, 'Tue')
            ls[2].insert(0, 'Wed')
            ls[3].insert(0, 'Thu')
            ls[4].insert(0, 'Fri')




            '''l = []
            for x in result:
                x = list(x.values())
                l.append(x)'''
            length=len(ls)
            #return redirect('/res2')
            #return render_template('ind2.html')


'''@app.route('/ind22', methods=['GET', 'POST'])
def ind2r():
    if request.method == 'POST':
            try:
                che = request.form['che']
            except:
                che=0
            
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("select facultyid from faculty;")
            facu=cursor.fetchall()
            fac=[]
            for x in facu:
                x = list(x.values())
                fac.append(x)
            
            ln=len(fac)
            lx=[]
            for i in range(ln):
                lx.append(str(fac[i][0]))

            if 'nfa' not in globals():
                global nfa
                nfa=0
            
            if che==1:
                nfa=0
            elif che==0:
                nfa=nfa


            #print(lx)
            ind22(lx[nfa])
            if nfa<len(lx):
                nfa=nfa+1
            else:
                nfa=0            
            return redirect('/res22')'''



@app.route('/ind22', methods=['GET', 'POST'])
def ind2r():
    if request.method == 'POST':
            #remove insted of move
            source_1 = 'C:/Users/imaks/Downloads/ICS213 Assignment 2 (2)/ICS213 Assignment 2/time_table_flsk/facul_indv'
            source_2 = 'C:/Users/imaks/Downloads/ICS213 Assignment 2 (2)/ICS213 Assignment 2/time_table_flsk'
            target_dir = 'C:/Users/imaks/Downloads/ICS213 Assignment 2 (2)/ICS213 Assignment 2/time_table_flsk/del_folder'
            file_names = os.listdir(source_1)
            for file_name in file_names:
                os.remove(os.path.join(source_1, file_name))
            if 'facul_indv.zip' in file_names:
                file_names = ['facul_indv.zip']
                for file_name in file_names:
                    os.remove(os.path.join(source_2, file_name))
                    
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("select distinct facultyid from faculty;")
            facu=cursor.fetchall()
            fac=[]
            for x in facu:
                x = list(x.values())
                fac.append(x)
            
            ln=len(fac)
            lx=[]
            for i in range(ln):
                lx.append(str(fac[i][0]))

            if 'nfa' not in globals():
                global nfa
                nfa=0
            nms=[]
            for x in range(len(lx)):
                ind22(lx[x])
                html = render_template('res2.html',data=ls,length=length,name=name,length2=length2,t2=satsun)
                pdfkit.from_string(html, name+".pdf")
                nms.append(name+".pdf")
            #source_dir = 'C:/Users/imaks/Downloads/ICS213 Assignment 2 (2)/ICS213 Assignment 2/time_table_flsk'
            #target_dir = 'C:/Users/imaks/Downloads/ICS213 Assignment 2 (2)/ICS213 Assignment 2/time_table_flsk/facul_indv'
            nms=list(set(nms))
            source_dir = 'C:/Users/imaks/Downloads/ICS213 Assignment 2 (2)/ICS213 Assignment 2/time_table_flsk'
            target_dir = './facul_indv'
            file_names = nms
            for file_name in file_names:
                try:
                    shutil.move(os.path.join(source_dir, file_name), target_dir)
                except Exception as e:
                    print("\nerrrrrrrrrrrorrrrrrrrrrrrrrr\nnerrrrrrrrrrrorrrrrrrrrrrrrrr\nnerrrrrrrrrrrorrrrrrrrrrrrrrr\nnerrrrrrrrrrrorrrrrrrrrrrrrrr\nnerrrrrrrrrrrorrrrrrrrrrrrrrr\nnerrrrrrrrrrrorrrrrrrrrrrrrrr\nnerrrrrrrrrrrorrrrrrrrrrrrrrr\nnerrrrrrrrrrrorrrrrrrrrrrrrrr\nnerrrrrrrrrrrorrrrrrrrrrrrrrr\nnerrrrrrrrrrrorrrrrrrrrrrrrrr")
                    print(e,"\nerrrrrrrrrrrorrrrrrrrrrrrrrr\nnerrrrrrrrrrrorrrrrrrrrrrrrrr\nnerrrrrrrrrrrorrrrrrrrrrrrrrr\nnerrrrrrrrrrrorrrrrrrrrrrrrrr\nnerrrrrrrrrrrorrrrrrrrrrrrrrr\nnerrrrrrrrrrrorrrrrrrrrrrrrrr\nnerrrrrrrrrrrorrrrrrrrrrrrrrr\nnerrrrrrrrrrrorrrrrrrrrrrrrrr\nnerrrrrrrrrrrorrrrrrrrrrrrrrr\nnerrrrrrrrrrrorrrrrrrrrrrrrrr")

            
            return redirect('/res22')
            

@app.route('/res22')
def res22():
    zip_path ='./facul_indv.zip'
    directory_to_zip = './facul_indv'

    folder = pathlib.Path(directory_to_zip)

    
    with ZipFile(zip_path,'w',ZIP_DEFLATED) as zip:
        for file in folder.iterdir():
            zip.write(file)
    
    return render_template('res22.html')

    
@app.route('/download')
def download_file():
    p="C:/Users/imaks/Downloads/ICS213 Assignment 2 (2)/ICS213 Assignment 2/time_table_flsk/facul_indv.zip"
    return send_file(p,as_attachment=True)
    

    #html = render_template('res22.html',data=ls,length=length,name=name)
    #pdfkit.from_string(html, name+".pdf")
    #response = make_response(pdf)
    #response.headers["Content-Type"] = "application/pdf"
    #response.headers["Content-Disposition"] = "inline; filename="+name+"_TT.pdf"
    #return response
    #return render_template('res2.html',data=ls,length=length)








@app.route('/ind21', methods=['GET', 'POST'])
def ind21():
    if request.method == 'POST':
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("select facultyid from faculty;")
            facu=cursor.fetchall()
            fac=[]
            for x in facu:
                x = list(x.values())
                fac.append(x)
            
            ln=len(fac)
            lx=[]
            for i in range(ln):
                lx.append(str(fac[i][0]))

            print(lx)

            global all
            global length
            global lgn
            all=[]
            for n in range(len(lx)):
                a="select days,tim_from,tim_to,faculty_subject_subjectid,class_room_roomid,set_batc_batchid from classes where faculty_facultyid="+"\'"+str(lx[n])+"\'"+" order by days,tim_from;"
                cursor.execute(a)
                result=cursor.fetchall()
                #print(result)
                t=[]
                for x in result:
                    x = list(x.values())
                    t.append(x)

                #print(t)

                sort_order = ['Mon','Tue','Wed','Thu','Fri']
                t = [tu for x in sort_order for tu in t if tu[0] == x]
                l=[]
                for x in t:
                    x = list(x)
                    l.append(x)


                for i in range(len(l)):
                    if str(l[i][0])=='Mon':
                        l[i].append(0)
                    elif str(l[i][0])=='Tue':
                        l[i].append(1)
                    elif str(l[i][0])=='Wed':
                        l[i].append(2)
                    elif str(l[i][0])=='Thu':
                        l[i].append(3)
                    elif str(l[i][0])=='Fri':
                        l[i].append(4)

                for i in range(len(l)):
                    if str(l[i][1])=='9:00:00':
                        l[i].append(0)
                    elif str(l[i][1])=='10:00:00':
                        l[i].append(1)
                    elif str(l[i][1])=='11:05:00' and str(l[i][2])=='12:00:00':
                        l[i].append(2)
                    elif str(l[i][1])=='11:05:00' and str(l[i][2])=='13:00:00':
                        l[i].append(23)
                    elif str(l[i][1])=='12:05:00':
                        l[i].append(3)
                    elif str(l[i][1])=='14:00:00' and str(l[i][2])=='14:55:00':
                        l[i].append(4)
                    elif str(l[i][1])=='14:00:00' and str(l[i][2])=='15:55:00':
                        l[i].append(45)
                    elif str(l[i][1])=='15:00:00' and str(l[i][2])=='15:55:00':
                        l[i].append(5)
                    elif str(l[i][1])=='15:00:00' and str(l[i][2])=='16:55:00':
                        l[i].append(56)
                    elif str(l[i][1])=='16:00:00' and str(l[i][2])=='16:55:00':
                        l[i].append(6)


                

                ls=[]
                for i in range(5):
                    lists = [[] for i in range(9)]
                    ls.append(lists)
                    
                    
                for i in range(len(l)):
                    a=l[i][-2]
                    b=l[i][-1]
                    if b<10:
                        if len(ls[a][b])==0:
                            ls[a][b]=[l[i][3],l[i][4],l[i][5]]
                        else:
                            ls[a][b].append(l[i][5])
                            
                            
                    else:
                        b1=b//10
                        b2=b%10
                        
                        if len(ls[a][b1])==0:
                            ls[a][b1]=[l[i][3],l[i][4],l[i][5]]
                        else:
                            ls[a][b1].append(l[i][5])

                        if len(ls[a][b2])==0:
                            ls[a][b2]=[l[i][3],l[i][4],l[i][5]]
                        else:
                            ls[a][b2].append(l[i][5])

                
                ls[0].insert(0, 'Mon'+"("+str(lx[n])+")")
                ls[1].insert(0, 'Tue'+"("+str(lx[n])+")")
                ls[2].insert(0, 'Wed'+"("+str(lx[n])+")")
                ls[3].insert(0, 'Thu'+"("+str(lx[n])+")")
                ls[4].insert(0, 'Fri'+"("+str(lx[n])+")")

                length=len(ls)
                all.append(ls)




            '''l = []
            for x in result:
                x = list(x.values())
                l.append(x)'''
            lgn=len(all)
            return redirect('/res21')
    return render_template('ind2.html')
@app.route('/res21')
def res21():
#    print(l)
    html = render_template('res21.html',data=all,length=length,lgn=lgn)
    pdf = pdfkit.from_string(html, False)
    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = "inline; filename=all_faculty_TT.pdf"
    return response
    #return render_template('res2.html',data=ls,length=length)












@app.route('/ind23', methods=['GET', 'POST'])
def ind23():
    if request.method == 'POST':
            global name
            dday = request.form['dday']
            name=str(dday)
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            a="select days,tim_from,tim_to,faculty_subject_subjectid,class_room_roomid,set_batc_batchid from classes where faculty_facultyid="+"\'"+str(dday)+"\'"+" order by days,tim_from;"
            cursor.execute(a)
            result=cursor.fetchall()
            #print(result)
            t=[]
            for x in result:
                x = list(x.values())
                t.append(x)

            #print(t)

            sort_order = ['Mon','Tue','Wed','Thu','Fri']
            t = [tu for x in sort_order for tu in t if tu[0] == x]
            l=[]
            for x in t:
                x = list(x)
                l.append(x)


            for i in range(len(l)):
                if str(l[i][0])=='Mon':
                    l[i].append(0)
                elif str(l[i][0])=='Tue':
                    l[i].append(1)
                elif str(l[i][0])=='Wed':
                    l[i].append(2)
                elif str(l[i][0])=='Thu':
                    l[i].append(3)
                elif str(l[i][0])=='Fri':
                    l[i].append(4)

            for i in range(len(l)):
                if str(l[i][1])=='8:00:00':
                    l[i].append(0)
                elif str(l[i][1])=='9:00:00':
                    l[i].append(1)
                elif str(l[i][1])=='10:00:00' or str(l[i][1])=='10:05:00':
                    l[i].append(2)
                elif str(l[i][1])=='11:05:00' and str(l[i][2])=='12:00:00':
                    l[i].append(3)
                elif str(l[i][1])=='11:05:00' and str(l[i][2])=='13:00:00':
                    l[i].append(34)
                elif str(l[i][1])=='12:05:00':
                    l[i].append(4)
                elif str(l[i][1])=='13:00:00'and str(l[i][2])=='15:55:00':
                    l[i].append(567)
                elif str(l[i][1])=='13:00:00' and str(l[i][2])=='13:55:00':
                    l[i].append(5)
                elif str(l[i][1])=='14:00:00' and str(l[i][2])=='14:55:00':
                    l[i].append(6)
                elif str(l[i][1])=='14:00:00' and str(l[i][2])=='15:55:00':
                    l[i].append(67)
                elif str(l[i][1])=='15:00:00' and str(l[i][2])=='15:55:00':
                    l[i].append(7)
                elif str(l[i][1])=='15:00:00' and str(l[i][2])=='16:55:00':
                    l[i].append(78)
                elif str(l[i][1])=='16:00:00' and str(l[i][2])=='16:55:00':
                    l[i].append(8)


            global ls
            global length

            ls=[]
            for i in range(5):
                lists = [[] for i in range(9)]
                ls.append(lists)
                
                
            for i in range(len(l)):
                a=l[i][-2]
                b=l[i][-1]
                if b<10:
                    if len(ls[a][b])==0:
                        ls[a][b]=[l[i][3],l[i][4],l[i][5]]
                    else:
                        ls[a][b].append(l[i][5])
                        
                        
                else:
                    b1=b//10
                    b2=b%10
                    
                    if len(ls[a][b1])==0:
                        ls[a][b1]=[l[i][3],l[i][4],l[i][5]]
                    else:
                        ls[a][b1].append(l[i][5])

                    if len(ls[a][b2])==0:
                        ls[a][b2]=[l[i][3],l[i][4],l[i][5]]
                    else:
                        ls[a][b2].append(l[i][5])

            
            ls[0].insert(0, 'Mon')
            ls[1].insert(0, 'Tue')
            ls[2].insert(0, 'Wed')
            ls[3].insert(0, 'Thu')
            ls[4].insert(0, 'Fri')

            print(ls)

            
            qr="select distinct roomid from class_room;"
            cursor.execute(qr)
            rqr=cursor.fetchall()

            rq=[]
            for x in rqr:
                x = list(x.values())
                rq.append(x)

            print(rq)
            global clashl
            global clashc
            clashc=0
            clashl=[]
            for i in range(len(ls)):
                for j in range(len(ls[i])):
                    cla=0
                    for x in rq:
                        if(x[0] in ls[i][j]):
                            cla=cla+1
                        if(cla>1):
                            clashc=clashc+1
                            print('clash')
                            break
                            

            if(clashc==0):
                print("NO CLASHHHHH")


            #for i in range(len(ls)):
            #    for j in range(1,len(ls[i])):
            #        for k in ls[i][j]:


            name=name
            '''l = []
            for x in result:
                x = list(x.values())
                l.append(x)'''
            length=len(ls)
            return redirect('/res23')
    return render_template('ind2.html')
@app.route('/res23')
def res23():
#    print(l)
    return render_template('res23.html',clashc=clashc)
    #return render_template('res2.html',data=ls,length=length)

















@app.route('/ind3', methods=['GET', 'POST'])
def ind3():
    if request.method == 'POST':
            frt = request.form['frt']
            tot = request.form['tot']
            dday=request.form['dday']
            print(type(dday))
            if dday=="monday":
                dday="mon"
            elif dday=="tuesday":
                dday="tue"
            elif dday=="wednesday":
                dday="wed"
            elif dday=="thursday":
                dday="thu"
            elif dday=="friday":
                dday="fri"
            elif dday=="saturday":
                dday="Sat"
            elif dday=="sunday":
                dday="Sun"
            
            print(dday)

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            #a="SELECT DISTINCT roomid FROM class_room where roomid not in (SELECT DISTINCT roomid FROM class_room where roomid in (SELECT distinct class_room_roomid FROM classes WHERE tim_from<="+"\'"+str(frt)+"\'"+" AND tim_to>="+"\'"+str(frt)+"\'"+" and days="+"\'"+str(dday)+"\'"+") or roomid in(SELECT distinct class_room_roomid FROM classes WHERE tim_from<="+"\'"+str(tot)+"\'"+" AND tim_to>="+"\'"+str(tot)+"\'"+" and days="+"\'"+str(dday)+"\'"+") or roomid in (SELECT distinct class_room_roomid FROM classes WHERE tim_to>="+"\'"+str(tot)+"\'"+" and days="+"\'"+str(dday)+"\'"+" and class_room_roomid in (SELECT distinct class_room_roomid FROM classes WHERE tim_from<="+"\'"+str(frt)+"\'"+" and days="+"\'"+str(dday)+"\'"+")));"
            a="SELECT DISTINCT roomid FROM class_room EXCEPT SELECT distinct class_room_roomid FROM classes WHERE tim_from<="+"\'"+str(tot)+"\'"+" and tim_to>="+"\'"+str(frt)+"\'"+" and days="+"\'"+str(dday)+"\'"+";"
            #a="SELECT DISTINCT roomid FROM class_room where roomid not in(SELECT class_room_roomid FROM classes WHERE tim_from<"+"\'"+str(frt)+"\'"+" AND tim_to>"+"\'"+str(tot)+"\'"+" and days="+"\'"+str(dday)+"\'"+");"
            cursor.execute(a)
            result=cursor.fetchall()
            #print(result)
            global l
            global length
            l = []
            for x in result:
                x = list(x.values())
                if 'CAB' in x[0]:
                    x.append("Admin block")
                elif 'AB' in x[0]:
                    x.append("Academic block")
                l.append(x)
            length=len(l)
            #print(l)
            return redirect('/res3')
    return render_template('ind3.html')
@app.route('/res3')
def res3():
#    print(l)
    return render_template('res3.html',data=l,length=length)




@app.route('/ind31', methods=['GET', 'POST'])
def ind31():
    if request.method == 'POST':
            frt = request.form['frt']
            tot = request.form['tot']
            dday=request.form['dday']
            rom = request.form['rom']

            print(dday)
            if str(dday)=="monday":
                dday="mon"
            elif str(dday)=="tuesday":
                dday="tue"
            elif str(dday)=="wednesday":
                dday="wed"
            elif str(dday)=="thursday":
                dday="thu"
            elif str(dday)=="friday":
                dday="fri"
            elif str(dday)=="saturday":
                dday="Sat"
            elif str(dday)=="sunday":
                dday="Sun"

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            #a="SELECT DISTINCT roomid FROM class_room where roomid not in (SELECT DISTINCT roomid FROM class_room where roomid in (SELECT distinct class_room_roomid FROM classes WHERE tim_from<="+"\'"+str(frt)+"\'"+" AND tim_to>="+"\'"+str(frt)+"\'"+" and days="+"\'"+str(dday)+"\'"+") or roomid in(SELECT distinct class_room_roomid FROM classes WHERE tim_from<="+"\'"+str(tot)+"\'"+" AND tim_to>="+"\'"+str(tot)+"\'"+" and days="+"\'"+str(dday)+"\'"+") or roomid in (SELECT distinct class_room_roomid FROM classes WHERE tim_to>="+"\'"+str(tot)+"\'"+" and days="+"\'"+str(dday)+"\'"+" and class_room_roomid in (SELECT distinct class_room_roomid FROM classes WHERE tim_from<="+"\'"+str(frt)+"\'"+" and days="+"\'"+str(dday)+"\'"+")));"
            #cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            a="SELECT DISTINCT roomid FROM class_room EXCEPT SELECT distinct class_room_roomid FROM classes WHERE tim_from<="+"\'"+str(tot)+"\'"+" and tim_to>="+"\'"+str(frt)+"\'"+" and days="+"\'"+str(dday)+"\'"+";"
            #a="SELECT DISTINCT roomid FROM class_room where roomid not in(SELECT class_room_roomid FROM classes WHERE tim_from<"+"\'"+str(frt)+"\'"+" AND tim_to>"+"\'"+str(tot)+"\'"+" and days="+"\'"+str(dday)+"\'"+");"
            cursor.execute(a)
            result=cursor.fetchall()
            #print(result)
            global l
            global length
            l = []
            for x in result:
                x = list(x.values())
                if 'CAB' in x[0]:
                    x.append("Admin block")
                elif 'AB' in x[0]:
                    x.append("Academic block")
                l.append(x)
            c=0
            for i in l:
                if i[0]==rom:
                    c=c+1
                    break
            if c==1:
                l=[["is","Available"]]
            elif c==0:
                l=[["is","Not Available"]]
            length=len(l)
            #print(l)
            return redirect('/res3')
    return render_template('ind3.html')






@app.route('/ind4', methods=['GET', 'POST'])
def ind4():
    if request.method == 'POST':
            frt = request.form['frt']
            tot = request.form['tot']
            dday=request.form['dday']

            if str(dday)=="monday":
                dday="mon"
            elif str(dday)=="tuesday":
                dday="tue"
            elif str(dday)=="wednesday":
                dday="wed"
            elif str(dday)=="thursday":
                dday="thu"
            elif str(dday)=="friday":
                dday="fri"
            elif str(dday)=="saturday":
                dday="Sat"
            elif str(dday)=="sunday":
                dday="Sun"

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            a="SELECT DISTINCT facultyid FROM faculty EXCEPT SELECT distinct faculty_facultyid FROM classes WHERE tim_from<="+"\'"+str(tot)+"\'"+" and tim_to>="+"\'"+str(frt)+"\'"+" and days="+"\'"+str(dday)+"\'"+";"
            #a="SELECT DISTINCT facultyid FROM faculty where facultyid not in(SELECT DISTINCT facultyid FROM faculty where facultyid in (SELECT distinct faculty_facultyid FROM classes WHERE tim_from<="+"\'"+str(frt)+"\'"+" AND tim_to>="+"\'"+str(frt)+"\'"+" and days="+"\'"+str(dday)+"\'"+") or facultyid in(SELECT distinct faculty_facultyid FROM classes WHERE tim_from<="+"\'"+str(tot)+"\'"+" AND tim_to>="+"\'"+str(tot)+"\'"+" and days="+"\'"+str(dday)+"\'"+") or facultyid in (SELECT distinct faculty_facultyid FROM classes WHERE tim_to>="+"\'"+str(tot)+"\'"+" and days="+"\'"+str(dday)+"\'"+" and faculty_facultyid in(SELECT distinct faculty_facultyid FROM classes WHERE tim_from<="+"\'"+str(frt)+"\'"+" and days="+"\'"+str(dday)+"\'"+")));"
            #a="SELECT DISTINCT facultyid FROM faculty where facultyid not in(SELECT faculty_facultyid FROM classes WHERE tim_from<"+"\'"+str(frt)+"\'"+" AND tim_to>"+"\'"+str(tot)+"\'"+" and days="+"\'"+str(dday)+"\'"+");"
            cursor.execute(a)
            result=cursor.fetchall()
            #print(result)
            global l
            global length
            l = []
            for x in result:
                x = list(x.values())
                l.append(x)
            global l1
            l1=[]
            for i in l:
                if str(dday).lower() not in weekoff(i):
                    l1.append(i)
            length=len(l1)

            return redirect('/res4')
    return render_template('ind4.html')
@app.route('/res4')
def res4():
#    print(l)
    return render_template('res4.html',data=l1,length=length)



@app.route('/ind41', methods=['GET', 'POST'])
def ind41():
    if request.method == 'POST':
            frt = request.form['frt']
            tot = request.form['tot']
            dday=request.form['dday']
            fac = request.form['fac']


            if str(dday)=="monday":
                dday="mon"
            elif str(dday)=="tuesday":
                dday="tue"
            elif str(dday)=="wednesday":
                dday="wed"
            elif str(dday)=="thursday":
                dday="thu"
            elif str(dday)=="friday":
                dday="fri"
            elif str(dday)=="saturday":
                dday="Sat"
            elif str(dday)=="sunday":
                dday="Sun"

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

            a="SELECT DISTINCT facultyid FROM faculty EXCEPT SELECT distinct faculty_facultyid FROM classes WHERE tim_from<="+"\'"+str(tot)+"\'"+" and tim_to>="+"\'"+str(frt)+"\'"+" and days="+"\'"+str(dday)+"\'"+";"
            cursor.execute(a)
            result=cursor.fetchall()
            #print(result)
            global l
            global length
            l = []
            for x in result:
                x = list(x.values())
                l.append(x)
            #print(l)
            global l1
            l1=[]
            if [fac] in l and (str(dday).lower() not in weekoff(str(fac))):
                l1=[["Available"]]
            else:
                l1=[["Not Available"]]
            length=len(l1)
            return redirect('/res4')
    return render_template('ind4.html')





@app.route('/ind5', methods=['GET', 'POST'])
def ind5():
    if request.method == 'POST':
            dday = request.form['dday']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            a="select facultyid,fname from faculty where subject_subjectid="+"\'"+str(dday)+"\'"+";"
            cursor.execute(a)
            result=cursor.fetchall()
            #print(result)
            global l
            global length
            l = []
            for x in result:
                x = list(x.values())
                l.append(x)
            length=len(l)
            return redirect('/res5')
    return render_template('ind5.html')
@app.route('/res5')
def res5():
#    print(l)
    return render_template('res5.html',data=l,length=length)





@app.route('/ind6', methods=['GET', 'POST'])
def ind6():
    if request.method == 'POST':
            frt = request.form['frt']
            tot = request.form['tot']
            dday=request.form['dday']

            if str(dday)=="monday":
                dday="mon"
            elif str(dday)=="tuesday":
                dday="tue"
            elif str(dday)=="wednesday":
                dday="wed"
            elif str(dday)=="thursday":
                dday="thu"
            elif str(dday)=="friday":
                dday="fri"
            elif str(dday)=="saturday":
                dday="Sat"
            elif str(dday)=="sunday":
                dday="Sun"

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

            #a="SELECT DISTINCT batchid FROM set_batc where batchid not in(SELECT set_batc_batchid FROM classes WHERE tim_from<"+"\'"+str(frt)+"\'"+" AND tim_to>"+"\'"+str(tot)+"\'"+" and days="+"\'"+str(dday)+"\'"+");"
            a="SELECT DISTINCT batchid FROM set_batc EXCEPT SELECT distinct set_batc_batchid FROM classes WHERE tim_from<="+"\'"+str(tot)+"\'"+" and tim_to>="+"\'"+str(frt)+"\'"+" and days="+"\'"+str(dday)+"\'"+";"
            
            cursor.execute(a)
            result=cursor.fetchall()
            #print(result)
            global l
            global length
            l = []
            for x in result:
                x = list(x.values())
                l.append(x)
            length=len(l)
            return redirect('/res6')
    return render_template('ind6.html')
@app.route('/res6')
def res6():
#    print(l)
    return render_template('res6.html',data=l,length=length)



@app.route('/ind61', methods=['GET', 'POST'])
def ind61():
    if request.method == 'POST':
            frt = request.form['frt']
            tot = request.form['tot']
            dday=request.form['dday']
            bat=request.form['bat']

            if str(dday)=="monday":
                dday="mon"
            elif str(dday)=="tuesday":
                dday="tue"
            elif str(dday)=="wednesday":
                dday="wed"
            elif str(dday)=="thursday":
                dday="thu"
            elif str(dday)=="friday":
                dday="fri"
            elif str(dday)=="saturday":
                dday="Sat"
            elif str(dday)=="sunday":
                dday="Sun"

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

            #a="SELECT DISTINCT batchid FROM set_batc where batchid not in(SELECT set_batc_batchid FROM classes WHERE tim_from<"+"\'"+str(frt)+"\'"+" AND tim_to>"+"\'"+str(tot)+"\'"+" and days="+"\'"+str(dday)+"\'"+");"
            a="SELECT DISTINCT batchid FROM set_batc EXCEPT SELECT distinct set_batc_batchid FROM classes WHERE tim_from<="+"\'"+str(tot)+"\'"+" and tim_to>="+"\'"+str(frt)+"\'"+" and days="+"\'"+str(dday)+"\'"+";"
            cursor.execute(a)
            result=cursor.fetchall()
            #print(result)
            global l
            global length
            l = []
            for x in result:
                x = list(x.values())
                l.append(x)
            if [bat] in l:
                l=[["Available"]]
            else:
                l=[["Not Available"]]
            length=len(l)
            return redirect('/res6')
    return render_template('ind6.html')




#import numpy as np
#import pandas as pd

def calc(batch,file1,file2,r1,r2):
    import pandas as pd
    #f1 = open('Flask_Upload/static/'+request.files['Key'].filename, "r")
    sf=pd.ExcelFile(file2)
    sheet2=pd.read_excel(sf)
    sf=pd.DataFrame(sheet2)
    subjects=[]
    for i in range(len(sf['COURSES'])):
        if isinstance(sf['COURSES'][i], str) and 'BTP-' not in sf['COURSES'][i].split():
            addit=" ".join(sf['COURSES'][i].split()[0:2])
            if '/' not in sf['FACULTY'][i]:    
                subjects.append(addit)
            else:
                char_count = sf['FACULTY'][i].count('/')+1
                for x in range(char_count):
                    subjects.append(addit)
                
    for i in range(len(sf['COURSES.1'])):
        if isinstance(sf['COURSES.1'][i], str) and 'BTP-' not in sf['COURSES.1'][i].split():
            addit=" ".join(sf['COURSES.1'][i].split()[0:2])
            if '/' not in sf['FACULTY.1'][i]:
                subjects.append(addit)
            else:
                char_count = sf['FACULTY.1'][i].count('/')+1
                for x in range(char_count):
                    subjects.append(addit)

    '''facultys={}
    for i in sf['FACULTY']:
        if isinstance(i, str):
            if '/' not in i:
                facultys[i.split(' (')[0]]=(i.split(' (')[1]).split(')')[0]
            else:
                char_count = i.count('/')+1
                ii=i.split('/ ')
                for r in range(char_count):
                    facultys[ii[r].split(' (')[0]]=(ii[r].split(' (')[1]).split(')')[0]
    for i in sf['FACULTY.1']:
        print(i)
        if isinstance(i, str):
            if '/' not in i:
                facultys[i.split(' (')[0]]=(i.split(' (')[1]).split(')')[0]
            else:
                char_count = i.count('/')+1
                ii=i.split('/ ')
                for r in range(char_count):
                    facultys[ii[r].split(' (')[0]]=(ii[r].split(' (')[1]).split(')')[0]
    '''

    facultys={}
    c=0
    for i in sf['FACULTY']:
        if isinstance(i, str):
            if '/' not in i:
                facultys[c]=[i.split(' (')[0],(i.split(' (')[1]).split(')')[0]]
                c+=1
            else:
                char_count = i.count('/')+1
                ii=i.split('/ ')
                for r in range(char_count):
                    facultys[c]=[ii[r].split(' (')[0],(ii[r].split(' (')[1]).split(')')[0]]
                    c+=1
    for i in sf['FACULTY.1']:
        #print(i)
        if isinstance(i, str):
            if '/' not in i:
                facultys[c]=[i.split(' (')[0],(i.split(' (')[1]).split(')')[0]]
                c+=1
            else:
                char_count = i.count('/')+1
                ii=i.split('/ ')
                for r in range(char_count):
                    facultys[c]=[ii[r].split(' (')[0],(ii[r].split(' (')[1]).split(')')[0]]
                    c+=1

    
    import mysql.connector
    from mysql.connector import Error
    import pandas as pd
    import pyodbc
    #from flask.ext.mysql import MySQL

    #cursor.close()
    #connection.close()
    def create_db_connection(host_name, user_name, user_password, db_name):
        connection = None
        try:
            connection = mysql.connector. connect (host=host_name,
                                            user=user_name,
                                            passwd=user_password,
                                                database = db_name)
            print("MySQl database connection successfull")
        except Error as err:
            print(f"Error: '{err}'")
        return connection

    
    pw='secret'
    db="tt_data"
    connection=create_db_connection("localhost","user",pw,db)

    cursor = connection.cursor()

    print("/n/n/n/n/n/n/n/n/n/n/n//n/n/n/n/n/n/n/n/n/n/n/")
    print("inserting subject details")
    q1 = "INSERT INTO subject (subjectid) VALUES (%s);"
    for v in subjects:
        try:
            cursor.execute(q1, (v,))
            print(v, 'done')
            connection.commit()
        except Exception as e:
            print("Error inserting", v, ":", e)

    


    print("/n/n/n/n/n/n/n/n")

    print("inserting faculty details")
    q2="INSERT INTO faculty (facultyid,fname,subject_subjectid) VALUES (%s,%s,%s)"
    facls=[]
    for i in facultys.values():
        facls.append(i[0])
    facls=list(facls)
    for i in range(len(facls)):
        v=[facultys[i][1],facls[i],subjects[i]]
        try:
            cursor.execute(q2,v)
            print(v,' done')
            connection.commit()
        except:
            print(v)

    print("/n/n/n/n/n/n/n/n/n/n/n//n/n/n/n/n/n/n/n/n/n/n/")


    df=pd.ExcelFile(file1)
    batch=batch
    year,course,btc=batch.split(' ')
    if btc=='1':
        sets=['1','2']
    elif btc=='2':
        sets=['3','4']
    elif btc=='3':
        sets=['5','6']


    sheet1=pd.read_excel(df)
    df=pd.DataFrame(sheet1)
    
    r=dict(df.iloc[0])
    r_k=list(r.keys())

    print(r_k)

    ftte=[]
    for i in range(len(df)):
        r=dict(df.iloc[i])
        r_k=list(r.keys())
        tte=[]
        for i in range(1,len(r_k)):
            s=""
            s=s+str(r[r_k[0]])+','+str(r_k[i])+','+str(r[r_k[i]])
            tte.append(s)
        ftte.append(tte)    
    
    print("\n\n",ftte)
    
    txx=[]
    for i in range(len(ftte)):
        for j in range(len(ftte[i])):
            x=ftte[i][j].split(",")
            txx.append(x)   

    try:
        for i in range(len(txx)):
            if txx[i][2]=='nan':
                txx[i][2]=txx[i-1][2]
            elif txx[i][2]=='--':
                del txx[i]
    except:
        pass    

    try:
        for i in range(len(txx)):
            if txx[i][2]=='nan':
                txx[i][2]=txx[i-1][2]
            elif txx[i][2]=='--':
                del txx[i]
    except:
        pass





    for i in range(len(txx)):
        if '\n' in txx[i][2]:
            txx[i].extend(txx[i][2].split('\n'))
            del txx[i][2]


    for i in range(len(txx)):
        if '|' in txx[i][2]:
            x=list(txx[i])
            #print(x)
            sx="".join(txx[i][2].split("|"))
            '''for i in range(len(sx)):
                sx[i]=''.join(sx[i].split('|'))'''
            
            #print(sx)
            j1=list(x)
            j2=list(x)
            #print(j1,j2)
            j1[2]=sx
            j2[2]=sx
            #print(j1,j2)
            txx.append(j1)
            txx.append(j2)
            #print('\n\n')
            '''try:
                del txx[i]
            except:
                pass'''

    txx = [e for e in txx if '|' not in e[2]]

    for i in range(len(txx)):
        if '\n' in txx[i][2]:
            txx[i].extend(txx[i][2].split('\n'))
            del txx[i][2]
    

    
    c=0
    for i in range(len(txx)):
        if txx[i][2]=='TECHNICAL CLUB ACTIVITIES':
            c=c+1
    for i in range(c):
        for i in range(len(txx)):
            if txx[i][2]=='TECHNICAL CLUB ACTIVITIES':
                del txx[i]
                break


    
    
    to_del=[]
    for i in range(len(txx)):
        print(i,txx[i])
        try:    
            if '/' in txx[i][3]:
                vals=txx[i][3].split('/')
                to_del.append(txx[i])
                for j in range(len(vals)):
                    x_val=list(txx[i])
                    x_val[3]=vals[j]
                    txx.append(x_val)
        except Exception as e:
            print(e)
    print('\n\n\n')
    print(to_del)
    print('\n\n\n')
    for dl in to_del:
        print(dl)
        txx.remove(dl)







    tt_ins=[]
    for i in range(len(txx)):
        if 'SET'+" "+sets[1] in txx[i][2]:
            x=list(txx[i])
            x.append(course+" "+'S'+sets[1])
            tt_ins.append(x)
        elif 'SET'+" "+sets[0] in txx[i][2]:
            x=list(txx[i])
            x.append(course+" "+'S'+sets[0])
            tt_ins.append(x)


    
    for i in range(len(txx)):
        if 'SET' not in txx[i][2]:
            x=list(txx[i])
            x.append(course+" "+'S'+sets[1])
            tt_ins.append(x)
            
            x=list(txx[i])
            x.append(course+" "+'S'+sets[0])
            tt_ins.append(x)


    
    m=tu=w=th=f=0
    for i in range(len(tt_ins)):
        if 'Mon' in tt_ins[i][0]:
            m=m+1
        elif 'Tue' in tt_ins[i][0]:
            tu=tu+1
        elif 'Wed' in tt_ins[i][0]:
            w=w+1
        elif 'Thu' in tt_ins[i][0]:
            th=th+1
        elif 'Fri' in tt_ins[i][0]:
            f=f+1

    
    
    for i in range(len(tt_ins)):
        tt_ins[i].extend(tt_ins[i][1].split(' '))
        del tt_ins[i][1]


    for i in range(len(tt_ins)):
        if ('LAB' not in tt_ins[i][1]):
            tt_ins[i].extend(['idk'])

    for i in range(len(tt_ins)):
        if ('LAB' in tt_ins[i][1]):
            tt_ins[i].extend(['idk'])


    for i in range(len(tt_ins)):
        tt_ins[i][1]=" ".join((tt_ins[i][1].split(" "))[0:2])
    for i in range(len(tt_ins)):
        tt_ins[i][2]=tt_ins[i][2].split("/")[0]

    

    cls_entry = pd.DataFrame(tt_ins, columns=['day','subject','faculty','set_batch','time_in','time_out','room'])
    cls_entry=cls_entry.loc[:,['day','time_in','time_out','faculty','subject','room','set_batch']]
    tt_ins=cls_entry.values.tolist()

    for i in range(len(tt_ins)):
        tt_ins[i][6]=year+" "+tt_ins[i][6]

    import mysql.connector
    from mysql.connector import Error
    import pandas as pd
    import pyodbc
    #from flask.ext.mysql import MySQL


    def create_db_connection(host_name, user_name, user_password, db_name):
        connection = None
        try:
            connection = mysql.connector. connect (host=host_name,
                                            user=user_name,
                                            passwd=user_password,
                                                database = db_name)
            print("MySQl database connection successfull")
        except Error as err:
            print(f"Error: '{err}'")
        return connection

    pw='secret'
    db="tt_data"
    connection=create_db_connection("localhost","user",pw,db)

    cursor = connection.cursor()


    #cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)


    for i in range(len(tt_ins)):
        tt_ins[i]=tuple(tt_ins[i])

    q="INSERT INTO classes (days, tim_from, tim_to, faculty_facultyid, faculty_subject_subjectid, class_room_roomid, set_batc_batchid) VALUES (%s,%s,%s,%s,%s,%s,%s)"
    print(".....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n")
    for i in range(len(tt_ins)):
        v=tt_ins[i]
        try:
            cursor.execute(q,v)
            connection.commit()
        except Exception as e:
            print("Error inserting", v, ":", e)
    print(".....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n.....\n")
    






















if __name__ == '__main__':
    app.run(debug=True,port=8001)




















