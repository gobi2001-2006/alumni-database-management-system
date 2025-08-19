from flask import Flask, render_template, request, redirect, url_for, session, flash
import oracledb
from datetime import datetime
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)

app.secret_key = '2006'

# Oracle DB connection details
dsn = "localhost/XEPDB1"

def get_connection():
    return oracledb.connect(user="system", password="2006", dsn=dsn)

# Decorator to check login for protected routes
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash("Please login first.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT username, password, role FROM users WHERE username=:username",
                    {'username': username}
                )
                user = cursor.fetchone()

        if user and check_password_hash(user[1], password):
            session['username'] = user[0]
            session['role'] = user[2]
            flash("Login successful!", "success")
            return redirect(url_for('home'))
        else:
            flash("Invalid credentials", "danger")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully", "info")
    return redirect(url_for('login'))

@app.route('/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        role = request.form['role'].strip()

        hashed_password = generate_password_hash(password)

        try:
            with get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO users (username, password, role)
                        VALUES (:username, :password, :role)
                    """, {'username': username, 'password': hashed_password, 'role': role})
                    connection.commit()
            flash('User added successfully!', 'success')
            return redirect(url_for('home'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('add_user'))

    return render_template('add_user.html')

@app.route('/add_alumni', methods=['GET', 'POST'])
@login_required
def add_alumni():
    if request.method == 'POST':
        data = {
            'register_number': request.form['register_number'].strip(),
            'name': request.form['name'].strip(),
            'graduation_year': int(request.form['graduation_year']),
            'department': request.form['department'].strip(),
            'branch': request.form['branch'].strip(),
            'contact': request.form['contact'].strip(),
            'linkedin_id': request.form.get('linkedin_id', '').strip() or None,
            'city': request.form['city'].strip()
        }
        try:
            with get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO alumni (
                            register_number, name, graduation_year, department, branch,
                            contact, linkedin_id, city
                        ) VALUES (
                            :register_number, :name, :graduation_year, :department, :branch,
                            :contact, :linkedin_id, :city
                        )
                    """, data)
                    connection.commit()
            flash("Alumni added successfully", "success")
            return redirect(url_for('home'))
        except Exception as e:
            flash(f"Error: {str(e)}", "danger")
            return redirect(url_for('add_alumni'))

    return render_template('add_alumni.html')

