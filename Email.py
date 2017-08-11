import imaplib
import smtplib
import os
import email
from email.MIMEBase import MIMEBase
from email.MIMEImage import MIMEImage
from email.MIMEText import MIMEText
from email.MIMEAudio import MIMEAudio
import mimetypes


class Email:
    def __init__(self, your_mail, your_password):
        self.mail = your_mail
        self.password = your_password
        self.server_ssl = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        self.read_conn = imaplib.IMAP4_SSL('imap.gmail.com')

    def login(self):
        self.server_ssl.login(self.mail, self.password)
        self.read_conn.login(self.mail, self.password)

    def send_mail(self, target, subject, *file_names):
        """
        send a mail with files to the target
        @param target: send the mail to the target
        @param subject: mail's subject
        @param file_names= list of files to send
        """
        msg = email.MIMEMultipart.MIMEMultipart()
        msg['From'] = self.mail
        msg['To'] = email.Utils.COMMASPACE.join(target)
        msg['Subject'] = subject
        for file_name in file_names:
            f = open(file_name, 'rb')
            ctype, encoding = mimetypes.guess_type(file_name)
            if ctype is None or encoding is not None:
                ctype = 'application/octet-stream'
            maintype, subtype = ctype.split('/', 1)
            # in case of a text file
            if maintype == 'text':
                part = MIMEText(f.read(), _subtype=subtype)
            # in case of an image file
            elif maintype == 'image':
                part = MIMEImage(f.read(), _subtype=subtype)
            # in case of an audio file
            elif maintype == 'audio':
                part = MIMEAudio(f.read(), _subtype=subtype)
            # any other file
            else:
                part = MIMEBase(maintype, subtype)
                msg.set_payload(f.read())
            part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(file_name))
            msg.attach(part)
            f.close()
        # ssl server doesn't support or need tls, so don't call server_ssl.starttls()
        self.server_ssl.sendmail(self.mail, target, msg.as_string())
        #server_ssl.quit()
        self.server_ssl.close()

    def get_all_mail(self):
        self.read_conn.select("inbox")  # connect to inbox.
        # select only unread messages
        result, data = self.read_conn.search(None, "ALL")
        if not data:
            return []
        ids = data[0]  # data is a list.
        id_list = ids.split()  # ids is a space separated string
        return id_list

    def get_mail_content(self, mail):
        try:
            # fetch the email body (RFC822) for the given ID
            result, data = self.read_conn.fetch(mail, "(RFC822)")
            content = data[0][1]  # here's the body, which is raw text of the whole email
            # including headers and alternate payloads
            return content
        except TypeError:
            self.get_mail_content(mail)

    def delete_mail(self, msg):
        self.read_conn.store(msg, '+FLAGS', '\\Deleted')
        self.read_conn.expunge()