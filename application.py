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
#

import os
import subprocess

os.chdir(os.path.dirname(os.path.realpath(__file__)))
subprocess.run(['pip', 'install', '-r', 'requirements.txt'])

from flask import Flask, jsonify, request, url_for, render_template
import datetime
import json
import time
import hashlib, uuid, urllib
import types
import traceback
import shutil
from flask_cors import CORS
from flask_compress import Compress
from datetime import datetime, timezone, timedelta, date
from waitress import serve
import time
import threading
import signal
import pyotp
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_limiter.wrappers import Limit, LimitGroup

import ITSRestAPILogin
import ITSMailer
import ITSRestAPIORMExtensions
import ITSRestAPIORM
import ITSRestAPIDB
import ITSRestAPISettings
import ITSJsonify
from ITSRestAPIORMExtendedFunctions import *
from ITSLogging import app_log, log_handler_backup_count, log_file, init_app_log, log_formatter
from ITSPrefixMiddleware import *
import ITSTranslate
import ITSHelpers
import ITSGit
import ITSEncrypt
from ITSCache import check_in_cache, add_to_cache, reset_cache, add_to_cache_with_timeout, global_cache, global_cache_timekey

app = Flask(__name__, instance_relative_config=True)
app.wsgi_app = PrefixMiddleware(app.wsgi_app, prefix='/api')
app.json_encoder = ITSJsonify.CustomJSONEncoder

startRequestTimer = {}  # only for debug purposes ! will not work with multiple calls at the same time

# fix for relative path not being picked up on windows 2019 / python 3.8
app_instance_path_global = os.path.join(os.sep, app.root_path, app.instance_path)


def app_instance_path():
    global app_instance_path_global
    return app_instance_path_global


@app.before_request
def before_request_callback():
    global startRequestTimer
    startRequestTimer[request.path] = time.time()


@app.teardown_request
def teardown_request(exception=None):
    global startRequestTimer

    endRequestTimer = time.time()
    company_id = "x"
    user_id = "x"
    browser_id = "x"
    ip_address = "x.x.x.x"
    try:
        ip_address = getIP(request)
    except:
        pass

    try:
        company_id = request.headers['CompanyID']
    except:
        pass

    try:
        user_id = request.headers['SessionID']
    except:
        pass

    try:
        browser_id = request.headers['BrowserID']
    except:
        pass

    try:
        app_log.info('Method called %s, %s, %s, %s, %s, %s, Timing %s', request.path, request.method, company_id, user_id,
                     ip_address, browser_id, str(endRequestTimer - startRequestTimer[request.path]))
        del startRequestTimer[request.path]
    except:
        app_log.info('Method called %s, %s, %s, %s, %s, x, Timing x', request.path, request.method, company_id, user_id, ip_address)

def get_browser_id():
    try:
        try:
            token = request.headers['SessionID']
            company_id, user_id, token_validated, token_session_id = ITSRestAPILogin.get_info_with_session_token(token)
            return token_session_id
        except:
            pass

        remhost = "x"
        try:
            remhost = request.environ['REMOTE_HOST']
        except:
            pass

        return getIP(request) + ":" + request.environ['REMOTE_PORT'] + "-" + remhost
    except:
        #app_log.error("Unknown browser ID found, %s returned", get_remote_address())
        return get_remote_address()

compress = Compress()
if ITSRestAPISettings.get_setting('ENABLE_CORS') == 'Y':
    CORS(app, max_age=600)
limiter = Limiter(app, key_func=get_browser_id)


# process the API request


# login and account related paths
# /LOGIN - this is a login request. There are no additional parameters allowed. In the header a userid and password key value pair must be present.
# /SENDRESETPASSWORD - send a password reset mail to the user as set in the header.
# /RESETPASSWORD - reset the password
# /CHECKTOKEN - check if the token passed is valid and refresh the validity of the token, this is required every 5 minutes
# /LOGOUT - remove the token as valid token and thus logging out the user

# information related paths (support both get and post, no update or partial updates are supported)
# audittrail
# batteries
# educations
# generatedreports
# groups
# nationalities
# organisations
# persons
# sessiontests
# sessions
# reportdefinitions
# reportdefinitionchapters
# companies
# creditgrants
# creditusages
# datagathering
# rightstemplates
# logins
# tokens
# systemsettings
# screentemplates
# tests
# To do :
# /TestTaking - will expose all information for taking a test by the candidate. Only available path to test taking users
# /Search  -set the SearchField header to search accross the system for the indicated string

# Other supported parameters as host headers are :
# MASTER - this call refers to the master database instead of the customer database. The second parameter will then contain the session id.
#          Effectively the parameters are shifted one position to the left. Set to Y if this is a master database call.
# SessionID - a unique number that identifies the session. This is the only number stored server side, together with the user id and company id.
#             the rest of the information is completely transparent. If someone logs in twice with different users this means that data for example
#             can be copied between customers and so forth. The Session ID is required and must be issued
# UserID - the user name of this user
# CompanyID - the id of the company this user is linked to
# Password - in case of login the password of this user
# IncludeArchived - set to Y to include archived information when requesting data
# IncludeMaster - set to Y to include information from the master database (if supported on that specific path)
# StartPage - pagination support - the first page to return information for
# PageSize - the size (number of records) to return
# Filter - the filter that needs to be applied to the returned records (SQL style so field=value. This will be converted to a sql LIKE search)
# Sort - the sort order (SQL style, so field names seperated by commas and DESC when you need to sort the other way around)
# SearchField - if you want to search but not on a specific field then set this string. It will be applied as generic search term (not on all paths)

def check_master_header(request):
    try:
        # if we dont know the user then no master database access by default
        master_header = "N"
        try:
            master_header = request.headers['MASTER']
        except:
            pass

        include_master_header = "N"
        try:
            include_master_header = request.headers['IncludeMaster']
        except:
            pass

        if master_header == "N" and include_master_header == "Y":
            master_header = "Y"

        token = request.headers['SessionID']
        company_id, user_id, token_validated, token_session_id = ITSRestAPILogin.get_info_with_session_token(token)
        id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, author_report_user, author_test_screen_templates_user, translator_user, office_user, is_password_manager, is_researcher = ITSRestAPILogin.get_id_of_user_with_token_and_company_id(
            user_id, company_id)

        return id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, translator_user, office_user, company_id, is_password_manager, master_header
    except:
        pass


def getIP(request):
    ip_address = ""
    try:
        ip_address = request.environ['HTTP_X_FORWARDED_FOR']
    except:
        try:
            ip_address = request.environ['REMOTE_ADDR']
        except:
            return ""
    return ip_address


def getWWW(request):
    ip_address = ""
    try:
        ip_address = request.environ['HTTP_X_FORWARDED_HOST']
    except:
        try:
            ip_address = request.environ['HTTP_ORIGIN']
        except:
            try:
                ip_address = request.environ['HOST']
            except:
                return ""
    return ip_address


def getWWWForToken(request):
    tempwww = request.host
    tempwww = tempwww.replace(".", "_").replace(":", "_")

    try:
        if tempwww.find("//") > 0:
            tempwww = tempwww.split("//")[1]
    except:
        pass

    return tempwww


# API implementations
@app.route('/')
@limiter.limit("1/second")
def hello_world():
    return current_app.send_static_file('default.html')


@app.route('/test')
@limiter.limit("1/second")
def route_test():
    return render_template('APITestPage.html')


@app.route('/test401')
@limiter.limit("1/second")
def route_test401():
    return 'Not authorised', 401


@app.route('/copyright')
def route_copyright():
    user_company = ""

    # try to check the request.host against the know administrative ids in the database to determine the company id
    wwwid = request.host.lower()
    return_obj = check_in_cache("copyright."+wwwid)
    if return_obj is None:
        with ITSRestAPIDB.session_scope("") as session:
            tempCompany = session.query(ITSRestAPIORMExtensions.SecurityCompany).filter(
                ITSRestAPIORMExtensions.SecurityCompany.AdministrativeID == wwwid).first()
            if tempCompany is not None:
                user_company = str(tempCompany.ID)

        parValue = ""

        try:
            with ITSRestAPIDB.session_scope(user_company, False) as session:
                if request.method == 'GET':
                    param = session.query(ITSRestAPIORMExtensions.SystemParam).filter(
                        ITSRestAPIORMExtensions.SystemParam.ParameterName == "COPYRIGHT").first()
                    parValue = param.ParValue
        except:
            with ITSRestAPIDB.session_scope("") as Msession:
                if request.method == 'GET':
                    param = Msession.query(ITSRestAPIORMExtensions.SystemParam).filter(
                        ITSRestAPIORMExtensions.SystemParam.ParameterName == "COPYRIGHT").first()
                if param is not None:
                    parValue = param.ParValue

        add_to_cache_with_timeout("copyright."+wwwid, 10, parValue)
        return parValue, 200
    else:
        return return_obj, 200


@app.route('/companyname')
def route_companyname():
    user_company = ""

    # try to check the request.host against the know administrative ids in the database to determine the company id
    wwwid = request.host.lower()
    return_obj = check_in_cache("companyname."+wwwid)
    if return_obj is None:
        with ITSRestAPIDB.session_scope("") as session:
            tempCompany = session.query(ITSRestAPIORMExtensions.SecurityCompany).filter(
                ITSRestAPIORMExtensions.SecurityCompany.AdministrativeID == wwwid).first()
            if tempCompany is not None:
                user_company = str(tempCompany.ID)

        parValue = ""

        try:
            with ITSRestAPIDB.session_scope(user_company, False) as session:
                if request.method == 'GET':
                    param = session.query(ITSRestAPIORMExtensions.SystemParam).filter(
                        ITSRestAPIORMExtensions.SystemParam.ParameterName == "COMPANYNAME").first()
                    parValue = param.ParValue
        except:
            with ITSRestAPIDB.session_scope("") as Msession:
                if request.method == 'GET':
                    param = Msession.query(ITSRestAPIORMExtensions.SystemParam).filter(
                        ITSRestAPIORMExtensions.SystemParam.ParameterName == "COMPANYNAME").first()
                if param is not None:
                    parValue = param.ParValue

        add_to_cache_with_timeout("companyname." + wwwid, 10, parValue)
        return parValue, 200
    else:
        return return_obj, 200


@app.route('/companylogo')
def route_companylogo():
    user_company = ""

    # try to check the request.host against the know administrative ids in the database to determine the company id
    wwwid = request.host.lower()
    return_obj = check_in_cache("companylogo."+wwwid)
    if return_obj is None:
        with ITSRestAPIDB.session_scope("") as session:
            tempCompany = session.query(ITSRestAPIORMExtensions.SecurityCompany).filter(
                ITSRestAPIORMExtensions.SecurityCompany.AdministrativeID == wwwid).first()
            if tempCompany is not None:
                user_company = str(tempCompany.ID)

        parValue = ""

        try:
            with ITSRestAPIDB.session_scope(user_company, False) as session:
                if request.method == 'GET':
                    param = session.query(ITSRestAPIORMExtensions.SystemParam).filter(
                        ITSRestAPIORMExtensions.SystemParam.ParameterName == "COMPANYLOGO").first()
                    parValue = param.ParValue
        except:
            pass

        add_to_cache_with_timeout("companylogo." + wwwid, 10, parValue)
        return parValue, 200
    else:
        return return_obj, 200

@app.route('/activesessions', methods=['GET'])
def active_sessions():
    # get the company id and session id from the header
    id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, translator_user, office_user, company_id, is_password_manager, master_header = check_master_header(
        request)

    if company_id == "":
        return "This API is only available to logged in office users", 403

    if office_user:
        amount_of_sessions = 0
        amount_of_testrun_sessions = 0
        server_amount_of_sessions = 0
        server_amount_of_testrun_sessions = 0

        with ITSRestAPIDB.session_scope("") as session:
            amount_of_sessions = session.query(ITSRestAPIORMExtensions.SecurityWebSessionToken).filter(
                ITSRestAPIORMExtensions.SecurityWebSessionToken.CompanyID == company_id).count()
            amount_of_testrun_sessions = session.query(ITSRestAPIORMExtensions.SecurityWebSessionToken).filter(
                ITSRestAPIORMExtensions.SecurityWebSessionToken.CompanyID == company_id).filter(
                ITSRestAPIORMExtensions.SecurityWebSessionToken.IsTestTakingUser).count()

            if master_user:
                server_amount_of_sessions = session.query(ITSRestAPIORMExtensions.SecurityWebSessionToken).count()
                server_amount_of_testrun_sessions = session.query(
                    ITSRestAPIORMExtensions.SecurityWebSessionToken).filter(
                    ITSRestAPIORMExtensions.SecurityWebSessionToken.IsTestTakingUser).count()

        if master_user:
            return "" + str(amount_of_sessions) + "(" + str(amount_of_testrun_sessions) + ")-" + str(
                server_amount_of_sessions) + "(" + str(server_amount_of_testrun_sessions) + ")", 200
        else:
            return "" + str(amount_of_sessions) + "(" + str(amount_of_testrun_sessions) + ")", 200
    else:
        return "This API is only available to logged in office users", 403


@app.route('/login', methods=['GET'])
@limiter.limit("1/second")
def login():
    user_id = ""
    user_password = ""
    poll = ""

    # first check if there is a polling code in the headers
    try:
        poll = request.headers['Poll']
    except:
        pass
    try:
        if poll != "":
            # try to locate the customer and sessions this poll is for
            with ITSRestAPIDB.session_scope("") as session:
                tempSession = session.query(ITSRestAPIORMExtensions.ClientSession).filter(
                    ITSRestAPIORMExtensions.ClientSession.ShortLoginCode == poll).first()
                tempUser = session.query(ITSRestAPIORMExtensions.SecurityUser).filter(
                    ITSRestAPIORMExtensions.SecurityUser.ID == tempSession.PersonID)\
                    .filter(ITSRestAPIORMExtensions.SecurityUser.IsTestTakingUser == True)\
                    .filter(ITSRestAPIORMExtensions.SecurityUser.IsOfficeUser == False).first()

                with ITSRestAPIDB.session_scope(tempUser.CompanyID) as session_customer:
                    tempCustomerUser = session_customer.query(ITSRestAPIORMExtensions.ClientPerson).filter(
                    ITSRestAPIORMExtensions.ClientPerson.ID == tempSession.PersonID).first()

                    user_id = tempUser.Email
                    user_password = ITSEncrypt.decrypt_string(tempCustomerUser.Password)
    except:
        return 'Poll code not found', 401
    # get the user id and password from the header
    if user_id == "":
        user_id = request.headers['UserID']
    if user_password == "":
        user_password = request.headers['Password']
    user_company = ""
    ip_address = getIP(request)  # we need to check for ip in the future
    www = getWWW(request)

    app_log.info('Login started for %s %s %s %s', user_id, ip_address, www, request.host)

    if request.headers.__contains__('CompanyID'):
        user_company = request.headers['CompanyID']
    else:
        # try to check the request.host against the know administrative ids in the database to determine the company id
        wwwid = request.host.lower()
        with ITSRestAPIDB.session_scope("") as session:
            tempCompany = session.query(ITSRestAPIORMExtensions.SecurityCompany).filter(
                ITSRestAPIORMExtensions.SecurityCompany.AdministrativeID == wwwid).first()
            if tempCompany is not None:
                user_company = tempCompany.ID

    # check them against the database and return whether or not OK
    login_result, found_company_id, is_test_taking_user = ITSRestAPILogin.login_user(user_id, user_password,
                                                                                     user_company)

    # login failed
    if login_result == ITSRestAPILogin.LoginUserResult.user_not_found:
        # sleep just a little while on failed login attempts to stop brute force attacks
        # this will block a thread. A better solution would be nicer off course
        # time.sleep(0.1)
        return 'User not found or password not valid', 401

    # the user is there so assign a session token
    if user_company != "":
        token = ITSRestAPILogin.create_session_token(user_id, user_company,
                                                     ITSRestAPILogin.LoginTokenType.regular_session)
    else:
        token = ITSRestAPILogin.create_session_token(user_id, found_company_id,
                                                     ITSRestAPILogin.LoginTokenType.regular_session)

    app_log.info('Token assigned to %s %s %s %s %s', user_id, ip_address, www, request.host, token)

    now = datetime.now() + timedelta(0, 600)
    return_obj = {}
    return_obj['SessionID'] = token
    return_obj['ExpirationDateTime'] = now.isoformat()
    return_obj['CompanyID'] = found_company_id
    return_obj[
        'MFAStatus'] = "NA"  # MFA status can be NA (for not applicable), CODE to request additional login code, and QR for registering the QR code as the common secret

    if login_result == ITSRestAPILogin.LoginUserResult.ok:
        # return a JSON that has Session, SessionID, multiple companies found = not present, ExpirationDateTime date time + 10 minutes (server based)
        return_obj['MultipleCompaniesFound'] = 'N'

        if not is_test_taking_user:
            # check if the company has MFA enabled
            with ITSRestAPIDB.session_scope("") as session:
                tempCompany = session.query(ITSRestAPIORMExtensions.SecurityCompany).filter(
                    ITSRestAPIORMExtensions.SecurityCompany.ID == found_company_id).first()

                if tempCompany.MFAEnabled:
                    # remove the current session token, a new token will be created after entering the MFA token or QR code
                    ITSRestAPILogin.delete_session_token(token)
                    return_obj['SessionID'] = ""
                    # check if the user already has a secret, if not the client must display a scan facility to register the shared secret
                    return_obj['MFAStatus'] = "QR"
                    user_secret_valid, user_secret = ITSRestAPILogin.get_user_secret(user_id, found_company_id, False)
                    if user_secret_valid and user_secret != "":
                        # If the user already has a secret then inform the client that the secret needs to be entered
                        return_obj['MFAStatus'] = "CODE"
                else:
                    pass
    if login_result == ITSRestAPILogin.LoginUserResult.multiple_companies_found:
        # return a JSON that has Session, SessionID, multiple companies found = T, ExpirationDateTime date time + 10 minutes (server based)
        return_obj['MultipleCompaniesFound'] = 'Y'
    return json.dumps(return_obj)


