# Copyright 2019 by Quopt IT Services BV
#
#  Licensed under the Artistic License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#    https://raw.githubusercontent.com/Quopt/ITR-webclient/master/LICENSE
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
import uuid
from datetime import datetime, timezone

import ITSRestAPISettings
import requests
from ITSLogging import *
import ITSRestAPIDB
import ITSRestAPIORMExtensions

def send_mail(customer_id, mail_subject, mail_content, to_receiver, cc_receiver="", bcc_receiver="", from_sender="",
              files_to_attach=[], reply_to = "", consultant_id="", post_payload="{}", session_id="", data_to_attach=""):
    # check if there is a generic cc adress for this company
    temp_company = ""
    temp_cc_mail = ""

    try:
        with ITSRestAPIDB.session_scope("") as qry_session_master:
            temp_company = qry_session_master.query(ITSRestAPIORMExtensions.SecurityCompany).filter(
                ITSRestAPIORMExtensions.SecurityCompany.ID == customer_id).first()
            if temp_company.CCEMail.strip() != "":
                temp_cc_mail = temp_company.CCEMail + ","
    except:
        pass

    # check the to_receiver for http and https addresses to be called
    new_to_receiver = temp_cc_mail + to_receiver
    to_receiver_array = new_to_receiver.split(",")

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
                    new_to_receiver = new_to_receiver + ","  + str.strip()
        to_receiver = temp_cc_mail + new_to_receiver

    if to_receiver.strip() != "":
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

        if data_to_attach != "":
            # attach the string as data.json file
            attachment = MIMEText(data_to_attach)
            attachment.add_header('Content-Disposition', 'attachment', filename='data.json')
            msg.attach(attachment)

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

        total_receiver = to_receiver
        if cc_receiver != "":
            total_receiver = total_receiver + "," + cc_receiver.strip().replace(" ", "")
        if bcc_receiver != "":
            total_receiver = total_receiver + "," + bcc_receiver.strip().replace(" ", "")

        try:
            s.sendmail(from_sender, total_receiver.split(","), msg.as_string())
            app_log.info('Mail send to %s, cc %s, bcc %s. Subject %s, message content is hidden', to_receiver, cc_receiver, bcc_receiver ,mail_subject)

            with ITSRestAPIDB.session_scope(customer_id) as qry_session:
                # save an audit trail record
                new_audit_trail = ITSRestAPIORMExtensions.ClientAuditLog()
                new_audit_trail.ID = uuid.uuid4()
                new_audit_trail.ObjectID = '00000000-0000-0000-0000-000000000000'
                if session_id != "":
                    new_audit_trail.SessionID = session_id
                else:
                    new_audit_trail.SessionID = '00000000-0000-0000-0000-000000000000'
                if customer_id != "":
                    new_audit_trail.CompanyID = customer_id
                else:
                    new_audit_trail.CompanyID = '00000000-0000-0000-0000-000000000000'
                if consultant_id != "":
                    new_audit_trail.UserID = consultant_id
                else:
                    new_audit_trail.UserID = '00000000-0000-0000-0000-000000000000'
                new_audit_trail.ObjectType = 1001 # email
                new_audit_trail.OldData = ""
                new_audit_trail.NewData = '{ "To": "' + to_receiver+ '","CC": "' + cc_receiver+ '","BCC": "' + bcc_receiver+ '", "Subject" : "' + mail_subject+ '" }'
                new_audit_trail.AuditMessage = "EMail sent to %%To%%, cc %%CC%%, bcc %%BCC%% with subject %%Subject%%"
                new_audit_trail.MessageID = 1 # 1 email sent
                new_audit_trail.CreateDate = datetime.now(timezone.utc)
                qry_session.add(new_audit_trail)
        finally:
            s.quit()
