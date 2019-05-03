import hashlib
import string
import random

def make_salt():
    return ''.join([random.choice(string.ascii_letters) for x in range(10)])

def hash_password(password, salt=None):
    if not salt:
        salt = make_salt()
    hash = hashlib.sha256(str.encode(password)).hexdigest()
    return '{0}:{1}'.format(hash, salt)

def check_hash(password, hash):
    salt = hash.split(':')[1]

    if hash_password(password, salt) == hash:
        return True
    return False
