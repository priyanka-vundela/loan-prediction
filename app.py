from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

app = Flask(__name__, template_folder='templates')
app.secret_key = '12345'

# Connect to MySQL (ensure your Render environment can access this)
mydb1 = mysql.connector.connect(
    host="localhost",  # Update if your database is hosted elsewhere
    user="root",       # Update with your database user
    password="",       # Update with your database password
    database="mydb"    # Update with your database name
)

def create_db_and_table():
    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password=""
        )
        cursor = mydb.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS mydb")
        mydb.commit()
        cursor.execute("USE mydb")
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
        print(f"Error creating DB/table: {err}")
    finally:
        if 'cursor' in locals() and cursor.is_connected():
            cursor.close()
        if 'mydb' in locals() and mydb.is_connected():
            mydb.close()

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            cursor = mydb1.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            cursor.close()

            if user and check_password_hash(user['password'], password):
                session['username'] = username
                return redirect(url_for('dashboard'))
            else:
                return render_template('login.html', error='Invalid username or password')
        except mysql.connector.Error as err:
            print(f"Error during login: {err}")
            return render_template('login.html', error='Database error during login')
        finally:
            if 'cursor' in locals() and cursor.is_connected():
                cursor.close()
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    create_db_and_table()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        mobile = request.form['mobile']
        email = request.form['email']

        try:
            cursor = mydb1.cursor()
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            cursor.execute("INSERT INTO users (username, password, mobile, email) VALUES (%s, %s, %s, %s)",
                           (username, hashed_password, mobile, email))
            mydb1.commit()
            session['username'] = username
            return redirect(url_for('dashboard'))
        except mysql.connector.Error as err:
            print(f"Error during registration: {err}")
            return render_template('register.html', error='Error registering user')
        finally:
            if 'cursor' in locals() and cursor.is_connected():
                cursor.close()
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        username = session['username']
        return render_template('index1.html', username=username)
    return redirect(url_for('login'))

@app.route('/report')
def report():
    return render_template('report.html')

@app.route('/jointreport')
def jointreport():
    return render_template('jointreport.html')

@app.route("/Loan_Application", methods=['GET', 'POST'])
def Loan_Application():
    # ... (rest of your Loan_Application route code remains the same)
    if request.method == 'GET':
        result = session.pop('result', None)
        original_input = session.pop('original_input', None)
        return render_template('Loan_Application.html', result=result, original_input=original_input)

    if request.method == 'POST':
        try:
            genders_type = request.form['genders_type']
            marital_status = request.form['marital_status']
            dependents = request.form['dependents']
            education_status = request.form['education_status']
            self_employment = request.form['self_employment']

            try:
                applicantIncome = float(request.form['applicantIncome'])
                coapplicantIncome = float(request.form['coapplicantIncome'])
                loan_amnt = float(request.form['loan_amnt'])
                term_d = int(request.form['term_d'])
                credit_history = int(request.form['credit_history'])
            except ValueError as e:
                return render_template('Loan_Application.html',
                                           error='Please enter valid numeric values for income, loan amount, and term.')

            property_area = request.form['property_area']

            if 'loan_bank' in request.form:
                selected_bank = request.form['loan_bank']
                bank_code = bank_to_int.get(selected_bank, -1)
            else:
                selected_bank = "Not selected"
                bank_code = -1

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

            x = np.zeros(21)
            x[0] = applicantIncome
            x[1] = coapplicantIncome
            x[2] = loan_amnt
            x[3] = term_d
            x[4] = credit_history
            x[5] = genders_to_int.get(genders_type, -1)
            x[6] = married_to_int.get(marital_status, -1)
            x[7] = education_to_int.get(education_status, -1)
            x[8] = dependents_to_int.get(dependents, -1)
            x[9] = self_employment_to_int.get(self_employment, -1)
            x[10] = property_area_to_int.get(property_area, -1)
            x[11] = bank_code

            print('------this is array data to predict-------')
            print('X = '+str(x))
            print('------------------------------------------')

            pred = clf_lr.predict([x])[0]

            if pred == 1:
                res = 'Congratulations! your Loan Application has been Approved!'
            else:
                res = 'Unfortunately your Loan Application has been Denied'

            session['result'] = res
            session['original_input'] = output_dict

            return render_template('Loan_Application.html',
                                        original_input=session['original_input'],
                                        result=session['result'])

        except Exception as e:
            print(f"Error in form processing: {e}")
            return render_template('Loan_Application.html',
                                        error=f"An error occurred: {str(e)}")

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)