@app.route('/login/qrcode', methods=['GET'])
@limiter.limit("1/second")
def get_qr_code():
    # when the user is logged in a QR code for registering the shared secret can be requested
    user_id = request.headers['UserID']
    user_password = request.headers['Password']
    user_company = request.headers['CompanyID']
    ip_address = getIP(request)  # we need to check for ip in the future
    www = getWWWForToken(request)

    app_log.info('QR code for MFA login requested for %s %s %s %s', user_id, ip_address, www, request.host)

    login_result, found_company_id, is_test_taking_user = ITSRestAPILogin.login_user(user_id, user_password,
                                                                                     user_company)

    if login_result == ITSRestAPILogin.LoginUserResult.ok:
        # now return the QR code
        user_secret_valid, user_secret = ITSRestAPILogin.get_user_secret(user_id, user_company, True)
        if user_secret_valid:
            # turn this into qr code on client
            return 'otpauth://totp/{0}:{1}?secret={2}&issuer={0}'.format(www, user_id, user_secret)
        else:
            return 'User secret cannot be retrieved', 401
    else:
        # this will block a thread. A better solution would be nicer off course
        time.sleep(0.1)
        return 'User not found or password not valid', 401


@app.route('/login/mfacode', methods=['POST'])
@limiter.limit("1/second")
def process_mfa_code():
    # log the user in with the userid, password, mfa code, and company id
    # get the user id and password from the header
    user_id = request.headers['UserID']
    user_password = request.headers['Password']
    user_mfa_code = request.headers['MFACode'].replace(" ", "")
    user_company = request.headers['CompanyID']
    ip_address = getIP(request)  # we need to check for ip in the future
    www = getWWWForToken(request)

    app_log.info('MFA login started for %s %s %s %s', user_id, ip_address, www, request.host)

    login_result, found_company_id, is_test_taking_user = ITSRestAPILogin.login_user(user_id, user_password,
                                                                                     user_company)

    if login_result == ITSRestAPILogin.LoginUserResult.ok and not is_test_taking_user:
        # first check user id and password
        token = ITSRestAPILogin.create_session_token(user_id, found_company_id,
                                                     ITSRestAPILogin.LoginTokenType.regular_session)

        # now check the token
        token_ok = False

        user_secret_valid, user_secret = ITSRestAPILogin.get_user_secret(user_id, user_company, True)
        totp = pyotp.TOTP(user_secret)
        token_ok = totp.verify(user_mfa_code, valid_window=1)

        if token_ok and user_secret != "":
            app_log.info('MFA token assigned to %s %s %s %s %s', user_id, ip_address, www, request.host, token)

            now = datetime.now() + timedelta(0, 600);
            return_obj = {}
            return_obj['SessionID'] = token;
            return_obj['ExpirationDateTime'] = now.isoformat()
            return_obj['CompanyID'] = found_company_id
            return_obj['MFAStatus'] = "OK"
            return json.dumps(return_obj)
        else:
            # this will block a thread. A better solution would be nicer off course
            time.sleep(0.1)
            return 'Token not valid or expired, please try again', 401
    else:
        # this will block a thread. A better solution would be nicer off course
        time.sleep(0.1)
        return 'User not found or password not valid', 401


@app.route('/sendresetpassword', methods=['POST'])
@limiter.limit("1/second")
def send_reset_password():
    # send a mail with the reset password to the known email adress. If there is no known email adress return an error 404
    # otherwise return a 200 and send an email

    # get the user id and password from the header
    user_id = request.headers['Username']
    url_base = request.headers['BaseURL']
    langcode = request.headers['ITRLang']
    app_log.info('Sendresetpassword %s ', user_id)

    # check if we know this user
    if ITSRestAPILogin.check_if_user_account_is_valid(user_id) != ITSRestAPILogin.LoginUserResult.user_not_found:
        # store a temporary email token for a password reset link
        # return_obj = {}
        token = ITSRestAPILogin.create_session_token(user_id, ITSRestAPILogin.last_logged_in_company_id,
                                                     ITSRestAPILogin.LoginTokenType.password_reset)
        # return_obj['SessionID'] = token;
        # now = datetime.datetime.now() + datetime.timedelta(0, 600)
        # return_obj['ExpirationDateTime'] = now.isoformat()

        # and now sent an email to the user
        translatedSubject = ITSTranslate.get_translation_if_needed_from_file(langcode, 'PasswordResetMail.Subject',
                                                                             'Password reset mail', app_instance_path(),
                                                                             True)
        translatedMail = ITSTranslate.get_translation_if_needed_from_file(langcode, 'PasswordResetMail.Body',
                                                                          'You have requested a password reset. This link is valid for 5 minutes. Please copy & paste the following link in your browser window to reset your password : ',
                                                                          app_instance_path(), True)


        ITSMailer.send_mail('Master', translatedSubject,
                            translatedMail + "\r\n" +
                            url_base + "/?Token=" + token + "&Path=PasswordReset", user_id)

        return "An email is sent to the users known email address", 200
    else:
        return "User not found or no known email address linked to this user", 404


@app.route('/resetpassword', methods=['POST'])
@limiter.limit("1/second")
def reset_password():
    # get the user id and password from the header
    user_id = request.headers['Username']
    url_base = request.headers['BaseURL']
    langcode = request.headers['ITRLang']
    new_password = request.headers['Password']
    app_log.info('Resetpassword %s ', user_id)

    # check if we know this user
    if ITSRestAPILogin.check_if_user_account_is_valid(user_id) != ITSRestAPILogin.LoginUserResult.user_not_found:
        # check if the token is valid
        token = request.headers['SessionID']

        if ITSRestAPILogin.check_session_token(token) and len(new_password) > 6:
            ITSRestAPILogin.update_user_password(user_id, new_password)
            return "The password has been reset to the indicated password", 200
        else:
            return "Invalid data or expired token", 404
    else:
        return "User not found or no known email address linked to this user", 404


@app.route('/checktoken', methods=['POST'])
def check_token():
    token = request.headers['SessionID']
    app_log.info('Checktoken %s ', token)

    if ITSRestAPILogin.check_session_token(token):
        return "Token is valid", 200
    else:
        return "Invalid or expired token", 404


@app.route('/logout', methods=['POST'])
def logout():
    token = request.headers['SessionID']
    app_log.info('Logout %s ', token)

    if ITSRestAPILogin.check_session_token(token):
        ITSRestAPILogin.delete_session_token(token)
        return "User has been logged out", 200
    else:
        return "Invalid or expired token", 404


@app.route('/audittrail', methods=['GET'])
def clientauditlog_get():
    return ITSRestAPIORMExtensions.ClientAuditLog().common_paginated_read_request(request,
                                                                                  ITR_minimum_access_levels.regular_office_user)


@app.route('/audittrail/object/<identity>', methods=['GET'])
def clientauditlog_get_for_object(identity):
    additional_where_clause = 'ObjectID = \'' + str(uuid.UUID(str(identity))) + '\''

    return ITSRestAPIORMExtensions.ClientAuditLog().common_paginated_read_request(request,
                                                                                  ITR_minimum_access_levels.regular_office_user,
                                                                                  additional_where_clause)


@app.route('/audittrail/session/<identity>', methods=['GET'])
def clientauditlog_get_for_session(identity):
    additional_where_clause = 'SessionID = \'' + str(uuid.UUID(str(identity))) + '\''

    return ITSRestAPIORMExtensions.ClientAuditLog().common_paginated_read_request(request,
                                                                                  ITR_minimum_access_levels.regular_office_user,
                                                                                  additional_where_clause)

global lastObjectTypeCleanUp
lastObjectTypeCleanUp = ""
@app.route('/audittrail/objecttype/<identity>', methods=['GET'])
def clientauditlog_get_for_objecttype(identity):
    id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, translator_user, office_user, company_id, is_password_manager, master_header = check_master_header(
        request)

    global lastObjectTypeCleanUp

    additional_where_clause = 'ObjectType = \'' + str(int(str(identity))) + '\''

    # cleanup old object type logs
    if lastObjectTypeCleanUp != date.today():
        lastObjectTypeCleanUp = date.today()
        with ITSRestAPIDB.session_scope(company_id) as clientsession:
            clientsession.query(ITSRestAPIORMExtensions.ClientAuditLog).filter(
                ITSRestAPIORMExtensions.ClientAuditLog.ObjectType > 1000 ).filter(
                ITSRestAPIORMExtensions.ClientAuditLog.CreateDate <= date.today() - timedelta(days=90)
            ).delete()

    return ITSRestAPIORMExtensions.ClientAuditLog().common_paginated_read_request(request,
                                                                                  ITR_minimum_access_levels.organisation_supervisor,
                                                                                  additional_where_clause)


@app.route('/audittrail/<identity>', methods=['GET', 'POST', 'DELETE'])
def clientauditlog_get_id(identity):
    if request.method == 'GET':
        return ITSRestAPIORMExtensions.ClientAuditLog().return_single_object(request,
                                                                             ITR_minimum_access_levels.regular_office_user,
                                                                             identity)
    elif request.method == 'POST':
        return ITSRestAPIORMExtensions.ClientAuditLog().change_single_object(request,
                                                                             ITR_minimum_access_levels.regular_office_user,
                                                                             identity)
    elif request.method == 'DELETE':
        return ITSRestAPIORMExtensions.ClientAuditLog().delete_single_object(request,
                                                                             ITR_minimum_access_levels.master_user,
                                                                             identity)


@app.route('/batteries', methods=['GET'])
def batteries_get():
    return ITSRestAPIORMExtensions.ClientBatteries().common_paginated_read_request(request,
                                                                                   ITR_minimum_access_levels.regular_office_user)


@app.route('/batteries/<identity>', methods=['GET', 'POST', 'DELETE'])
def batteries_get_id(identity):
    if request.method == 'GET':
        return ITSRestAPIORMExtensions.ClientBatteries().return_single_object(request,
                                                                              ITR_minimum_access_levels.regular_office_user,
                                                                              identity)
    elif request.method == 'POST':
        return ITSRestAPIORMExtensions.ClientBatteries().change_single_object(request,
                                                                              ITR_minimum_access_levels.regular_office_user,
                                                                              identity)
    elif request.method == 'DELETE':
        return ITSRestAPIORMExtensions.ClientBatteries().delete_single_object(request,
                                                                              ITR_minimum_access_levels.regular_office_user,
                                                                              identity)


@app.route('/educations', methods=['GET'])
def educations_get():
    return ITSRestAPIORMExtensions.ClientEducation().common_paginated_read_request(request,
                                                                                   ITR_minimum_access_levels.regular_office_user)


@app.route('/educations/<identity>', methods=['GET', 'POST', 'DELETE'])
def educations_get_id(identity):
    if request.method == 'GET':
        return ITSRestAPIORMExtensions.ClientEducation().return_single_object(request,
                                                                              ITR_minimum_access_levels.regular_office_user,
                                                                              identity)
    elif request.method == 'POST':
        return ITSRestAPIORMExtensions.ClientEducation().change_single_object(request,
                                                                              ITR_minimum_access_levels.regular_office_user,
                                                                              identity)
    elif request.method == 'DELETE':
        return ITSRestAPIORMExtensions.ClientEducation().delete_single_object(request,
                                                                              ITR_minimum_access_levels.regular_office_user,
                                                                              identity)


@app.route('/generatedreports/<sourceid>', methods=['GET', 'DELETE'])
def generatedreports_get(sourceid):
    id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, translator_user, office_user, company_id, is_password_manager, master_header = check_master_header(
        request)

    if request.method == 'GET':
        additional_where_clause = 'LinkedObjectID = \'' + str(uuid.UUID(str(sourceid))) + '\''
        return ITSRestAPIORMExtensions.ClientGeneratedReport().common_paginated_read_request(request,
                                                                                             ITR_minimum_access_levels.regular_office_user,
                                                                                             additional_where_clause)
    elif request.method == 'DELETE':
        if office_user:
            # remove linked stored reports
            with ITSRestAPIDB.session_scope(company_id) as clientsession:
                clientsession.query(ITSRestAPIORMExtensions.ClientGeneratedReport).filter(
                    ITSRestAPIORMExtensions.ClientGeneratedReport.LinkedObjectID == sourceid
                ).delete()
        else:
            return "You do not have the rights to remove generated session reports", 403


@app.route('/generatedreports/<sourceid>/<identity>', methods=['GET', 'POST', 'DELETE'])
def generatedreports_get_id(sourceid, identity):
    if request.method == 'GET':
        return ITSRestAPIORMExtensions.ClientGeneratedReport().return_single_object(request,
                                                                                    ITR_minimum_access_levels.regular_office_user,
                                                                                    identity)
    elif request.method == 'POST':
        return ITSRestAPIORMExtensions.ClientGeneratedReport().change_single_object(request,
                                                                                    ITR_minimum_access_levels.regular_office_user,
                                                                                    identity)
    elif request.method == 'DELETE':
        return ITSRestAPIORMExtensions.ClientGeneratedReport().delete_single_object(request,
                                                                                    ITR_minimum_access_levels.regular_office_user,
                                                                                    identity)


@app.route('/groups', methods=['GET'])
def groups_get():
    return ITSRestAPIORMExtensions.ClientGroup().common_paginated_read_request(request,
                                                                               ITR_minimum_access_levels.regular_office_user)


@app.route('/groups/<identity>', methods=['GET', 'POST', 'DELETE'])
def groups_get_id(identity):
    if request.method == 'GET':
        return ITSRestAPIORMExtensions.ClientGroup().return_single_object(request,
                                                                          ITR_minimum_access_levels.regular_office_user,
                                                                          identity)
    elif request.method == 'POST':
        return ITSRestAPIORMExtensions.ClientGroup().change_single_object(request,
                                                                          ITR_minimum_access_levels.regular_office_user,
                                                                          identity)
    elif request.method == 'DELETE':
        return ITSRestAPIORMExtensions.ClientGroup().delete_single_object(request,
                                                                          ITR_minimum_access_levels.regular_office_user,
                                                                          identity)


@app.route('/nationalities', methods=['GET'])
def nationalities_get():
    return ITSRestAPIORMExtensions.ClientNationality().common_paginated_read_request(request,
                                                                                     ITR_minimum_access_levels.regular_office_user)


@app.route('/nationalities/<identity>', methods=['GET', 'POST', 'DELETE'])
def nationalities_get_id(identity):
    if request.method == 'GET':
        return ITSRestAPIORMExtensions.ClientNationality().return_single_object(request,
                                                                                ITR_minimum_access_levels.regular_office_user,
                                                                                identity)
    elif request.method == 'POST':
        return ITSRestAPIORMExtensions.ClientNationality().change_single_object(request,
                                                                                ITR_minimum_access_levels.regular_office_user,
                                                                                identity)
    elif request.method == 'DELETE':
        return ITSRestAPIORMExtensions.ClientNationality().delete_single_object(request,
                                                                                ITR_minimum_access_levels.regular_office_user,
                                                                                identity)


@app.route('/organisations', methods=['GET'])
def organisations_get():
    return ITSRestAPIORMExtensions.ClientOrganisation().common_paginated_read_request(request,
                                                                                      ITR_minimum_access_levels.regular_office_user)


@app.route('/organisations/<identity>', methods=['GET', 'POST', 'DELETE'])
def organisations_get_id(identity):
    if request.method == 'GET':
        return ITSRestAPIORMExtensions.ClientOrganisation().return_single_object(request,
                                                                                 ITR_minimum_access_levels.regular_office_user,
                                                                                 identity)
    elif request.method == 'POST':
        return ITSRestAPIORMExtensions.ClientOrganisation().change_single_object(request,
                                                                                 ITR_minimum_access_levels.regular_office_user,
                                                                                 identity)
    elif request.method == 'DELETE':
        return ITSRestAPIORMExtensions.ClientOrganisation().delete_single_object(request,
                                                                                 ITR_minimum_access_levels.regular_office_user,
                                                                                 identity)


@app.route('/persons', methods=['GET'])
def persons_get():
    return ITSRestAPIORMExtensions.ClientPerson().common_paginated_read_request(request,
                                                                                ITR_minimum_access_levels.regular_office_user)

@app.route('/persons/deleteunused', methods=['POST'])
def persons_delete_unused():
    id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, translator_user, office_user, company_id, is_password_manager, master_header = check_master_header(
        request)

    if office_user:
        ORMExtendedFunctions.remove_unused_user_logins(company_id)
        return "remove ok", 200
    else:
        return "Users cannot be deleted with your rights", 404

