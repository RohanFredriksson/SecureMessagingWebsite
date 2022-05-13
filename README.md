## Overview ##

## Changing Default User Database

Go into run.py and edit the code in the reset_db function. It should look something like this.
```python
db = sql.SQLDatabase()
db.database_setup()
db.add_user('AdminAlex', 'AdminAlex', 'rohan.fredriksson@gmail.com', public=None, tutor=0, admin=1)
db.add_user('TutorTim', 'TutorTim', 'rohan.fredriksson@gmail.com', public=None, tutor=1, admin=0)
db.add_user('StudentSam', 'StudentSam', 'rohan.fredriksson@gmail.com', public=None, tutor=0, admin=0)
db.add_user('StudentSandra', 'StudentSandra', 'rohan.fredriksson@gmail.com', public=None, tutor=0, admin=0)
db.add_user('RohanFredriksson', 'RohanFredriksson', 'rohan.fredriksson@gmail.com', public=None, tutor=0, admin=0)
db.close()
return
```
To add a new user just add a new line. You can specify whether they are tutors or admins as well. NOTE when you add a user using this method, they do not have a public key or private key. To fix this, you need to login to the specified account and generate a new key pair under the Profile page on the website.
