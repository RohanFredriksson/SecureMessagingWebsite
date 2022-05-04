'''
    This file will handle our typical Bottle requests and responses 
    You should not have anything beyond basic page loads, handling forms and 
    maybe some simple program logic
'''

from bottle import route, get, post, error, request, response, redirect, static_file
from json import dumps
import util
import session
import sql
import view
import random
import verify
# Initialise our views, all arguments are defaults for the template
page_view = view.View()

#-----------------------------------------------------------------------------
# Static file paths
#-----------------------------------------------------------------------------

# Allow image loading
@route('/img/<picture:path>')
def serve_pictures(picture):
    '''
        serve_pictures

        Serves images from static/img/

        :: picture :: A path to the requested picture

        Returns a static file object containing the requested picture
    '''
    return static_file(picture, root='static/img/')

#-----------------------------------------------------------------------------

# Allow CSS
@route('/css/<css:path>')
def serve_css(css):
    '''
        serve_css

        Serves css from static/css/

        :: css :: A path to the requested css

        Returns a static file object containing the requested css
    '''
    return static_file(css, root='static/css/')

#-----------------------------------------------------------------------------

# Allow javascript
@route('/js/<js:path>')
def serve_js(js):
    '''
        serve_js

        Serves js from static/js/

        :: js :: A path to the requested javascript

        Returns a static file object containing the requested javascript
    '''
    return static_file(js, root='static/js/')

#-----------------------------------------------------------------------------
# Pages
#-----------------------------------------------------------------------------

# Redirect to login
@get('/')
@get('/home')
def get_index():
    '''
        get_index
        
        Serves the index page
    '''

    if session.is_logged_in():
        # Change 'friends' html
        db = sql.SQLDatabase()
        friendlist = db.show_friendlist(session.get_username())
        db.close()
        return page_view("chat", friends=friendlist)
    return page_view("index")

@post('/')
@post('/home')
def post_chat():
    username = request.forms.get('username')
    me = session.get_username()
    db = sql.SQLDatabase()
    friendlist = db.show_friendlist(session.get_username())
    if db.is_friends(me, username):
        db.close()
        redirect('/#' + username)
    else:
        db.close()
        msg = "You are not friends with "+username+". If you'd like to chat with "+username+", please add "+username+" to your friendlist first."
        session.send_notification(msg)
        return page_view("chat", friends=friendlist)


#-----------------------------------------------------------------------------

# Display the login page
@get('/login')
def get_login():
    '''
        get_login
        
        Serves the login page
    '''

    # Use the user header if logged in.
    if session.is_logged_in():
        redirect('/')

    return page_view("login")

#-----------------------------------------------------------------------------

# Attempt the login
@post('/login')
def post_login():
    '''
        post_login
        
        Handles login attempts
        Expects a form containing 'username' and 'password' fields
    '''

    # Handle the form processing
    username = request.forms.get('username')
    password = request.forms.get('password')

    db = sql.SQLDatabase()
    if (db.check_credentials(username, password)):

        user_email = db.get_email(username)
        verification_code = verify.verify_login(user_email)

        # Store all required information to log in after verification
        s = session.get()
        s['verification_username'] = username
        s['verification_code'] = verification_code
        s['verification_password'] = None
        s['verification_email'] = None
        s['verification_public_key'] = None
        s['verification_tutor'] = None
        s['verification_admin'] = None

        db.close()
        return page_view("verify")

    db.close()
    session.send_notification("Username or password is incorrect.")
    return page_view("login")

#-----------------------------------------------------------------------------

# Display the registration page
@get('/register')
def get_register():
    '''
        get_login
        
        Serves the registration page
    '''

    return page_view("register")


