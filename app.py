from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)
app.secret_key = 'ashraf_secret_key_123' 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///exam.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)
    opt_a = db.Column(db.String(200), nullable=False)
    opt_b = db.Column(db.String(200), nullable=False)
    opt_c = db.Column(db.String(200), nullable=False)
    opt_d = db.Column(db.String(200), nullable=False)
    ans = db.Column(db.String(200), nullable=False)

# ইউজারের ডাটাবেস টেবিল থেকে ফোন নম্বর বাদ দেওয়া হয়েছে
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)

with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        
        user = User.query.filter_by(email=email).first()
        if not user:
            # নতুন ইউজার হলে শুধু নাম ও ইমেইল সেভ করবে
            user = User(name=name, email=email)
            db.session.add(user)
            db.session.commit()
            
        session['user_id'] = user.id
        session['user_name'] = user.name
        return redirect(url_for('user_dash'))
    return render_template('index.html')

@app.route('/user_dash')
def user_dash():
    if 'user_id' not in session:
        return redirect(url_for('user_login'))
    return render_template('user_dash.html', name=session['user_name'])

@app.route('/exam', methods=['POST'])
def exam():
    if 'user_id' not in session:
        return redirect(url_for('user_login'))
    
    q_count = int(request.form['q_count'])
    time_limit = int(request.form['time_limit'])
    
    all_questions = Question.query.all()
    if len(all_questions) < q_count:
        flash(f'দুঃখিত! ডাটাবেসে মাত্র {len(all_questions)} টি প্রশ্ন আছে।')
        return redirect(url_for('user_dash'))
        
    selected_questions = random.sample(all_questions, q_count)
    return render_template('exam.html', questions=selected_questions, time_limit=time_limit)

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'ashraf123':
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dash'))
        else:
            flash('ভুল ইউজারনেম বা পাসওয়ার্ড!')
    return render_template('admin_login.html')

@app.route('/admin_dash', methods=['GET', 'POST'])
@app.route('/admin_dash', methods=['GET', 'POST'])
def admin_dash():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
        
    if request.method == 'POST':
        text = request.form['text']
        opt_a = request.form['opt_a']
        opt_b = request.form['opt_b']
        opt_c = request.form['opt_c']
        opt_d = request.form['opt_d']
        ans = request.form['ans']
        
        new_q = Question(text=text, opt_a=opt_a, opt_b=opt_b, opt_c=opt_c, opt_d=opt_d, ans=ans)
        db.session.add(new_q)
        db.session.commit()
        flash('Proshno shofolvabe jog kora hoyeche!')
        
    questions = Question.query.all()
    # Nicher line ti notun add kora hoyeche database theke user der data anar jonno
    users = User.query.all() 
    
    return render_template('admin_dash.html', questions=questions, users=users)

@app.route('/delete_q/<int:id>')
def delete_q(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    q = Question.query.get_or_404(id)
    db.session.delete(q)
    db.session.commit()
    flash('প্রশ্ন মুছে ফেলা হয়েছে!')
    return redirect(url_for('admin_dash'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('user_login'))

if __name__ == '__main__':
    app.run(debug=True)