@app.route('/persons/<identity>', methods=['GET', 'POST', 'DELETE'])
def persons_get_id(identity):
    id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, translator_user, office_user, company_id, is_password_manager, master_header = check_master_header(
        request)
    if request.method == 'GET':
        # test taking user may read their own data (to do : make sure they can only read their own data!)
        to_return = ITSRestAPIORMExtensions.ClientPerson().return_single_object(request,
                                                                                ITR_minimum_access_levels.test_taking_user,
                                                                                identity)
        if test_taking_user and not office_user:
            try:
                if str(to_return["ID"]) != str(id_of_user):
                    return "Person cannot be accessed as test taking user", 404
            except:
                pass
            return to_return
        else:
            return to_return
    elif request.method == 'POST':
        with ITSRestAPIDB.session_scope(company_id) as session:
            # if the person is in the login table in the master database then delete & recreate the user
            tempPerson = ITSRestAPIORMExtensions.ClientPerson()
            company_id, filter_expression, include_archived, include_master, limit_by_user_id, master_only, page_size, proceed, record_filter, sort_fields, start_page, include_client, is_test_taking_user, user_id = tempPerson.check_and_parse_request_parameters(
                "", tempPerson, request, ITR_minimum_access_levels.test_taking_user)
            request.get_data()
            data = request.data
            data_dict = json.loads(data)
            # save the password of the candidates in the database (NEVER save the password for consultants)
            old_password = data_dict['Password']
            new_password = ""
            fix_password = False
            allowed_fields_to_update = [col.name for col in ITSRestAPIORMExtensions.ClientPerson.__table__.columns]
            if office_user:
                if data_dict['Password'] == "":
                    #no password is given but this might be an archived user with an old password in the user. Check that
                    tempPerson = session.query(ITSRestAPIORMExtensions.ClientPerson).filter(
                        ITSRestAPIORMExtensions.ClientPerson.ID == identity).first()
                    if tempPerson is not None:
                        data_dict['Password'] = ITSEncrypt.decrypt_string(tempPerson.Password)
                new_password = ITSRestAPILogin.create_or_update_testrun_user(data_dict['ID'], company_id,
                                                                             data_dict['EMail'], data_dict['Password'],
                                                                             data_dict['Active'], False)
                fix_password = (old_password != new_password and new_password != "") or old_password != ""
            allowed_fields_to_update.remove("Password")
            allowed_fields_to_update = ",".join(allowed_fields_to_update)
            if test_taking_user and not office_user:
                # check if the offered session is for this person
                request.get_data()
                data = request.data
                data_dict = json.loads(data)
                if str(data_dict["ID"]) != str(id_of_user):
                    return "Person cannot be updated as test taking user", 404
                allowed_fields_to_update = 'DateOfLastTest'

            to_return = ITSRestAPIORMExtensions.ClientPerson().change_single_object(request,
                                                                                    ITR_minimum_access_levels.test_taking_user,
                                                                                    identity, allowed_fields_to_update)
            if fix_password:
                tempPerson = session.query(ITSRestAPIORMExtensions.ClientPerson).filter(
                    ITSRestAPIORMExtensions.ClientPerson.ID == identity).first()
                tempPerson.Password = ITSEncrypt.encrypt_string(new_password)
                session.add(tempPerson)

            return to_return
    elif request.method == 'DELETE':
        # if the person is in the login table in the master database then delete the user and the related sessions
        if office_user:
            ITSRestAPILogin.delete_login(identity)
            with ITSRestAPIDB.session_scope(company_id) as session:
                session.query(ITSRestAPIORMExtensions.ClientSessionTest).filter(
                    ITSRestAPIORMExtensions.ClientSessionTest.PersID == identity).delete()
                session.query(ITSRestAPIORMExtensions.ClientSession).filter(
                    ITSRestAPIORMExtensions.ClientSession.PersonID == identity).delete()

                return ITSRestAPIORMExtensions.ClientPerson().delete_single_object(request,
                                                                                   ITR_minimum_access_levels.regular_office_user,
                                                                                   identity)


@app.route('/persons/<identity>/password', methods=['GET'])
def persons_get_id_password(identity):
    id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, translator_user, office_user, company_id, is_password_manager, master_header = check_master_header(
        request)

    if is_password_manager:
        with ITSRestAPIDB.session_scope(company_id) as qry_session:
            # save to the local master database
            user_found = qry_session.query(ITSRestAPIORMExtensions.ClientPerson).filter(
                ITSRestAPIORMExtensions.ClientPerson.ID == identity).first()
            return '{"Password":"' + ITSEncrypt.decrypt_string(user_found.Password) + '"}'
    else:
        return "You do not have the right to view a candidate password", 403


@app.route('/sessiontests', methods=['GET'])
def sessiontests_get():
    return ITSRestAPIORMExtensions.ClientSessionTest().common_paginated_read_request(request,
                                                                                     ITR_minimum_access_levels.regular_office_user)


@app.route('/sessiontestsview', methods=['GET'])
def sessiontestsview_get():
    a = ITSRestAPIORMExtensions.ViewClientSessionTestsWithPerson().common_paginated_read_request(request,
                                                                                                 ITR_minimum_access_levels.regular_office_user)
    return a


@app.route('/sessionsview', methods=['GET'])
def sessionsview_get():
    a = ITSRestAPIORMExtensions.ViewClientSessionsWithPerson().common_paginated_read_request(request,
                                                                                             ITR_minimum_access_levels.regular_office_user)
    return a


@app.route('/groupsessionsview', methods=['GET'])
def groupsessionsview_get():
    a = ITSRestAPIORMExtensions.ViewClientGroupSessions().common_paginated_read_request(request,
                                                                                        ITR_minimum_access_levels.regular_office_user)
    return a


@app.route('/sessiontests/<sessionid>', methods=['GET'])
def sessiontests_get_for_session(sessionid):
    additional_where_clause = "SessionID='" + str(sessionid) + "'"

    if request.method == 'GET':
        return ITSRestAPIORMExtensions.ClientSessionTest().common_paginated_read_request(request,
                                                                                         ITR_minimum_access_levels.regular_office_user,
                                                                                         additional_where_clause)


@app.route('/sessiontests/<sessionid>/<identity>', methods=['GET', 'POST', 'DELETE'])
def sessiontests_get_id(sessionid, identity):
    id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, translator_user, office_user, company_id, is_password_manager, master_header = check_master_header(
        request)

    try:
        langcode = request.headers['ITRLang']
    except:
        langcode = "en"

    if request.method == 'GET':
        to_return = ITSRestAPIORMExtensions.ClientSessionTest().return_single_object(request,
                                                                                     ITR_minimum_access_levels.regular_office_user,
                                                                                     identity)

        # before the test is returned to the client check if it is billed (but only when the test is done)
        try:
            json_obj = json.loads(to_return.data)
            if json_obj["Status"] >= 30:
                if not json_obj["Billed"]:
                    sessionTestPostTrigger(company_id, id_of_user, identity, langcode)
                    to_return = ITSRestAPIORMExtensions.ClientSessionTest().return_single_object(request,
                                                                                                 ITR_minimum_access_levels.regular_office_user,
                                                                                                 identity)
                    json_obj = json.loads(to_return.data)
                    if not json_obj["Billed"]:
                        return "The session test is not invoiced yet. Are you out of credits?", 403
        except:
            pass

        return to_return
    elif request.method == 'POST':
        to_return = ITSRestAPIORMExtensions.ClientSessionTest().change_single_object(request,
                                                                                     ITR_minimum_access_levels.regular_office_user,
                                                                                     identity)
        # now save the test session to the anonymous results, but only when it is done
        sessionTestPostTrigger(company_id, id_of_user, identity, langcode)

        return to_return
    elif request.method == 'DELETE':
        with ITSRestAPIDB.session_scope(company_id) as qry_session:
            temp_test = ITSRestAPIORMExtensions.ClientSessionTest().return_single_object(request,
                                                                                         ITR_minimum_access_levels.regular_office_user,
                                                                                         identity)
            json_obj = json.loads(temp_test.data)

            # save an audit trail record
            new_audit_trail = ITSRestAPIORMExtensions.ClientAuditLog()
            new_audit_trail.ID = uuid.uuid4()
            new_audit_trail.ObjectID = identity
            new_audit_trail.SessionID = str(json_obj["SessionID"])
            new_audit_trail.CompanyID = company_id
            new_audit_trail.UserID = id_of_user
            new_audit_trail.ObjectType = 2  # 2 = sessiontest
            new_audit_trail.OldData = ""
            new_audit_trail.NewData = '{ "TestID": ' + str(json_obj["TestID"]) + ' }'
            new_audit_trail.AuditMessage = "Session test deleted from session"
            new_audit_trail.MessageID = 4  # 4 = sessiontest delete
            new_audit_trail.CreateDate = datetime.now(timezone.utc)
            qry_session.add(new_audit_trail)

        return ITSRestAPIORMExtensions.ClientSessionTest().delete_single_object(request,
                                                                                ITR_minimum_access_levels.regular_office_user,
                                                                                identity)


def sessionTestPostTrigger(company_id, id_of_user, identity, langcode):
    temp_test = ITSRestAPIORMExtensions.ClientSessionTest().return_single_object(request,
                                                                                 ITR_minimum_access_levels.test_taking_user,
                                                                                 identity)
    json_obj = json.loads(temp_test.data)

    if int(json_obj["Status"]) >= 30:
        # save as anonymous data
        temp_dict = json_obj["Results"]
        for toplevelitem in temp_dict:
            try:
                for secondlevelitem in temp_dict[toplevelitem]:
                    for thirdlevelitem in temp_dict[toplevelitem][secondlevelitem]:
                        if thirdlevelitem == "Anonimise":
                            try:
                                if temp_dict[toplevelitem][secondlevelitem][thirdlevelitem]:
                                    json_obj["Results"][toplevelitem][secondlevelitem]["Value"] = "*ANONIMISED*"
                            except:
                                pass
            except:
                pass

        # save to the central server system
        # get the person, session, group and test data
        temp_person = ITSRestAPIORMExtensions.ClientPerson().return_single_object(request,
                                                                                  ITR_minimum_access_levels.test_taking_user,
                                                                                  json_obj['PersID'])
        temp_session = ITSRestAPIORMExtensions.ClientSession().return_single_object(request,
                                                                                    ITR_minimum_access_levels.test_taking_user,
                                                                                    json_obj['SessionID'])
        json_person_obj = json.loads(temp_person.data)
        json_session_obj = json.loads(temp_session.data)

        with ITSRestAPIDB.session_scope(company_id) as qry_session:
            with ITSRestAPIDB.session_scope("") as qry_session_master:
                # first save an audit trail record
                new_audit_trail = ITSRestAPIORMExtensions.ClientAuditLog()
                new_audit_trail.ID = uuid.uuid4()
                new_audit_trail.ObjectID = identity
                new_audit_trail.SessionID = str(json_obj["SessionID"])
                new_audit_trail.CompanyID = company_id
                new_audit_trail.UserID = id_of_user
                new_audit_trail.ObjectType = 2  # 2 = sessiontest
                new_audit_trail.OldData = str(json_obj["Results"])
                new_audit_trail.NewData = '{ "CurrentPage": ' + str(json_obj["CurrentPage"]) + ', "TestID" : "' + str(
                    json_obj["TestID"]) + '" }'
                new_audit_trail.AuditMessage = "Session test finished or viewed for test %%TestID%% at page %%CurrentPage%%"
                new_audit_trail.MessageID = 3  # 3 = sessiontest finished
                new_audit_trail.CreateDate = datetime.now(timezone.utc)
                qry_session.add(new_audit_trail)

                # get the test definition
                temp_testdef = qry_session.query(ITSRestAPIORMExtensions.Test).filter(
                    ITSRestAPIORMExtensions.Test.ID == json_obj['TestID']).first()
                if temp_testdef is None:
                    temp_testdef = qry_session_master.query(ITSRestAPIORMExtensions.Test).filter(
                        ITSRestAPIORMExtensions.Test.ID == json_obj['TestID']).first()
                temp_company = qry_session_master.query(ITSRestAPIORMExtensions.SecurityCompany).filter(
                    ITSRestAPIORMExtensions.SecurityCompany.ID == company_id).first()

                json_group_obj = ""
                temp_group = {}
                tempPersonData = {}

                # console test program to get to for example the anonise flag
                # app = Flask(__name__, instance_relative_config=True)
                # app.app_context()
                # qry_session = sessionmaker(bind=ITSRestAPIDB.get_db_engine_connection_client('015e1e32-4377-4a10-8312-4d4be357cc3c', False))()
                # temp_object = qry_session.query(ITSRestAPIORMExtensions.ClientSessionTest).filter(ITSRestAPIORMExtensions.ClientSessionTest.SessionID == '5834452d-c4e8-4d53-a701-c9cc6bca96c5').first()
                # temp_dict = json.loads(temp_object.Results) # of json_obj["Results"]
                # temp_dict['Question1']['Antwoord']['Anonimise']
                # for toplevelitem in temp_dict:
                #    for secondlevelitem in temp_dict[toplevelitem]:
                #        for thirdlevelitem in temp_dict[toplevelitem][secondlevelitem]:
                #            if thirdlevelitem == "Anonimise":
                #                try:
                #                    print(temp_dict[toplevelitem][secondlevelitem][thirdlevelitem])
                #                    if temp_dict[toplevelitem][secondlevelitem][thirdlevelitem]:
                #                     print(toplevelitem, secondlevelitem, thirdlevelitem,
                #                          temp_dict[toplevelitem][secondlevelitem]["Value"])
                #                     temp_dict[toplevelitem][secondlevelitem]["Value"] = "*ANONIMISED*"
                #                except:
                #                    pass

                if json_session_obj['GroupSessionID'] != '00000000-0000-0000-0000-000000000000':
                    try:
                        temp_group = ITSRestAPIORMExtensions.ClientSession().return_single_object(request,
                                                                                                  ITR_minimum_access_levels.test_taking_user,
                                                                                                  json_session_obj[
                                                                                                      'GroupSessionID'])
                        json_group_obj = json.loads(temp_group.data)
                        json_group_obj['PluginData'] = ""
                    except:
                        pass

                # check if a data gathering id for this test is already present
                with ITSRestAPIDB.session_scope("") as qry_session:
                    # save to the local master database
                    data_gathering = qry_session.query(ITSRestAPIORMExtensions.SecurityDataGathering).filter(
                        ITSRestAPIORMExtensions.SecurityDataGathering.SessionID == json_obj['SessionID']).filter(
                        ITSRestAPIORMExtensions.SecurityDataGathering.TestID == json_obj['TestID']).first()
                    if data_gathering == None:
                        data_gathering = ITSRestAPIORMExtensions.SecurityDataGathering()
                        data_gathering.ID = uuid.uuid4()
                    data_gathering.CompanyID = company_id
                    data_gathering.SessionID = json_obj['SessionID']
                    data_gathering.TestID = json_obj['TestID']
                    tempPersonData['Sex'] = json_person_obj['Sex']
                    tempPersonData['DateOfLastTest'] = json_person_obj['DateOfLastTest']
                    tempPersonData['BirthDate'] = json_person_obj['BirthDate']
                    tempPersonData['Age'] = json_person_obj['Age']
                    tempPersonData['UserDefinedFields'] = json_person_obj['UserDefinedFields']
                    data_gathering.PersonData = json.dumps(tempPersonData)
                    data_gathering.PluginData = "{}"
                    data_gathering.GroupData = json.dumps(json_group_obj)
                    data_gathering.SessionData = json.dumps(json_session_obj)
                    data_gathering.TestData = json.dumps(json_obj)

                    data_gathering.SessionDescription = json_session_obj['Description']
                    data_gathering.TestDescription = temp_testdef.Description
                    data_gathering.CompanyDescription = temp_company.CompanyName
                    try:
                        data_gathering.GroupDescription = json_group_obj['Description']
                    except:
                        pass
                    data_gathering.SessionEndData = json_session_obj['EndedAt']

                    qry_session.add(data_gathering)

                with ITSRestAPIDB.session_scope(company_id) as qry_session:
                    # save to the local master database
                    data_gathering = qry_session.query(ITSRestAPIORMExtensions.SecurityDataGathering).filter(
                        ITSRestAPIORMExtensions.SecurityDataGathering.SessionID == json_obj['SessionID']).filter(
                        ITSRestAPIORMExtensions.SecurityDataGathering.TestID == json_obj['TestID']).first()
                    if data_gathering == None:
                        data_gathering = ITSRestAPIORMExtensions.SecurityDataGathering()
                        data_gathering.ID = uuid.uuid4()
                    data_gathering.CompanyID = company_id
                    data_gathering.SessionID = json_obj['SessionID']
                    data_gathering.TestID = json_obj['TestID']
                    tempPersonData['Sex'] = json_person_obj['Sex']
                    tempPersonData['DateOfLastTest'] = json_person_obj['DateOfLastTest']
                    tempPersonData['BirthDate'] = json_person_obj['BirthDate']
                    tempPersonData['Age'] = json_person_obj['Age']
                    tempPersonData['UserDefinedFields'] = json_person_obj['UserDefinedFields']
                    data_gathering.PersonData = json.dumps(tempPersonData)
                    data_gathering.PluginData = "{}"
                    data_gathering.GroupData = json.dumps(json_group_obj)
                    data_gathering.SessionData = json.dumps(json_session_obj)
                    data_gathering.TestData = json.dumps(json_obj)

                    data_gathering.SessionDescription = json_session_obj['Description']
                    data_gathering.TestDescription = temp_testdef.Description
                    data_gathering.CompanyDescription = temp_company.CompanyName
                    try:
                        data_gathering.GroupDescription = json_group_obj['Description']
                    except:
                        pass
                    data_gathering.SessionEndData = json_session_obj['EndedAt']

                    qry_session.add(data_gathering)

                # now save to the central server using a json call
                tempPersonData['UserDefinedFields'] = ""
                data_gathering.PersonData = json.dumps(tempPersonData)
                # to do

        # invoice the test
        if int(json_obj["Status"]) == 30:
            with ITSRestAPIDB.session_scope("") as mastersession:
                with ITSRestAPIDB.session_scope(company_id) as clientsession:
                    # loop through all tests
                    invoicing_ok = False
                    creditunits_low = False
                    totalCosts = 0
                    clientsessiontest = clientsession.query(ITSRestAPIORMExtensions.ClientSessionTest).filter(
                        ITSRestAPIORMExtensions.ClientSessionTest.ID == json_obj["ID"]).first()

                    if not clientsessiontest.Billed:
                        # if this is a system local test then invoice the test in credit units
                        localtest = clientsession.query(ITSRestAPIORMExtensions.Test).filter(
                            ITSRestAPIORMExtensions.Test.ID == clientsessiontest.TestID).first()
                        if localtest == None:
                            localtest = mastersession.query(ITSRestAPIORMExtensions.Test).filter(
                                ITSRestAPIORMExtensions.Test.ID == clientsessiontest.TestID).first()
                        if localtest != None:
                            # start with the default costs for this test
                            totalCosts = localtest.Costs
                            localcompany = mastersession.query(ITSRestAPIORMExtensions.SecurityCompany).filter(
                                ITSRestAPIORMExtensions.SecurityCompany.ID == company_id).first()

                            # check if this company has an alternative cost for this test
                            try:
                                invoice_data = json.loads(localcompany.PluginData)
                                if invoice_data['Invoicing'][localtest.InvoiceCode].strip() != "":
                                    totalCosts = int(invoice_data['Invoicing'][localtest.InvoiceCode].strip())
                            except:
                                pass

                            # take the company discount and costs per test into account
                            if localcompany.CostsPerTestInUnits > 0:
                                totalCosts = totalCosts + localcompany.CostsPerTestInUnits
                            if localcompany.TestTakingDiscount > 0:
                                if localcompany.TestTakingDiscount > 100:
                                    localcompany.TestTakingDiscount = 100
                                totalCosts = int(totalCosts * (localcompany.TestTakingDiscount / 100))
                            if totalCosts < 0:
                                totalCosts = 0

                            # check if the current user has a personal credit pool
                            consultant = clientsession.query(ITSRestAPIORMExtensions.SecurityUser).filter(
                                ITSRestAPIORMExtensions.SecurityUser.ID == json_session_obj['ManagedByUserID']).first()

                            # check if we need invoicing
                            invoicing_ok = localtest.Costs == 0
                            if not invoicing_ok:
                                invoicing_ok = localcompany.TestTakingDiscount == 100
                            consultantHasPersonalCreditPool = False
                            if not invoicing_ok:
                                invoicing_ok = localcompany.CurrentCreditLevel > 0
                                # in principle this should be >= TotalCosts. But we give the customer a little headroom to view the last test
                                try:
                                    consultantHasPersonalCreditPool = consultant.HasPersonalCreditPool
                                    if consultant.HasPersonalCreditPool:
                                        invoicing_ok = consultant.CurrentPersonalCreditLevel > 0
                                except:
                                    pass
                            if not invoicing_ok and not consultantHasPersonalCreditPool:
                                invoicing_ok = localcompany.AllowNegativeCredits
                            if invoicing_ok and totalCosts > 0:
                                # create the records for invoice logging
                                if localtest.InvoiceCode == "" or localtest.InvoiceCode is None:
                                    localtest.InvoiceCode = localtest.TestName
                                newinvoicelog = ITSRestAPIORMExtensions.SecurityCreditUsage()
                                newinvoicelog.ID = uuid.uuid4()
                                newinvoicelog.UserID = id_of_user
                                newinvoicelog.CompanyID = company_id
                                newinvoicelog.InvoiceCode = localtest.InvoiceCode
                                newinvoicelog.OriginalTicks = localtest.Costs
                                newinvoicelog.DiscountedTicks = localtest.Costs - totalCosts
                                newinvoicelog.TotalTicks = totalCosts
                                newinvoicelog.UsageDateTime = datetime.now(timezone.utc)
                                newinvoicelog.SessionID = json_session_obj["ID"]
                                newinvoicelog.SessionName = json_session_obj["Description"]
                                newinvoicelog.UserName = json_person_obj["EMail"]
                                newinvoicelogM = ITSRestAPIORMExtensions.SecurityCreditUsage()
                                newinvoicelogM.ID = uuid.uuid4()
                                newinvoicelogM.UserID = id_of_user
                                newinvoicelogM.CompanyID = company_id
                                newinvoicelogM.InvoiceCode = localtest.InvoiceCode
                                newinvoicelogM.OriginalTicks = localtest.Costs
                                newinvoicelogM.DiscountedTicks = localtest.Costs - totalCosts
                                newinvoicelogM.TotalTicks = totalCosts
                                newinvoicelogM.UsageDateTime = datetime.now(timezone.utc)
                                newinvoicelogM.SessionID = json_session_obj["ID"]
                                newinvoicelogM.SessionName = json_session_obj["Description"]
                                newinvoicelogM.UserName = "*ANONIMISED*"

                                # store in master and client db in case client messes it up by hand
                                clientsession.add(newinvoicelog)
                                mastersession.add(newinvoicelogM)

                                # now execute the query to deduct the CurrentCreditLevel directly in the database (avoiding concurrency issues)
                                masterengine = ITSRestAPIDB.get_db_engine_connection_master()
                                qryCredit = 'UPDATE "SecurityCompanies" SET "CurrentCreditLevel" = "CurrentCreditLevel" - ' + str(
                                    totalCosts) + ' where "ID" = \'' + str(company_id) + '\' '
                                masterengine.execution_options(isolation_level="AUTOCOMMIT").execute(qryCredit)
                                app_log.info('Invoicing credits %s', qryCredit)
                                # and deduct if from the personal credit pool
                                try:
                                    if consultant.HasPersonalCreditPool:
                                        consultant.CurrentPersonalCreditLevel = consultant.CurrentPersonalCreditLevel - totalCosts
                                        app_log.info('Invoicing credits %s from personal credit pool of %s', qryCredit,
                                                     consultant.Email)
                                except:
                                    pass

                                # check if we need to send a credits low email later
                                if not creditunits_low:
                                    creditunits_low = localcompany.CurrentCreditLevel > localcompany.LowCreditWarningLevel and (
                                                localcompany.CurrentCreditLevel - totalCosts <= localcompany.LowCreditWarningLevel)

                            if invoicing_ok:
                                clientsessiontest.Billed = True

                    # if this is a commercial test then invoice in currency using the invoice server
                    # TO DO

                # score and norm the test if invoicing was successfull
                # this is done on the client. For commercial tests the complete definition is downloaded from the suppliers server.
                # please note that during test taking this information is NOT available as an option to prevent disclosing test details to the candidates
                # this means that tests and reports CANNOT be included in the session ready mail.

                # if credit units are low send the out of credits mail
                if creditunits_low:
                    this_company = mastersession.query(ITSRestAPIORMExtensions.SecurityCompany).filter(
                        ITSRestAPIORMExtensions.SecurityCompany.ID == company_id).first()

                    translatedSubject = ITSTranslate.get_translation_if_needed_from_file(langcode,
                                                                                         'OutOfCreditsMail.Subject',
                                                                                         'You are almost out of credits (%s left)',
                                                                                         app_instance_path(), True)
                    translatedMail = ITSTranslate.get_translation_if_needed_from_file(langcode,
                                                                                      'OutOfCreditsMail.Body',
                                                                                      'The credit level has gone below the credit warning level that you have indicated. Please add more credits to your system.',
                                                                                      app_instance_path(), True)

                    ITSMailer.send_mail(company_id, translatedSubject % this_company.CurrentCreditLevel,
                                        translatedMail,
                                        this_company.ContactEMail, consultant_id=id_of_user)
    else:
        with ITSRestAPIDB.session_scope(company_id) as qry_session:
            # always save an audit trail record
            new_audit_trail = ITSRestAPIORMExtensions.ClientAuditLog()
            new_audit_trail.ID = uuid.uuid4()
            new_audit_trail.ObjectID = identity
            new_audit_trail.SessionID = str(json_obj["SessionID"])
            new_audit_trail.CompanyID = company_id
            new_audit_trail.UserID = id_of_user
            new_audit_trail.ObjectType = 2  # 2 = sessiontest
            new_audit_trail.OldData = ""
            new_audit_trail.NewData = '{ "CurrentPage": ' + str(json_obj["CurrentPage"]) + ', "TestID" : "' + str(
                json_obj["TestID"]) + '" }'
            new_audit_trail.AuditMessage = "Session test updated for test %%TestID%% for page %%CurrentPage%%"
            new_audit_trail.MessageID = 2  # 2 = sessiontest updated
            new_audit_trail.CreateDate = datetime.now(timezone.utc)
            qry_session.add(new_audit_trail)


