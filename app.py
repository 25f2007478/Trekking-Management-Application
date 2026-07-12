from flask import Flask, render_template, request, redirect, url_for, session
from models import *

app = Flask(__name__)
app.config['SECRET_KEY']="trekking_app_2026"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydb.sqlite3'

db.init_app(app)

#-------- LOGIN & SIGNUP --------#

@app.route('/', methods=['GET','POST'])
def user_login():

    passed_msg = request.args.get('msg')

    if request.method == 'GET':
        return render_template('onboarding.html', user='user', msg=passed_msg)
    else:
        email = request.form.get('email')
        password = request.form.get('password') 
        curr_user = User.query.filter_by(email=email).first()
        
            
        if curr_user:
            if curr_user.role == 'Admin':
                if curr_user.password == password:
                    session['u_id'] = curr_user.user_id
                    return redirect(url_for('admin_home'))
                
            if curr_user.role != 'staff':
                if curr_user.is_approved:
                    if curr_user.password == password:
                        session['u_id'] = curr_user.user_id
                        return redirect(url_for('user_home'))
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
            if curr_user.role == 'Admin':
                if curr_user.password == password:
                    session['u_id'] = curr_user.user_id
                    return redirect(url_for('admin_home'))
            
            if curr_user.role == 'staff':
                if curr_user.is_approved:
                    if curr_user.password == password:
                        session['u_id'] = curr_user.user_id
                        return redirect(url_for('staff_home'))
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


@app.route('/logout')
def logout():
    session.pop('u_id',None)
    return redirect(url_for('user_login'))

def isadmin(u_id):
    user = User.query.get(u_id)
    if user != None and user.role == 'Admin':
        return False
    return True

def isstaff(u_id):
    user = User.query.get(u_id)
    if user != None and user.role == 'staff':
        return False
    return True


#------ADMIN FUNTIONALITIES------#

@app.route("/admin_dashboard", methods=['GET','POST'])
def admin_home():
    u_id = session.get('u_id',None)
    if isadmin(u_id):
        return redirect(url_for('user_login', msg='Unauthorised access !'))

    staff_num = User.query.filter_by(role='staff', is_approved=True).count()
    user_num = User.query.filter_by(role='trekker').count()
    trek_num = Trek.query.filter_by(status='Open').count()
    booking_num = Booking.query.filter_by(booking_status='Confirmed').count()

    recent_activity = Booking.query.order_by(Booking.id.desc()).limit(5).all()

    return render_template('admin_dashboard.html',func='home', total_staff=staff_num, total_users=user_num, active_treks=trek_num, total_bookings=booking_num, recent_activity=recent_activity)
    

@app.route('/admin_dashboard/staffs')                           
def admin_staff():
    u_id = session.get('u_id')
    if isadmin(u_id):
        return redirect(url_for('user_login', msg='Unauthorised access !'))

    active_staff= User.query.filter_by(role='staff', is_approved=True).all()
    pending_staff= User.query.filter_by(role='staff', is_approved=False).all()
    blacklisted_staff= User.query.filter_by(role='Blacklisted_staff').all()

    return render_template('admin_dashboard.html',func='staff', pending_staffs=pending_staff, active_staffs=active_staff, blacklisted_staffs=blacklisted_staff)

@app.route('/admin_dashboard/users')
def admin_user():
    u_id = session.get('u_id')
    if isadmin(u_id):
        return redirect(url_for('user_login', msg='Unauthorised access !'))
    active_user= User.query.filter_by(role='trekker', is_approved=True).all()
    blacklisted= User.query.filter_by(role='Blacklisted').all()

    return render_template('admin_dashboard.html',func='user', active_users=active_user, blacklisted=blacklisted)

@app.route('/admin_dashboard/treks')
def admin_trek():
    u_id = session.get('u_id')
    if isadmin(u_id):
        return redirect(url_for('user_login', msg='Unauthorised access !'))

    active_treks = Trek.query.filter_by(status='Open').all()
    ongoing_treks = Trek.query.filter_by(status='Ongoing').all()
    completed_treks = Trek.query.filter_by(status='Completed').all()
    cancelled_treks = Trek.query.filter_by(status='Cancelled').all()

    return render_template('admin_dashboard.html', func='trek', active_treks=active_treks, cancelled_treks=cancelled_treks, completed_treks=completed_treks, ongoing=ongoing_treks)

@app.route('/approve/<int:staff_id>', methods=['POST'])
def approve(staff_id):
    u_id = session.get('u_id')
    if isadmin(u_id):
        return redirect(url_for('user_login', msg='Unauthorised access !'))

    staff = User.query.get(staff_id)
    staff.is_approved = True

    speciality=request.form.get('speciality')

    staff_prof = StaffProfile(
        user_id=staff_id,
        speciality=speciality
    )

    db.session.add(staff_prof)
    db.session.commit()

    return redirect(url_for('admin_staff'))

