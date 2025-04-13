import flask
import pickle
import pandas as pd
import numpy as np
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

from sklearn.preprocessing import StandardScaler


#load models at top of app to load into memory only one time
with open('models/loan_application_model_lr.pickle', 'rb') as f:
    clf_lr = pickle.load(f)


# with open('models/knn_regression.pkl', 'rb') as f:
#     knn = pickle.load(f)    
ss = StandardScaler()


genders_to_int = {'MALE':1,
                  'FEMALE':0}

married_to_int = {'YES':1,
                  'NO':0}

education_to_int = {'GRADUATED':1,
                  'NOT GRADUATED':0}

dependents_to_int = {'0':0,
                      '1':1,
                      '2':2,
                      '3+':3}

self_employment_to_int = {'YES':1,
                          'NO':0}                      

property_area_to_int = {'RURAL':0,
                        'SEMIRURAL':1, 
                        'URBAN':2}

#priya code
bank_to_int = {
    'ICICI': 0,   # You can assign any number or category value
    'SBI': 1,
    'Canara': 2,
    'Hindustan': 3
}
#priya code
app = flask.Flask(__name__, template_folder='templates')

app.secret_key = '12345'
# Connect to MySQL
mydb1 = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="mydb"
)

@app.route('/')
def main():
    return (flask.render_template('index.html'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mydb1.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()

        if user and check_password_hash(user['password'], password):
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')

def create_db_and_table():
    try:
        # Connect to MySQL server (without specifying database)
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password=""
        )
        cursor = mydb.cursor()

        # Create database if it doesn't exist
        cursor.execute("CREATE DATABASE IF NOT EXISTS mydb")
        mydb.commit()
        
        # Use the database
        cursor.execute("USE mydb")

        # Create the users table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                mobile VARCHAR(15),
                email VARCHAR(100)
            )
        """)
        mydb.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        mydb.close()


@app.route('/register', methods=['GET', 'POST'])
def register():
    create_db_and_table()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        mobile = request.form['mobile']
        email = request.form['email']
        
        # Ensure connection is established inside the function
        mydb1 = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="mydb"
        )
        cursor = mydb1.cursor()
        
        try:
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    mobile VARCHAR(15),
                    email VARCHAR(100)
                )
            """)
            cursor.execute("INSERT INTO users (username, password, mobile, email) VALUES (%s, %s, %s, %s)", 
                           (username, hashed_password, mobile, email))
            
            mydb1.commit()
            session['username'] = username
            return redirect(url_for('dashboard'))
        except mysql.connector.Error as err:
            print(f"Error: {err}")  # Debugging info
            return render_template('register.html', error='Error registering user')
        finally:
            cursor.close()
            mydb1.close()  # Close connection after execution

    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        username = session['username']
        return render_template('index1.html', username=username)
    return redirect(url_for('login'))

@app.route('/report')
def report():
    return (flask.render_template('report.html'))

@app.route('/jointreport')
def jointreport():
    return (flask.render_template('jointreport.html'))


@app.route("/Loan_Application", methods=['GET', 'POST'])
def Loan_Application():
    
    if flask.request.method == 'GET':
        result = session.pop('result', None)
        original_input = session.pop('original_input', None)
        return (flask.render_template('Loan_Application.html', result=result, original_input=original_input))
    
    if flask.request.method == 'POST':
        try:
            # Get input fields from form
            genders_type = flask.request.form['genders_type']
            marital_status = flask.request.form['marital_status']
            dependents = flask.request.form['dependents']
            education_status = flask.request.form['education_status']
            self_employment = flask.request.form['self_employment']
            
            # Parse numeric fields with error handling
            try:
                applicantIncome = float(flask.request.form['applicantIncome'])
                coapplicantIncome = float(flask.request.form['coapplicantIncome'])
                loan_amnt = float(flask.request.form['loan_amnt'])
                term_d = int(flask.request.form['term_d'])
                credit_history = int(flask.request.form['credit_history'])
            except ValueError as e:
                return flask.render_template('Loan_Application.html', 
                                           error='Please enter valid numeric values for income, loan amount, and term.')
            
            property_area = flask.request.form['property_area']
            
            # Check if loan_bank exists in the form
            if 'loan_bank' in flask.request.form:
                selected_bank = flask.request.form['loan_bank']
                bank_code = bank_to_int.get(selected_bank, -1)
            else:
                selected_bank = "Not selected"
                bank_code = -1
                
            # Create output dictionary for display
            output_dict = dict()
            output_dict['Applicant Income'] = applicantIncome
            output_dict['Co-Applicant Income'] = coapplicantIncome
            output_dict['Loan Amount'] = loan_amnt
            output_dict['Loan Amount Term'] = term_d
            output_dict['Credit History'] = credit_history
            output_dict['Gender'] = genders_type
            output_dict['Marital Status'] = marital_status
            output_dict['Education Level'] = education_status
            output_dict['No of Dependents'] = dependents
            output_dict['Self Employment'] = self_employment
            output_dict['Property Area'] = property_area
            output_dict['Bank Loan'] = selected_bank
            
            # Set up the feature array for prediction
            # Note: Your model was trained to expect 21 features, but you're only using 5
            # This is a potential source of errors if your model actually needs all 21 features
            x = np.zeros(21)
            
            # Fill in the basic features
            x[0] = applicantIncome
            x[1] = coapplicantIncome
            x[2] = loan_amnt
            x[3] = term_d
            x[4] = credit_history
            
            # Add additional categorical features if your model needs them
            # For example:
            x[5] = genders_to_int.get(genders_type, -1)
            x[6] = married_to_int.get(marital_status, -1)
            x[7] = education_to_int.get(education_status, -1)
            x[8] = dependents_to_int.get(dependents, -1)
            x[9] = self_employment_to_int.get(self_employment, -1)
            x[10] = property_area_to_int.get(property_area, -1)
            x[11] = bank_code
            
            # Add logging to help debug
            print('------this is array data to predict-------')
            print('X = '+str(x))
            print('------------------------------------------')
            
            # Make prediction
            pred = clf_lr.predict([x])[0]
            
            if pred == 1:
                res = 'Congratulations! your Loan Application has been Approved!'
            else:
                res = 'Unfortunately your Loan Application has been Denied'
            
            session['result'] = res
            session['original_input'] = output_dict

            # Render form again and add prediction
            return flask.render_template('Loan_Application.html', 
                                        original_input=session['original_input'],
                                        result=session['result'])
                                        
        except Exception as e:
            # Log the error and return an error message
            print(f"Error in form processing: {e}")
            return flask.render_template('Loan_Application.html', 
                                        error=f"An error occurred: {str(e)}")

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))
        
        
      
if __name__ == '__main__':
    app.run(debug=True)