@app.route('/add_employment', methods=['GET', 'POST'])
@login_required
def add_employment():
    if request.method == 'POST':
        data = {
            'employment_id': request.form['employment_id'].strip(),
            'register_number': request.form['register_number'].strip(),
            'company_name': request.form['company_name'].strip(),
            'job_title': request.form['job_title'].strip(),
            'past_experiences': request.form['past_experiences'].strip()
        }
        try:
            with get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO employment (employment_id, register_number, company_name, job_title, past_experiences)
                        VALUES (:employment_id, :register_number, :company_name, :job_title, :past_experiences)
                    """, data)
                    connection.commit()
            flash("Employment details added successfully!", "success")
            return redirect(url_for('home'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('add_employment'))

    return render_template('add_employment.html')

@app.route('/add_event', methods=['GET', 'POST'])
@login_required
def add_event():
    if request.method == 'POST':
        data = {
            'event_id': request.form['event_id'].strip(),
            'event_name': request.form['event_name'].strip(),
            'event_date': request.form['event_date'].strip(),  # expect 'YYYY-MM-DD'
            'location': request.form['location'].strip(),
            'description': request.form['description'].strip()
        }
        try:
            with get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO events (event_id, event_name, event_date, location, description)
                        VALUES (:event_id, :event_name, TO_DATE(:event_date, 'YYYY-MM-DD'), :location, :description)
                    """, data)
                    connection.commit()
            flash("Event added successfully!", "success")
            return redirect(url_for('home'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('add_event'))

    return render_template('add_event.html')

@app.route('/add_eventattendance', methods=['GET', 'POST'])
@login_required
def add_eventattendance():
    if request.method == 'POST':
        data = {
            'event_id': request.form['event_id'].strip(),
            'register_number': request.form['register_number'].strip(),
            'status': request.form['status'].strip()
        }
        try:
            with get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO event_attendance (event_id, register_number, status)
                        VALUES (:event_id, :register_number, :status)
                    """, data)
                    connection.commit()
            flash("Attendance recorded successfully!", "success")
            return redirect(url_for('home'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('add_eventattendance'))

    return render_template('add_eventattendance.html')

@app.route('/add_contributions', methods=['GET', 'POST'])
@login_required
def add_contributions():
    if request.method == 'POST':
        data = {
            'contribution_id': request.form['contribution_id'].strip(),
            'register_number': request.form['register_number'].strip(),
            'amount': float(request.form['amount']),
            'contribution_date': request.form['contribution_date'].strip(),
            'event_id': request.form['event_id'].strip()
        }
        try:
            with get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO contributions (contribution_id, register_number, amount, contribution_date, event_id)
                        VALUES (:contribution_id, :register_number, :amount, TO_DATE(:contribution_date, 'YYYY-MM-DD'), :event_id)
                    """, data)
                    connection.commit()
            flash("Contribution added successfully!", "success")
            return redirect(url_for('home'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('add_contributions'))

    return render_template("add_contributions.html")

@app.route('/add_mentorship', methods=['GET', 'POST'])
@login_required
def add_mentorship():
    if request.method == 'POST':
        data = {
            'program_id': request.form['program_id'].strip(),
            'register_number': request.form['register_number'].strip(),
            'purpose': request.form['purpose'].strip(),
            'total_attended': int(request.form['total_attended']),
            'start_date': request.form['start_date'].strip(),
            'end_date': request.form['end_date'].strip()
        }
        try:
            with get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO mentorship (
                            program_id, register_number, purpose, total_attended, start_date, end_date
                        ) VALUES (
                            :program_id, :register_number, :purpose, :total_attended, TO_DATE(:start_date, 'YYYY-MM-DD'), TO_DATE(:end_date, 'YYYY-MM-DD')
                        )
                    """, data)
                    connection.commit()
            flash("Mentorship program added successfully!", "success")
            return redirect(url_for('home'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('add_mentorship'))

    return render_template('add_mentorship.html')


# ==== UPDATE ROUTES WITH LOGIN REQUIRED AND HANDLING NONE ====

@app.route('/update_personal_details', methods=['GET', 'POST'])
@login_required
def update_personal_details():
    register_number = request.args.get('register_number')
    if not register_number:
        flash("No register number provided", "danger")
        return redirect(url_for('home'))

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT name, graduation_year, department, branch, contact, linkedin_id, city
                FROM alumni WHERE register_number=:register_number
            """, {'register_number': register_number})
            alumni_record = cursor.fetchone()

    if not alumni_record:
        flash("No alumni record found", "warning")
        return redirect(url_for('home'))

    if request.method == 'POST':
        if 'delete' in request.form:
            try:
                with get_connection() as connection:
                    with connection.cursor() as cursor:
                        cursor.execute("DELETE FROM alumni WHERE register_number=:register_number", {'register_number': register_number})
                        connection.commit()
                flash("Alumni record deleted", "warning")
                return redirect(url_for('home'))
            except Exception as e:
                flash(f"Error deleting record: {str(e)}", "danger")
                return redirect(url_for('update_personal_details', register_number=register_number))
        else:
            updated_data = {
                'name': request.form['name'].strip(),
                'graduation_year': int(request.form['graduation_year']),
                'department': request.form['department'].strip(),
                'branch': request.form['branch'].strip(),
                'contact': request.form['contact'].strip(),
                'linkedin_id': request.form.get('linkedin_id', '').strip() or None,
                'city': request.form['city'].strip(),
                'register_number': register_number
            }
            try:
                with get_connection() as connection:
                    with connection.cursor() as cursor:
                        cursor.execute("""
                            UPDATE alumni
                            SET name=:name, graduation_year=:graduation_year, department=:department, branch=:branch,
                                contact=:contact, linkedin_id=:linkedin_id, city=:city
                            WHERE register_number=:register_number
                        """, updated_data)
                        connection.commit()
                flash("Alumni details updated successfully", "success")
                return redirect(url_for('update_personal_details', register_number=register_number))
            except Exception as e:
                flash(f'Error updating record: {str(e)}', 'danger')
                return redirect(url_for('update_personal_details', register_number=register_number))

    return render_template('update_personal_details.html', alumni_record=alumni_record)


