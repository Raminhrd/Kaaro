import secrets
import string
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
import random
import re

from users.defaults import (
    ACCESS_TOKEN_COOKIE_KEY_NAME,
    REFRESH_TOKEN_COOKIE_KEY_NAME,
    ACCESS_TOKEN_LIFETIME,
    REFRESH_TOKEN_LIFETIME,
)


def set_cookie(response: Response, key, value, max_age = REFRESH_TOKEN_LIFETIME * 86400):
    response.set_cookie(
        key=key,
        value=value,
        max_age=max_age,
        httponly=True,
        secure=False,
        samesite='Lax',
    )
    # response.set_cookie(
    #     key=key,
    #     value=value,
    #     max_age=max_age,
    #     httponly=True,
    #     samesite='None',
    #     secure=True,
    # )


def set_tokens_on_cookie(response: Response, access_token: str, refresh_token: str):
    set_cookie(response, ACCESS_TOKEN_COOKIE_KEY_NAME, access_token, ACCESS_TOKEN_LIFETIME)
    set_cookie(response, REFRESH_TOKEN_COOKIE_KEY_NAME, refresh_token)
    

def remove_tokens_from_cookie(response: Response):
    response.delete_cookie(key=ACCESS_TOKEN_COOKIE_KEY_NAME, samesite='Lax')
    response.delete_cookie(key=REFRESH_TOKEN_COOKIE_KEY_NAME, samesite='Lax')


def generate_random_password(length=25):
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(length))
    return password


def generate_otp(length=4):
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])


def normalize_phone_number(phone_number):

    if not phone_number:
        raise ValidationError("Phone number is required.")

    persian_digits = "۰۱۲۳۴۵۶۷۸۹"
    arabic_digits = "٠١٢٣٤٥٦٧٨٩"
    english_digits = "0123456789"
    
    translation_table = str.maketrans(persian_digits + arabic_digits, english_digits * 2)
    phone_number = phone_number.translate(translation_table)
    
    phone_number = phone_number.strip()

    if phone_number.startswith("+98"):
        phone_number = "0" + phone_number[3:]
    elif phone_number.startswith("98"):
        phone_number = "0" + phone_number[2:]
    elif phone_number.startswith("0098"):
        phone_number = "0" + phone_number[4:]

    if not phone_number.isdigit():
        raise ValidationError("Phone number must contain only digits.")
        
    if not phone_number.startswith("09"):
        raise ValidationError("Phone number must start with '09'.")
    
    if len(phone_number) != 11:
        raise ValidationError("Phone number must be exactly 11 digits.")

    return phone_number    