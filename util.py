import re

"""
4 to 16 character inclusive
Must be alphanumeric.
"""
def validate_username(username):
    
    if not username.isalnum():
        return False

    if len(username) < 4:
        return False

    if len(username) > 16:
        return False

    return True

"""
At least 8 characters
A-Z, a-z, 0-9, @#$%^&+=
"""
def validate_password(password):
    if re.fullmatch(r'[A-Za-z0-9@#$%^&+=]{8,}', password):
        return True
    return False
        