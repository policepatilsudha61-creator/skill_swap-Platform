import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect,session
import mysql.connector

app = Flask(__name__)
app.secret_key = "skillswap123"


#db = mysql.connector.connect(
 #   host="localhost",
  #  user="root",
   # password="sudha@123",
    #database="skill_swap"
#)

#cursor = db.cursor()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        skill = request.form['skill']

        sql = """
        INSERT INTO users(name,email,password,skill)
        VALUES(%s,%s,%s,%s)
        """

        values = (name, email, password, skill)

        cursor.execute(sql, values)
        db.commit()

        return redirect('/login')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():

    error = ""

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        sql = """
        SELECT * FROM users
        WHERE email=%s AND password=%s
        """

        values = (email, password)

        cursor = db.cursor()
        cursor.execute(sql, values)

        user = cursor.fetchone()

        cursor.fetchall()

        if user:
         session['username'] = email
         print("LOGIN SUCCESS")
         print(session)
         return redirect('/dashboard')
        else:
          error = "Invalid Email or Password"

    return render_template('login.html', error=error)
@app.route('/dashboard')
def dashboard():

    if 'username' not in session:
        return redirect('/login')

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM profiles")
    total_profiles = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM requests")
    total_requests = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM requests WHERE status='Accepted'"
    )
    accepted_requests = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM requests WHERE status='Pending'"
    )
    pending_requests = cursor.fetchone()[0]

    return render_template(
        'dashboard.html',
        total_users=total_users,
        total_profiles=total_profiles,
        total_requests=total_requests,
        accepted_requests=accepted_requests,
        pending_requests=pending_requests
    )
@app.route('/browse')
def browse():

    if 'username' not in session:
        return redirect('/login')

    # existing browse code
    skill = request.args.get('skill')

    if skill:

        cursor.execute(
            "SELECT name,skill FROM profiles WHERE skill LIKE %s",
            ('%' + skill + '%',)
        )

    else:

        cursor.execute(
            "SELECT name,skill FROM profiles"
        )

    users = cursor.fetchall()

    return render_template(
        'browse.html',
        users=users
    )

@app.route('/requests')
def requests_page():

    if 'username' not in session:
        return redirect('/login')

    # existing requests code

    cursor.execute("SELECT * FROM requests")

    requests = cursor.fetchall()

    return render_template(
        'requests.html',
        requests=requests
    )
@app.route('/send_request/<receiver>')
def send_request(receiver):

    sender = "Sudha"

    sql = """
    INSERT INTO requests(sender_name, receiver_name, status)
    VALUES(%s,%s,%s)
    """

    val = (sender, receiver, "Pending")

    cursor.execute(sql, val)
    db.commit()

    cursor.execute("""
    INSERT INTO notifications(username, message)
    VALUES(%s, %s)
""", (receiver, f"{sender} sent you a skill swap request"))

    db.commit()

    return redirect('/requests')
@app.route('/accept/<int:id>')
def accept_request(id):

    sql = "UPDATE requests SET status='Accepted' WHERE id=%s"

    cursor.execute(sql, (id,))
    db.commit()

    return redirect('/requests')


@app.route('/reject/<int:id>')
def reject_request(id):

    sql = "UPDATE requests SET status='Rejected' WHERE id=%s"
    cursor.execute(sql, (id,))
    db.commit()

    return redirect('/requests')

@app.route('/myrequests')
def myrequests():

    cursor.execute(
        "SELECT * FROM requests WHERE sender='Current User'"
    )

    data = cursor.fetchall()

    return render_template(
        'myrequests.html',
        requests=data
    )
@app.route('/complete/<int:id>')
def complete_request(id):

    sql = """
    UPDATE requests
    SET status='Completed'
    WHERE id=%s
    """

    cursor.execute(sql, (id,))
    db.commit()

    return redirect('/requests')
@app.route('/logout')
def logout():

    session.clear()

    return redirect('/login')

@app.route('/history')
def history():

    if 'username' not in session:
        return redirect('/login')

    cursor.execute("""
        SELECT *
        FROM requests
        WHERE status='Completed'
        ORDER BY id DESC
    """)

    data = cursor.fetchall()

    return render_template(
        'history.html',
        requests=data
    )
@app.route('/profile', methods=['GET', 'POST'])
def profile():

    if request.method == 'POST':

        name = request.form['name']
        skill = request.form['skill']
        bio = request.form['bio']
        image = request.files['image']

        filename = ""

        if image and image.filename != "":
           filename = secure_filename(image.filename)
           image.save(os.path.join("static/uploads", filename))

        
        cursor.execute("""
    INSERT INTO profiles(name, skill, bio, image)
    VALUES (%s, %s, %s, %s)
""", (name, skill, bio, filename))
        db.commit()

    cursor.execute("""
        SELECT *
        FROM profiles
        ORDER BY id DESC
        LIMIT 1
    """)

    profile = cursor.fetchone()

    return render_template(
        'profile.html',
        profile=profile
    )
@app.route('/feedback', methods=['GET', 'POST'])
def feedback():

    if 'username' not in session:
        return redirect('/login')

    # existing feedback code

    if request.method == 'POST':

        username = request.form['username']
        feedback = request.form['feedback']
        rating = request.form['rating']

        sql = """
        INSERT INTO feedback(username, feedback, rating)
        VALUES(%s,%s,%s)
        """

        cursor.execute(sql, (username, feedback, rating))
        db.commit()

        return redirect('/dashboard')

    return render_template('feedback.html')
