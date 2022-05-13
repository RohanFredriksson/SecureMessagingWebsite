'''
    This is a file that configures how your server runs
    You may eventually wish to have your own explicit config file
    that this reads from.

    For now this should be sufficient.

    Keep it clean and keep it simple, you're going to have
    Up to 5 people running around breaking this constantly
    If it's all in one file, then things are going to be hard to fix

    If in doubt, `import this`
'''

#-----------------------------------------------------------------------------
import os
import sys
import bottle
from bottle import run

from beaker.middleware import SessionMiddleware
session_options = {
    'session.type': 'file',
    'session.data_dir': './session/',
    'session.auto': True,
}
middleware = SessionMiddleware(bottle.app(), session_options)
session = bottle.request.environ.get('beaker.session')

#-----------------------------------------------------------------------------
# You may eventually wish to put these in their own directories and then load 
# Each file separately

# For the template, we will keep them together

import view
import routes

#-----------------------------------------------------------------------------

# It might be a good idea to move the following settings to a config file and then load them
# Change this to your IP address or 0.0.0.0 when actually hosting
host = '127.0.0.1'

# Test port, change to the appropriate port to host
port = 8081

# Turn this off for production
debug = True

def run_server():    
    '''
        run_server
        Runs a bottle server
    '''
    run(host=host, port=port, debug=debug, app=middleware)

#-----------------------------------------------------------------------------
# Optional SQL support
# Comment out the current manage_db function, and 
# uncomment the following one to load an SQLite3 database

import sql
    
def reset_db():
    '''
        manage_db
        Starts up and re-initialises an SQL databse for the server
    '''
    db = sql.SQLDatabase()
    db.database_setup()
    db.add_user('AdminAlex', 'AdminAlex', 'rohan.fredriksson@gmail.com', public=None, tutor=0, admin=1)
    db.add_user('TutorTim', 'TutorTim', 'rohan.fredriksson@gmail.com', public=None, tutor=1, admin=0)
    db.add_user('StudentSam', 'StudentSam', 'rohan.fredriksson@gmail.com', public=None, tutor=0, admin=0)
    db.add_user('StudentSandra', 'StudentSandra', 'rohan.fredriksson@gmail.com', public=None, tutor=0, admin=0)
    db.add_user('RohanFredriksson', 'RohanFredriksson', 'rohan.fredriksson@gmail.com', public=None, tutor=0, admin=0)
    db.close()
    return

#-----------------------------------------------------------------------------

# What commands can be run with this python file
# Add your own here as you see fit

command_list = {
    'reset_db' : reset_db,
    'server'   : run_server
}

# The default command if none other is given
default_command = 'server'

def run_commands(args):
    '''
        run_commands
        Parses arguments as commands and runs them if they match the command list

        :: args :: Command line arguments passed to this function
    '''
    commands = args[1:]

    # Default command
    if len(commands) == 0:
        commands = [default_command]

    for command in commands:
        if command in command_list:
            command_list[command]()
        else:
            print("Command '{command}' not found".format(command=command))

#-----------------------------------------------------------------------------

run_commands(sys.argv)