@app.route('/sessionteststaking/<sessionid>', methods=['GET'])
# copy of sessiontests point only for test taking users
def sessionteststaking_get(sessionid):
    id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, translator_user, office_user, company_id, is_password_manager, master_header = check_master_header(
        request)
    additional_where_clause = 'PersID=\'' + str(id_of_user) + "',SessionID='" + str(sessionid) + "'"
    return ITSRestAPIORMExtensions.ClientSessionTest().common_paginated_read_request(request,
                                                                                     ITR_minimum_access_levels.test_taking_user,
                                                                                     additional_where_clause)


@app.route('/sessionteststaking/<sessionid>/<identity>', methods=['GET', 'POST'])
def sessionteststaking_get_id(sessionid, identity):
    try:
        id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, translator_user, office_user, company_id, is_password_manager, master_header = check_master_header(
          request)
    except:
        return "Session expired", 403

    try:
        langcode = request.headers['ITRLang']
    except:
        langcode = "en"

    if request.method == 'GET':
        to_return = ITSRestAPIORMExtensions.ClientSessionTest().return_single_object(request,
                                                                                     ITR_minimum_access_levels.test_taking_user,
                                                                                     identity)
        try:
            if str(to_return["PersID"]) != str(id_of_user):
                return "Session cannot be accessed as test taking user", 404
        except:
            pass
        return to_return
    elif request.method == 'POST':
        # check if the request is for this person
        request.get_data()
        data = request.data
        data_dict = json.loads(data)
        if str(data_dict["PersID"]) != str(id_of_user):
            return  "Session cannot be updated as test taking user", 404
        results_limit = int( ITSRestAPISettings.get_setting_for_customer("", "MAX_RESULTS_LIMIT", true, ""))
        scores_limit = int( ITSRestAPISettings.get_setting_for_customer("", "MAX_SCORES_LIMIT", true, ""))
        plugin_data_limit = int( ITSRestAPISettings.get_setting_for_customer("", "MAX_PLUGINDATA_LIMIT", true, ""))

        if results_limit > 0 and len(str(data_dict["Results"])) > results_limit:
            app_log.error('Results field limit exceeded')
            return "Results field has exceeded maximum configured limit",429
        if scores_limit > 0 and len(str(data_dict["Scores"])) > scores_limit:
            app_log.error('Scores field limit exceeded')
            return "Scores field has exceeded maximum configured limit",429
        if plugin_data_limit > 0 and len(str(data_dict["PluginData"])) > plugin_data_limit:
            app_log.error('PluginData field limit exceeded')
            return "PluginData field has exceeded maximum configured limit",429

        # check if the session in the database is also for this person
        to_check = ITSRestAPIORMExtensions.ClientSessionTest().return_single_object(request,
                                                                                    ITR_minimum_access_levels.test_taking_user,
                                                                                    identity)
        jsonObj = json.loads(to_check.data)
        if str(jsonObj["PersID"]) != str(id_of_user) or str(jsonObj["SessionID"]) != str(sessionid):
            return  "Session cannot be updated as test taking user", 404

        to_return = ITSRestAPIORMExtensions.ClientSessionTest().change_single_object(request,
                                                                                     ITR_minimum_access_levels.test_taking_user,
                                                                                     identity,
                                                                                     'Results,Scores,TestStart,TestEnd,PercentageOfQuestionsAnswered,TotalTestTime,Status,CurrentPage,TotalPages,PluginData')

        sessionTestPostTrigger(company_id, id_of_user, identity, langcode)

        return to_return


@app.route('/sessions', methods=['GET'])
def sessions_get():
    id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, translator_user, office_user, company_id, is_password_manager, master_header = check_master_header(
        request)

    additional_where_clause = ""
    if test_taking_user and not office_user:
        additional_where_clause = 'PersonID=\'' + str(id_of_user) + '\''
    return ITSRestAPIORMExtensions.ClientSession().common_paginated_read_request(request,
                                                                                 ITR_minimum_access_levels.test_taking_user,
                                                                                 additional_where_clause)


@app.route('/sessions/<identity>/groupmembers', methods=['GET'])
def sessions_groupmembers(identity):
    additional_where_clause = 'parentsessionid=\'' + str(identity) + '\''
    return ITSRestAPIORMExtensions.ViewClientGroupSessionCandidates().common_paginated_read_request(request,
                                                                                                    ITR_minimum_access_levels.regular_office_user,
                                                                                                    additional_where_clause)

@app.route('/sessions/<identity>/<testid>/results', methods=['GET'])
def sessions_groupresults(identity, testid):
    # GroupSessionID on the session and TestID= on the session test
    id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, translator_user, office_user, company_id, is_password_manager, master_header = check_master_header(
        request)
    if request.method == 'GET':
        # get all the sessions and tests
        with ITSRestAPIDB.session_scope(company_id) as clientsession:
            # loop through all sessions and locate the test
            clientsessions = clientsession.query(ITSRestAPIORMExtensions.ClientSessionTest).filter(
                ITSRestAPIORMExtensions.ClientSessionTest.TestID == testid).join(
                ITSRestAPIORMExtensions.ClientSession, ITSRestAPIORMExtensions.ClientSessionTest.SessionID == ITSRestAPIORMExtensions.ClientSession.ID).filter(
                ITSRestAPIORMExtensions.ClientSession.GroupSessionID == identity).filter(
                ITSRestAPIORMExtensions.ClientSession.SessionType == 1).all()

            init_json = '{ "tests" : ['
            temp_json = init_json
            for elem in clientsessions:
                if temp_json != init_json:
                    temp_json += ","
                temp_json += json.dumps(elem.object_to_dict())
            temp_json += "]}"

            return temp_json, 200

    return "No access allowed", 403

@app.route('/sessions/<identity>/deletealltests', methods=['DELETE'])
def sessions_delete_tests(identity):
    # delete all tests from this session that have not been started yet
    id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, translator_user, office_user, company_id, is_password_manager, master_header = check_master_header(
        request)
    if request.method == 'DELETE':
        if office_user:
            with ITSRestAPIDB.session_scope(company_id) as qry_session:
                qry_session.query(ITSRestAPIORMExtensions.ClientSessionTest).filter(
                    ITSRestAPIORMExtensions.ClientSessionTest.SessionID == identity).filter(
                    ITSRestAPIORMExtensions.ClientSessionTest.Status == 10).delete()

                # save an audit trail record
                new_audit_trail = ITSRestAPIORMExtensions.ClientAuditLog()
                new_audit_trail.ID = uuid.uuid4()
                new_audit_trail.ObjectID = identity
                new_audit_trail.SessionID = identity
                new_audit_trail.CompanyID = company_id
                new_audit_trail.UserID = id_of_user
                new_audit_trail.ObjectType = 2  # 2 = sessiontest
                new_audit_trail.OldData = ""
                new_audit_trail.NewData = ""
                new_audit_trail.AuditMessage = "Session update : all ready tests will be redefined"
                new_audit_trail.MessageID = 5  # 4 = sessiontest list refresh
                new_audit_trail.CreateDate = datetime.now(timezone.utc)
                qry_session.add(new_audit_trail)

            return "OK", 200
        else:
            return "you do not have the rights to delete tests from the session", 403

@app.route('/sessions/group/<identity>', methods=['DELETE'])
def group_session_delete(identity):
    id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, translator_user, office_user, company_id, is_password_manager, master_header = check_master_header(
        request)

    if office_user:
        # delete this by using queries. This might be a HUGE amount of data.
        id = uuid.UUID(str(identity))
        connection = ITSRestAPIDB.get_db_engine_connection_client(company_id)
        try:
            # TO DO check and delete all users
            # select distinct "PersonID" FROM "ClientSessions"
            #            where "GroupSessionID" = '3da74613-0113-41a0-d580-c2912be76368' or "ID" = '3da74613-0113-41a0-d580-c2912be76368'
            # .filter((AddressBook.lastname == 'bulger') | (AddressBook.firstname == 'whitey'))
            users_to_check = []
            with ITSRestAPIDB.session_scope(company_id) as clientsession:
                session_list = clientsession.query(ITSRestAPIORMExtensions.ClientSession).filter(
                    (ITSRestAPIORMExtensions.ClientSession.ID == id) |
                    (ITSRestAPIORMExtensions.ClientSession.GroupSessionID == id)).all()
                for client_session in session_list:
                    users_to_check.append(client_session.PersonID)

            tempStr = """delete from "ClientAuditLog" where
                        "SessionID" in (
                         SELECT "ID" FROM "ClientSessions"
                        where "GroupSessionID" = '{id}' or "ID" = '{id}' ) """.format(id=id)
            app_log.info('Bulk query %s ', tempStr)
            connection.execution_options(isolation_level="AUTOCOMMIT").execute(tempStr)

            tempStr = """delete from "ClientSessionTests" where
                        "SessionID" in (
                         SELECT "ID" FROM "ClientSessions"
                        where "GroupSessionID" = '{id}' or "ID" = '{id}' ) """.format(id=id)
            app_log.info('Bulk query %s ', tempStr)
            connection.execution_options(isolation_level="AUTOCOMMIT").execute(tempStr)

            tempStr = """delete from "ClientGeneratedReports" where
                        "LinkedObjectID" in (
                         SELECT "ID" FROM "ClientSessions"
                        where "GroupSessionID" = '{id}' or "ID" = '{id}' ) """.format(id=id)
            app_log.info('Bulk query %s ', tempStr)
            connection.execution_options(isolation_level="AUTOCOMMIT").execute(tempStr)

            tempStr = """DELETE FROM "ClientSessions"
                        where "GroupSessionID" = '{id}' or "ID" = '{id}' """.format(id=id)
            app_log.info('Bulk query %s ', tempStr)
            connection.execution_options(isolation_level="AUTOCOMMIT").execute(tempStr)

            for checkuser in users_to_check:
                ORMExtendedFunctions.remove_unnecessary_user_logins(company_id, checkuser)
        finally:
            connection.dispose()

        connection = ITSRestAPIDB.get_db_engine_connection_master()
        try:
            tempStr = """DELETE FROM "ClientSessions"
                        where "GroupSessionID" = '{id}' or "ID" = '{id}' """.format(id=id)
            app_log.info('Bulk query %s ', tempStr)
            connection.execution_options(isolation_level="AUTOCOMMIT").execute(tempStr)
        finally:
            connection.dispose()

        return "ok"
    else:
        return "Session cannot be deleted as test taking user"

@app.route('/sessions/group/<identity>/archive', methods=['POST'])
def archive_sessions_group_on(identity):
    if archive_group_status_toggle(request, identity, False):
        return 'OK'
    else:
        return "Archive status cannot be changed with your permissions"

@app.route('/sessions/group/<identity>/unarchive', methods=['POST'])
def archive_sessions_group_offch(identity):
    if archive_group_status_toggle(request, identity, True):
        return 'OK'
    else:
        return "Archive status cannot be changed with your permissions"