# Attempt the registration
@post('/register')
def post_register():
    '''
        post_register
        
        Handles registration attempts
        Expects a form containing 'username' and 'password' fields
    '''

    # Handle the form processing
    username = request.forms.get('username')
    password = request.forms.get('password')
    email = request.forms.get('email')
    public_key = request.forms.get('public')

    if username == None or password == None or public_key == None or email == None:
        session.send_notification("Missing required information.")
        return page_view("register")

    db = sql.SQLDatabase()
    if (db.has_user(username)):
        db.close()
        session.send_notification("Username already taken. Please enter a different username.")
        return page_view("register")

    if len(username) < 4:
        db.close()
        session.send_notification("Username too short. Please enter a different username.")
        return page_view("register")

    if len(username) > 16:
        db.close()
        session.send_notification("Username too long. Please enter a different username.")
        return page_view("register")

    if not util.validate_username(username):
        db.close()
        session.send_notification("Username must be alphanumeric. Please enter a different username.")
        return page_view("register")

    if len(password) < 8:
        db.close()
        session.send_notification("Password too short. Please enter a different password.")
        return page_view("register")

    if not util.validate_password(password):
        db.close()
        session.send_notification("Invalid password characters. (A-Z,a-z,0-9,@#$%^&+=) Please enter a different password.")
        return page_view("register")

    if not util.validate_email(email):
        db.close()
        session.send_notification("E-mail address in wrong format. Please enter a valid email.")
        return page_view("register")
    

    db.close()

    verification_code = verify.verify_email(email)

    # Store all required information to register an account after verification.
    s = session.get()
    s['verification_username'] = username
    s['verification_code'] = verification_code
    s['verification_password'] = password
    s['verification_email'] = email
    s['verification_public_key'] = public_key
    s['verification_tutor'] = 0
    s['verification_admin'] = 0

    return page_view("verify")

#-----------------------------------------------------------------------------

@post('/verify')
def post_verify():
    '''
        Checks the verification code
    '''

    s = session.get()

    userinput = request.forms.get('digitcode')
    username = s['verification_username']
    code = s['verification_code']
    password = s['verification_password']
    email = s['verification_email']
    public_key = s['verification_public_key']
    tutor = s['verification_tutor']
    admin = s['verification_admin']

    if username == None:
        session.send_notification("You need to log in or register to verify!")
        redirect('/')

    #Checks for a valid user input
    if userinput == None or len(userinput) != 4 :
        session.send_notification("It must be a 4 digit code!")
        return page_view("verify")

    if userinput != code:
        session.send_notification("Failed to verify. Please try again.")
        return page_view("verify")

    db = sql.SQLDatabase()
    if db.has_user(username):
        user_id = db.get_id(username)
        session.send_notification("Welcome " + username + "!")
    else:
        db.add_user(username, password, email, public_key, tutor, admin)
        user_id = db.get_id(username)
        session.send_notification("Thank you for signing up. You are all set!")
    
    db.close()

    # Remove all things from the session now.
    s['verification_username'] = None
    s['verification_code'] = None
    s['verification_password'] = None
    s['verification_email'] = None
    s['verification_public_key'] = None
    s['verification_tutor'] = None
    s['verification_admin'] = None

    #Verification successful, user logged in
    session.login(user_id, username)
    redirect('/')
    
#-----------------------------------------------------------------------------

@get('/friends')
def get_friends():
    '''
        show_friends
        
        Serves the friends page
    '''

    # Change 'friends' html
    db = sql.SQLDatabase()
    friendlist = db.show_friendlist(session.get_username())
    db.close()
    return page_view("friends", friends=friendlist)

@post('/friends')
def post_friends():
    
    # Change 'friends' html 

    # Handle the form processing
    username = request.forms.get('username')

    db = sql.SQLDatabase()

    if username == session.get_username():
        session.send_notification("You can't add yourself silly!")
        redirect("friends")

    if db.has_user(username) and db.is_friends(session.get_username(), username) == False:
        db.add_friendship(session.get_username(), username)
        session.send_notification("User added to your friendlist!")
        db.close()
        redirect("friends")
    
    if not db.has_user(username):
        session.send_notification("User does not exist")
    else:
        session.send_notification("You are already friends with " + username)
    db.close()
    redirect("friends")

