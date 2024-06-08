import string
from flask import Flask, request, render_template, redirect, url_for, make_response
import numpy as np
import pandas as pd
import pickle
import sqlite3
import os

app = Flask(__name__)

# Load models safely
model_path = 'model.pkl'
model1_path = 'model1.pkl'

if os.path.exists(model_path) and os.path.exists(model1_path):
    model = pickle.load(open(model_path, 'rb'))
    model1 = pickle.load(open(model1_path, 'rb'))
else:
    raise FileNotFoundError("Model files not found. Please check the paths.")

def is_logged_in():
    return request.cookies.get('user') is not None

@app.route('/')
def welcome():
    user_logged_in = request.cookies.get('user')
    return render_template("welcome.html", user_logged_in=user_logged_in)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if is_logged_in():
        return redirect(url_for('prediction'))
    result = None
    if request.method == 'POST':
        hr_id = request.form.get('hr_id')
        password = request.form.get('password')
        
        # Connect to the database securely
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        
        # Use parameterized queries to prevent SQL injection
        cursor.execute("SELECT * FROM Employees WHERE hr_id = ?", (hr_id,))
        search = cursor.fetchone()
        connection.close()
        
        if search is None:
            result = "Please Enter Valid HR ID"
        elif password != search[1]:
            result = "Please Enter Correct Password"
        else:
            response = make_response(redirect(url_for('prediction')))
            response.set_cookie('user', hr_id) #type:ignore
            return response
        
    return render_template("login.html", result=result)

@app.route('/prediction')
def prediction():
    if not is_logged_in():
        return redirect(url_for('login'))
    user_logged_in = request.cookies.get('user')
    return render_template("index.html", user_logged_in=user_logged_in)

@app.route('/predict', methods=['POST']) # type:ignore
def predict():
    if not is_logged_in():
        return redirect(url_for('login')) 
    if request.method == 'POST':
        try:
            time_spend_company = float(request.form["time_spend_company"])
            avg_montly_hours = float(request.form["avg_montly_hours"])
            number_project = float(request.form["number_project"])
            EMP_Engagement = float(request.form["EMP_Engagement"])
            Emp_Role = float(request.form["Emp_Role"])
            Percent_Remote = float(request.form["Percent_Remote"]) / 100
            EMP_Sat_Remote = float(request.form["EMP_Sat_Remote"])
            LinkedIn_Hits = float(request.form["LinkedIn_Hits"])

            x = pd.DataFrame({
                "Percent_Remote": [Percent_Remote],
                "number_project": [number_project],
                "average_montly_hours": [avg_montly_hours],
                "time_spend_company": [time_spend_company],
                "LinkedIn_Hits": [LinkedIn_Hits],
                "Emp_Role": [Emp_Role],
                "EMP_Sat_Remote": [EMP_Sat_Remote],
                "EMP_Engagement": [EMP_Engagement]
            })

            ml = model.predict(x)
            if ml == 1:
                x1 = pd.DataFrame({
                    "Percent_Remote": [Percent_Remote],
                    "number_project": [number_project],
                    "average_montly_hours": [avg_montly_hours],
                    "LinkedIn_Hits": [LinkedIn_Hits],
                    "Emp_Role": [Emp_Role],
                    "EMP_Sat_Remote": [EMP_Sat_Remote],
                    "EMP_Engagement": [EMP_Engagement]
                })
                ml1 = model1.predict(x1)
                k = ml1 - time_spend_company
                if k <= 0:
                    t = "immediately"
                else:
                    k = k.item()
                    k = round(k, 1)
                    t = "within " + str(k) + " years"
                return render_template('result.html', result='The employee is more likely to leave the organization {}!'.format(t), res_Img='static/images/Attrition.jpg')
            else:
                g = "continue in"
                return render_template('result.html', result='The employee is more likely to {} the organization!'.format(g), res_Img='static/images/Retention.jpg')
        except Exception as e:
            return render_template('index.html', result=f"Error: {e}")

if __name__ == "__main__":
    app.run(debug=True)