@app.route('/update_employment_details', methods=['GET', 'POST'])
@login_required
def update_employment_details():
    register_number = request.args.get('register_number')
    if not register_number:
        flash("No register number provided", "danger")
        return redirect(url_for('home'))

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT company_name, job_title, past_experiences FROM employment WHERE register_number=:register_number
            """, {'register_number': register_number})
            employment_record = cursor.fetchone()

    if not employment_record:
        flash("No employment record found", "warning")
        return redirect(url_for('home'))

    if request.method == 'POST':
        if 'delete' in request.form:
            try:
                with get_connection() as connection:
                    with connection.cursor() as cursor:
                        cursor.execute("DELETE FROM employment WHERE register_number=:register_number", {'register_number': register_number})
                        connection.commit()
                flash("Employment record deleted", "warning")
                return redirect(url_for('home'))
            except Exception as e:
                flash(f"Error deleting record: {str(e)}", "danger")
                return redirect(url_for('update_employment_details', register_number=register_number))
        else:
            updated_data = {
                'company_name': request.form['company_name'].strip(),
                'job_title': request.form['job_title'].strip(),
                'past_experiences': request.form['past_experiences'].strip(),
                'register_number': register_number
            }
            try:
                with get_connection() as connection:
                    with connection.cursor() as cursor:
                        cursor.execute("""
                            UPDATE employment
                            SET company_name=:company_name, job_title=:job_title, past_experiences=:past_experiences
                            WHERE register_number=:register_number
                        """, updated_data)
                        connection.commit()
                flash("Employment record updated", "success")
                return redirect(url_for('update_employment_details', register_number=register_number))
            except Exception as e:
                flash(f'Error updating record: {str(e)}', 'danger')
                return redirect(url_for('update_employment_details', register_number=register_number))

    return render_template('update_employment_details.html', employment_record=employment_record)


@app.route('/update_mentorship_details', methods=['GET', 'POST'])
@login_required
def update_mentorship_details():
    # Fixed to use program_id and register_number as key identifiers, per original schema
    program_id = request.args.get('program_id')
    register_number = request.args.get('register_number')

    if not program_id or not register_number:
        flash("No mentorship program id or register number provided", "danger")
        return redirect(url_for('home'))

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT purpose, total_attended, start_date, end_date
                FROM mentorship WHERE program_id=:program_id AND register_number=:register_number
            """, {'program_id': program_id, 'register_number': register_number})
            mentorship_record = cursor.fetchone()

    if not mentorship_record:
        flash("No mentorship record found", "warning")
        return redirect(url_for('home'))

    if request.method == 'POST':
        if 'delete' in request.form:
            try:
                with get_connection() as connection:
                    with connection.cursor() as cursor:
                        cursor.execute(
                            "DELETE FROM mentorship WHERE program_id=:program_id AND register_number=:register_number",
                            {'program_id': program_id, 'register_number': register_number}
                        )
                        connection.commit()
                flash("Mentorship record deleted", "warning")
                return redirect(url_for('home'))
            except Exception as e:
                flash(f"Error deleting record: {str(e)}", "danger")
                return redirect(url_for('update_mentorship_details', program_id=program_id, register_number=register_number))
        else:
            updated_data = {
                'purpose': request.form['purpose'].strip(),
                'total_attended': int(request.form['total_attended']),
                'start_date': request.form['start_date'].strip(),
                'end_date': request.form['end_date'].strip(),
                'program_id': program_id,
                'register_number': register_number
            }
            try:
                with get_connection() as connection:
                    with connection.cursor() as cursor:
                        cursor.execute("""
                            UPDATE mentorship
                            SET purpose=:purpose, total_attended=:total_attended,
                                start_date=TO_DATE(:start_date, 'YYYY-MM-DD'),
                                end_date=TO_DATE(:end_date, 'YYYY-MM-DD')
                            WHERE program_id=:program_id AND register_number=:register_number
                        """, updated_data)
                        connection.commit()
                flash("Mentorship record updated", "success")
                return redirect(url_for('update_mentorship_details', program_id=program_id, register_number=register_number))
            except Exception as e:
                flash(f'Error updating record: {str(e)}', 'danger')
                return redirect(url_for('update_mentorship_details', program_id=program_id, register_number=register_number))

    return render_template('update_mentorship_details.html', mentorship_record=mentorship_record)