def archive_group_status_toggle(request, session_id, archive_status):
    id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, translator_user, office_user, company_id, is_password_manager, master_header = check_master_header(
        request)

    if office_user:
        # delete this by using queries. This might be a HUGE amount of data.
        id = uuid.UUID(str(session_id))
        connection = ITSRestAPIDB.get_db_engine_connection_client(company_id)
        try:
            users_to_check = []
            with ITSRestAPIDB.session_scope(company_id) as clientsession:
                session_list = clientsession.query(ITSRestAPIORMExtensions.ClientSession).filter(
                    (ITSRestAPIORMExtensions.ClientSession.ID == id) |
                    (ITSRestAPIORMExtensions.ClientSession.GroupSessionID == id)).all()
                for client_session in session_list:
                    users_to_check.append(client_session.PersonID)

            tempStr = """UPDATE "ClientSessions"
                        set "Active" = {activeflag}
                        where "GroupSessionID" = '{id}' or "ID" = '{id}' """.format(id=id, activeflag=archive_status)
            app_log.info('Bulk query %s ', tempStr)
            connection.execution_options(isolation_level="AUTOCOMMIT").execute(tempStr)

            for thisuser in users_to_check:
                if archive_status:
                    ORMExtendedFunctions.reactivate_archived_user_logins(company_id, thisuser)
                else:
                    ORMExtendedFunctions.remove_unnecessary_user_logins(company_id, thisuser)
        finally:
            connection.dispose()
        return True
    else:
        return False

@app.route('/sessions/<identity>', methods=['GET', 'POST', 'DELETE'])
def sessions_get_id(identity):
    id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, translator_user, office_user, company_id, is_password_manager, master_header = check_master_header(
        request)
    try:
        langcode = request.headers['ITRLang']
    except:
        langcode = "en"

    if request.method == 'GET':
        # test taking user may read their own data (to do : make sure they can only read their own data!)
        to_return = ITSRestAPIORMExtensions.ClientSession().return_single_object(request,
                                                                                 ITR_minimum_access_levels.test_taking_user,
                                                                                 identity)
        if test_taking_user and not office_user:
            temp_return = json.loads(to_return.data)
            try:
                if str(temp_return["PersonID"]) != str(id_of_user):
                    return "Session cannot be accessed as test taking user", 404
            except:
                pass

            # now check if this is a public session. If so then clone the public session and return the new one
            if str(temp_return["SessionType"]) == "200" or str(temp_return["SessionType"]) == "1200" :
                token = request.headers['SessionID']
                company_id, user_id, token_validated, token_session_id = ITSRestAPILogin.get_info_with_session_token(
                    token)
                new_session_id = token_session_id
                ORMExtendedFunctions.clone_session(company_id, identity, new_session_id, 1, " " + datetime.now().strftime("%d-%b-%Y %H:%M"))

                return ITSRestAPIORMExtensions.ClientSession().return_single_object(request,
                                                                                 ITR_minimum_access_levels.test_taking_user,
                                                                                 new_session_id)
            else:
                return to_return
        else:
            return to_return
    elif request.method == 'POST':
        # test taking user may also post results (to do : make sure they can only post their own data!)
        allowed_fields_to_update = ''

        request.get_data()
        data = request.data
        data_dict = json.loads(data)

        if test_taking_user and not office_user:
            # check if the offered session is for this person
            if str(data_dict["PersonID"]) != str(id_of_user):
                return "Session cannot be updated as test taking user", 404

            plugin_data_limit = int(ITSRestAPISettings.get_setting_for_customer("", "MAX_PLUGINDATA_LIMIT", true, ""))

            if plugin_data_limit > 0 and len(str(data_dict["PluginData"])) > plugin_data_limit:
                app_log.error('PluginData field limit exceeded')
                return "PluginData field has exceeded maximum configured limit", 429

            # check if the session in the database is also for this person
            to_return = ITSRestAPIORMExtensions.ClientSession().return_single_object(request,
                                                                                     ITR_minimum_access_levels.test_taking_user,
                                                                                     identity)

            try:
                if to_return["PersonID"] != id_of_user or to_return["ID"] != data_dict["ID"]:
                    return "Session cannot be updated as test taking user", 404
            except:
                pass

            allowed_fields_to_update = 'Status,SessionState,StartedAt,EndedAt,PluginData'

        if office_user:
            # check if there is a short login code. If so AND this is a group session type (200 or 1200) then save the session in the master database as well.
            if ( str(data_dict["SessionType"]) == "200" or str(data_dict["SessionType"]) == "1200" ) and (str(data_dict["ShortLoginCode"]) != ""):
                ITSRestAPIORMExtensions.ClientSession().change_single_object(request,
                                                                             ITR_minimum_access_levels.test_taking_user,
                                                                             identity, "", True)

        to_return = ITSRestAPIORMExtensions.ClientSession().change_single_object(request,
                                                                                 ITR_minimum_access_levels.test_taking_user,
                                                                                 identity, allowed_fields_to_update)

        # perform the session post trigger
        sessionPostTrigger(company_id, id_of_user, identity, data_dict, request, langcode)

        return to_return
    elif request.method == 'DELETE':
        return ORMExtendedFunctions.delete_session(request, company_id, identity)


def sessionPostTrigger(company_id, id_of_user, identity, data_dict, request, langcode):
    # send the end session e-mail
    if int(data_dict["Status"]) == 30:
        with ITSRestAPIDB.session_scope(company_id) as clientsession:
            temp_session = clientsession.query(ITSRestAPIORMExtensions.ClientSession).filter(
                ITSRestAPIORMExtensions.ClientSession.ID == data_dict["ID"]).first()

            temp_session.Status = 31

            url_to_click = request.url_root
            url_to_click = url_to_click.split("api/")[0] + "default.htm"

            translatedSubject = ITSTranslate.get_translation_if_needed_from_file(langcode,
                                                                                 'SessionReadyMail.Subject',
                                                                                 'Session %s is ready for reporting',
                                                                                 app_instance_path(), True)
            translatedMail = ITSTranslate.get_translation_if_needed_from_file(langcode, 'SessionReadyMail.Body',
                                                                              "The following session has completed : \r\n%s" + "\r\n\r\n",
                                                                              app_instance_path(), True)
            if translatedSubject is None:
                translatedSubject = "Session %s is ready for reporting"
            if translatedMail is None:
                translatedMail = "The following session has completed : \r\n\r\n%s"

            if (temp_session.SessionType != 1 or temp_session.EMailNotificationAdresses != '') and temp_session.Active:
                ITSMailer.send_mail(company_id, translatedSubject % temp_session.Description,
                                translatedMail % temp_session.Description +
                                "\r\n\r\n%s" % url_to_click,
                                temp_session.EMailNotificationAdresses, session_id=data_dict["ID"], consultant_id=id_of_user)

            ORMExtendedFunctions.remove_unnecessary_user_logins(company_id, temp_session.PersonID)

            # Save an audit trail record
            new_audit_trail = ITSRestAPIORMExtensions.ClientAuditLog()
            new_audit_trail.ID = uuid.uuid4()
            new_audit_trail.ObjectID = identity
            new_audit_trail.SessionID = identity
            new_audit_trail.CompanyID = company_id
            new_audit_trail.UserID = id_of_user
            new_audit_trail.ObjectType = 1  # 1 = session
            new_audit_trail.OldData = ""
            new_audit_trail.NewData = '{ "SessionStatus": ' + str(temp_session.Status) + '}'
            new_audit_trail.AuditMessage = "Session updated to status %%SessionStatus%%"
            new_audit_trail.MessageID = 1  # 1 = session updated
            new_audit_trail.CreateDate = datetime.now(timezone.utc)
            clientsession.add(new_audit_trail)

    else:
        with ITSRestAPIDB.session_scope(company_id) as qry_session:
            sess = qry_session.query(ITSRestAPIORMExtensions.ClientSession).filter(
                ITSRestAPIORMExtensions.ClientSession.ID == identity).first()

            # Save an audit trail record
            new_audit_trail = ITSRestAPIORMExtensions.ClientAuditLog()
            new_audit_trail.ID = uuid.uuid4()
            new_audit_trail.ObjectID = identity
            new_audit_trail.SessionID = identity
            new_audit_trail.CompanyID = company_id
            new_audit_trail.UserID = id_of_user
            new_audit_trail.ObjectType = 1  # 1 = session
            new_audit_trail.OldData = ""
            new_audit_trail.NewData = '{ "SessionStatus": ' + str(sess.Status) + '}'
            new_audit_trail.AuditMessage = "Session updated to status %%SessionStatus%%"
            new_audit_trail.MessageID = 1  # 1 = session updated
            new_audit_trail.CreateDate = datetime.now(timezone.utc)
            qry_session.add(new_audit_trail)

            if sess:
                ORMExtendedFunctions.remove_unnecessary_user_logins(company_id, sess.PersonID)


@app.route('/reportdefinitions', methods=['GET'])
def reportdefinition_get():
    return ITSRestAPIORMExtensions.Report().common_paginated_read_request(request,
                                                                          ITR_minimum_access_levels.regular_office_user)


@app.route('/reportdefinitions/<identity>', methods=['GET', 'POST', 'DELETE'])
def reportdefinition_get_id(identity):
    basepathname = os.path.dirname(os.path.join(os.sep, app_instance_path(), 'cache'))
    pathname = os.path.dirname(
        os.path.join(os.sep, app_instance_path(), 'cache', ITSHelpers.string_split_to_filepath(identity)))
    include_master = False
    try:
        include_master = request.headers['IncludeMaster'] == "Y"
    except:
        pass
    cachedfilename = os.path.join(os.sep, pathname, "master_report.json") if include_master else os.path.join(os.sep,
                                                                                                              pathname,
                                                                                                              "report.json")

    if request.method == 'GET':
        if os.path.isfile(cachedfilename):
            return (open(cachedfilename, 'r').read()), 200
        else:
            to_return = ITSRestAPIORMExtensions.Report().return_single_object(request,
                                                                              ITR_minimum_access_levels.test_taking_user,
                                                                              identity)
            try:
                if to_return[1] == 404:
                    to_return = ITSRestAPIORMExtensions.Report().return_single_object(request,
                                                                                      ITR_minimum_access_levels.test_taking_user,
                                                                                      identity, True)
            except:
                pass

            try:
                if to_return.status == "200 OK":
                    if not os.path.exists(pathname):
                        os.makedirs(pathname)
                    text_file = open(cachedfilename, "w")
                    text_file.write(json.dumps(to_return.json))
                    text_file.close()
            except:
                pass

            return to_return
    elif request.method == 'POST':
        if os.path.exists(pathname):
            ITSHelpers.remove_folder(pathname, basepathname)
        return ITSRestAPIORMExtensions.Report().change_single_object(request,
                                                                     ITR_minimum_access_levels.report_author,
                                                                     identity)
    elif request.method == 'DELETE':
        if os.path.exists(pathname):
            ITSHelpers.remove_folder(pathname, basepathname)
        return ITSRestAPIORMExtensions.Report().delete_single_object(request,
                                                                     ITR_minimum_access_levels.report_author,
                                                                     identity)


@app.route('/companies', methods=['GET'])
def companies_get():
    return ITSRestAPIORMExtensions.SecurityCompany().common_paginated_read_request(request,
                                                                                   ITR_minimum_access_levels.master_user,
                                                                                   "", "",
                                                                                   True)


@app.route('/companies/<identity>', methods=['GET', 'POST', 'DELETE'])
def companies_get_id(identity):
    allowTestTakingUser = false
    token = request.headers['SessionID']

    id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, translator_user, office_user, company_id, is_password_manager, master_header = check_master_header(
        request)
    if identity == "currentcompany":
        identity = company_id
        allowTestTakingUser = true

    if request.method == 'GET':
        if allowTestTakingUser:
            return ITSRestAPIORMExtensions.SecurityCompany().return_single_object(request,
                                                                                  ITR_minimum_access_levels.test_taking_user,
                                                                                  identity, True)
        else:
            if identity == company_id and not master_user:
                return ITSRestAPIORMExtensions.SecurityCompany().return_single_object(request,
                                                                                      ITR_minimum_access_levels.regular_office_user,
                                                                                      identity, True)
            if master_user:
                return ITSRestAPIORMExtensions.SecurityCompany().return_single_object(request,
                                                                                      ITR_minimum_access_levels.regular_office_user,
                                                                                      identity, True)
    elif request.method == 'POST' and master_user:
        return ITSRestAPIORMExtensions.SecurityCompany().change_single_object(request,
                                                                              ITR_minimum_access_levels.master_user,
                                                                              identity, "", True)
    elif request.method == 'DELETE' and master_user:
        company_id, user_id, token_validated, token_session_id = ITSRestAPILogin.get_info_with_session_token(token)

        # delete the database
        try:
            ITSRestAPIDB.drop_database(identity)
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            app_log.info('Database drop failed for %s. Trace %s', company_id, ''.join(' ' + line for line in lines))

        # delete the logins
        ITSRestAPILogin.delete_all_company_users(identity)
        # delete the credit grants
        with ITSRestAPIDB.session_scope("") as session:
            session.query(ITSRestAPIORMExtensions.SecurityCreditGrant).filter(
                ITSRestAPIORMExtensions.SecurityCreditGrant.CompanyID == identity).delete()
        # delete the credit usages
        with ITSRestAPIDB.session_scope("") as session:
            session.query(ITSRestAPIORMExtensions.SecurityCreditUsage).filter(
                ITSRestAPIORMExtensions.SecurityCreditUsage.CompanyID == identity).delete()

        # delete any stored files
        folder_to_delete = os.path.join(os.sep, app_instance_path(), 'media', str(identity))
        shutil.rmtree(folder_to_delete, ignore_errors=True)

        return ITSRestAPIORMExtensions.SecurityCompany().delete_single_object(request,
                                                                              ITR_minimum_access_levels.master_user,
                                                                              identity, True)

    return "You need to be master user to make this call with these parameters", 403


creditgrants_checkdate = ""
@app.route('/creditgrants', methods=['GET'])
def creditgrants_get():
    global creditgrants_checkdate
    token = request.headers['SessionID']
    company_id, user_id, token_validated, token_session_id = ITSRestAPILogin.get_info_with_session_token(token)
    id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, author_report_user, author_test_screen_templates_user, translator_user, office_user, is_password_manager, is_researcher = ITSRestAPILogin.get_id_of_user_with_token_and_company_id(
        user_id, company_id)

    if master_user:
        return ITSRestAPIORMExtensions.SecurityCreditGrant().common_paginated_read_request(request,
                                                                                           ITR_minimum_access_levels.master_user,
                                                                                           "", "", True)
    else:
        if creditgrants_checkdate != datetime.now().strftime("%D"):
            creditgrants_checkdate = datetime.now().strftime("%D")

            qryDelete10Years = 'DELETE FROM "SecurityCreditGrants" where DATE_PART(\'year\', "GrantedWhen"::date) < date_part(\'year\', CURRENT_DATE)-10'
            masterengine = ITSRestAPIDB.get_db_engine_connection_master()
            masterengine.execution_options(isolation_level="AUTOCOMMIT").execute(qryDelete10Years)
            clientengine = ITSRestAPIDB.get_db_engine_connection_client(company_id)
            clientengine.execution_options(isolation_level="AUTOCOMMIT").execute(qryDelete10Years)

        additional_where_clause = "CompanyID='" + str(company_id) + "'"
        return ITSRestAPIORMExtensions.SecurityCreditGrant().common_paginated_read_request(request,
                                                                                           ITR_minimum_access_levels.regular_office_user,
                                                                                           additional_where_clause, "",
                                                                                           True)

    return "You need to be master user, or query the grants for your own organisation", 403


@app.route('/creditgrants/<identity>', methods=['GET', 'POST', 'DELETE'])
def creditgrants_get_id(identity):
    if request.method == 'GET':
        return ITSRestAPIORMExtensions.SecurityCreditGrant().return_single_object(request,
                                                                                  ITR_minimum_access_levels.master_user,
                                                                                  identity, True)
    elif request.method == 'POST':
        # increase the companies credit level with the saved credit grant
        token = request.headers['SessionID']
        company_id, user_id, token_validated, token_session_id = ITSRestAPILogin.get_info_with_session_token(token)
        id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, author_report_user, author_test_screen_templates_user, translator_user, office_user, is_password_manager, is_researcher = ITSRestAPILogin.get_id_of_user_with_token_and_company_id(
            user_id, company_id)

        if master_user:
            request.get_data()
            data = request.data
            data_dict = json.loads(data)

            masterengine = ITSRestAPIDB.get_db_engine_connection_master()
            qryToAdd = 'UPDATE "SecurityCompanies" SET "CurrentCreditLevel" = "CurrentCreditLevel" + ' + str(
                data_dict["CreditsGranted"]) + ' where "ID" = \'' + str(data_dict["CompanyID"]) + '\' '
            app_log.info('Adding credits ' + qryToAdd)
            masterengine.execution_options(isolation_level="AUTOCOMMIT").execute(qryToAdd)

        return ITSRestAPIORMExtensions.SecurityCreditGrant().change_single_object(request,
                                                                                  ITR_minimum_access_levels.master_user,
                                                                                  identity, "", True)
    elif request.method == 'DELETE':
        return ITSRestAPIORMExtensions.SecurityCreditGrant().delete_single_object(request,
                                                                                  ITR_minimum_access_levels.master_user,
                                                                                  identity, True)


creditusages_checkdate = ""
@app.route('/creditusages', methods=['GET'])
def creditusage_get():
    global creditusages_checkdate
    token = request.headers['SessionID']
    company_id, user_id, token_validated, token_session_id = ITSRestAPILogin.get_info_with_session_token(token)

    if creditusages_checkdate != datetime.now().strftime("%D"):
        creditusages_checkdate = datetime.now().strftime("%D")

        qryDelete7Years = 'DELETE FROM "SecurityCreditUsage" where DATE_PART(\'year\', "UsageDateTime"::date) < date_part(\'year\', CURRENT_DATE)-7'
        qryDelete3Years = 'DELETE FROM "SecurityCreditUsage" where DATE_PART(\'year\', "UsageDateTime"::date) < date_part(\'year\', CURRENT_DATE)-2'
        masterengine = ITSRestAPIDB.get_db_engine_connection_master()
        masterengine.execution_options(isolation_level="AUTOCOMMIT").execute(qryDelete7Years)
        clientengine = ITSRestAPIDB.get_db_engine_connection_client(company_id)
        clientengine.execution_options(isolation_level="AUTOCOMMIT").execute(qryDelete3Years)

    return ITSRestAPIORMExtensions.SecurityCreditUsage().common_paginated_read_request(request,
                                                                                       ITR_minimum_access_levels.regular_office_user)