@app.route('/reject/<int:staff_id>', methods=['POST'])
def fire_staff(staff_id):
    u_id = session.get('u_id')
    if isadmin(u_id):
        return redirect(url_for('user_login', msg='Unauthorised access !'))
    
    staff = User.query.get_or_404(staff_id)
    target = ''

    if staff.staff_profile:
        target = 'admin_staff'
        db.session.delete(staff.staff_profile)
    else:
        target = 'admin_user'
    
    db.session.delete(staff)
    db.session.commit()
    return redirect(url_for(target))


@app.route('/blacklist/<int:user_id>', methods=['POST'])
def blacklist(user_id):
    u_id = session.get('u_id')
    if isadmin(u_id):
        return redirect(url_for('user_login', msg='Unauthorised access !'))

    user = User.query.get(user_id)

    user.is_approved = False
    target = ''

    if user.staff_profile:
        user.staff_profile.status = 'Blacklisted'
        user.role = 'Blacklisted_staff'
        target = 'admin_staff'
    
    else:
        user.role = 'Blacklisted'
        target = 'admin_user'

    db.session.commit()

    return redirect(url_for(target))

@app.route('/unblacklist/<int:user_id>', methods=['POST'])
def unblacklist(user_id):
    u_id = session.get('u_id')
    if isadmin(u_id):
        return redirect(url_for('user_login', msg='Unauthorised access !'))

    user = User.query.get(user_id)
    target = ''
    user.is_approved = True

    if user.staff_profile:
        user.staff_profile.status = 'Available'
        user.role = 'staff'
        target = 'admin_staff'
    
    else:
        user.role = 'trekker'
        target = 'admin_user'
        
    db.session.commit()

    return redirect(url_for(target))

@app.route('/addtrek', methods=['GET','POST'])
def add_trek():
    u_id = session.get('u_id')
    if isadmin(u_id):
        return redirect(url_for('user_login', msg='Unauthorised access !'))

    if request.method == 'GET':

        active_staff= User.query.filter_by(role='staff', is_approved=True).all()
        available_staff = []
        for staff in active_staff:
            if staff.staff_profile.status == 'Available':
                available_staff.append(staff)

        return render_template('trek_add.html', available_staffs=available_staff)
    
    else:
        name = request.form.get('name')
        location = request.form.get('location')
        difficulty = request.form.get('difficulty')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        available_slots = request.form.get('available_slots')
        img = request.form.get('img')
        assigned_staff_id = request.form.get('assigned_staff')
        print(assigned_staff_id)
        new_trek = Trek(
            trek_name = name,
            location = location,
            difficulty = difficulty,
            start_date = start_date,
            end_date = end_date,
            available_slots = available_slots,
            img = img,
            assigned_staff_id = assigned_staff_id
        )

        staff = StaffProfile.query.get(assigned_staff_id)
        staff.status = 'Occupied'

        db.session.add(new_trek)
        db.session.commit()

        return redirect(url_for('admin_trek'))

@app.route('/edittrek/<int:trek_id>', methods=['GET','POST'])
def edit_trek(trek_id):

    u_id = session.get('u_id')
    if isadmin(u_id):
        return redirect(url_for('user_login', msg='Unauthorised access !'))

    curr_trek = Trek.query.filter_by(id=trek_id).first()

    if request.method == 'GET':
        
        active_staff= User.query.filter_by(role='staff', is_approved=True).all()

        return render_template('trek_edit.html', trek=curr_trek, available_staffs=active_staff)
   
    else:
    
        curr_trek.name = request.form.get('name')
        curr_trek.location = request.form.get('location')
        curr_trek.difficulty = request.form.get('difficulty')
        curr_trek.start_date = request.form.get('start_date')
        curr_trek.end_date = request.form.get('end_date')
        curr_trek.available_slots = request.form.get('available_slots')
        curr_trek.img = request.form.get('img')
        curr_trek.staff_profile.status = 'Available'
        new_staff_id = request.form.get('assigned_staff')
        curr_trek.assigned_staff_id = new_staff_id
        new_staff = StaffProfile.query.get(new_staff_id)
        if new_staff:
            new_staff.status = 'Occupied'

        db.session.commit()
        return redirect(url_for('admin_trek'))
    
@app.route('/deletetrek/<int:trek_id>', methods=['POST'])
def delete_trek(trek_id):
    u_id = session.get('u_id')
    if isadmin(u_id):
        return redirect(url_for('user_login', msg='Unauthorised access !'))

    curr_trek = Trek.query.filter_by(id=trek_id).first()

    staff_id = curr_trek.assigned_staff_id 
    curr_staff = StaffProfile.query.get(staff_id)
    if curr_staff:
        curr_staff.status = 'Available'

    curr_trek.status = 'Cancelled'

    db.session.commit()

    return redirect(url_for('admin_trek'))