@app.route('/update_contributions_details', methods=['GET', 'POST'])
@login_required
def update_contributions_details():
    contribution_id = request.args.get('contribution_id')
    if not contribution_id:
        flash("No contribution id provided", "danger")
        return redirect(url_for('home'))

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT register_number, event_id, amount, contribution_date
                FROM contributions WHERE contribution_id=:contribution_id
            """, {'contribution_id': contribution_id})
            contribution_record = cursor.fetchone()

    if not contribution_record:
        flash("No contribution record found", "warning")
        return redirect(url_for('home'))

    if request.method == 'POST':
        if 'delete' in request.form:
            try:
                with get_connection() as connection:
                    with connection.cursor() as cursor:
                        cursor.execute("DELETE FROM contributions WHERE contribution_id=:contribution_id", {'contribution_id': contribution_id})
                        connection.commit()
                flash("Contribution deleted", "warning")
                return redirect(url_for('home'))
            except Exception as e:
                flash(f"Error deleting record: {str(e)}", "danger")
                return redirect(url_for('update_contributions_details', contribution_id=contribution_id))
        else:
            updated_data = {
                'register_number': request.form['register_number'].strip(),
                'event_id': request.form['event_id'].strip(),
                'amount': float(request.form['amount']),
                'contribution_date': request.form['contribution_date'].strip(),
                'contribution_id': contribution_id
            }
            try:
                with get_connection() as connection:
                    with connection.cursor() as cursor:
                        cursor.execute("""
                            UPDATE contributions
                            SET register_number=:register_number, event_id=:event_id, amount=:amount,
                                contribution_date=TO_DATE(:contribution_date, 'YYYY-MM-DD')
                            WHERE contribution_id=:contribution_id
                        """, updated_data)
                        connection.commit()
                flash("Contribution updated", "success")
                return redirect(url_for('update_contributions_details', contribution_id=contribution_id))
            except Exception as e:
                flash(f'Error updating record: {str(e)}', 'danger')
                return redirect(url_for('update_contributions_details', contribution_id=contribution_id))

    return render_template('update_contributions_details.html', contribution_record=contribution_record)

@app.route('/update_event_details', methods=['GET', 'POST'])
@login_required
def update_event_details():
    event_id = request.args.get('event_id')
    if not event_id:
        flash("No event id provided", "danger")
        return redirect(url_for('home'))

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT event_name, TO_CHAR(event_date, 'YYYY-MM-DD'), location, description FROM events WHERE event_id=:event_id
            """, {'event_id': event_id})
            event_record = cursor.fetchone()

    if not event_record:
        flash("No event record found", "warning")
        return redirect(url_for('home'))

    if request.method == 'POST':
        if 'delete' in request.form:
            try:
                with get_connection() as connection:
                    with connection.cursor() as cursor:
                        cursor.execute("DELETE FROM events WHERE event_id=:event_id", {'event_id': event_id})
                        connection.commit()
                flash("Event deleted", "warning")
                return redirect(url_for('home'))
            except Exception as e:
                flash(f"Error deleting event: {str(e)}", "danger")
                return redirect(url_for('update_event_details', event_id=event_id))
        else:
            updated_data = {
                'event_name': request.form['event_name'].strip(),
                'event_date': request.form['event_date'].strip(),
                'location': request.form['location'].strip(),
                'description': request.form['description'].strip(),
                'event_id': event_id
            }
            try:
                with get_connection() as connection:
                    with connection.cursor() as cursor:
                        cursor.execute("""
                            UPDATE events
                            SET event_name=:event_name, event_date=TO_DATE(:event_date, 'YYYY-MM-DD'),
                                location=:location, description=:description
                            WHERE event_id=:event_id
                        """, updated_data)
                        connection.commit()
                flash("Event updated", "success")
                return redirect(url_for('update_event_details', event_id=event_id))
            except Exception as e:
                flash(f'Error updating event: {str(e)}', 'danger')
                return redirect(url_for('update_event_details', event_id=event_id))

    return render_template('update_event_details.html', event_record=event_record)

@app.route('/update_event_attendance', methods=['GET', 'POST'])
@login_required
def update_event_attendance():
    register_number = request.args.get('register_number')
    if not register_number:
        flash("No register number provided", "danger")
        return redirect(url_for('home'))

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT event_id, status FROM event_attendance WHERE register_number=:register_number
            """, {'register_number': register_number})
            attendance_record = cursor.fetchone()

    if not attendance_record:
        flash("No attendance record found", "warning")
        return redirect(url_for('home'))

    if request.method == 'POST':
        if 'delete' in request.form:
            try:
                with get_connection() as connection:
                    with connection.cursor() as cursor:
                        cursor.execute("DELETE FROM event_attendance WHERE register_number=:register_number", {'register_number': register_number})
                        connection.commit()
                flash("Attendance record deleted", "warning")
                return redirect(url_for('home'))
            except Exception as e:
                flash(f"Error deleting attendance record: {str(e)}", "danger")
                return redirect(url_for('update_event_attendance', register_number=register_number))
        else:
            updated_data = {
                'event_id': request.form['event_id'].strip(),
                'status': request.form['status'].strip(),
                'register_number': register_number
            }
            try:
                with get_connection() as connection:
                    with connection.cursor() as cursor:
                        cursor.execute("""
                            UPDATE event_attendance
                            SET event_id=:event_id, status=:status
                            WHERE register_number=:register_number
                        """, updated_data)
                        connection.commit()
                flash("Attendance record updated", "success")
                return redirect(url_for('update_event_attendance', register_number=register_number))
            except Exception as e:
                flash(f'Error updating attendance: {str(e)}', 'danger')
                return redirect(url_for('update_event_attendance', register_number=register_number))

    return render_template('update_event_attendance.html', attendance_record=attendance_record)


if __name__ == '__main__':
    app.run(debug=True)
