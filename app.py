from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
import json, os
from fpdf import FPDF
import pandas as pd

app = Flask(__name__)
app.secret_key = 'secret-key'

ADMIN_USERNAME = 'admin'

def load_users():
    with open('users.json', 'r') as f:
        return json.load(f)

def save_users(users):
    with open('users.json', 'w') as f:
        json.dump(users, f, indent=2)

def load_risks():
    if not os.path.exists('risks.json'):
        return []
    with open('risks.json', 'r') as f:
        return json.load(f)

def save_risks(risks):
    with open('risks.json', 'w') as f:
        json.dump(risks, f, indent=2)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = load_users()
        if username in users and users[username] == password:
            session['user'] = username
            return redirect('/dashboard')
        else:
            flash('Invalid credentials')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/')
    risks = load_risks()
    return render_template('dashboard.html', risks=risks, user=session['user'])

@app.route('/add-risk', methods=['GET', 'POST'])
def add_risk():
    if 'user' not in session:
        return redirect('/')
    if request.method == 'POST':
        new_risk = {
            'risk': request.form['risk'],
            'category': request.form['category'],
            'department': request.form['department'],
            'rating': request.form['rating'],
            'description': request.form['description']
        }
        risks = load_risks()
        risks.append(new_risk)
        save_risks(risks)
        flash('Risk added successfully')
        return redirect('/dashboard')
    return render_template('add_risk.html')

@app.route('/manage-users', methods=['GET', 'POST'])
def manage_users():
    if 'user' not in session or session['user'] != ADMIN_USERNAME:
        return redirect('/')
    users = load_users()
    if request.method == 'POST':
        action = request.form['action']
        username = request.form['username']
        password = request.form.get('password')
        if action == 'add' and username and password:
            users[username] = password
        elif action == 'delete' and username in users:
            del users[username]
        save_users(users)
        flash('User updated')
    return render_template('manage_users.html', users=users)

@app.route('/permissions')
def permissions():
    if 'user' not in session:
        return redirect('/')
    is_admin = session['user'] == ADMIN_USERNAME
    return render_template('permissions.html', user=session['user'], is_admin=is_admin)

@app.route('/export/pdf')
def export_pdf():
    risks = load_risks()
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(200, 10, 'Risk Report - Yanbu Cement Company', ln=True, align='C')
    pdf.set_font('Arial', '', 12)
    for r in risks:
        pdf.multi_cell(0, 10, f"Risk: {r['risk']}\nCategory: {r['category']}\nDepartment: {r['department']}\nRating: {r['rating']}\nDescription: {r['description']}\n")
    pdf_path = 'static/risk_report.pdf'
    pdf.output(pdf_path)
    return send_file(pdf_path, as_attachment=True)

@app.route('/export/excel')
def export_excel():
    risks = load_risks()
    df = pd.DataFrame(risks)
    path = 'static/risk_report.xlsx'
    df.to_excel(path, index=False)
    return send_file(path, as_attachment=True)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
