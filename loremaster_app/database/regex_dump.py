import re

email_regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
password_regex = re.compile(r'(?=.*[a-z]+)(?=.*[A-Z]+)(?=.*[0-9]+)(?=.*\W+)(.{8,})+')
#(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[@#$%^&+=]).*$

def isValidEmail(email:str) -> bool:
    return re.fullmatch(email_regex, email)

def isValidPassword(password:str) -> bool:
    return re.fullmatch(password_regex, password)