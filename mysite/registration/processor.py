import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from django.db import connection


class Email:
    LOGIN = 'v.brunko99@gmail.com'
    PASSWORD = 'lvoq yetp osor zhmr'
    DATA_SUBJECT = 'Email confirmation'
    DATA_BODY = 'To confirm your registration, Follow the link {0}'


def send_email(host: str, email: str, confirm_code: str) -> str:
    gmail_user = Email.LOGIN
    gmail_password = Email.PASSWORD

    msg = MIMEMultipart()
    msg['From'] = gmail_user
    msg['To'] = email
    msg['Subject'] = Email.DATA_SUBJECT
    url = Email.DATA_BODY.format(
        f'{host}/registration/confirm_registration/{confirm_code}'
    )

    msg.attach(MIMEText(url, 'plain'))

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, email, msg.as_string())

    return url


def query_database(user_id: int) -> list:
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM user_profile_userprofile WHERE id = %s", [user_id]
        )
        rows = cursor.fetchall()
    if not rows:
        return rows
    else:
        return rows.pop(0)
