import sqlite3
import hashlib

# This class is a simple handler for all of our SQL database actions
# Practicing a good separation of concerns, we should only ever call 
# These functions from our models

# If you notice anything out of place here, consider it to your advantage and don't spoil the surprise
class SQLDatabase():
    '''
        Our SQL Database

    '''

    # Get the database running
    def __init__(self, database_arg="website.db"):
        self.conn = sqlite3.connect(database_arg)
        self.cur = self.conn.cursor()
        self.salt = "mmm_salty_salt_is_salty"

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

        self.conn.execute("DROP TABLE IF EXISTS Friends")
        self.conn.commit()

        self.conn.execute("DROP TABLE IF EXISTS Messages")
        self.conn.commit()

        # Create the users table
        self.cur.execute("""CREATE TABLE Users(
            id INTEGER PRIMARY KEY,
            username VARCHAR(16),
            password CHAR(64),
            public CHAR(150),
            admin INTEGER DEFAULT 0
        )""")
        self.conn.commit()

        # Represent the Friends relation as a table.
        self.cur.execute("""CREATE TABLE Friends(
            user1 INTEGER NOT NULL REFERENCES Users(id),
            user2 INTEGER NOT NULL REFERENCES Users(id),
            CONSTRAINT PK_Friends PRIMARY KEY (user1, user2)
        )""")
        self.conn.commit()

        # Create a messages table.
        self.cur.execute("""CREATE TABLE Messages(
            sender INTEGER NOT NULL REFERENCES Users(id),
            recipient INTEGER NOT NULL REFERENCES Users(id),
            message TEXT,
            mac CHAR(44),
            vector CHAR(12),
            CONSTRAINT PK_Messages PRIMARY KEY (sender, recipient)
        )""")
        self.conn.commit()

        # Add our admin user
        self.add_user('admin', admin_password, None, admin=1)

    # Add a user to the database
    def add_user(self, username, password, public=None, admin=0):

        sql_query = """
                INSERT INTO Users(username, password, public, admin)
                VALUES('{}', '{}', '{}', {})
            """

        if self.has_user(username):
            return False

        hashed_pwd = hashlib.sha256((password+self.salt).encode('utf-8')).hexdigest()
        sql_query = sql_query.format(username, hashed_pwd, public, admin)

        self.cur.execute(sql_query)
        self.conn.commit()
        return True

    def add_friendship(self, username1, username2):

        user1 = self.get_id(username1)
        user2 = self.get_id(username2)

        if (user1 == -1 or user2 == -1):
            return False

        if (user1 == user2):
            return False

        sql_query = """
                INSERT INTO Friends(user1, user2)
                VALUES({}, {})
            """

        q1 = sql_query.format(user1, user2)
        q2 = sql_query.format(user2, user1)

        self.cur.execute(q1)
        self.conn.commit()

        self.cur.execute(q2)
        self.conn.commit()

        return True
    
    def is_friends(self, username1, username2):

        user1 = self.get_id(username1)
        user2 = self.get_id(username2)

        if (user1 == -1 or user2 == -1):
            return False

        if (user1 == user2):
            return False

        sql_query = """
                SELECT 1 
                FROM Friends
                WHERE user1 = '{}' AND user2 = '{}'
            """

        sql_query = sql_query.format(user1, user2)
        self.cur.execute(sql_query)

        # If our query returns
        if self.cur.fetchone():
            return True
        return False

    #Show a list of friends
    def show_friendlist(self, username):

        user1 = self.get_id(username)

        sql_query = """
                SELECT Users.username
                FROM Friends
                INNER JOIN Users ON Friends.user2=Users.id 
                AND user1={}
            """

        sql_query = sql_query.format(user1)

        self.cur.execute(sql_query)
        ls = self.cur.fetchall()
        friends = []
        for i in friends:
            friends.append(i[0])

        return friends

    # Check whether a username exists.
    def has_user(self, username):

        sql_query = """
                SELECT 1 
                FROM Users
                WHERE username = '{username}'
            """

        sql_query = sql_query.format(username=username)
        self.cur.execute(sql_query)

        # If our query returns
        if self.cur.fetchone():
            return True
        return False

    def get_id(self, username):

        sql_query = """
                SELECT id
                FROM Users
                WHERE username = '{username}'
            """

        sql_query = sql_query.format(username=username)
        self.cur.execute(sql_query)

        userdata = self.cur.fetchone()
        if userdata:
            return userdata[0]
        return -1        

    # Check login credentials
    def check_credentials(self, username, password):

        sql_query = """
                SELECT 1 
                FROM Users
                WHERE username = '{username}' AND password = '{password}'
            """
        
        pwd = hashlib.sha256((password+self.salt).encode('utf-8')).hexdigest()

        sql_query = sql_query.format(username=username, password=pwd)
        self.cur.execute(sql_query)

        # If our query returns
        if self.cur.fetchone():
            return True
        else:
            return False

    def close(self):
        self.conn.close()  

    def add_message(self, sender, recipient, message, mac, vector):

        sender = self.get_id(sender)
        recipient = self.get_id(recipient)

        if (sender == -1 or recipient == -1):
            return False

        if (sender == recipient):
            return False

        if (self.is_friends(sender, recipient) == False):
            return False

        sql_query = """
                INSERT INTO Messages(sender, recipient, message, mac, vector)
                VALUES({}, {}, {}, {}, {})
            """

        sql = sql_query.format(sender, recipient, message, mac, vector)

        self.cur.execute(sql)
        self.conn.commit()

        return True
