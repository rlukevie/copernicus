from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
import smtplib

from copernicus_tools.settings import *


class MailHandler:
    def __init__(self):
        self.user = ''
        self.password = ''
        self.msg = MIMEMultipart()
        self.text = MIMEText('')
        self.file_to_attach_path = ''
        self.image = None

    def send_admin_mail(self,
                        mail_subject='',
                        mail_text='',
                        mail_from=admin_mail_from,
                        mail_to=admin_mail_to,
                        image_to_attach_path=None):
        self.msg = MIMEMultipart()
        self.msg['Subject'] = str(mail_subject)
        self.msg['From'] = str(mail_from)
        self.msg['To'] = str(mail_to)
        self.text = MIMEText(str(mail_text))
        self.msg.attach(self.text)
        self.user = email_user
        self.password = email_password

        if image_to_attach_path:
            try:
                f = open(image_to_attach_path, 'rb')
                self.image = MIMEImage(f.read())
                f.close()
                self.msg.attach(self.image)
            except IOError as e:
                logging.info(
                    'Could not send Admin Mail '
                    '(From: {}, To: {}, Attached Image (if any): {}). '
                    'IOError: {}'.format(
                        self.msg['From'], self.msg['To'],
                        image_to_attach_path, str(e)))
                return

        try:
            smtp = smtplib.SMTP_SSL(email_host + ':' + email_port)
            smtp.login(self.user, self.password)
            smtp.sendmail(mail_from, mail_to, self.msg.as_string())
            smtp.quit()
            logging.debug(
                'Admin Mail sent. '
                'From: {}, To: {}, Attached Image (if any): {}'.format(
                    self.msg['From'], self.msg['To'], image_to_attach_path))
        except smtplib.SMTPException as e:
            logging.info(
                'Could not send Admin Mail '
                '(From: {}, To: {}, Attached Image (if any): {}). '
                'SMTPException: {}'.format(
                    self.msg['From'], self.msg['To'], image_to_attach_path,
                    str(e)))
            return

    def send_product_selected_mail(self, factory_product_instance):
        self.send_admin_mail(
            mail_subject='Product selected for download',
            mail_text='The following product has '
                      'been selected for download:\n\n' +
                      factory_product_instance.title + '\n' +
                      factory_product_instance.summary
        )

    def send_product_downloaded_mail(self, factory_product_instance):
        self.send_admin_mail(
            mail_subject='Product downloaded',
            mail_text='The following product has '
                      'been downloaded:\n\n' +
                      factory_product_instance.title + '\n' +
                      factory_product_instance.summary
        )

    def send_product_processed_mail(self, factory_product_instance):
        self.send_admin_mail(
            mail_subject='Product processed to Level 2A',
            mail_text='The following product has '
                      'been processed to Level 2A:\n\n' +
                      factory_product_instance.title + '\n' +
                      factory_product_instance.summary
        )

    def send_preview_generated_mail(self, lab_product_instance):
        self.send_admin_mail(
            mail_subject='Preview generated',
            mail_text='Preview image generated for:\n\n' +
            lab_product_instance.title,
            image_to_attach_path=lab_product_instance.preview_image_path
        )
