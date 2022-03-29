import sqlite3
import hashlib
import random
import string 

# This class is a simple handler for all of our SQL database actions
# Practicing a good separation of concerns, we should only ever call 
# These functions from our models

# If you notice anything out of place here, consider it to your advantage and don't spoil the surprise

class SQLDatabase():
    '''
        Our SQL Database

    '''

    # Get the database running
    def __init__(self, database_arg="Users.db"):
        self.conn = sqlite3.connect(database_arg)
        self.cur = self.conn.cursor()

    # SQLite 3 does not natively support multiple commands in a single statement
    # Using this handler restores this functionality
    # This only returns the output of the last command
    # def execute(self, sql_string):
    #     out = None
    #     for string in sql_string.split(";"):
    #         try:
    #             out = self.cur.execute(string)
    #         except:
    #             pass
    #     return out

    # Commit changes to the database
    # def commit(self):
    #     self.conn.commit()

    #-----------------------------------------------------------------------------
    
    # Sets up the database
    # Default admin password
    def database_setup(self, admin_password='admin1234'):

        # Clear the database if needed
        self.conn.execute("DROP TABLE IF EXISTS Users")
        self.conn.commit()

        # Create the users table
        self.cur.execute("""CREATE TABLE Users(
            Id INT,
            username TEXT,
            password TEXT,
            admin INTEGER DEFAULT 0
        )""")

        self.conn.commit()

        # Add our admin user
        self.add_user('admin', admin_password, admin=1)

    #-----------------------------------------------------------------------------
    # User handling
    #-----------------------------------------------------------------------------

    # Add a user to the database
    def add_user(self, username, password, admin=0):
        sql_cmd = """
                INSERT INTO Users
                VALUES({id}, '{username}', '{password}', {admin})
            """

        if self.check_credentials(username, password):
            print("A user already exists. Try a different username.")
            return False

        unique_id = string.ascii_letters + string.digits
        id = ''.join((random.choice(unique_id) for i in range(7)))

        hashed_pwd = hashlib.sha256(password.encode('utf-8')).hexdigest()

        sql_cmd = sql_cmd.format(id, username=username, password=hashed_pwd, admin=admin)

        self.cur.execute(sql_cmd)
        self.conn.commit()
        return True

    #-----------------------------------------------------------------------------

    # Check login credentials
    def check_credentials(self, username, password):
        sql_query = """
                SELECT 1 
                FROM Users
                WHERE username = '{username}' AND password = '{password}'
            """
        
        pwd = hashlib.sha256(password.encode('utf-8')).hexdigest()

        sql_query = sql_query.format(username=username, password=pwd)
        self.cur.execute(sql_query)

        # If our query returns
        if self.cur.fetchone():
            print("Login Successful. Welcome {}!".format(username))
            self.conn.close()
            return True
        else:
            print("Sorry, please try again.")
            return False

    
    #def show_friendlist(self, )