@app.route('/admin')
def admin():

    if 'username' not in session:
        return redirect('/login')

    # existing admin code

    # Users
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    total_users = len(users)

    # Profiles
    cursor.execute("SELECT * FROM profiles")
    profiles = cursor.fetchall()
    total_profiles = len(profiles)

    # Requests
    cursor.execute("SELECT * FROM requests")
    requests = cursor.fetchall()
    total_requests = len(requests)

    # Feedback
    cursor.execute("SELECT * FROM feedback")
    feedbacks = cursor.fetchall()
    total_feedback = len(feedbacks)

    return render_template(
        'admin.html',
        users=users,
        profiles=profiles,
        requests=requests,
        feedbacks=feedbacks,
        total_users=total_users,
        total_profiles=total_profiles,
        total_requests=total_requests,
        total_feedback=total_feedback
    )
@app.route('/delete_feedback/<int:id>')
def delete_feedback(id):

    cursor.execute(
        "DELETE FROM feedback WHERE id=%s",
        (id,)
    )

    db.commit()

    return redirect('/admin')
@app.route('/delete_user/<int:id>')
def delete_user(id):

    cursor.execute(
        "DELETE FROM users WHERE id=%s",
        (id,)
    )

    db.commit()

    return redirect('/admin')
@app.route('/delete_profile/<int:id>')
def delete_profile(id):

    cursor.execute(
        "DELETE FROM profiles WHERE id=%s",
        (id,)
    )

    db.commit()

    return redirect('/admin')
@app.route('/delete_request/<int:id>')
def delete_request(id):

    cursor.execute(
        "DELETE FROM requests WHERE id=%s",
        (id,)
    )

    db.commit()

    return redirect('/admin')
@app.route('/change_password', methods=['GET', 'POST'])
def change_password():

    message = ""

    if request.method == 'POST':

        # your password change code

        message = "Password changed successfully"

    return render_template(
        'change_password.html',
        message=message
    )
@app.route('/edit_profile/<int:id>', methods=['GET', 'POST'])
def edit_profile(id):

    if request.method == 'POST':

        name = request.form['name']
        skill = request.form['skill']
        bio = request.form['bio']

        sql = """
        UPDATE profiles
        SET name=%s, skill=%s, bio=%s
        WHERE id=%s
        """

        cursor.execute(sql, (name, skill, bio, id))
        db.commit()

        return redirect('/profile')

    cursor.execute(
        "SELECT * FROM profiles WHERE id=%s",
        (id,)
    )

    profile = cursor.fetchone()

    return render_template(
        'edit_profile.html',
        profile=profile
    )
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():

    error = ""

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        if username == "admin" and password == "admin123":
            session['admin'] = True
            return redirect('/admin')
        else:
            error = "Invalid Admin Credentials"

    return render_template('admin_login.html', error=error)

@app.route('/send_message/<receiver>', methods=['GET', 'POST'])
def send_message(receiver):

    if request.method == 'POST':

        sender = session['username']

        message = request.form['message']

        cursor.execute("""
            INSERT INTO messages(sender, receiver, message)
            VALUES (%s, %s, %s)
        """, (sender, receiver, message))

        db.commit()

        return redirect('/messages')

    return render_template(
        'send_message.html',
        receiver=receiver
    )
@app.route('/messages')
def messages():

    cursor.execute("""
        SELECT sender, receiver, message, created_at
        FROM messages
        ORDER BY created_at DESC
    """)

    data = cursor.fetchall()

    return render_template(
        'messages.html',
        messages=data
    )
@app.route('/notifications')
def notifications():

    cursor.execute("""
        SELECT *
        FROM notifications
        ORDER BY created_at DESC
    """)

    notifications = cursor.fetchall()

    return render_template(
        'notifications.html',
        notifications=notifications
    )
@app.route('/sessions', methods=['GET', 'POST'])
def sessions():

    if request.method == 'POST':

        title = request.form['title']
        skill = request.form['skill']
        description = request.form['description']
        meeting_link = request.form['meeting_link']
        session_time = request.form['session_time']

        cursor.execute("""
        INSERT INTO sessions
        (title, skill, description, meeting_link,
        session_time, created_by)

        VALUES(%s,%s,%s,%s,%s,%s)
        """,

        (
            title,
            skill,
            description,
            meeting_link,
            session_time,
            session.get('username')
        ))

        db.commit()

    cursor.execute("""
    SELECT * FROM sessions
    ORDER BY session_time DESC
    """)

    sessions = cursor.fetchall()

    return render_template(
        'sessions.html',
        sessions=sessions
    )
@app.route('/like/<int:id>')
def like_session(id):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE sessions SET likes = likes + 1 WHERE id=%s",(id,))
    mysql.connection.commit()
    return redirect('/sessions')


@app.route('/join/<int:id>')
def join_session(id):
    cur = mysql.connection.cursor()

    cur.execute(
        "UPDATE sessions SET joined_count = joined_count + 1 WHERE id=%s",
        (id,)
    )

    mysql.connection.commit()

    cur.execute(
        "SELECT meeting_link FROM sessions WHERE id=%s",
        (id,)
    )

    link = cur.fetchone()[0]

    return redirect(link)


@app.route('/comment/<int:id>', methods=['POST'])
def add_comment(id):
    comment = request.form['comment']

    cur = mysql.connection.cursor()

    cur.execute(
        "INSERT INTO comments(session_id,comment) VALUES(%s,%s)",
        (id,comment)
    )

    mysql.connection.commit()

    return redirect('/sessions')
if __name__ == '__main__':
    app.run(debug=True)