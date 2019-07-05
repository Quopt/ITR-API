# Copyright 2019 by Quopt IT Services BV
#
#  Licensed under the Artistic License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#    https://opensource.org/licenses/Artistic-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

# Import smtplib for the actual sending function
import smtplib

# Here are the email package modules we'll need
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import ITSRestAPISettings
import requests

def send_mail(customer_id, mail_subject, mail_content, to_receiver, cc_receiver="", bcc_receiver="", from_sender="",
              files_to_attach=[], reply_to = "", consultant_id="", post_payload="{}"):
    # check the to_receiver for http and https addresses to be called
    new_to_receiver = to_receiver
    to_receiver_array = to_receiver.split(",")

    if len(to_receiver_array) > 1 :
        new_to_receiver = ""
        for str in to_receiver_array:
            if str.find("http://") == 0 or str.find("https://") == 0:
                # curl the URL with post_payload
                url = str
                payload = post_payload
                headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
                requests.post(url, data=payload, headers=headers)
            else:
                if new_to_receiver == "":
                    new_to_receiver = str
                else:
                    new_to_receiver = new_to_receiver + " , "  + str
        to_receiver = new_to_receiver

    # Create the container (outer) email message.
    if len(files_to_attach) > 0:
        msg = MIMEMultipart()
        msg.preamble = mail_content
    else:
        msg = MIMEText(mail_content,'html')
    msg['Subject'] = mail_subject
    msg['To'] = to_receiver
    if cc_receiver != "":
        msg['CC'] = cc_receiver
    if from_sender == "":
        from_sender = ITSRestAPISettings.get_setting_for_customer(customer_id,'SMTP_SENDER',True, consultant_id)
    msg['From'] = from_sender
    if reply_to == "":
        msg['Reply-to'] = from_sender
    else:
        msg['Reply-to'] = reply_to

    # Assume we know that the image files are all in PNG format
    for file in files_to_attach:
        # Open the files in binary mode.  Let the MIMEImage class automatically
        # guess the specific file type.
        with open(file, 'rb') as fp:
            img = MIMEImage(fp.read())
        msg.attach(img)

    # Send the email via our own SMTP server.
    smtp_server = ITSRestAPISettings.get_setting_for_customer(customer_id,'SMTP_SERVER',True, consultant_id)
    smtp_port = ITSRestAPISettings.get_setting_for_customer(customer_id,'SMTP_PORT',True, consultant_id)
    smtp_usetls = ITSRestAPISettings.get_setting_for_customer(customer_id,'SMTP_USETLS',True, consultant_id) == "T"
    smtp_user = ITSRestAPISettings.get_setting_for_customer(customer_id,'SMTP_USER',True, consultant_id)
    smtp_password = ITSRestAPISettings.get_setting_for_customer(customer_id,'SMTP_PASSWORD',True, consultant_id)

    if smtp_port != "":
        s = smtplib.SMTP(smtp_server + ":" + smtp_port)
    else:
        s = smtplib.SMTP(smtp_server)
    if smtp_usetls:
        s.ehlo()
        s.starttls()
    if smtp_user != "":
        s.login(smtp_user, smtp_password)

    if cc_receiver != "":
        cc_receiver="," + cc_receiver
    if bcc_receiver != "":
        bcc_receiver="," + bcc_receiver

    try:
        s.sendmail(from_sender, to_receiver + cc_receiver + bcc_receiver, msg.as_string())
    finally:
        s.quit()
