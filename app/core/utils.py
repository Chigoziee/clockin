from fastapi import HTTPException
from jose import jwt
from datetime import datetime, timedelta, timezone
from mailjet_rest import Client
from core.config import settings
from db.mongo import admin_collection

JWT_SECRET = settings.JWT_SECRET
JWT_ALGORITHM = settings.JWT_ALGORITHM
MAILJET_API_KEY = settings.MAILJET_API_KEY
MAILJET_API_SECRET = settings.MAILJET_API_SECRET
BASE_URL = settings.BASE_URL

mailjet = Client(auth=(MAILJET_API_KEY, MAILJET_API_SECRET), version='v3.1')


async def get_verified_admin(username: str) -> dict:
    admin = await admin_collection.find_one({"username": username})
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    if not admin.get("verified"):
        raise HTTPException(status_code=403, detail="Admin not verified")
    return admin


def attendance_log_limiter(logs: list, new_log: str):
    if len(logs) < 4:
        logs.append(new_log)
    else:
        logs.pop(0)
        logs.append(new_log)
    return logs

def is_token_expired(token_data: dict) -> bool:
    exp = token_data.get("exp")
    if not exp:
        return True
    return datetime.fromtimestamp(token_data["exp"], tz=timezone.utc) < datetime.now(timezone.utc)
  
async def password_reset(email: str):
    expire = datetime.now(timezone.utc) + timedelta(minutes=15)  # expires in 15 minutes
    payload = {"sub": email, "exp": expire}
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    reset_link = f"{BASE_URL}/admin/reset-password-token?token={token}"
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
        raise HTTPException(status_code=400, detail="Failed to send verification email")

def email_verification(email: str, firstName: str):
    expire = datetime.now(timezone.utc) + timedelta(hours=1)  # expires in 1 hour
    payload = {"sub": email, "exp": expire}
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    verification_link = f"{BASE_URL}/admin/verify-email?token={token}"
    data = {'Messages': [{"From": { "Email": "sk.hyginus@gmail.com",
                                    "Name": "CLOCKIN"},
                          "To": [{"Email": email,
                                  "Name": firstName}],
                        "Subject": "Verify email", 
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
        raise HTTPException(status_code=400, detail="Failed to send verification email")