from flask import Flask, render_template, request, redirect, url_for
from models import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydb.sqlite3'

db.init_app(app)

################# LOGIN & SIGNUP ###################

@app.route('/', methods=['GET','POST'])
def user_login():
    if request.method == 'GET':
        return render_template('onboarding.html', user='user')
    else:
        email = request.form.get('email')
        password = request.form.get('password') 
        curr_user = User.query.filter_by(email=email).first()
        if curr_user.role == 'Admin':
            if curr_user.password == password:
                return redirect(url_for('admin_dashboard'))
            
        if curr_user:
            if curr_user.role != 'staff':
                if curr_user.is_approved:
                    if curr_user.password == password:
                        return render_template('onboarding.html', user='user', msg='Redirecting')
                    else:
                        return render_template('onboarding.html', user='user', msg='Incorrect password !')
                else:
                    return render_template('onboarding.html',user='user', msg="Access denied!, Contact Admin")
            else:
                return render_template('onboarding.html', user='user', msg="Staff can't login here !")
        else:
            return render_template('onboarding.html', user='user', msg='Email not registered !')
                

@app.route('/staff_login', methods=['GET','POST'])
def staff_login():
    if request.method == 'GET':
        return render_template('onboarding.html', user='staff')

    else:
        email = request.form.get('email')
        password = request.form.get('password') 
        curr_user = User.query.filter_by(email=email).first()
        if curr_user:
            if curr_user.role == 'staff':
                if curr_user.is_approved:
                    if curr_user.password == password:
                        return render_template('onboarding.html', user='staff', msg='Redirecting')
                    else:
                        return render_template('onboarding.html', user='staff', msg='Incorrect password !')
                else:
                    return render_template('onboarding.html',user='staff', msg="Wait for Admin approval !")
            else:
                return render_template('onboarding.html', user='staff', msg="Customers can't login here !")
        else:
            return render_template('onboarding.html', user='staff', msg='Email not registered !')

@app.route('/signup', methods=['GET','POST'])
def user_signup():
    if request.method == 'GET':
        return render_template('onboarding.html', user='new_user')

    else:
        full_name = request.form.get('name')
        gender = request.form.get('gender')
        dob = request.form.get('dob')
        email = request.form.get('email')
        password = request.form.get('password')

        user_exist = User.query.filter_by(email=email).first()
        if user_exist:
            return render_template('onboarding.html', user='new_user',msg='Email already registered !')
            
        new_user = User(
            name=full_name,
            gender=gender,
            dob=dob,
            email=email,
            password=password,
            role='trekker'
        )
        
        db.session.add(new_user)
        db.session.commit()

        return render_template('onboarding.html', user='user',msg='Account created successfully !')
    

@app.route('/staff_apply', methods=['GET','POST'])
def staff_apply():
    if request.method == 'GET':
        return render_template('onboarding.html', user='new_staff')

    else:
        full_name = request.form.get('name')
        gender = request.form.get('gender')
        dob = request.form.get('dob')
        m_no = request.form.get('m_no.')
        email = request.form.get('email')
        password = request.form.get('password')

        staff_exist = User.query.filter_by(email=email).first()
        if staff_exist:
            return render_template('onboarding.html', user='new_user',msg='Cannot apply more than once !')
            
        new_staff = User(
            name=full_name,
            gender=gender,
            dob=dob,
            m_no=m_no,
            email=email,
            password=password,
            role='staff',
            is_approved=False
        )
        
        db.session.add(new_staff)
        db.session.commit()

        return render_template('onboarding.html', user='staff',msg='Application successful, Wait for Admin approval !')
    











if __name__ == '__main__':
    with app.app_context():
        db.create_all() 
        
        admin_exists = User.query.filter_by(role='Admin').first()
    
        if not admin_exists:
            default_admin = User(
                email='admin@gmail.com',
                password='admin_password',
                role='Admin',
                gender='male',
                dob='2007-01-25',
                name='System Administrator'
            )
            db.session.add(default_admin)
            db.session.commit()
    app.run(debug=True) 