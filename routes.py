'''
    This file will handle our typical Bottle requests and responses 
    You should not have anything beyond basic page loads, handling forms and 
    maybe some simple program logic
'''

from bottle import route, get, post, error, request, redirect, static_file
#import model
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

    # Get the session
    session = request.environ.get('beaker.session')
    if 'logged_in' in session:
        if session['logged_in'] == True:
            redirect('/about')

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
    
    # Get the session.
    session = request.environ.get('beaker.session')

    db = sql.SQLDatabase()
    if (db.check_credentials(username, password)):
        session['id'] = db.get_id(username)
        session['username'] = username
        session['logged_in'] = True
        db.close()
        return page_view("valid", name=username)

    db.close()
    return page_view("invalid", reason="invalid")

#-----------------------------------------------------------------------------

@get('/logout')
def get_logout():
    '''
        post_login
        
        Handles logout attempts
    '''

    # Get the session.
    session = request.environ.get('beaker.session')

    if 'logged_in' in session:
        if session['logged_in'] == True:
            session.delete()
            redirect('/')
    return page_view("invalid", reason="not logged in")

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

# 404 errors, use the same trick for other types of errors
@error(404)
def error(error): 
    error_type = error.status_line
    error_msg = error.body
    return page_view("error", error_type=error_type, error_msg=error_msg)