@app.route('/admin_dashboard/bookings')
def admin_booking():
    u_id = session.get('u_id')
    if isadmin(u_id):
        return redirect(url_for('user_login', msg='Unauthorised access !'))
    
    bookings = Booking.query.all()
    
    return render_template('admin_dashboard.html', func='bookings', bookings=bookings)


#--------STAFF FUNCTIONALITIES--------#

@app.route('/staff_dashboard', methods=['GET'])
def staff_home():
    u_id = session.get('u_id',None)
    if isstaff(u_id):
        return redirect(url_for('user_login', msg='Unauthorised access !'))
    
    staff = StaffProfile.query.filter_by(user_id=u_id).first() 
    completed_treks = Trek.query.filter_by(assigned_staff_id=staff.id, status='Completed').count()
    assigned_treks = Trek.query.filter_by(assigned_staff_id=staff.id).all()
    participants = 0
    for trek in assigned_treks:
        participants += Booking.query.filter_by(trek_id=trek.id).count()

    next_trek = Trek.query.filter(
        Trek.assigned_staff_id == staff.id,
        Trek.status.in_(['Open', 'Ongoing'])
    ).first()
    

    return render_template('staff_dashboard.html', total_treks_completed=completed_treks, total_participants_managed=participants, next_trek=next_trek)

@app.route('/staff_dashboard/treks', methods=['GET','POST'])
def staff_treks():
    u_id = session.get('u_id',None)
    if isstaff(u_id):
        return redirect(url_for('user_login', msg='Unauthorised access !'))
    
    staff = StaffProfile.query.filter_by(user_id=u_id).first()
    
    assigned_treks = Trek.query.filter_by(assigned_staff_id=staff.id).first()
    
    if request.method == 'GET':

        return render_template('staff_dashboard.html', func='trek', trek=assigned_treks)
    
    else:
        action_clicked = request.form.get('action')

        if action_clicked == 'UpdateSlots':
            slots = request.form.get('available_slots')
            assigned_treks.available_slots = int(slots)
        
        elif action_clicked == 'Start':
            assigned_treks.status = 'Ongoing'
        
        elif action_clicked == 'Complete':
            assigned_treks.status = 'Completed'
            staff.status = 'Available'

        db.session.commit()
        return redirect(url_for('staff_treks'))


@app.route('/staff_dashboard/trek/history', methods=['GET'])
def trek_history():

    u_id = session.get('u_id',None)
    if isstaff(u_id):
        return redirect(url_for('user_login', msg='Unauthorised access !'))
    
    staff = StaffProfile.query.filter_by(user_id=u_id).first()

    trek = Trek.query.filter_by(assigned_staff_id=staff.id, status='Completed').all()

    return render_template('staff_dashboard.html', func='history', trek_hist=trek)


@app.route('/staff_dashboard/participants', methods=['GET'])
def staff_users():
    u_id = session.get('u_id',None)
    if isstaff(u_id):
        return redirect(url_for('user_login', msg='Unauthorised access !'))
    
    staff = StaffProfile.query.filter_by(user_id=u_id).first() 
    assigned_treks = Trek.query.filter_by(assigned_staff_id=staff.id).first()
    booked = Booking.query.filter_by(trek_id=assigned_treks.id).all()

    return render_template('staff_dashboard.html', func='participants', bookings=booked)


@app.route('/staff_dashboard/profile', methods=['GET'])
def staff_profile():
    u_id = session.get('u_id',None)
    if isstaff(u_id):
        return redirect(url_for('user_login', msg='Unauthorised access !')) 
    
    if request.method == 'GET':
        user = User.query.filter_by(user_id=u_id).first()

        return render_template('staff_dashboard.html', func='Profile', current_user=user)
    
        
@app.route('/profile/edit',methods=['GET','POST'])
def edit_profile():
    u_id = session.get('u_id',None)
    if not u_id:
        return redirect(url_for('user_login', msg='Login first !'))
    
    user = User.query.filter_by(user_id=u_id).first()
    
    if request.method == 'GET':
        if user.role == 'staff':
            return render_template('edit-profile.html', role='base_staff.html', user=user)
        else:
            return render_template('edit-profile.html', role='base_user.html', user=user)
        
    else:
        user.name = request.form.get('name')
        user.email = request.form.get('email')
        user.password = request.form.get('password')
        user.dob = request.form.get('dob')
        user.gender = request.form.get('gender')
        user.mobile = request.form.get('mobile')

        db.commit()

        if user.role == 'staff':
            return redirect(url_for('staff_profile'))
        
        return redirect(url_for('user_profile'))
        

