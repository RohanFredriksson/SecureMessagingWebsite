from bottle import request

def is_logged_in():
    current_session = request.environ.get('beaker.session')
    if 'logged_in' in current_session:
        if current_session['logged_in'] == True:
            return True
    return False

def login(id, username):
    current_session = request.environ.get('beaker.session')
    current_session['user_id'] = id
    current_session['username'] = username
    current_session['logged_in'] = True

def logout():
    current_session = request.environ.get('beaker.session')
    current_session['user_id'] = None
    current_session['username'] = None
    current_session['logged_in'] = False

def has_notification():
    current_session = request.environ.get('beaker.session')
    if 'notification' in current_session:
        if current_session['notification'] != None:
            return True
    return False

def get_notification():
    current_session = request.environ.get('beaker.session')
    if 'notification' in current_session:
        if current_session['notification'] != None:
            return current_session['notification']
    return None

def clear_notification():
    current_session = request.environ.get('beaker.session')
    current_session['notification'] = None

def send_notification(message: str):
    current_session = request.environ.get('beaker.session')
    current_session['notification'] = message

def get_username():
    current_session = request.environ.get('beaker.session')
    return current_session['username']

def get_id():
    current_session = request.environ.get('beaker.session')
    return current_session['user_id']

def get():
    return request.environ.get('beaker.session')