@app.route('/creditusagespermonth', methods=['GET'])
def creditusagespermonth_get():
    token = request.headers['SessionID']
    company_id, user_id, token_validated, token_session_id = ITSRestAPILogin.get_info_with_session_token(token)
    if company_id != "":
     id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, author_report_user, author_test_screen_templates_user, translator_user, office_user, is_password_manager, is_researcher = ITSRestAPILogin.get_id_of_user_with_token_and_company_id(
        user_id, company_id)

    if company_id != "" and office_user:
        qry_session = ITSRestAPIDB.get_db_engine_connection_client(company_id)
        try:
            a = []
            a = qry_session.execute(
                'select date_part( \'year\', "UsageDateTime") as Year, date_part( \'month\', "UsageDateTime") as Month, sum("TotalTicks") as Ticks, sum("DiscountedTicks") as DiscountedTicks ' +
                'from "SecurityCreditUsage"' +
                'where "UsageDateTime" >= make_date(CAST(date_part( \'year\', CURRENT_DATE)-2 AS INT), 1, 1)' +
                'group by date_part( \'year\', "UsageDateTime"), date_part( \'month\', "UsageDateTime") ' +
                'order by date_part( \'year\', "UsageDateTime") desc, date_part( \'month\', "UsageDateTime") desc ').fetchall()
            if a == []:
                a.append({'Year': '2000', 'Month': '1', 'Ticks': '0', 'DiscountedTicks': '0'})
        finally:
            qry_session.dispose()
        return ITSRestAPIDB.query_array_to_jsonify(a)
    else:
        return "404", "No valid session token"


@app.route('/creditusagespermonthforall/<year>', methods=['GET'])
def creditusagespermonthforall_get(year):
    token = request.headers['SessionID']
    company_id, user_id, token_validated, token_session_id = ITSRestAPILogin.get_info_with_session_token(token)
    id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, author_report_user, author_test_screen_templates_user, translator_user, office_user, is_password_manager, is_researcher = ITSRestAPILogin.get_id_of_user_with_token_and_company_id(
        user_id, company_id)

    if company_id != "" and master_user:
        qry_session = ITSRestAPIDB.get_db_engine_connection_master()
        try:
            yearfilter = ''
            if int(year) > 0:
                yearfilter = 'where "UsageDateTime" >= make_date(CAST(' + year + ' AS INT), 1, 1) and "UsageDateTime" <= make_date(CAST(' + year + ' AS INT), 12, 31) '
            query = ''' select date_part( 'year', "UsageDateTime") as Year, date_part( 'month', "UsageDateTime") as Month, sum("TotalTicks") as Ticks, sum("DiscountedTicks") as DiscountedTicks, "InvoiceCode", B."CompanyName", B."ID"
                    from "SecurityCreditUsage" A left join "SecurityCompanies" B on A."CompanyID" = B."ID" ''' + yearfilter + '''
                    group by date_part( 'year', "UsageDateTime"), date_part( 'month', "UsageDateTime"), "InvoiceCode", B."CompanyName", B."ID"
                    order by date_part( 'year', "UsageDateTime") desc, date_part( 'month', "UsageDateTime") desc, "InvoiceCode", B."CompanyName" '''

            a = []
            a = qry_session.execute(query).fetchall()
            if a == []:
                a.append({'Year': '2000', 'Month': '1', 'Ticks': '0', 'DiscountedTicks': '0'})
        finally:
            qry_session.dispose()
        return ITSRestAPIDB.query_array_to_jsonify(a)
    else:
        return "404", "No valid session token"


@app.route('/creditusages/<identity>', methods=['GET', 'POST', 'DELETE'])
def creditusage_get_id(identity):
    if request.method == 'GET':
        return ITSRestAPIORMExtensions.SecurityCreditUsage().return_single_object(request,
                                                                                  ITR_minimum_access_levels.regular_office_user,
                                                                                  identity)
    elif request.method == 'POST':
        return ITSRestAPIORMExtensions.SecurityCreditUsage().change_single_object(request,
                                                                                  ITR_minimum_access_levels.master_user,
                                                                                  identity)
    elif request.method == 'DELETE':
        return ITSRestAPIORMExtensions.SecurityCreditUsage().delete_single_object(request,
                                                                                  ITR_minimum_access_levels.master_user,
                                                                                  identity)


@app.route('/datagathering', methods=['GET'])
def datagathering_get():
    return ITSRestAPIORMExtensions.SecurityDataGathering().common_paginated_read_request(request,
                                                                                         ITR_minimum_access_levels.data_researcher)


@app.route('/datagathering/<identity>', methods=['GET', 'POST', 'DELETE'])
def datagathering_get_id(identity):
    if request.method == 'GET':
        return ITSRestAPIORMExtensions.SecurityDataGathering().return_single_object(request,
                                                                                    ITR_minimum_access_levels.data_researcher,
                                                                                    identity)
    elif request.method == 'POST':
        return ITSRestAPIORMExtensions.SecurityDataGathering().change_single_object(request,
                                                                                    ITR_minimum_access_levels.data_researcher,
                                                                                    identity)
    elif request.method == 'DELETE':
        return ITSRestAPIORMExtensions.SecurityDataGathering().delete_single_object(request,
                                                                                    ITR_minimum_access_levels.data_researcher,
                                                                                    identity)


@app.route('/rightstemplates', methods=['GET'])
def rightstemplates_get():
    return ITSRestAPIORMExtensions.SecurityTemplate().common_paginated_read_request(request,
                                                                                    ITR_minimum_access_levels.regular_office_user)


@app.route('/rightstemplates/<identity>', methods=['GET', 'POST', 'DELETE'])
def rightstemplates_get_id(identity):
    if request.method == 'GET':
        return ITSRestAPIORMExtensions.SecurityTemplate().return_single_object(request,
                                                                               ITR_minimum_access_levels.regular_office_user,
                                                                               identity)
    elif request.method == 'POST':
        return ITSRestAPIORMExtensions.SecurityTemplate().change_single_object(request,
                                                                               ITR_minimum_access_levels.organisation_supervisor,
                                                                               identity)
    elif request.method == 'DELETE':
        return ITSRestAPIORMExtensions.SecurityTemplate().delete_single_object(request,
                                                                               ITR_minimum_access_levels.organisation_supervisor,
                                                                               identity)


@app.route('/logins', methods=['GET'])
def logins_get():
    token = request.headers['SessionID']
    company_id, user_id, token_validated, token_session_id = ITSRestAPILogin.get_info_with_session_token(token)

    if company_id == "":
        return "This API is only available to logged in office users", 403

    id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, author_report_user, author_test_screen_templates_user, translator_user, office_user, is_password_manager, is_researcher = ITSRestAPILogin.get_id_of_user_with_token_and_company_id(
        user_id, company_id)

    additional_where_clause = ""
    if (not master_user) :
        additional_where_clause = "IsMasterUser = false"

    return ITSRestAPIORMExtensions.SecurityUser().common_paginated_read_request(request,
                                                                                ITR_minimum_access_levels.regular_office_user,
                                                                                additional_where_clause)


@app.route('/logins/<identity>', methods=['GET', 'POST', 'DELETE'])
def logins_get_id(identity):
    # get the session id and the user id from the token
    master_db_query = False
    token = request.headers['SessionID']
    company_id, user_id, token_validated, token_session_id = ITSRestAPILogin.get_info_with_session_token(token)
    id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, author_report_user, author_test_screen_templates_user, translator_user, office_user, is_password_manager, is_researcher = ITSRestAPILogin.get_id_of_user_with_token_and_company_id(
        user_id, company_id)
    if identity == 'currentuser':
        identity = id_of_user
        # master_db_query = True
    else:
        if not organisation_supervisor_user and not master_user:
            return "You are not allowed to change other users settings", 403

    if request.method == 'GET':
        to_return = ITSRestAPIORMExtensions.SecurityUser().return_single_object(request,
                                                                                ITR_minimum_access_levels.test_taking_user,
                                                                                identity)
        # if not found then try the master database as well, candidates will NOT be created in the local company database
        try:
            if to_return[1] == 404:
                to_return = ITSRestAPIORMExtensions.SecurityUser().return_single_object(request,
                                                                                        ITR_minimum_access_levels.test_taking_user,
                                                                                        identity, True)
        except:
            pass

        # decrypt the API key if present
        if is_password_manager:
            temp_return = json.loads(to_return.data)
            try:
                temp_return['APIKey'] = ITSEncrypt.decrypt_string(temp_return['APIKey'])
                to_return = json.dumps(temp_return)
            except:
                pass

        return to_return
    elif request.method == 'POST':
        with ITSRestAPIDB.session_scope(company_id) as clientsession:
            # clientsession = sessionmaker(bind=ITSRestAPIDB.get_db_engine_connection_client(company_id))()
            # make sure that a new account cannot be added when the system is already at the maximum amount of consultants
            max_number_of_consultants = ITSRestAPISettings.get_setting_for_customer(company_id,
                                                                                    'MAXNUMBEROFCONSULTANTS', True, "")
            if max_number_of_consultants != "":
                max_number_of_consultants = int(max_number_of_consultants)
                if max_number_of_consultants >= 0:
                    consultant_count = clientsession.query(ITSRestAPIORMExtensions.SecurityUser).count()
                    if (consultant_count >= max_number_of_consultants):
                        # check if this is a new account, in that case abort
                        consultant_to_add_check = clientsession.query(ITSRestAPIORMExtensions.SecurityUser).filter(
                            ITSRestAPIORMExtensions.SecurityUser.ID == identity).count()
                        if (consultant_to_add_check == 0):
                            return "Maximum number of consultants reached", 404
            # make sure the current user cannot grant more rights than the user itself owns
            consultant = clientsession.query(ITSRestAPIORMExtensions.SecurityUser).filter(
                ITSRestAPIORMExtensions.SecurityUser.ID == id_of_user).first()
            AllowedFieldsToChange = [col.name for col in ITSRestAPIORMExtensions.SecurityUser.__table__.columns]

            if (not master_user) and consultant.IsMasterUser:
                return "You are not allowed to change a master user record", 403

            if not consultant.IsMasterUser and not consultant.IsOrganisationSupervisor:
                AllowedFieldsToChange.remove('IsMasterUser')
                if not consultant.IsTestTakingUser:
                    AllowedFieldsToChange.remove('IsTestTakingUser')
                if not consultant.IsOfficeUser:
                    AllowedFieldsToChange.remove('IsOfficeUser')
                if not consultant.IsOrganisationSupervisor:
                    AllowedFieldsToChange.remove('IsOrganisationSupervisor')
                if not consultant.IsTestAuthor:
                    AllowedFieldsToChange.remove('IsTestAuthor')
                if not consultant.IsReportAuthor:
                    AllowedFieldsToChange.remove('IsReportAuthor')
                if not consultant.IsTestScreenTemplateAuthor:
                    AllowedFieldsToChange.remove('IsTestScreenTemplateAuthor')
                if not consultant.IsPasswordManager:
                    AllowedFieldsToChange.remove('IsPasswordManager')
                if not consultant.IsResearcher:
                    AllowedFieldsToChange.remove('IsResearcher')
                if not consultant.IsTranslator:
                    AllowedFieldsToChange.remove('IsTranslator')
                if not consultant.MayOrderCredits:
                    AllowedFieldsToChange.remove('MayOrderCredits')
                if consultant.MayWorkWithBatteriesOnly:
                    AllowedFieldsToChange.remove('MayWorkWithBatteriesOnly')
                AllowedFieldsToChange.remove('HasTestingOfficeAccess')
                AllowedFieldsToChange.remove('HasEducationalOfficeAccess')
            if consultant.IsOrganisationSupervisor:
                AllowedFieldsToChange.remove('IsMasterUser')

            # encrypt the API key if present
            request.get_data()
            if is_password_manager:
                temp_param = json.loads(request.data)
                temp_param['APIKey'] = ITSEncrypt.encrypt_string(temp_param['APIKey'])
                request.data = json.dumps(temp_param)
            else:
                AllowedFieldsToChange.remove('APIKey')

            # check if the password is present and can be updated
            temp_param = ITSHelpers.Empty()
            temp_param = json.loads(request.data)
            password = temp_param["Password"]
            password = password.strip()
            if len(password) < 10:
                if password == "":
                    AllowedFieldsToChange.remove('Password')
                else:
                    return "The password should be at least 10 characters long", 404

            # save the user to the master database
            ITSRestAPIORMExtensions.SecurityUser().change_single_object(request,
                                                                        ITR_minimum_access_levels.regular_office_user,
                                                                        identity, ",".join(AllowedFieldsToChange), True)

            if len(password) >= 10:
                ITSRestAPILogin.update_user_password(temp_param["Email"], password)

            # never save the password in the clients database
            try:
                AllowedFieldsToChange.remove('Password')
            except:
                pass

            # save the user to the clients database
            return ITSRestAPIORMExtensions.SecurityUser().change_single_object(request,
                                                                               ITR_minimum_access_levels.regular_office_user,
                                                                               identity,
                                                                               ",".join(AllowedFieldsToChange))
    elif request.method == 'DELETE':
        ITSRestAPIORMExtensions.SecurityUser().delete_single_object(request,
                                                                    ITR_minimum_access_levels.regular_office_user,
                                                                    identity, True)
        return ITSRestAPIORMExtensions.SecurityUser().delete_single_object(request,
                                                                           ITR_minimum_access_levels.regular_office_user,
                                                                           identity)


@app.route('/logins/currentuser/companies', methods=['GET'])
def logins_get_companies_memberships():
    # this is only available to the user him/herself
    # get the session id and the user id from the token
    token = request.headers['SessionID']
    company_id, user_id, token_validated, token_session_id = ITSRestAPILogin.get_info_with_session_token(token)

    if company_id == "":
        return "no company id known", 404

    if user_id != "":
        user_id = user_id.replace("'", "''")

        return ITSRestAPIORMExtensions.SecurityCompany().common_paginated_read_request(request,
                                                                                       ITR_minimum_access_levels.test_taking_user,
                                                                                       additional_unchecked_where_clause=
                                                                                       'a."ID" in (select distinct b."CompanyID" from "SecurityUsers" as b where b."Email" = \'' + user_id + '\')',
                                                                                       force_masterdb=True)
    else:
        return "User not found or no known token linked to this user", 404


@app.route('/logins/currentuser/changepassword', methods=['POST'])
@limiter.limit("1/second")
def login_change_password():
    # this is only available to the user him/herself
    # get the session id and the user id from the token
    token = request.headers['SessionID']
    app_log.info('logins currentuser changepassword %s %s ', token, request.method)
    company_id, user_id, token_validated, token_session_id = ITSRestAPILogin.get_info_with_session_token(token)
    id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, author_report_user, author_test_screen_templates_user, translator_user, office_user, is_password_manager, is_researcher = ITSRestAPILogin.get_id_of_user_with_token_and_company_id(
        user_id, company_id)

    if user_id != "":
        user_id = user_id.replace("'", "''")

        request.get_data()
        temp_param = ITSHelpers.Empty()
        temp_param = json.loads(request.data)
        oldPW = temp_param["old_password"]
        newPW = temp_param["new_password"]

        login_result, found_company_id, is_test_taking_user = ITSRestAPILogin.login_user(user_id, oldPW, company_id)
        if login_result in (
        ITSRestAPILogin.LoginUserResult.ok, ITSRestAPILogin.LoginUserResult.multiple_companies_found):
            ITSRestAPILogin.update_user_password(user_id, newPW)
            return "The password has been changed", 200
        else:
            return "Your old password is not correct, please retry", 404
    else:
        return "User not found or no known token linked to this user", 404


@app.route('/tokens', methods=['GET'])
@limiter.limit("1/second")
def tokens_get():
    app_log.warning('TOKEN LIST RETRIEVED')
    id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, translator_user, office_user, company_id, is_password_manager, master_header = check_master_header(
        request)

    if master_user:
        return ITSRestAPIORMExtensions.SecurityWebSessionToken().common_paginated_read_request(request,
                                                                                               ITR_minimum_access_levels.master_user)
    else:
        return ITSRestAPIORMExtensions.SecurityWebSessionToken().common_paginated_read_request(request,
                                                                                               ITR_minimum_access_levels.regular_office_user,
                                                                                               additional_unchecked_where_clause="\"CompanyID\" = '" + str(
                                                                                                   company_id) + "'",
                                                                                               force_masterdb=True)


@app.route('/tokens/<identity>', methods=['GET', 'POST', 'DELETE'])
def tokens_get_id(identity):
    if request.method == 'GET':
        return ITSRestAPIORMExtensions.SecurityWebSessionToken().return_single_object(request,
                                                                                      ITR_minimum_access_levels.master_user,
                                                                                      identity)
    elif request.method == 'POST':
        return ITSRestAPIORMExtensions.SecurityWebSessionToken().change_single_object(request,
                                                                                      ITR_minimum_access_levels.master_user,
                                                                                      identity)
    elif request.method == 'DELETE':
        return ITSRestAPIORMExtensions.SecurityWebSessionToken().delete_single_object(request,
                                                                                      ITR_minimum_access_levels.master_user,
                                                                                      identity)


@app.route('/tokens/<identity>/<newcompany>', methods=['POST'])
def token_change_company(identity, newcompany):
    id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, translator_user, office_user, company_id, is_password_manager, master_header = check_master_header(
        request)

    if master_user:
        try:
            token = request.headers['SessionID']
            company_id, user_id, token_validated, token_session_id = ITSRestAPILogin.get_info_with_session_token(token)

            #invalidate all caching of users here
            reset_cache()
            ITSRestAPILogin.change_token_company(identity, newcompany)

            # create a login for this company if it does not exist yet
            ITSRestAPILogin.clone_user_login(user_id, id_of_user, company_id, newcompany)
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            app_log.info('Exception on db switch %s', ''.join(' ' + line for line in lines))
            return "An error occured during the switch", 404
        return "switch OK", 200
    else:
        return "You are not authorised to make this call ", 404


