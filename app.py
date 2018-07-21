from flask import Flask, render_template, flash, redirect, session, url_for, request
from flask_mysqldb import MySQL
from functools import wraps

app = Flask(__name__)

# config database
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'live_chat'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)


@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for("chat"))
    return render_template("home.html")

@app.route('/user_init',methods=['POST'])
def user_init():
    if request.form['username'].strip() != '':
        session['username'] = request.form['username']
        flash('Start Chatting', 'success')
        return redirect(url_for('chat'))
    else:
        flash('Invalid username, try again','danger')
        return redirect(url_for('home'))


def has_entered_name(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'username' in session:
            return f(*args, **kwargs)
        else:
            flash("Unauthorized, Please Enter Name to Proceed", "danger")
            return redirect(url_for('home'))
    return wrap


@app.route('/chat')
@has_entered_name
def chat():
    # PERFORM MYSQL QUERY
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM chatter")
    chats = cur.fetchall()
    cur.close()
    # CLOSE CONNECTION
    if result > 0:
        return render_template('chat.html', chats=chats)
    else:
        return render_template('chat.html', msg="s")


@app.route('/send_message',methods=['POST'])
@has_entered_name
def send_message():
    username = session['username']
    message = request.form['message']
    if request.form['message'].strip() == '':
        flash('Invalid message, try again','danger')
        return redirect(url_for('chat'))
    # PERFORM MYSQL QUERY
    cur = mysql.connection.cursor()
    cur.execute(
        'INSERT INTO chatter(username,message) VALUES(%s,%s)', (username, message))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('chat'))

@app.route('/delete',methods=['POST'])
def delete():
    if request.method == "POST":
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM chatter')
        mysql.connection.commit()
        cur.close()
    return redirect(url_for('chat'))

if __name__ == "__main__":
    app.secret_key = "secretla"
    app.run(debug=True, host='0.0.0.0')
