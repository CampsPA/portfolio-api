
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

def hash_password(password: str) -> str:
    return password_hash.hash(password)

# Create a function to compared the hashed login password to the hashed_password in the database
# Takes the attempeted login password, hash it then compared to the one stored in the database
def verify_password(plain_password: str, hashed_password: str):
    return password_hash.verify(plain_password, hashed_password)


