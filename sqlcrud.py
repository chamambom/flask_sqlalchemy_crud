from database import init_db
from database import db_session
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from models import User

app = Flask(__name__)
app.config.update(dict(
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


@app.before_request
def before_request():
    print 'before_request'


@app.teardown_request
def teardown_request(exception):
    print 'teardown_request'


@app.route('/')
def show_entries():
    users_query = db_session.query(User)
    entries = [dict(id=user.id, name=user.name, email=user.email, description=user.description) for user in users_query]

    # print entries

    return render_template('show_entries.html', entries=entries)


@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)

    u = User(request.form['name'], request.form['email'], request.form['description'])
    db_session.add(u)
    db_session.commit()

    flash('New User was successfully posted')
    return redirect(url_for('show_entries'))


@app.route('/edit_entry/<int:user_id>')
def edit_entry(user_id):
    id = str(user_id)
    users = db_session.query(User).filter(User.id == id).first()

    return render_template('edit.html', users=users)


@app.route('/update/<int:user_id>', methods=['GET', 'POST'])
def update_entry(user_id):
    id = str(user_id)
    u = db_session.query(User).filter(User.id == id).first()

    u.name = request.form['name']
    u.email = request.form['email']
    u.description = request.form['description']
    # u.description = 'my description'
    db_session.commit()

    return redirect(url_for('show_entries'))


@app.route('/delete/<int:user_id>')
def delete_entry(user_id):
    id = str(user_id)
    u = db_session.query(User).filter(User.id == id)

    u.delete()
    db_session.commit()

    flash('Selected User was successfully deleted')
    return redirect(url_for('show_entries'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))


if __name__ == '__main__':
    init_db()
    app.run(debug=True)