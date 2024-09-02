# ====================HASHING BCRYPT ========================#

import bcrypt


def hash_password_bcrypt(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def check_password_bcrypt(hashed_password: str, password: str) -> bool:
    # Verification
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


# Examples
hashed = hash_password_bcrypt("my_secure_password")
print(hashed)
print(check_password_bcrypt(hashed, "my_secure_password"))
print(check_password_bcrypt(hashed, "wrong_password"))

# ====================HASHING Argon2 ========================#
from argon2 import PasswordHasher

ph = PasswordHasher()


def hash_password_argon2(password: str) -> str:
    return ph.hash(password)


def check_password_argon2(hashed_password: str, password: str) -> bool:

    try:
        ph.verify(hashed_password, password)
        return True
    except:
        return False


# Examples
hashed = hash_password_argon2("my_secure_password")
print(hashed)
print(check_password_argon2(hashed, "my_secure_password"))
print(check_password_argon2(hashed, "wrong_password"))

# ====================HASHING HASHLIB ========================#
import hashlib
import os


def hash_password_pbkdf2(password: str, salt: bytes = None) -> str:
    if not salt:
        salt = os.urandom(16)
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return salt.hex() + hashed.hex()


def check_password_pbkdf2(hashed_password: str, password: str) -> bool:
    salt = bytes.fromhex(hashed_password[:32])
    original_hash = hashed_password[32:]
    return original_hash == hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000).hex()


# Examples
hashed = hash_password_pbkdf2("my_secure_password")
print(hashed)
print(check_password_pbkdf2(hashed, "my_secure_password"))
print(check_password_pbkdf2(hashed, "wrong_password"))

import hashlib
import os


def hash_password_scrypt(password: str, salt: bytes = None) -> str:
    if not salt:
        salt = os.urandom(16)
    hashed = hashlib.scrypt(password.encode('utf-8'), salt=salt, n=16384, r=8, p=1)
    return salt.hex() + hashed.hex()


def check_password_scrypt(hashed_password: str, password: str) -> bool:
    salt = bytes.fromhex(hashed_password[:32])
    original_hash = hashed_password[32:]
    return original_hash == hashlib.scrypt(password.encode('utf-8'), salt=salt, n=16384, r=8, p=1).hex()



hashed = hash_password_scrypt("my_secure_password")
print(hashed)
print(check_password_scrypt(hashed, "my_secure_password"))
print(check_password_scrypt(hashed, "wrong_password"))
