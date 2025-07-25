from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta, timezone
import os
from mailjet_rest import Client

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
JWT_SECRET = os.getenv("JWT_SECRET", "defaultsecret")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, expires_minutes=60):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.JWTError:
        return None

def email_verification(email: str, firstName: str):
    expire = datetime.now(timezone.utc) + timedelta(hours=1)  # expires in 1 hour
    payload = {"sub": email, "exp": expire}
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    api_key = os.environ["MAILJET_API_KEY"]
    api_secret = os.environ["MAILJET_API_SECRET"]

    mailjet = Client(auth=(api_key, api_secret), version='v3.1')
    verification_link = f"http://localhost:8000/users/verify-email?token={token}"
    data = {
        'Messages': [ 
            {
            "From": {
                "Email": "sk.hyginus@gmail.com",
                "Name": "CLOCKIN"
            },
            "To": [
                {
                "Email": email,
                "Name": firstName
                }
            ],
            "Subject": "Email Verification",
            "HTMLPart": """<!DOCTYPE html>
                        <html lang="en">
                        <head>
                        <meta charset="UTF-8">
                        <title>Verify Your Email</title>
                        <style>
                            body {
                            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                            background-color: #f2f4f8;
                            margin: 0;
                            padding: 0;
                            }
                            .container {
                            max-width: 600px;
                            margin: 50px auto;
                            background: #ffffff;
                            padding: 30px 40px;
                            border-radius: 10px;
                            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                            }
                            h1 {
                            color: #1a1a1a;
                            font-size: 24px;
                            margin-bottom: 20px;
                            }
                            p {
                            color: #4a4a4a;
                            line-height: 1.6;
                            margin-bottom: 16px;
                            }
                            .btn {
                            display: inline-block;
                            background-color: #1a73e8;
                            color: #ffffff;
                            text-decoration: none;
                            padding: 12px 28px;
                            border-radius: 6px;
                            font-weight: 600;
                            font-size: 16px;
                            margin-top: 10px;
                            transition: background-color 0.3s ease;
                            }
                            .btn:hover {
                            background-color: #A9A9A9;
                            }
                            .footer {
                            font-size: 13px;
                            color: #999999;
                            margin-top: 40px;
                            text-align: center;
                            }
                            .fallback {
                            background-color: #f9f9f9;
                            padding: 10px;
                            border-left: 3px solid #ccc;
                            word-break: break-all;
                            font-size: 14px;
                            color: #666666;
                            }
                        </style>
                        </head>""" + f"""\n<body>
                        <div class="container">
                            <h1>Welcome to ClockIn 👋</h1>
                            <p>Hello {firstName},</p>
                            <p>Thanks for signing up! To get started, please verify your email address by clicking the button below:</p>
                            <p style="text-align: center;">
                            <a href="{ verification_link }" class="btn">Verify Email</a>
                            </p>
                            <p>If the button above doesn’t work, simply copy and paste the following link into your browser:</p>
                            <p class="fallback"><a href="{ verification_link }">{ verification_link }</a></p>
                            <p class="footer">Didn't request this email? No worries — just ignore it.</p>
                        </div>
                        </body>
                        </html>"""
    
            }
        ]
        }

    result = mailjet.send.create(data=data)
    if result.status_code != 200:
        raise Exception("Failed to send verification email")