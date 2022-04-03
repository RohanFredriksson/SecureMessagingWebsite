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
    return page_view("index")

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
        session.login(id, username)
        db.close()
        session.send_notification("Welcome " + username + "!")
        redirect('/')

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
    public_key = request.forms.get('public')

    if username == None or password == None or public_key == None:
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
    
    db.add_user(username, password, public_key, 0)
    db.close()
    session.login(id, username)
    session.send_notification("Welcome " + username + "!")
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
    if len(friendlist) > 0:
        string = """
        <div class="content" style="width: 400px; height: 300px; margin-top: 100px;">
        <div style="margin-left: 40px; padding-top: 24px; width: 320px; height: 100%"><ul>\n"""
        string += "\n".join(["<li>" + str(i) + "</li>" for i in friendlist])
        string += "\n</div>\n</div>\n</ul>\n</center>"
    
        f = open("templates/friends.html", "w")
        f.write("""
        <center>
        <div class="content" style="width: 400px; height: 300px; margin-top: 100px;">
            <div style="margin-left: 40px; padding-top: 24px; width: 320px; height: 100%">
                <p style="margin:0;">Search a friend</p>
                <form action="/friends" method="post">
                <label><center><input style="height: 40px; width:250px;" name="username" type="text" placeholder="Enter username" required/></center></label>
                <label><center><input style="height: 40px; width:250px;" value="Add" type="submit"/></center></label>
                </form>
            </div>
        </div>
        
        """ + string)
        f.close()

    return page_view("friends")

@post('/friends')
def post_friends():
    
    # Change 'firends' html 


    # Handle the form processing
    username = request.forms.get('username')

    db = sql.SQLDatabase()
    if db.has_user(username) and db.is_friends(session.get_username(), username) == False:
        #print(session.get_username())
        db.add_friendship(session.get_username(), username)
        session.send_notification("User added to your friendlist!")
        print(db.show_friendlist(get_username))
        db.close()
        
        return redirect("friends")
    db.close()
    session.send_notification("User already a friend or user does not exist")
    return page_view("friends")


@get('/logout')
def get_logout():
    '''
        post_login
        
        Handles logout attempts
    '''
    f = open("templates/friends.html", "w")
    f.write("""
    <center>
    <div class="content" style="width: 400px; height: 300px; margin-top: 100px;">
        <div style="margin-left: 40px; padding-top: 24px; width: 320px; height: 100%">
            <p style="margin:0;">Search a friend</p>
            <form action="/friends" method="post">
            <label><center><input style="height: 40px; width:250px;" name="username" type="text" placeholder="Enter username" required/></center></label>
            <label><center><input style="height: 40px; width:250px;" value="Add" type="submit"/></center></label>
            </form>
        </div>
    </div>
    </center>
    """)
    f.close()
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

@route('/chat')
def get_chat():
    '''
        get_chat
        
        Serves the chat page
    '''

    if session.is_logged_in():
        return page_view("chat")
    return redirect('/login')

@route('/profile')
def get_chat():
    '''
        get_chat
        
        Serves the chat page
    '''

    if session.is_logged_in():
        return page_view("profile")
    return redirect('/login')

@post('/validate_register')
def validate_register():

    # Handle the form processing
    username = request.forms.get('username')
    password = request.forms.get('password')

    if username == None or password == None:
        rv = {"status": False}
        response.content_type = 'application/json'
        return dumps(rv)

    db = sql.SQLDatabase()
    if (db.has_user(username)):
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

    rv = {"status": True}
    response.content_type = 'application/json'
    return dumps(rv)

@get('/get_username')
def get_username():

    rv = {'username': session.get_username()}    
    response.content_type = 'application/json'
    return dumps(rv)

# 404 errors, use the same trick for other types of errors
@error(404)
def error(error): 
    error_type = error.status_line
    error_msg = error.body
    return page_view("error", error_type=error_type, error_msg=error_msg)
