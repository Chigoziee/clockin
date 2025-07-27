from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta, timezone
import os
from mailjet_rest import Client
import cloudinary

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
JWT_SECRET = os.getenv("JWT_SECRET", "defaultsecret")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
MAILJET_API_KEY = os.environ["MAILJET_API_KEY"]
MAILJET_API_SECRET = os.environ["MAILJET_API_SECRET"]
mailjet = Client(auth=(MAILJET_API_KEY, MAILJET_API_SECRET), version='v3.1')
base_url = os.getenv("BASE_URL", "http://localhost:8000")

# Configure Cloudinary    
cloudinary.config( 
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key = os.getenv("CLOUDINARY_API_KEY"),
    api_secret = os.getenv("CLOUDINARY_API_SECRET"),
    secure=True)

def cd_upload(file):
    result = cloudinary.uploader.upload(file)
    return result['secure_url']

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
    
async def password_reset(email: str):
    expire = datetime.now(timezone.utc) + timedelta(minutes=15)  # expires in 15 minutes
    payload = {"sub": email, "exp": expire}
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    reset_link = f"{base_url}/admin/reset-password-token?token={token}"
    data = {'Messages': [{"From": { "Email": "sk.hyginus@gmail.com",
                                    "Name": "CLOCKIN"},
                          "To": [{"Email": email}],
                        "Subject": "Password reset",                        
                        "HTMLPart": f"""
                        <!DOCTYPE html>
                            <html lang="en">
                            <head>
                            <meta charset="UTF-8" />
                            <title>Reset Your Password</title>
                            <style>
                                body {{
                                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                                background-color: #f4f6f8;
                                margin: 0;
                                padding: 0;
                                }}
                                .container {{
                                max-width: 600px;
                                margin: 40px auto;
                                background: #ffffff;
                                padding: 30px 40px;
                                border-radius: 8px;
                                box-shadow: 0 3px 10px rgba(0,0,0,0.1);
                                }}
                                h1 {{
                                color: #2c3e50;
                                font-size: 24px;
                                margin-bottom: 20px;
                                }}
                                p {{
                                color: #555555;
                                font-size: 16px;
                                line-height: 1.6;
                                }}
                                .btn {{
                                display: inline-block;
                                margin: 25px 0;
                                padding: 12px 24px;
                                background-color: #1a73e8;
                                color: #ffffff;
                                text-decoration: none;
                                border-radius: 5px;
                                font-weight: 600;
                                font-size: 16px;
                                }}
                                .btn:hover {{
                                background-color: #155ab6;
                                }}
                                .fallback {{
                                font-size: 14px;
                                color: #777;
                                background: #f9f9f9;
                                padding: 10px;
                                border-left: 4px solid #ccc;
                                word-break: break-word;
                                }}
                                .footer {{
                                margin-top: 40px;
                                font-size: 12px;
                                color: #aaa;
                                text-align: center;
                                }}
                            </style>
                            </head>
                            <body>
                            <div class="container">
                                <h1>Password Reset Request</h1>
                                <p>Hello 👋,</p>
                                <p>We received a request to reset your password. If you made this request, click the button below to set a new password:</p>

                                <p style="text-align: center;">
                                <a href="{ reset_link }" class="btn">Reset Password</a>
                                </p>

                                <p>If the button doesn't work, you can copy and paste this link into your browser:</p>
                                <p class="fallback">{ reset_link }</p>

                                <p class="footer">
                                If you didn`t request a password reset, you can safely ignore this email.<br />
                                — ClockIn Team
                                </p>
                            </div>
                            </body>
                            </html>"""}]}
    
    result = mailjet.send.create(data=data) 
    if result.status_code != 200:
        raise Exception("Failed to send verification email")

def email_verification(email: str, firstName: str):
    expire = datetime.now(timezone.utc) + timedelta(hours=1)  # expires in 1 hour
    payload = {"sub": email, "exp": expire}
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    verification_link = f"{base_url}/admin/verify-email?token={token}"
    data = {'Messages': [{"From": { "Email": "sk.hyginus@gmail.com",
                                    "Name": "CLOCKIN"},
                          "To": [{"Email": email,
                                  "Name": firstName}],
                        "Subject": "Password reset", 
                        "HTMLPart": f"""<!DOCTYPE html>
                                    <html lang="en">
                                    <head>
                                    <meta charset="UTF-8">
                                    <title>Verify Your Email</title>
                                    <style>
                                        body {{
                                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                                        background-color: #f2f4f8;
                                        margin: 0;
                                        padding: 0;
                                        }}
                                        .container {{
                                        max-width: 600px;
                                        margin: 50px auto;
                                        background: #ffffff;
                                        padding: 30px 40px;
                                        border-radius: 10px;
                                        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                                        }}
                                        h1 {{
                                        color: #1a1a1a;
                                        font-size: 24px;
                                        margin-bottom: 20px;}}
                                        p {{
                                        color: #4a4a4a;
                                        line-height: 1.6;
                                        margin-bottom: 16px;}}
                                        .btn {{
                                        display: inline-block;
                                        background-color: #1a73e8;
                                        color: #ffffff;
                                        text-decoration: none;
                                        padding: 12px 28px;
                                        border-radius: 6px;
                                        font-weight: 600;
                                        font-size: 16px;
                                        margin-top: 10px;
                                        transition: background-color 0.3s ease;}}
                                        .btn:hover {{
                                        background-color: #A9A9A9;
                                        }}
                                        .footer {{
                                        font-size: 13px;
                                        color: #999999;
                                        margin-top: 40px;
                                        text-align: center;
                                        }}
                                        .fallback {{
                                        background-color: #f9f9f9;
                                        padding: 10px;
                                        border-left: 3px solid #ccc;
                                        word-break: break-all;
                                        font-size: 14px;
                                        color: #666666;
                                        }}
                                    </style>
                                    </head>
                                    <body>
                                    <div class="container">
                                        <h1>Welcome to ClockIn 👋</h1>
                                        <p>Hello {firstName},</p>
                                        <p>Thanks for signing up! To get started, please verify your email address by clicking the button below:</p>
                                        <p style="text-align: center;">
                                        <a href="{ verification_link }" class="btn">Verify Email</a>
                                        </p>
                                        <p>If the button above doesn`t work, simply copy and paste the following link into your browser:</p>
                                        <p class="fallback"><a href="{ verification_link }">{ verification_link }</a></p>
                                        <p class="footer">Didn't request this email? No worries — just ignore it.</p>
                                    </div>
                                    </body>
                                    </html>"""}]}

    result = mailjet.send.create(data=data)
    if result.status_code != 200:
        raise Exception("Failed to send verification email")