#--------USER FUNCTIONALITIES--------#

@app.route('/user_dashboard')
def user_home():
    u_id = session.get('u_id',None)
    if u_id is None:
        return redirect(url_for('user_login', msg='Unauthorised access !')) 
    
    bookings = Booking.query.filter_by(user_id=u_id, booking_status='Confirmed').all()
    com_trek = 0
    for book in bookings:

        if book.trek.status == 'Completed':
            com_trek += 1
    
    total_booking = Booking.query.filter_by(user_id=u_id, booking_status='Confirmed').count() 
    pending_booking = Booking.query.filter_by(user_id=u_id, booking_status='Pending').count()
    ongoing_treks= Trek.query.filter_by(status='Open').count()

    return render_template('user_dashboard.html', total_treks=com_trek, total_bookings=total_booking, pending_bookings=pending_booking, bookings=bookings, ongoing_treks=ongoing_treks)

@app.route('/user/treks', methods=['GET','POST'])
def user_treks():
    u_id = session.get('u_id',None)
    if u_id is None:
        return redirect(url_for('user_login', msg='Unauthorised access !')) 

    if request.method == 'GET':
        treks = Trek.query.filter_by(status='Open').all()

        passed_msg = request.args.get('msg')
                
        return render_template('user_dashboard.html', func='open_trek', treks=treks, msg=passed_msg)

@app.route('/trek/book/<int:trek_id>', methods=['POST'])
def book_treks(trek_id):
    u_id = session.get('u_id',None)
    if u_id is None:
        return redirect(url_for('user_login', msg='Unauthorised access !')) 
    
    trek = Trek.query.filter_by(id=trek_id).first()

    book = Booking.query.filter_by(trek_id=trek_id, user_id=u_id).first()

    if book:
        return redirect(url_for('user_treks', msg='You have already booked for '+ trek.trek_name +'. Please check the Booking tab.'))

    else:
        if trek.available_slots != 0:
            book = Booking(
                user_id = u_id,
                trek_id = trek_id,
            )

            trek.available_slots -= 1

            db.session.add(book)
            db.session.commit()

            return redirect(url_for('user_treks', msg='Your have been temporarily allocated a slot for '+ trek.trek_name +'. Please make the necessary payments to confirm your booking in the Booking tabs.'))


        else:
            return redirect(url_for('user_treks', msg='All Slots for '+ trek.trek_name +' are filled. Please contact the Admin or the respective staff for assistance.'))
            

@app.route('/user/treks/history', methods=['GET'])
def user_history():
    u_id = session.get('u_id',None)
    if u_id is None:
        return redirect(url_for('user_login', msg='Unauthorised access !')) 

    if request.method == 'GET':
        treks = Trek.query.all()
        booking = Booking.query.filter_by(user_id=u_id, booking_status='Confirmed').all()

        his_trek = []
        for trek in treks:
            for book in booking:
                if trek.id == book.trek_id:
                    his_trek.append(trek)
                
        return render_template('user_dashboard.html', func='trek_history', completed_treks=his_trek)
    
@app.route('/user/bookings', methods=['GET'])
def user_bookings():
    u_id = session.get('u_id',None)
    if u_id is None:
        return redirect(url_for('user_login', msg='Unauthorised access !')) 
    
    bookings = Booking.query.filter_by(user_id=u_id).all()
    return render_template('user_dashboard.html', func='bookings', bookings=bookings)

@app.route('/user/profile', methods=['GET'])
def user_profile():
    u_id = session.get('u_id',None)
    if u_id is None:
        return redirect(url_for('user_login', msg='Unauthorised access !')) 
    
    user = User.query.filter_by(user_id=u_id).first()

    return render_template('user_dashboard.html', func='Profile', current_user=user)

@app.route('/user/bookings/<booking_id>/confirm', methods=['POST'])
def confirm_booking(booking_id):
    book = Booking.query.filter_by(id=booking_id).first()
    book.booking_status = 'Confirmed'
    trek = Trek.query.filter_by(id=book.trek_id).first()

    db.session.commit()

    return redirect(url_for('user_bookings', msg='Your booking for '+ trek.trek_name+ ' is Confirmed'))

@app.route('/user/bookings/<booking_id>/cancel', methods=['POST'])
def cancel_booking(booking_id):
    book = Booking.query.filter_by(id=booking_id).first()
    trek = Trek.query.filter_by(id=book.trek_id).first()
    trek.available_slots += 1
    db.session.delete(book)
    db.session.commit()

    return redirect(url_for('user_bookings', msg='Your booking for '+ trek.trek_name+ ' is Cancelled'))





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