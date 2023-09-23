from flask import Flask, render_template, request,url_for,redirect,session;
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__)
app.secret_key = 'Bait3273'

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
studentTable = 'student'
companyTable = 'company'

#pages
@app.route("/")
def Register():
    return render_template('Login.html')

@app.route("/Home")
def Home():
    if 'user' in session:
        return render_template('index.html')
    else:
        return redirect(url_for('Login'))

@app.route("/Signup")
def Signup():
    return render_template('SignUp.html')

@app.route("/Login")
def Login():
    return render_template('Login.html')

@app.route("/Documents")
def Documents():
    if 'user' in session:
        return render_template('Documents.html')
    else:
        return redirect(url_for('Login'))

@app.route("/UploadDocument", methods=['POST'])
def UploadDocument():
    if 'user' in session:
        userId = session['user'][0]
        userName = session['user'][1]
        userStudentId = session['user'][2]
        resume = request.files['resume-pdf-upload']
        indemnity = request.files['indemnity-pdf-upload']
        company = request.files['company-pdf-upload']
        parent = request.files['parent-pdf-upload']
        cursor = db_conn.cursor()
        insert_sql = "INSERT INTO leave_application (Employee_ID, Submission_Date, Reason_of_Leave, Total_Day) VALUES (%s, %s, %s, %s)"
        #if resume.filename != "":
        try:
            resume_name_in_s3 = userName + "_" + userStudentId + "_resume"
            parent_name_in_s3 = userName + "_" + userStudentId + "_parent"
            indemnity_name_in_s3 = userName + "_" + userStudentId + "_indemnity"
            company_name_in_s3 = userName + "_" + userStudentId + "_company"
            s3 = boto3.resource('s3')

   

            try:
                print('pass0')
                bucket = s3.Bucket(custombucket)

                # Upload objects to the S3 bucket
                bucket.put_object(Key=resume_name_in_s3, Body=resume)
                bucket.put_object(Key=company_name_in_s3, Body=company)
                bucket.put_object(Key=indemnity_name_in_s3, Body=indemnity)
                bucket.put_object(Key=parent_name_in_s3, Body=parent)
                print('pass1')
                bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
                s3_location = (bucket_location['LocationConstraint'])
                print('pass2')
                if s3_location is None:
                    s3_location = ''
                else:
                    s3_location = '-' + s3_location

                print('pass3')
                object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                    s3_location,
                    custombucket,
                    resume_name_in_s3)

            except Exception as e:
                return str(e)

        finally:
            cursor.close()

    else:
        return redirect(url_for('Login'))

@app.route("/Profile")
def Profile():
    if 'user' in session:
        return render_template('Profile.html',user=session["user"])
    else:
        return redirect(url_for('Login'))
    

@app.route("/CompanyDetailsPage/<string:id>")
def CompanyDetailsPage(id):
    cursor = db_conn.cursor()
    getById_sql = "SELECT * FROM company WHERE id=%s"
    cursor.execute(getById_sql,(id))
    company = cursor.fetchone()
    cursor.close()
    return render_template('CompanyDetailsPage.html',company=company)


#function
@app.route("/RegisterStudent", methods=['POST'])
def RegisterStudent():
    stud_name = request.form['name']
    stud_id = request.form['studentID']
    stud_email= request.form['email']
    stud_cohort = request.form['cohort']
    stud_programme = request.form['programme']
    stud_cgpa = request.form['cgpa']
    stud_ucSupervisor = request.form['ucSupervisor']
    stud_ucEmail = request.form['ucEmail']

    insert_sql = "INSERT INTO " + studentTable + " (stud_name,stud_id,stud_email,cohort,stud_programme,cgpa,stud_supervisor,supervisor_email)" + " VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()
    try:

        cursor.execute(insert_sql, (stud_name,stud_id,stud_email,stud_cohort,stud_programme,stud_cgpa,stud_ucSupervisor,stud_ucEmail))
        db_conn.commit()
    finally:
        cursor.close()
    print("all modification done...")
    return redirect(url_for('home'))
   
    
@app.route("/LoginStudent", methods=['POST'])
def LoginStudent():
    login_email = request.form['email']
    login_password = request.form['password']
    
    search_sql = "SELECT * FROM " + studentTable + " WHERE stud_email=%s AND password=%s"
    
    cursor = db_conn.cursor()
    cursor.execute(search_sql, (login_email,login_password))

    student = cursor.fetchone()
    cursor.close()  

    if student:
        session["user"] = student
        print("Login success")

    else:
        print("Login failed")

    return redirect(url_for('Home'))

@app.route("/Logout")
def Logout():
    session.pop('user', None)
    return redirect(url_for('Login'))

@app.route("/Company")
def Company():
    getAllCompany_sql = "SELECT * FROM " + companyTable 
    
    cursor = db_conn.cursor()
    cursor.execute(getAllCompany_sql)

    companies = cursor.fetchall()
    cursor.close()  

    return render_template('Company.html',companies=companies)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)