@get('/logout')
def get_logout():
    '''
        post_login
        
        Handles logout attempts
    '''
    session.logout()
    session.send_notification("Successfully logged out!")
    redirect("/")

@get('/about')
def get_about():
    '''
        get_about
        
        Serves the about page
    '''
    # Returns a random string each time
    def about_garble():
        '''
            about_garble
            Returns one of several strings for the about page
        '''
        garble = ["leverage agile frameworks to provide a robust synopsis for high level overviews.", 
        "iterate approaches to corporate strategy and foster collaborative thinking to further the overall value proposition.",
        "organically grow the holistic world view of disruptive innovation via workplace change management and empowerment.",
        "bring to the table win-win survival strategies to ensure proactive and progressive competitive domination.",
        "ensure the end of the day advancement, a new normal that has evolved from epistemic management approaches and is on the runway towards a streamlined cloud solution.",
        "provide user generated content in real-time will have multiple touchpoints for offshoring."]
        return garble[random.randint(0, len(garble) - 1)]

    return page_view("about", garble=about_garble())

@get('/profile')
def get_profile():

    if session.is_logged_in():
        return page_view("profile")
    return redirect('/login')

@get('/manage')
def manage():

    if session.is_admin():
        return page_view("manage")
    session.send_notification("You don't have permission to access this!")
    return redirect('/')

@get('/tutor')
def tutor():

    if not session.is_logged_in():
        session.send_notification("You don't have permission to access this!")
        return redirect('/')

    if session.is_tutor():
        return page_view("tutor_help")
    return page_view("user_help")


@post('/change_key')
def change_key():

    username = session.get_username()
    public = request.forms.get('public')

    if username == None or public == None:
        rv = {"status": False}
        response.content_type = 'application/json'
        return dumps(rv)

    db = sql.SQLDatabase()
    if not db.change_public_key(username, public):
        db.close()
        rv = {"status": False}
        response.content_type = 'application/json'
        return dumps(rv)

    db.close()
    rv = {"status": True}
    response.content_type = 'application/json'
    return dumps(rv)

@post('/validate_register')
def validate_register():

    # Handle the form processing
    username = request.forms.get('username')
    password = request.forms.get('password')
    email = request.forms.get('email')

    if username == None or password == None or email == None:
        rv = {"status": False}
        response.content_type = 'application/json'
        return dumps(rv)

    db = sql.SQLDatabase()
    if db.has_user(username):
        db.close()
        rv = {"status": False}
        response.content_type = 'application/json'
        return dumps(rv)
    db.close()

    if not util.validate_username(username):
        rv = {"status": False}
        response.content_type = 'application/json'
        return dumps(rv)

    if not util.validate_password(password):
        rv = {"status": False}
        response.content_type = 'application/json'
        return dumps(rv)

    if not util.validate_email(email):
        rv = {"status": False}
        response.content_type = 'application/json'
        return dumps(rv)

    rv = {"status": True}
    response.content_type = 'application/json'
    return dumps(rv)

@post('/send_message')
def send_message():

    # Check if logged in
    if not session.is_logged_in():
        rv = {"status": False}
        response.content_type = 'application/json'
        return dumps(rv)

    # Handle the form processing
    sender = session.get_username()
    recipient = request.forms.get('to')
    message = request.forms.get('message')
    mac = request.forms.get('mac')
    vector = request.forms.get('vector')

    # Check if all required elements are there.
    if recipient == None or message == None or mac == None or vector == None:
        rv = {"status": False}
        response.content_type = 'application/json'
        return dumps(rv)

    # Upload to database
    # checks if the recipient exists, is_friends, or recipient == sender
    db = sql.SQLDatabase()
    if db.add_message(sender, recipient, message, mac, vector):
        db.close()
        rv = {"status": True}
        response.content_type = 'application/json'
        return dumps(rv)
    else:
        db.close()
        rv = {"status": False}
        response.content_type = 'application/json'
        return dumps(rv)

