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
            email CHAR(120),
            public CHAR(150),
            tutor INTEGER DEFAULT 0,
            admin INTEGER DEFAULT 0
        )""")
        self.conn.commit()

        # Represent the Friends relation as a table.
        self.cur.execute("""CREATE TABLE Friends(
            user1 INTEGER NOT NULL REFERENCES Users(id) ON DELETE CASCADE,
            user2 INTEGER NOT NULL REFERENCES Users(id) ON DELETE CASCADE,
            CONSTRAINT PK_Friends PRIMARY KEY (user1, user2)
        )""")
        self.conn.commit()

        # Create a messages table.
        self.cur.execute("""CREATE TABLE Messages(
            sender INTEGER NOT NULL REFERENCES Users(id) ON DELETE CASCADE,
            recipient INTEGER NOT NULL REFERENCES Users(id) ON DELETE CASCADE,
            message TEXT,
            mac CHAR(44),
            vector CHAR(16),
            timesent DATETIME,
            CONSTRAINT PK_Messages PRIMARY KEY (sender, recipient, timesent)
        )""")
        self.conn.commit()

    # Add a user to the database
    def add_user(self, username, password, email, public=None, tutor=0, admin=0):

        if public == None:

            sql_query = """
                    INSERT INTO Users(username, password, email, tutor, admin)
                    VALUES('{}', '{}', '{}', {}, {})
                """

            if self.has_user(username):
                return False

            hashed_pwd = hashlib.sha256((password+self.salt).encode('utf-8')).hexdigest()
            sql_query = sql_query.format(username, hashed_pwd, email, tutor, admin)

            self.cur.execute(sql_query)
            self.conn.commit()
            return True

        else:

            sql_query = """
                    INSERT INTO Users(username, password, email, public, tutor, admin)
                    VALUES('{}', '{}', '{}', '{}', {}, {})
                """

            if self.has_user(username):
                return False

            hashed_pwd = hashlib.sha256((password+self.salt).encode('utf-8')).hexdigest()
            sql_query = sql_query.format(username, hashed_pwd, email, public, tutor, admin)

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
        for i in ls:
            friends.append(i[0])

        if self.is_tutor(username):
            students = self.get_students(username)
            return [user for user in friends if user not in students]

        tutors = self.get_tutors()
        return [user for user in friends if user not in tutors]

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

    # Returns email address for the following user
    def get_email(self, username):

        sql_query = """
                SELECT email
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

        if (self.is_friends(sender, recipient) == False):
            return False

        sender = self.get_id(sender)
        recipient = self.get_id(recipient)

        if (sender == -1 or recipient == -1):
            return False

        if (sender == recipient):
            return False

        sql_query = """
                INSERT INTO Messages(sender, recipient, message, mac, vector, timesent)
                VALUES({}, {}, '{}', '{}', '{}', DateTime('now'))
            """

        sql = sql_query.format(sender, recipient, message, mac, vector)

        self.cur.execute(sql)
        self.conn.commit()

        return True

    def get_messages(self, sender, recipient):

        if (self.is_friends(sender, recipient) == False):
            return []

        sender = self.get_id(sender)
        recipient = self.get_id(recipient)

        if (sender == -1 or recipient == -1):
            return []

        if (sender == recipient):
            return []

        messages = []

        sql_query = """
                SELECT sender, message, mac, vector, timesent
                FROM Messages
                WHERE sender = {} AND recipient = {}
            """

        sql = sql_query.format(sender, recipient)

        self.cur.execute(sql)
        ls = self.cur.fetchall()

        for i in ls:
            messages.append({"sender": i[0], "message": i[1], "mac": i[2], "vector": i[3], "time": i[4]})

        sql_query = """
                SELECT sender, message, mac, vector, timesent
                FROM Messages
                WHERE sender = {} AND recipient = {}
            """

        sql = sql_query.format(recipient, sender)

        self.cur.execute(sql)
        ls = self.cur.fetchall()
        for i in ls:
            messages.append({"sender": i[0], "message": i[1], "mac": i[2], "vector": i[3], "time": i[4]})

        return messages

    def get_public_key(self, requester, requested):

        if (self.is_friends(requester, requested) == False):
            return None

        requester = self.get_id(requester)
        requested = self.get_id(requested)

        sql_query = """
                SELECT public
                FROM Users
                WHERE id = {}
            """

        sql = sql_query.format(requested)
        self.cur.execute(sql)

        userdata = self.cur.fetchone()[0]
        if userdata:
            return userdata
        return None

    def change_public_key(self, username, key):

        id = self.get_id(username)
        if id < 0:
            return False

        sql_query = """
                UPDATE Users
                SET public = '{}'
                WHERE id = {}
            """

        try:
            sql = sql_query.format(key, id)
            self.cur.execute(sql)
            self.conn.commit()
        except:
            return False

        return True

    def is_admin(self, username):

        sql_query = """
                SELECT 1 
                FROM USERS
                WHERE username = '{}' AND admin = 1
            """

        sql_query = sql_query.format(username)
        self.cur.execute(sql_query)

        # If our query returns
        if self.cur.fetchone():
            return True
        return False

    def is_tutor(self, username):

        sql_query = """
                SELECT 1 
                FROM USERS
                WHERE username = '{}' AND tutor = 1
            """

        sql_query = sql_query.format(username)
        self.cur.execute(sql_query)

        # If our query returns
        if self.cur.fetchone():
            return True
        return False

    def delete_user(self, username):

        sql_query = """
                DELETE 
                FROM USERS
                WHERE username = '{}'
            """

        sql_query = sql_query.format(username)
        self.cur.execute(sql_query)

        return not self.has_user(username)

    def get_students(self, tutor):

        if not self.is_tutor(tutor):
            return []

        id = self.get_id(tutor)

        sql_query = """
                SELECT Users.username
                FROM Friends
                INNER JOIN Users ON Friends.user2=Users.id 
                AND user1={}
                AND Users.tutor = 0
            """

        sql_query = sql_query.format(id)

        self.cur.execute(sql_query)
        ls = self.cur.fetchall()
        students = []
        for i in ls:
            students.append(i[0])

        return students

    def get_tutors(self):

        sql_query = """
                SELECT username
                FROM Users
                WHERE tutor = 1
            """

        self.cur.execute(sql_query)
        ls = self.cur.fetchall()
        tutors = []
        for i in ls:
            tutors.append(i[0])

        return tutors

    def get_users(self):

        sql_query = """
                SELECT username
                FROM Users
            """

        self.cur.execute(sql_query)
        ls = self.cur.fetchall()
        users = []
        for i in ls:
            users.append(i[0])

        return users

