import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from fastapi import BackgroundTasks

from app.config.settings import get_settings

settings = get_settings()
sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))


async def send_email(recipient: str, subject: str, content: dict, background_tasks: BackgroundTasks):
    message = Mail(
        from_email='from_email@example.com',
        to_emails=recipient,
        subject=subject,
    )
    message.template_id = 'd-3f0081e4ff5d4ffe94f61059a4d0cae7'
    message.dynamic_template_data = content

    background_tasks.add_task(sg.send, message)
    # try:
    #     # sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
    #     background_tasks.add_task(sg.send, message)
    #     # print("Email sent:", response.status_code)
    #     # print(response.body)
    #     # print(response.headers)
    # except Exception as e:
    #     print("Error sending email:", e.message)