@app.route('/systemsettings', methods=['GET'])
def systemsettings_get():
    additional_where_clause = "ParProtected = false"
    return ITSRestAPIORMExtensions.SystemParam().common_paginated_read_request(request,
                                                                               ITR_minimum_access_levels.regular_office_user,
                                                                               additional_where_clause)


@app.route('/systemsettings/<identity>', methods=['GET', 'POST', 'DELETE'])
def systemsettings_get_id(identity):
    id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, translator_user, office_user, company_id, is_password_manager, master_header = check_master_header(
        request)

    if not office_user:
        return "You do not have sufficient rights to make this call", 404

    include_master_header = "N"
    try:
        include_master_header = request.headers['IncludeMaster']
    except:
        pass
    include_client_header = "N"
    try:
        include_client_header = request.headers['IncludeClient']
    except:
        pass

    if include_master_header == "Y":
        if not master_user and request.method != 'GET':
            return "You do not have sufficient rights to make this call", 404
        sessionid = ""
    else:
        if not organisation_supervisor_user and request.method != 'GET':
            return "You do not have sufficient rights to make this call", 404
        if (not master_user) and (identity.upper() == "MAXNUMBEROFCONSULTANTS") and (request.method != 'GET'):
            return "You do not have sufficient rights to make this call", 404
        sessionid = company_id

    if include_master_header == "Y" and include_client_header == "N":
        cache_key = "master"
    else:
        cache_key = str(company_id)

    with ITSRestAPIDB.session_scope(sessionid) as session:
        if request.method == 'GET':
            if identity == "CC_ADDRESS":
                cached = check_in_cache('systemsettings.' + cache_key + "." + identity)
                if cached is not None:
                    return cached

                with ITSRestAPIDB.session_scope("") as master_session:
                    comp = master_session.query(ITSRestAPIORMExtensions.SecurityCompany).filter(
                        ITSRestAPIORMExtensions.SecurityCompany.ID == company_id).first()

                    add_to_cache_with_timeout('systemsettings.' + cache_key + "." + identity, 60, comp.CCEMail)

                    return comp.CCEMail
            else:
                param = check_in_cache('systemsettings.' + cache_key + "." + identity)

                if param is None:
                    param = session.query(ITSRestAPIORMExtensions.SystemParam).filter(
                        ITSRestAPIORMExtensions.SystemParam.ParameterName == identity).first()
                    if param is not None:
                        session.expunge(param)
                        add_to_cache_with_timeout('systemsettings.' + cache_key + "." + identity, 60, param)

                if param is None:
                    return "Parameter not found", 404
                else:
                    if param.ParProtected and (organisation_supervisor_user or master_user):
                        return param.ParValue
                    else:
                        if not param.ParProtected:
                            return param.ParValue
                        else:
                            return "You do not have sufficient rights to make this call", 404
        elif request.method == 'POST':
            reset_cache()

            request.get_data()
            if identity == "CC_ADDRESS":
                with ITSRestAPIDB.session_scope("") as master_session:
                    comp = master_session.query(ITSRestAPIORMExtensions.SecurityCompany).filter(
                        ITSRestAPIORMExtensions.SecurityCompany.ID == company_id).first()
                    comp.CCEMail = request.data.decode('utf-8')

                    return "Parameter value updated", 200
            else:
                param = session.query(ITSRestAPIORMExtensions.SystemParam).filter(
                    ITSRestAPIORMExtensions.SystemParam.ParameterName == identity).first()

                if param is None:
                    param2 = ITSRestAPIORMExtensions.SystemParam()
                    param2.ParameterName = identity
                    param2.ParValue = request.data.decode('utf-8')
                    # check if this parameter is protected
                    param2.ParProtected = False
                    try:
                        temp_param = ITSHelpers.Empty()
                        temp_param = json.loads(request.data)
                        param2.ParProtected = temp_param.ParProtected
                    except:
                        pass
                    session.add(param2)
                    session.commit()
                    return "Parameter added", 200
                else:
                    param.ParValue = request.data.decode('utf-8')
                    session.commit()
                    return "Parameter value updated", 200
        elif request.method == 'DELETE':
            if not master_user:
                return "You do not have sufficient rights to make this call", 404

            reset_cache()

            session.query(ITSRestAPIORMExtensions.SystemParam).filter(
                ITSRestAPIORMExtensions.SystemParam.ParameterName == identity).delete()
            session.commit()
            return "Parameter deleted", 200


@app.route('/screentemplates', methods=['GET'])
def screentemplates_get():
    return ITSRestAPIORMExtensions.TestScreenTemplate().common_paginated_read_request(request,
                                                                                      ITR_minimum_access_levels.test_taking_user)


@app.route('/screentemplates/<identity>', methods=['GET', 'POST', 'DELETE'])
def screentemplates_get_id(identity):
    basepathname = os.path.dirname(os.path.join(os.sep, app_instance_path(), 'cache'))
    pathname = os.path.dirname(
        os.path.join(os.sep, app_instance_path(), 'cache', ITSHelpers.string_split_to_filepath(identity)))
    try:
        include_master = request.headers['IncludeMaster'] == "Y"
    except:
        pass
    cachedfilename = os.path.join(os.sep, pathname, "master_template.json") if include_master else os.path.join(os.sep,
                                                                                                                pathname,
                                                                                                                "template.json")

    if request.method == 'GET':
        # test taking users may request all screen templates since that is needed for test taking
        if os.path.isfile(cachedfilename):
            return (open(cachedfilename, 'r').read()), 200
        else:
            to_return = ITSRestAPIORMExtensions.TestScreenTemplate().return_single_object(request,
                                                                                          ITR_minimum_access_levels.test_taking_user,
                                                                                          identity)
            try:
                if to_return[1] == 404:
                    to_return = ITSRestAPIORMExtensions.TestScreenTemplate().return_single_object(request,
                                                                                                  ITR_minimum_access_levels.test_taking_user,
                                                                                                  identity, True)
            except:
                pass

            try:
                if to_return.status == "200 OK":
                    if not os.path.exists(pathname):
                        os.makedirs(pathname)
                    text_file = open(cachedfilename, "w")
                    text_file.write(json.dumps(to_return.json))
                    text_file.close()
            except:
                pass

            return to_return
    elif request.method == 'POST':
        if os.path.exists(pathname):
            ITSHelpers.remove_folder(pathname, basepathname)
        temp = ITSRestAPIORMExtensions.TestScreenTemplate().change_single_object(request,
                                                                                 ITR_minimum_access_levels.test_screen_template_author,
                                                                                 identity)
        return temp
    elif request.method == 'DELETE':
        if os.path.exists(pathname):
            ITSHelpers.remove_folder(pathname, basepathname)
        return ITSRestAPIORMExtensions.TestScreenTemplate().delete_single_object(request,
                                                                                 ITR_minimum_access_levels.test_screen_template_author,
                                                                                 identity)


@app.route('/tests', methods=['GET'])
def tests_get():
    return ITSRestAPIORMExtensions.Test().common_paginated_read_request(request,
                                                                        ITR_minimum_access_levels.regular_office_user)


@app.route('/tests/<identity>', methods=['GET', 'POST', 'DELETE'])
def tests_get_id(identity):
    basepathname = os.path.dirname(os.path.join(os.sep, app_instance_path(), 'cache'))
    pathname = os.path.dirname(
        os.path.join(os.sep, app_instance_path(), 'cache', ITSHelpers.string_split_to_filepath(identity)))
    if request.method == 'GET':
        cachefilename = "test.json"
        # test taking users may request all test definitions since they need them for test taking, but will get limited fields back to protect scoring and norming rules
        token = request.headers['SessionID']
        company_id, user_id, token_validated, token_session_id = ITSRestAPILogin.get_info_with_session_token(token)
        id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, author_report_user, author_test_screen_templates_user, translator_user, office_user, is_password_manager, is_researcher = ITSRestAPILogin.get_id_of_user_with_token_and_company_id(
            user_id, company_id)
        if (not office_user) and test_taking_user:
            # use a special cache file for the test cache for test takers
            cachefilename = "test_limited.json"

        # return the object
        try:
            include_master = request.headers['IncludeMaster'] == "Y"
        except:
            pass
        cachedfilefull = os.path.join(os.sep, pathname, "master_" + cachefilename) if include_master else os.path.join(
            os.sep, pathname, cachefilename)
        if os.path.isfile(cachedfilefull):
            return (open(cachedfilefull, 'r').read()), 200
        else:
            to_return = ITSRestAPIORMExtensions.Test().return_single_object(request,
                                                                            ITR_minimum_access_levels.test_taking_user,
                                                                            identity)
            try:
                if to_return[1] == 404:
                    to_return = ITSRestAPIORMExtensions.Test().return_single_object(request,
                                                                                    ITR_minimum_access_levels.test_taking_user,
                                                                                    identity, True)
            except:
                pass

            try:
                if to_return.status == "200 OK":
                    if not os.path.exists(pathname):
                        os.makedirs(pathname)
                    text_file = open(cachedfilefull, "w")
                    tempjson = to_return.json
                    # remove the fields for a protected test
                    if cachefilename == "test_limited.json":
                        if tempjson['TestDefinitionIsProtected']:
                            del tempjson["norms"]
                            del tempjson["documents"]
                            del tempjson["scoreRules"]
                            del tempjson["ScoringScript"]
                            del tempjson["BeforeNormingScript"]
                            del tempjson["AfterNormingScript"]
                            del tempjson["Per360"]
                            del tempjson["Post360"]
                            del tempjson["Pre360"]
                            del tempjson["graphs"]
                            del tempjson["RequiredParsPerson"]
                            del tempjson["RequiredParsSession"]
                            del tempjson["RequiredParsGroup"]
                            del tempjson["RequiredParsOrganisation"]
                    tempdump = json.dumps(tempjson)
                    text_file.write(tempdump)
                    text_file.close()
                    # in case of a protected file return the file and not the to_return
                    if cachefilename == "test_limited.json":
                        return (open(cachedfilefull, 'r').read()), 200
            except:
                pass

            return to_return
    elif request.method == 'POST':
        if os.path.exists(pathname):
            ITSHelpers.remove_folder(pathname, basepathname)

        return ITSRestAPIORMExtensions.Test().change_single_object(request,
                                                                   ITR_minimum_access_levels.test_author,
                                                                   identity)
    elif request.method == 'DELETE':
        if os.path.exists(pathname):
            ITSHelpers.remove_folder(pathname, basepathname)
        return ITSRestAPIORMExtensions.Test().delete_single_object(request,
                                                                   ITR_minimum_access_levels.test_author,
                                                                   identity)


@app.route('/files/<company_id>/<maintainingObjectIdentity>/<fileType>', methods=['GET', 'DELETE'])
def files_get_id(company_id, maintainingObjectIdentity, fileType):
    masterFiles = False
    if company_id == "master":
        masterFiles = True
    token = request.headers['SessionID']
    company_id, user_id, token_validated, token_session_id = ITSRestAPILogin.get_info_with_session_token(token)
    id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, author_report_user, author_test_screen_templates_user, translator_user, office_user, is_password_manager, is_researcher = ITSRestAPILogin.get_id_of_user_with_token_and_company_id(
        user_id, company_id)
    pathname = os.path.dirname(
        os.path.join(os.sep, app_instance_path(), 'media', str(company_id),
                     ITSHelpers.string_split_to_filepath(maintainingObjectIdentity)))
    basepathname = os.path.dirname(
        os.path.join(os.sep, app_instance_path(), 'media', str(company_id)))
    # check if path exists, if not try the master path
    if (not os.path.isdir(pathname)) or masterFiles:
        pathname = os.path.dirname(
            os.path.join(os.sep, app_instance_path(), 'media', 'master',
                         ITSHelpers.string_split_to_filepath(maintainingObjectIdentity)))
        basepathname = os.path.dirname(
            os.path.join(os.sep, app_instance_path(), 'media', 'master'))
    fileType = fileType.upper()
    if fileType != "ALL":
        pathname = pathname + os.sep + fileType

    if master_user or organisation_supervisor_user or author_user or test_taking_user:
        if request.method == 'GET':
            # return a list of files in this folder
            file_array = ITSHelpers.list_folder(pathname)
            return jsonify(file_array), 200
        elif request.method == 'DELETE':
            # delete this folder
            if os.path.exists(pathname) and not test_taking_user:
                ITSHelpers.remove_folder(pathname, basepathname)
            return "folder removed", 200
    else:
        return "You need to be master user, organisation supervisor or test author to use the files/<maintainingObjectId> endpoint", 403


@app.route('/filecopy/<maintainingObjectIdentity_src>/<maintainingObjectIdentity_dst>', methods=['POST'])
@limiter.limit("1/second")
def files_copy_folder(maintainingObjectIdentity_src, maintainingObjectIdentity_dst):
    token = request.headers['SessionID']
    company_id, user_id, token_validated, token_session_id = ITSRestAPILogin.get_info_with_session_token(token)
    id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, author_report_user, author_test_screen_templates_user, translator_user, office_user, is_password_manager, is_researcher = ITSRestAPILogin.get_id_of_user_with_token_and_company_id(
        user_id, company_id)
    pathname_src = os.path.dirname(
        os.path.join(os.sep, app_instance_path(), 'media', str(company_id),
                     ITSHelpers.string_split_to_filepath(maintainingObjectIdentity_src)))
    if maintainingObjectIdentity_dst.upper() == "MASTER":
        pathname_dst = os.path.dirname(os.path.join(os.sep, app_instance_path(), 'media', 'master',
                                                    ITSHelpers.string_split_to_filepath(maintainingObjectIdentity_src)))
    else:
        pathname_dst = os.path.dirname(
            os.path.join(os.sep, app_instance_path(), 'media', str(company_id),
                         ITSHelpers.string_split_to_filepath(maintainingObjectIdentity_dst)))

    if master_user or organisation_supervisor_user or author_user:
        # make sure to remove any files in the target dir before copying
        if os.path.exists(pathname_dst):
            shutil.rmtree(pathname_dst)
        # and now copy
        if os.path.exists(pathname_src):
            os.makedirs(pathname_dst)
            ITSHelpers.copy_folder(pathname_src, pathname_dst)
        return "Folder copied", 200
    else:
        return "You need to be master user, organisation supervisor or test author to use the files/<maintainingObjectId> endpoint", 403


@app.route('/files/<company_id>/<maintainingObjectIdentity>/<fileType>/<fileId>', methods=['GET', 'POST', 'DELETE'])
def files_get_file(company_id, maintainingObjectIdentity, fileType, fileId):
    if request.method != 'GET':
        try:
            token = request.headers['SessionID']
        except Exception as e:
            app_log.error('File API failed %s', str(e))
            return "File API failed", 500
        # get the company id from the token instead of the api
        company_id, user_id, token_validated, token_session_id = ITSRestAPILogin.get_info_with_session_token(token)
        id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, author_report_user, author_test_screen_templates_user, translator_user, office_user, is_password_manager, is_researcher = ITSRestAPILogin.get_id_of_user_with_token_and_company_id(
            user_id, company_id)
    fileType = fileType.upper()
    pathname = os.path.dirname(
        os.path.join(os.sep, app_instance_path(), 'media', str(company_id),
                     ITSHelpers.string_split_to_filepath(maintainingObjectIdentity))) + os.sep + fileType
    filename = pathname + os.sep + ITSHelpers.to_filename(fileId)

    if request.method == 'GET':
        # if the file is not found try the master folder
        if not os.path.exists(filename):
            pathname = os.path.dirname(
                os.path.join(os.sep, app_instance_path(), 'media', 'master',
                             ITSHelpers.string_split_to_filepath(maintainingObjectIdentity))) + os.sep + fileType
            filename = pathname + os.sep + ITSHelpers.to_filename(fileId)

        # return the file
        if os.path.exists(filename):
            raw_bytes = ""
            with open(filename, 'rb') as r:
                raw_bytes = r.read()
            response = make_response(raw_bytes)
            response.headers['Content-Type'] = "application/octet-stream"
            head, tail = os.path.split(filename)
            response.headers['Content-Disposition'] = "inline; filename=" + tail
            return response
        else:
            return 'File not found', 404
    elif request.method == 'POST':
        if master_user or organisation_supervisor_user or author_user:
            # replace or create the file
            if not os.path.exists(pathname):
                os.makedirs(pathname)
            request.get_data()

            f = open(filename, "wb")
            try:
                tempStr = request.data
                f.write(tempStr)
            except Exception as e:
                app_log.error('File uploading failed %s', str(e))
                return "File uploading failed", 500
            f.close()
            app_log.info('File written to %s', filename)
            return "File uploaded OK", 200
        else:
            return "You need to be master user, organisation supervisor or test author to post to files/<maintainingObjectId>/<fileId> endpoint", 403
    elif request.method == 'DELETE':
        if master_user or organisation_supervisor_user or author_user:
            # delete the file
            if os.path.exists(filename):
                os.remove(filename)
                return "File removed", 200
            else:
                return 'File not found', 404
        else:
            return "You need to be master user, organisation supervisor or test author to delete from  files/<maintainingObjectId>/<fileId> endpoint", 403


@app.route('/translations', methods=['GET'])
def list_available_translations():
    pathname = os.path.dirname(os.path.join(app_instance_path(), 'translations/'))
    # check for master database existence. if not init the system for a smoother first time user experience
    # session = sessionmaker(bind=ITSRestAPIDB.get_db_engine_connection_master())()
    with ITSRestAPIDB.session_scope("") as session:
        if os.path.isdir(pathname):
            onlyfiles = [f for f in os.listdir(pathname) if
                         os.path.isfile(os.path.join(pathname, f)) and f.endswith('.json')]
            returnfiles = []
            for line in onlyfiles:
                returnfiles.append(line[: line.index('.json')])
            return jsonify(returnfiles), 200
        else:
            return "[]", 200


