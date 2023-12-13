import time
from flask import Flask, jsonify, request, render_template, redirect, url_for
import numpy as np
import pandas as pd
import pickle

app = Flask(__name__)
model = pickle.load(open('model.pkl', 'rb'))
model1 = pickle.load(open('model1.pkl', 'rb'))

# Load credentials from cred.txt
with open('static/cred.txt', 'r') as file:
    credentials = [line.strip().split() for line in file]

@app.route('/')
def welcome():
    return render_template("welcome.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        hr_id = request.form.get('hr_id')
        password = request.form.get('password')

        # Check if provided credentials match
        if [hr_id, password] in credentials:
            return redirect(url_for('prediction'))
        else:
            login_error = "*Failure to login. Please check your ID and password."
            return render_template('login.html', result=login_error)

    return render_template('login.html')

@app.route('/prediction')
def prediction():
    return render_template("index.html")

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    # Your existing prediction code remains unchanged
     if request.method == 'POST':
        time_spend_company = float(request.form["time_spend_company"])
        avg_montly_hours = float(request.form["avg_montly_hours"])
        number_project = float(request.form["number_project"])
        EMP_Engagement = float(request.form["EMP_Engagement"])
        Emp_Role = float(request.form["Emp_Role"])
        Percent_Remote = float(request.form["Percent_Remote"])/100
        EMP_Sat_Remote = float(request.form["EMP_Sat_Remote"])
        LinkedIn_Hits = float(request.form["LinkedIn_Hits"])

        x = pd.DataFrame({"Percent_Remote": [Percent_Remote], "number_project": [number_project],  "average_montly_hours": [avg_montly_hours], "time_spend_company": [time_spend_company],
                           "LinkedIn_Hits": [LinkedIn_Hits],"Emp_Role": [Emp_Role], "EMP_Sat_Remote": [EMP_Sat_Remote], "EMP_Engagement": [EMP_Engagement]})
        ml = model.predict(x)
        if ml == 1:
            x1 = pd.DataFrame({"Percent_Remote":[Percent_Remote], "number_project":[number_project]	, "average_montly_hours":[avg_montly_hours],
        	               "LinkedIn_Hits":[LinkedIn_Hits],	"Emp_Role":[Emp_Role],	"EMP_Sat_Remote":[EMP_Sat_Remote], 
                           "EMP_Engagement":[EMP_Engagement]})
            ml1 = model1.predict(x1)
            k = ml1-time_spend_company
        
            if k<=0:
                t="immediately"
            else:
                k = k.item()
                k = round(k, 1)
                t="within "+ str(k) + " years" 
            return render_template('result.html', result='The employee is more likely to leave the organization {}!'.format(t), res_Img= 'static/images/Attrition.jpg')
        else:
            g = "continue in"
            return render_template('result.html', result='The employee is more likely to {} the organization!'.format(g), res_Img= 'static/images/Retention.jpg')

if __name__ == "__main__":
    app.run(debug=True)