@post('/get_messages')
def get_messages():

    # Check if logged in
    if not session.is_logged_in():
        rv = {"status": False}
        response.content_type = 'application/json'
        return dumps(rv)

    # Handle the form processing
    sender = request.forms.get('from')
    recipient = session.get_username()

    # If the sender is the recipient, return error
    if sender == recipient:
        rv = {"status": False}
        response.content_type = 'application/json'
        return dumps(rv)

    # If the users are not friends, return error.
    # This also checks if users exists.
    db = sql.SQLDatabase()
    if not db.is_friends(sender, recipient):
        db.close()
        rv = {"status": False}
        response.content_type = 'application/json'
        return dumps(rv)

    # Return all the messages.
    messages = db.get_messages(sender, recipient)
    db.close()
    rv = {"status": True, "messages": messages}
    response.content_type = 'application/json'
    return dumps(rv)

@post('/is_friends')
def is_friends():

    # Check if logged in
    if not session.is_logged_in():
        rv = {"status": False}
        response.content_type = 'application/json'
        return dumps(rv)

    # Handle the form processing
    user = request.forms.get('username')
    you = session.get_username()

    if user == None:
        rv = {"status": False}
        response.content_type = 'application/json'
        return dumps(rv)

    # Check if friends
    db = sql.SQLDatabase()
    if not db.is_friends(you, user):
        db.close()
        rv = {"status": False}
        response.content_type = 'application/json'
        return dumps(rv)

    db.close()
    rv = {"status": True}
    response.content_type = 'application/json'
    return dumps(rv)

@post('/get_public_key')
def get_public_key():

    # Check if logged in
    if not session.is_logged_in():
        rv = {"status": False}
        response.content_type = 'application/json'
        return dumps(rv)

    # Handle the form processing
    user = request.forms.get('username')
    you = session.get_username()

    if user == None:
        rv = {"status": False}
        response.content_type = 'application/json'
        return dumps(rv)

    # Check friendship
    db = sql.SQLDatabase()
    if not db.is_friends(you, user):
        db.close()
        rv = {"status": False}
        response.content_type = 'application/json'
        return dumps(rv)

    key = db.get_public_key(you, user)
    db.close()

    if (key == None):
        rv = {"status": False}
        response.content_type = 'application/json'
        return dumps(rv)

    rv = {"status": True, "public": key}
    response.content_type = 'application/json'
    return dumps(rv)

@get('/get_username')
def get_username():

    rv = {'username': session.get_username()}    
    response.content_type = 'application/json'
    return dumps(rv)

@get('/get_id')
def get_id():

    rv = {'id': session.get_id()}    
    response.content_type = 'application/json'
    return dumps(rv)

@get('/get_all_users')
def get_all_users():

    if not session.is_admin():
        rv = {"status": False}
        response.content_type = 'application/json'
        return dumps(rv)

    rv = {'status': True}
    response.content_type = 'application/json'
    return dumps(rv)

@post('/delete_user')
def delete_user():

    if not session.is_admin():
        rv = {"status": False}
        response.content_type = 'application/json'
        return dumps(rv)

    # Handle the form processing
    user = request.forms.get('username')

    db = sql.SQLDatabase()
    if db.delete_user(user):
        db.close()
        rv = {'status': False}
        response.content_type = 'application/json'
        return dumps(rv)

    db.close()
    rv = {'status': True}
    response.content_type = 'application/json'
    return dumps(rv)

# 404 errors, use the same trick for other types of errors
@error(404)
def error(error): 
    error_type = error.status_line
    error_msg = error.body
    return page_view("error", error_type=error_type, error_msg=error_msg)