@app.route('/translations/<langcode>', methods=['GET', 'POST'])
@limiter.limit("1/second")
def translations(langcode):
    if langcode == "":
        langcode = "en"
    langcode = langcode.lower()
    filename = os.path.join(app_instance_path(), 'translations/', langcode + '.json')
    if request.method == 'GET':
        if os.path.isfile(filename):
            with open(filename, 'r') as translationFile:
                return translationFile.read(), 200
        else:
            return "[]", 200
    elif request.method == 'POST':
        token = request.headers['SessionID']
        company_id, user_id, token_validated, token_session_id = ITSRestAPILogin.get_info_with_session_token(token)

        if company_id == "":
            return "no company id known", 404

        id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, author_report_user, author_test_screen_templates_user, translator_user, office_user, is_password_manager, is_researcher = ITSRestAPILogin.get_id_of_user_with_token_and_company_id(
            user_id, company_id)

#        if (master_user or translator_user) and ITSTranslate.translation_available():
        if ITSTranslate.translation_available():
            # get the request data into json
            linesChanged = 0
            request.get_data()
            new_data = json.loads(request.data)
            old_data = {}
            if os.path.isfile(filename):
                old_data = json.load(open(filename, 'r'))
            else:
                if not os.path.isdir(os.path.dirname(filename)):
                    os.makedirs(os.path.dirname(filename))
            for line in new_data:
                # needs translation
                header_force_translation = False
                try:
                    header_force_translation = request.headers['ForceTranslation'] == "Y"
                except:
                    pass
                if header_force_translation:
                    newTranslation = True
                    translatedText = new_data[line]['value']
                else:
                    translatedText, newTranslation = ITSTranslate.get_translation_if_needed(langcode, line,
                                                                                            new_data[line]['value'],
                                                                                            old_data)
                if translatedText is not None and newTranslation:
                    old_data[line] = new_data[line]
                    old_data[line]['originalValue'] = new_data[line]['value']
                    old_data[line]['value'] = translatedText
                    old_data[line]['valueAsOriginal'] = 'N'
                    if old_data[line]['originalValue'] == old_data[line]['value']:
                        old_data[line]['valueAsOriginal'] = 'Y'
                    old_data[line]['changeDateTime'] = datetime.now().isoformat()
                    old_data[line]['changedBy'] = str(id_of_user) + " (" + str(company_id) + ")"

                    linesChanged = linesChanged + 1

                    if linesChanged > 0 and linesChanged % 25 == 0:
                        with open(filename, 'w') as translationFile:  # make sure to save every 25 translations
                            translationFile.write(json.dumps(old_data, indent=1, sort_keys=True))
                            translationFile.close()
            # and now save the file
            if linesChanged > 0:
                with open(filename, 'w') as translationFile:
                    translationFile.write(json.dumps(old_data, indent=1, sort_keys=True))
                    translationFile.close()
            return "OK", 200
        else:
            return "no master user or no translation key set", 404


@app.route('/translate/<sourcelangcode>/<targetlangcode>', methods=['GET'])
def translate_string(sourcelangcode, targetlangcode):
    token = request.headers['SessionID']
    company_id, user_id, token_validated, token_session_id = ITSRestAPILogin.get_info_with_session_token(token)
    id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, author_report_user, author_test_screen_templates_user, translator_user, office_user, is_password_manager, is_researcher = ITSRestAPILogin.get_id_of_user_with_token_and_company_id(
        user_id, company_id)

    if (master_user or translator_user or author_user or author_report_user) and ITSTranslate.translation_available():
        request.get_data()
        x = request.headers['ToTranslate']
        text_to_translate = urllib.parse.unquote(x)

        translated_text = ITSTranslate.get_translation_with_source_language(sourcelangcode, targetlangcode,
                                                                            text_to_translate)
        return translated_text, 200
    else:
        return "Translations not available, check the azure translate string and the user's rights", 404


@app.route('/sendmail', methods=['POST'])
def send_mail():
    id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, translator_user, office_user, company_id, is_password_manager, master_header = check_master_header(
        request)

    if office_user:
        request.get_data()
        data = request.data
        data_dict = json.loads(data)

        # and now sent an email to the user
        try:
            ITSMailer.send_mail(company_id, data_dict["Subject"],
                                data_dict["Body"],
                                data_dict["To"],
                                data_dict["CC"],
                                data_dict["BCC"],
                                data_dict["From"], [],
                                data_dict["ReplyTo"], consultant_id=id_of_user)

            return "An email is sent", 200
        except Exception as e:
            return str(e), 500
    else:
        return "You are not authorised to sent emails", 404

@app.route('/sendmailconsultant/<sessionid>', methods=['POST'])
def send_mail_consultant(sessionid):
    # and now sent an email to a registered consultant
    try:
        id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, translator_user, office_user, company_id, is_password_manager, master_header = check_master_header(
            request)

        request.get_data()
        data = request.data
        data_dict = json.loads(data)

        consultantmail = data_dict["To"]

        # check if the consultant is known
        with ITSRestAPIDB.session_scope(company_id) as session:
            consultant = session.query(ITSRestAPIORMExtensions.SecurityUser).filter(
                ITSRestAPIORMExtensions.SecurityUser.Email == consultantmail).first()

            if (consultant is not None) and (consultant.EndDateLicense > datetime.now().replace(tzinfo=timezone.utc).astimezone(tz=None)):
                # get the session results data
                this_session = session.query(ITSRestAPIORMExtensions.ClientSession).filter(
                    ITSRestAPIORMExtensions.ClientSession.ID == sessionid).first()
                this_session_tests = session.query(ITSRestAPIORMExtensions.ClientSessionTest).filter(
                    ITSRestAPIORMExtensions.ClientSessionTest.SessionID == sessionid).all()
                json_results = {}

                for this_test_result in this_session_tests:
                    json_results['Scores'] = json.loads(this_test_result.Scores)
                    json_results['Results'] = json.loads(this_test_result.Results)
                    json_results[str(this_test_result.TestID)+'.Scores'] = json.loads(this_test_result.Scores)
                    json_results[str(this_test_result.TestID)+'.Results'] = json.loads(this_test_result.Results)

                    this_session.ManagedByUserID = consultant.ID

                    # send the mail with the session results attached
                    ITSMailer.send_mail(company_id, data_dict["Subject"],
                                data_dict["Body"],
                                data_dict["To"],
                                data_to_attach=json.dumps(json_results))

        return "An email is sent when the session id and the consultant mail were valid", 200
    except Exception as e:
        app_log.info('Error sending mail to consulant %s ', e)
        return str(e), 500

@app.route('/refreshpublics', methods=['POST'])
def refresh_publics():
    id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, translator_user, office_user, company_id, is_password_manager, master_header = check_master_header(
        request)
    clone_needed = False

    if master_user:
        currentrefreshday = (datetime.today() - datetime.utcfromtimestamp(0)).days
        lastrefreshday = 0
        with ITSRestAPIDB.session_scope("") as session:
            param = session.query(ITSRestAPIORMExtensions.SystemParam).filter(
                ITSRestAPIORMExtensions.SystemParam.ParameterName == "LASTREPOREFRESH").first()
            newinstall = False
            if param is None:
                param = ITSRestAPIORMExtensions.SystemParam()
                param.ParameterName = "LASTREPOREFRESH"
                session.add(param)
                newinstall = True
            else:
                lastrefreshday = int(param.ParValue)
            if lastrefreshday != currentrefreshday:
                param.ParValue = currentrefreshday
                clone_needed = True

        if clone_needed:
            ITSGit.clone_or_refresh_repo(app_instance_path(), 'https://github.com/Quopt/itr-reporttemplates')
            ITSGit.clone_or_refresh_repo(app_instance_path(), 'https://github.com/Quopt/itr-testtemplates')
            ITSGit.clone_or_refresh_repo(app_instance_path(), 'https://github.com/Quopt/itr-testscreentemplates')
            ITSGit.clone_or_refresh_repo(app_instance_path(), 'https://github.com/Quopt/itr-plugins')
            ITSGit.clone_or_refresh_repo(app_instance_path(), 'https://github.com/Quopt/itr-translations')

        return "OK", 200

    else:
        return "You are not authorised to refresh the public repositories", 404


@app.route('/listpublics/<reponame>', methods=['GET'])
def list_publics(reponame):
    id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, translator_user, office_user, company_id, is_password_manager, master_header = check_master_header(
        request)
    if master_user:
        # app_log.info("List publics %s %s", str(app_instance_path()), str(reponame))
        tempfile = ITSGit.list_repo_files(app_instance_path(), reponame)
        return tempfile, 200


@app.route('/listpublics/<reponame>/<filename>', methods=['GET'])
def list_publics_file(reponame, filename):
    id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, translator_user, office_user, company_id, is_password_manager, master_header = check_master_header(
        request)
    if master_user:
        short_repo_name = reponame.split('/')[-1]
        newfilename = os.path.join(os.sep, app_instance_path(), 'cache', 'git', short_repo_name, filename)
        if os.path.exists(newfilename):
            raw_bytes = ""
            with open(newfilename, 'rb') as r:
                raw_bytes = r.read()
            response = make_response(raw_bytes)
            response.headers['Content-Type'] = "application/octet-stream"
            head, tail = os.path.split(newfilename)
            response.headers['Content-Disposition'] = "inline; filename=" + tail
            return response
        else:
            return 'File not found', 404


@app.route('/installpublics/itr-translations/<filename>', methods=['POST', 'DELETE'])
def install_publics_file(filename):
    id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, translator_user, office_user, company_id, is_password_manager, master_header = check_master_header(
        request)
    if master_user:
        srcfilename = os.path.join(os.sep, app_instance_path(), 'cache', 'git', 'itr-translations', filename)
        newfilename = os.path.join(os.sep, app_instance_path(), 'translations', filename)
        if request.method == "POST":
            try:
                os.makedirs(os.path.dirname(newfilename), exist_ok=True)
                shutil.copyfile(srcfilename, newfilename)
                return "OK", 200
            except Exception as e:
                app_log.error('Install publics API failed %s', str(e))
                return "File copy failed. Maybe you do not have sufficient rights on the file system", 404
        elif request.method == "DELETE":
            try:
                os.remove(newfilename)
                return "OK", 200
            except Exception as e:
                app_log.error('Install publicsls API failed %s', str(e))
                return "File delete failed. Maybe you do not have sufficient rights on the file system", 404


@app.route('/installpublics/itr-api', methods=['POST'])
def install_publics_itr_api():
    global APIRequiresRestart

    id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, translator_user, office_user, company_id, is_password_manager, master_header = check_master_header(
        request)
    if master_user:
        # force clone now
        ITSGit.clone_or_refresh_repo(app_instance_path(), 'https://github.com/Quopt/ITR-API')
        # copy into folder
        srcfoldername = os.path.join(os.sep, app_instance_path(), 'cache', 'git', 'ITR-API')
        newfoldername = os.path.join(os.sep, app.root_path)
        if request.method == "POST":
            # Copy only requirements.txt
            srcfilename = os.path.join(os.sep, srcfoldername, 'requirements.txt')
            newfilename = os.path.join(os.sep, newfoldername, 'requirements.txt')
            app_log.info("Installing new requirements.txt  " + srcfilename + " - " + newfilename)
            shutil.copyfile(srcfilename, newfilename)

            if not pip_install():
                return "PIP Install failed", 500

            app_log.info("Syncing folders from " + srcfoldername + " to " + newfoldername)
            ITSHelpers.copy_folder_excluding_dot_folders(srcfoldername, newfoldername, True)

            return "OK", 200
    return "You are not authorised to install public repositories", 403


def pip_install():
    # install new requirements if set
    try:
        os.chdir(app.root_path)
        app_log.info(app.root_path)
        output_text = subprocess.run(['pip', 'install', '-r', 'requirements.txt'], stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, stdin=subprocess.DEVNULL)
        app_log.info(output_text.stdout)
        #output_text = subprocess.run(['pip', 'install', '--upgrade', 'pip'], stdout=subprocess.PIPE,
        #                             stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, start_new_session=True, check=True)
        #app_log.info(output_text.stdout)
        return True
    except Exception as err:
        app_log.error('pip -r install requirements.txt failed ' + "Error {}".format(err))
        return False


@app.route('/installpublics/itr-webclient', methods=['POST'])
def install_publics_itr_webclient():
    id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, translator_user, office_user, company_id, is_password_manager, master_header = check_master_header(
        request)
    if master_user:
        # force clone now
        ITSGit.clone_or_refresh_repo(app_instance_path(), 'https://github.com/Quopt/ITR-webclient')
        # copy into folder
        srcfoldername = os.path.join(os.sep, app_instance_path(), 'cache', 'git', 'ITR-webclient')
        newfoldername = ITSRestAPISettings.get_setting('WEBFOLDER')
        if request.method == "POST":
            app_log.info("Syncing folders from " + srcfoldername + " to " + newfoldername)
            ITSHelpers.copy_folder_excluding_dot_folders(srcfoldername, newfoldername)

        return "OK", 200
    return "You are not authorised to install public repositories", 403


@app.route('/installpublics/itr-public-api', methods=['POST'])
def install_publics_itr_public_api():
    id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, translator_user, office_user, company_id, is_password_manager, master_header = check_master_header(
        request)
    if master_user:
        # force clone now
        ITSGit.clone_or_refresh_repo(app_instance_path(), 'https://github.com/Quopt/ITR-Public-API')
        # copy into folder
        srcfoldername = os.path.join(os.sep, app_instance_path(), 'cache', 'git', 'ITR-Public-API')
        newfoldername = ITSRestAPISettings.get_setting('EXTERNALAPIFOLDER')
        if request.method == "POST":
            app_log.info("Syncing folders from " + srcfoldername + " to " + newfoldername)
            ITSHelpers.copy_folder_excluding_dot_folders(srcfoldername, newfoldername)
            # make sure to restart the API
            filename = os.path.join(newfoldername, 'api_refresh_date.txt')
            with open(filename, 'w') as file_write:
                file_write.write(str(datetime.now()))
            return "OK", 200
    return "You are not authorised to install public repositories", 403


@app.route('/installpublics/itr-stop', methods=['POST'])
def install_publics_itr_restart():
    id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, translator_user, office_user, company_id, is_password_manager, master_header = check_master_header(
        request)
    if master_user:
        try:
            os.chdir(app.root_path)
            app_log.info(app.root_path)
            output_text = subprocess.run(['pip', 'install', '-r', 'requirements.txt'], stdout=subprocess.PIPE,
                                         stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, shell=True)
            app_log.info(output_text.stdout)
        except Exception as err:
            app_log.error('pip -r install requirements.txt failed ' + "Error {}".format(err))

        app_log.info('Stopping waitress')
        os._exit(1)

    return "You are not authorised to stop the server", 403


@app.route('/version', methods=['GET'])
def version():
    return "ITR API " + time.ctime(os.path.getmtime('application.py')), 200


@app.route('/log/<logid>/<startlogdatetime>', methods=['GET'])
def log(logid, startlogdatetime):
    id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, translator_user, office_user, company_id, is_password_manager, master_header = check_master_header(
        request)
    if master_user:
        try:
            log_id = int(logid)
            if len(startlogdatetime) > 20:
                startlogdatetime = startlogdatetime[:20]
            start_datetime = startlogdatetime.upper()

            log_filename = log_file
            if log_id > 0:
                log_filename = log_filename + "." + str(log_id)

            if start_datetime == "LAST":
                # retrieve last 100 lines in the log
                return jsonify(open(log_filename, "r").readlines()[-100:]), 200
            elif start_datetime == "ALL":
                # retrieve all log lines
                return jsonify(open(log_filename, "r").readlines()), 200
            else:
                lines_to_scan = open(log_filename, "r").readlines()
                scan_index = len(lines_to_scan) - 1
                border = datetime.strptime(start_datetime, log_formatter.default_time_format)
                line_found = False
                while scan_index > 0 and not line_found:
                    try:
                        line_border = datetime.strptime(lines_to_scan[scan_index][4:23],
                                                        log_formatter.default_time_format)
                        if line_border < border:
                            line_found = True
                        else:
                            scan_index -= 1
                    except:
                        scan_index -= 1
                scan_index += 1
                return jsonify(lines_to_scan[-(len(lines_to_scan) - scan_index):]), 200

        except:
            return "You are not authorised to retrieve server log files using these parameters. It may also be that the log file is not present yet", 403

    return "You are not authorised to retrieve server log files", 403


@app.errorhandler(500)
def internal_error(error):
    app_log.error("Internal server error 500 : %s", error)
    app_log.error(traceback.format_exc())
    return "500 error"


waitress_thread = ""

def start_waitress():
    global waitress_thread, limiter
    init_app_log()

    # init compression for static files
    compress.init_app(app)

    # init rate limiter per browser id for 10 calls/sec
    default_limit = ITSRestAPISettings.get_setting_for_customer( "", "MAX_CALL_LIMIT", true, "") + " per second"
    app_log.info("Call rate limit set to %s", default_limit)
    # do NOT re-initialise the limiter object, instead use this hack to set the default limit. otherwise limits set on the decorator will not work
    #limiter = Limiter.( app, key_func=get_browser_id, default_limits=[default_limit] )
    limiter._default_limits.extend([ LimitGroup(default_limit,get_browser_id, None, False, None, None, None, None, None ) ])
    # make sure OPTIONS requests are excluded
    Limiter.limit(limiter, limit_value=get_browser_id, methods=['GET', 'POST', 'DELETE'])
    # and init the app limiter
    limiter.init_app(app)

    waitress_thread = threading.current_thread()

    itrport = "443"
    try:
        itrport = str(os.environ['ITRPORT'])
    except:
        pass
    itrthreads = 25
    try:
        itrthreads = int(os.environ['ITRTHREADS'])
    except:
        pass
    itrqueue = 2500
    try:
        itrqueue = int(os.environ['ITRQUEUE'])
    except:
        pass

    connection_limit = 500
    try:
        connection_limit = int(os.environ['ITRCONNECTIONLIMIT'])
    except:
        pass

    app_log.info("Starting waitress server on port %s with %s threads and queue size of %s and connection limit %s.",
                 itrport, itrthreads, itrqueue, connection_limit)
    serve(app.wsgi_app, threads=itrthreads, listen="*:" + itrport, backlog=itrqueue, connection_limit=connection_limit)


if __name__ == '__main__':
    # app.debug = True
    # MET FLASK app.run()
    # app.run(debug=True)
    start_waitress()
