import os
import base64

# send grid
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (
    Mail,
    Attachment,
    FileContent,
    FileName,
    FileType,
    Disposition,
    ContentId,
)
from sendgrid.helpers.mail.attachment import Attachment
from sendgrid.helpers.mail.content import Content

from app.api.utility.utils import TemplateEngine

API_KEY = os.environ.get("SENDGRID_API_KEY")
SENDER = os.environ.get("SENDER_EMAIL", "report-dev@modana.id")


class EmailError(Exception):
    """ raised when email error """

    def __init__(self, error):
        self.error = error


def create_attachment(fullpath):
    """ create sendgrid attachment """
    with open(fullpath, "rb") as f:
        data = f.read()

    # split filename only
    path, filename = os.path.split(fullpath)

    encoded = base64.b64encode(data).decode()
    attachment = Attachment()
    attachment.file_content = FileContent(encoded)
    attachment.file_type = FileType(
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    attachment.file_name = FileName(filename)
    attachment.disposition = Disposition("attachment")
    attachment.content_id = ContentId("Example Content ID")
    return attachment


def prepare_email(sender, to, subject, content, attachment, template):
    """ prepare sendgrid email """
    # render HTML template
    email_template = TemplateEngine(
        template_name=template,
        data=content,
        template_dir_path="app/api/reports/templates/",
    ).render()

    # prepare email
    message = Mail(
        from_email=SENDER, to_emails=to, subject=subject, html_content=email_template
    )
    message.attachment = attachment
    sg = SendGridAPIClient(API_KEY)
    return sg, message


def send_email(recipients, subject, content, fullpath, template):
    """ send email through sendgrid """
    # convert filename to attachment
    attachment = create_attachment(fullpath)
    sg, mail = prepare_email(SENDER, recipients, subject, content, attachment, template)

    try:
        response = sg.send(mail)
    except Exception as e:
        raise EmailError(e)
    else:
        return "OK"
