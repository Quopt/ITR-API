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

from flask import Flask, jsonify, request, url_for, render_template
import datetime
import json
import time
import os
import hashlib, uuid, urllib
import types
import traceback
import shutil
from flask_cors import CORS
from flask_compress import Compress
from datetime import datetime, timezone, timedelta
from waitress import serve

import ITSRestAPILogin
import ITSMailer
import ITSRestAPIORMExtensions
import ITSRestAPIORM
import ITSRestAPIDB
import ITSRestAPISettings
import ITSJsonify
from ITSRestAPIORMExtendedFunctions import *
from ITSLogging import *
from ITSPrefixMiddleware import *
import ITSTranslate
import ITSHelpers
import ITSGit
import ITSEncrypt

app = Flask(__name__, instance_relative_config=True)
app.wsgi_app = PrefixMiddleware(app.wsgi_app, prefix='/api')
app.json_encoder = ITSJsonify.CustomJSONEncoder

@app.teardown_request
def teardown_request(exception=None):
    #stop all open database connections
    #app_log.info("teardown request")
    try:
     for key, dbengine in ITSRestAPIDB.db_engines_created.items():
        try:
            #dbengine.dispose()
            pass
        except:
            pass
    except:
        pass

Compress(app)
if ITSRestAPISettings.get_setting('ENABLE_CORS') == 'Y':
    CORS(app)


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
            if request.headers['MASTER'] == "Y":
                request.headers['MASTER'] = "N"
        except:
            pass

        include_master_header = "N"
        try:
            include_master_header = request.headers['IncludeMaster']
            if request.headers['IncludeMaster'] == "Y":
                request.headers['IncludeMaster'] = "N"
        except:
            pass

        token = request.headers['SessionID']
        company_id, user_id, token_validated = ITSRestAPILogin.get_info_with_session_token(token)
        id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, author_report_user, author_test_screen_templates_user, translator_user, office_user, is_password_manager = ITSRestAPILogin.get_id_of_user_with_token_and_company_id(
            user_id, company_id)

        if master_user:
            try:
                request.headers['MASTER'] = master_header
            except:
                pass
            try:
                request.headers['IncludeMaster'] = include_master_header
            except:
                pass

        return id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, translator_user, office_user, company_id, is_password_manager
    except:
        pass

def getIP(request):
    ip_address = ""
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None: # if behind engine x offloading server
        ip_address = request.environ['REMOTE_ADDR']
    else:
        ip_address = request.environ['HTTP_X_FORWARDED_FOR']
    return ip_address

# API implementations
@app.route('/')
def hello_world():
    return current_app.send_static_file('default.html')


@app.route('/test')
def route_test():
    return render_template('APITestPage.html')


@app.route('/test401')
def route_test401():
    return 'Not authorised', 401

@app.route('/copyright')
def route_copyright():
    user_company = ""
    if request.headers.__contains__('CompanyID'):
        user_company = request.headers['CompanyID']

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

    return parValue, 200

@app.route('/companyname')
def route_companyname():
    user_company = ""
    if request.headers.__contains__('CompanyID'):
        user_company = request.headers['CompanyID']

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

    return parValue, 200


@app.route('/login', methods=['GET'])
def login():
    # get the user id and password from the header
    user_id = request.headers['UserID']
    user_password = request.headers['Password']
    user_company = ""
    app_log.info('Login started for %s', user_id)
    if request.headers.__contains__('CompanyID'):
        user_company = request.headers['CompanyID']

    # check them against the database and return whether or not OK
    login_result = ITSRestAPILogin.login_user(user_id, user_password, user_company)

    # login failed
    if login_result == ITSRestAPILogin.LoginUserResult.user_not_found:
        # sleep just a little while on failed login attempts to stop brute force attacks
        # this will block a thread. A better solution would be nicer off course
        time.sleep(0.1)
        return 'User not found or password not valid', 401

    # the user is there so assign a session token
    ip_address = getIP(request)
    if user_company != "" :
        token = ITSRestAPILogin.create_session_token(user_id, user_company,
                                                     ITSRestAPILogin.LoginTokenType.regular_session)
    else:
        token = ITSRestAPILogin.create_session_token(user_id, ITSRestAPILogin.last_logged_in_company_id,
                                                 ITSRestAPILogin.LoginTokenType.regular_session)

    now = datetime.now() + timedelta(0, 600);
    return_obj = {}
    return_obj['SessionID'] = token;
    return_obj['ExpirationDateTime'] = now.isoformat()
    return_obj['CompanyID'] = ITSRestAPILogin.last_logged_in_company_id
    if login_result == ITSRestAPILogin.LoginUserResult.ok:
        # return a JSON that has Session, SessionID, multiple companies found = not present, ExpirationDateTime date time + 10 minutes (server based)
        return_obj['MultipleCompaniesFound'] = 'N';
    if login_result == ITSRestAPILogin.LoginUserResult.multiple_companies_found:
        # return a JSON that has Session, SessionID, multiple companies found = T, ExpirationDateTime date time + 10 minutes (server based)
        return_obj['MultipleCompaniesFound'] = 'Y';
    return json.dumps(return_obj)


@app.route('/sendresetpassword', methods=['POST'])
def send_reset_password():
    # send a mail with the reset password to the known email adress. If there is no known email adress return an error 404
    # otherwise return a 200 and send an email

    # get the user id and password from the header
    user_id = request.headers['UserID']

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
        ITSMailer.send_mail('Master','Password reset mail',
                            "You have requested a password reset. This link is valid for 5 minutes. Please copy & paste the following link in your browser window to reset your password : \r\n" +
                            request.url + "/ITS2/default.html?Token=" + token + "&Path=PasswordReset", user_id)

        return "An email is sent to the users known email address", 200
    else:
        return "User not found or no known email address linked to this user", 404


@app.route('/resetpassword', methods=['POST'])
def reset_password():
    # get the user id and password from the header
    user_id = request.headers['UserID']
    new_password = request.headers['Password']

    # check if we know this user
    if ITSRestAPILogin.check_if_user_account_is_valid(user_id) != ITSRestAPILogin.LoginUserResult.user_not_found:
        # check if the token is valid
        token = request.headers['SessionID']

        if ITSRestAPILogin.check_session_token(token):
            ITSRestAPILogin.update_user_password(user_id, new_password)
            return "The password has been reset to the indicated password", 200
        else:
            return "Invalid or expired token", 404
    else:
        return "User not found or no known email address linked to this user", 404


@app.route('/checktoken', methods=['POST'])
def check_token():
    token = request.headers['SessionID']

    if ITSRestAPILogin.check_session_token(token):
        return "Token is valid", 200
    else:
        return "Invalid or expired token", 404


@app.route('/logout', methods=['POST'])
def logout():
    token = request.headers['SessionID']

    if ITSRestAPILogin.check_session_token(token):
        ITSRestAPILogin.delete_session_token(token)
        return "User has been logged out", 200
    else:
        return "Invalid or expired token", 404


@app.route('/audittrail', methods=['GET'])
def clientauditlog_get():
    check_master_header(request)

    return ITSRestAPIORMExtensions.ClientAuditLog().common_paginated_read_request(request,
                                                                                  ITR_minimum_access_levels.regular_office_user)


@app.route('/audittrail/<identity>', methods=['GET', 'POST', 'DELETE'])
def clientauditlog_get_id(identity):
    check_master_header(request)

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
        check_master_header(request)
        return ITSRestAPIORMExtensions.ClientBatteries().change_single_object(request,
                                                                              ITR_minimum_access_levels.regular_office_user,
                                                                              identity)
    elif request.method == 'DELETE':
        check_master_header(request)
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
        check_master_header(request)
        return ITSRestAPIORMExtensions.ClientEducation().change_single_object(request,
                                                                              ITR_minimum_access_levels.regular_office_user,
                                                                              identity)
    elif request.method == 'DELETE':
        check_master_header(request)
        return ITSRestAPIORMExtensions.ClientEducation().delete_single_object(request,
                                                                              ITR_minimum_access_levels.regular_office_user,
                                                                              identity)


@app.route('/generatedreports', methods=['GET'])
def generatedreports_get():
    check_master_header(request)
    return ITSRestAPIORMExtensions.ClientGeneratedReport().common_paginated_read_request(request,
                                                                                         ITR_minimum_access_levels.regular_office_user)


@app.route('/generatedreports/<identity>', methods=['GET', 'POST', 'DELETE'])
def generatedreports_get_id(identity):
    check_master_header(request)
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
    check_master_header(request)
    return ITSRestAPIORMExtensions.ClientGroup().common_paginated_read_request(request,
                                                                               ITR_minimum_access_levels.regular_office_user)


@app.route('/groups/<identity>', methods=['GET', 'POST', 'DELETE'])
def groups_get_id(identity):
    check_master_header(request)
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
        check_master_header(request)
        return ITSRestAPIORMExtensions.ClientNationality().change_single_object(request,
                                                                                ITR_minimum_access_levels.regular_office_user,
                                                                                identity)
    elif request.method == 'DELETE':
        check_master_header(request)
        return ITSRestAPIORMExtensions.ClientNationality().delete_single_object(request,
                                                                                ITR_minimum_access_levels.regular_office_user,
                                                                                identity)


@app.route('/organisations', methods=['GET'])
def organisations_get():
    check_master_header(request)
    return ITSRestAPIORMExtensions.ClientOrganisation().common_paginated_read_request(request,
                                                                                      ITR_minimum_access_levels.regular_office_user)


@app.route('/organisations/<identity>', methods=['GET', 'POST', 'DELETE'])
def organisations_get_id(identity):
    check_master_header(request)
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
    check_master_header(request)
    return ITSRestAPIORMExtensions.ClientPerson().common_paginated_read_request(request,
                                                                                ITR_minimum_access_levels.regular_office_user)


@app.route('/persons/<identity>', methods=['GET', 'POST', 'DELETE'])
def persons_get_id(identity):
    id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, translator_user, office_user, company_id, is_password_manager = check_master_header(request)
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
            new_password = ITSRestAPILogin.create_or_update_testrun_user(data_dict['ID'], company_id, data_dict['EMail'], data_dict['Password'], data_dict['Active'], False)
            fix_password = (old_password != new_password and new_password != "") or old_password != ""
        allowed_fields_to_update.remove("Password")
        allowed_fields_to_update = ",".join(allowed_fields_to_update)
        if test_taking_user and not office_user:
            #check if the offered session is for this person
            request.get_data()
            data = request.data
            data_dict = json.loads(data)
            if str(data_dict["ID"]) != str(id_of_user) :
                return "Person cannot be updated as test taking user", 404
            allowed_fields_to_update = 'DateOfLastTest'

        to_return =  ITSRestAPIORMExtensions.ClientPerson().change_single_object(request,
                                                                           ITR_minimum_access_levels.test_taking_user,
                                                                           identity, allowed_fields_to_update)
        if fix_password:
            with ITSRestAPIDB.session_scope(company_id) as session:
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
    id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, translator_user, office_user, company_id, is_password_manager = check_master_header(request)

    if is_password_manager:
        with ITSRestAPIDB.session_scope(company_id) as qry_session:
            # save to the local master database
            user_found = qry_session.query(ITSRestAPIORMExtensions.ClientPerson).filter(
                ITSRestAPIORMExtensions.ClientPerson.ID == identity).first()
            return '{"Password":"' + ITSEncrypt.decrypt_string(user_found.Password) + '"}'
    else:
        return 403, "You do not have the right to view a candidate password"


@app.route('/sessiontests', methods=['GET'])
def sessiontests_get():
    check_master_header(request)
    return ITSRestAPIORMExtensions.ClientSessionTest().common_paginated_read_request(request,
                                                                                     ITR_minimum_access_levels.regular_office_user)

@app.route('/sessiontestsview', methods=['GET'])
def sessiontestsview_get():
    check_master_header(request)
    a = ITSRestAPIORMExtensions.ViewClientSessionTestsWithPerson().common_paginated_read_request(request,
                                                                                     ITR_minimum_access_levels.regular_office_user)
    return a

@app.route('/sessionsview', methods=['GET'])
def sessionsview_get():
    check_master_header(request)
    a = ITSRestAPIORMExtensions.ViewClientSessionsWithPerson().common_paginated_read_request(request,
                                                                                     ITR_minimum_access_levels.regular_office_user)
    return a

@app.route('/groupsessionsview', methods=['GET'])
def groupsessionsview_get():
    check_master_header(request)
    a = ITSRestAPIORMExtensions.ViewClientGroupSessions().common_paginated_read_request(request,
                                                                                     ITR_minimum_access_levels.regular_office_user)
    return a

@app.route('/sessiontests/<sessionid>', methods=['GET'])
def sessiontests_get_for_session(sessionid):
    id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, translator_user, office_user, company_id, is_password_manager = check_master_header(
        request)
    additional_where_clause = "SessionID='" + str(sessionid) + "'"
    if request.method == 'GET':
        return ITSRestAPIORMExtensions.ClientSessionTest().common_paginated_read_request(request,
                                                                                ITR_minimum_access_levels.regular_office_user,
                                                                                additional_where_clause)


@app.route('/sessiontests/<sessionid>/<identity>', methods=['GET', 'POST', 'DELETE'])
def sessiontests_get_id(sessionid, identity):
    app_log.info('SessionTests %s %s', sessionid, identity)
    id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, translator_user, office_user, company_id, is_password_manager = check_master_header(
        request)
    if request.method == 'GET':
        return ITSRestAPIORMExtensions.ClientSessionTest().return_single_object(request,
                                                                                ITR_minimum_access_levels.regular_office_user,
                                                                                identity)
    elif request.method == 'POST':
        to_return = ITSRestAPIORMExtensions.ClientSessionTest().change_single_object(request,
                                                                                ITR_minimum_access_levels.regular_office_user,
                                                                                identity)
        # now save the test session to the anonymous results, but only when it is done
        sessionTestPostTrigger(company_id, id_of_user, identity)

        return to_return
    elif request.method == 'DELETE':
        return ITSRestAPIORMExtensions.ClientSessionTest().delete_single_object(request,
                                                                                ITR_minimum_access_levels.regular_office_user,
                                                                                identity)


def sessionTestPostTrigger(company_id, id_of_user, identity):
    temp_test = ITSRestAPIORMExtensions.ClientSessionTest().return_single_object(request,
                                                                            ITR_minimum_access_levels.test_taking_user,
                                                                            identity)
    json_obj = json.loads(temp_test.data)
    if int(json_obj["Status"]) >= 30:
        # save as anonymous data
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
        json_group_obj = ""
        temp_group = {}
        tempPersonData = {}
        if json_session_obj['GroupID'] != '00000000-0000-0000-0000-000000000000':
            try:
                temp_group = ITSRestAPIORMExtensions.ClientGroup().return_single_object(request,
                                                                                        ITR_minimum_access_levels.test_taking_user,
                                                                                        json_session_obj['GroupID'])
                json_group_obj = json.loads(temp_group.data)
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
                tempPersonData['UserDefinedFields'] = json_person_obj['UserDefinedFields']
                data_gathering.PersonData = json.dumps(tempPersonData)
                data_gathering.PluginData = "{}"
                data_gathering.GroupData = json.dumps(json_group_obj)
                data_gathering.SessionData = json.dumps(json_session_obj)
                data_gathering.TestData = json.dumps(json_obj)

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
            tempPersonData['UserDefinedFields'] = json_person_obj['UserDefinedFields']
            data_gathering.PersonData = json.dumps(tempPersonData)
            data_gathering.PluginData = "{}"
            data_gathering.GroupData = json.dumps(json_group_obj)
            data_gathering.SessionData = json.dumps(json_session_obj)
            data_gathering.TestData = json.dumps(json_obj)

            qry_session.add(data_gathering)

        # now save to the central server using a json call
        tempPersonData['UserDefinedFields'] = ""
        data_gathering.PersonData = json.dumps(tempPersonData)
        # to do

        # invoice the test
        if int(json_obj["Status"]) == 30 :
            with ITSRestAPIDB.session_scope("") as mastersession:
                with ITSRestAPIDB.session_scope(company_id) as clientsession:
                    # loop through all tests
                    invoicing_ok = False
                    creditunits_low = False
                    totalCosts = 0
                    clientsessiontest = clientsession.query(ITSRestAPIORMExtensions.ClientSessionTest).filter(
                            ITSRestAPIORMExtensions.ClientSessionTest.ID == json_obj["ID"] ).first()

                    if not clientsessiontest.Billed :
                        # if this is a system local test then invoice the test in credit units
                        localtest = clientsession.query(ITSRestAPIORMExtensions.Test).filter(
                            ITSRestAPIORMExtensions.Test.ID == clientsessiontest.TestID ).first()
                        if localtest == None:
                            localtest = mastersession.query(ITSRestAPIORMExtensions.Test).filter(
                                ITSRestAPIORMExtensions.Test.ID == clientsessiontest.TestID).first()
                        if localtest != None:
                            totalCosts = localtest.Costs
                            localcompany = mastersession.query(ITSRestAPIORMExtensions.SecurityCompany).filter(
                                ITSRestAPIORMExtensions.SecurityCompany.ID == company_id).first()
                            if localcompany.TestTakingDiscount > 0:
                                if localcompany.TestTakingDiscount > 100 :
                                    localcompany.TestTakingDiscount = 100
                                totalCosts = totalCosts * ( localcompany.TestTakingDiscount / 100 )
                            if totalCosts < 0 :
                                totalCosts = 0

                            invoicing_ok = localtest.Costs == 0
                            if not invoicing_ok:
                                invoicing_ok = localcompany.TestTakingDiscount == 100
                            if not invoicing_ok:
                                invoicing_ok = localcompany.CurrentCreditLevel > totalCosts
                            if not invoicing_ok:
                                invoicing_ok = localcompany.AllowNegativeCredits
                            if invoicing_ok and totalCosts > 0:
                                # now execute the query to deduct the CurrentCreditLevel directly in the database (avoiding concurrency issues)
                                if localtest.InvoiceCode == "" or localtest.InvoiceCode is None :
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
                                newinvoicelogM.UserName = json_person_obj["EMail"]

                                # store in master and client db in case client messes it up by hand
                                clientsession.add(newinvoicelog)
                                mastersession.add(newinvoicelogM)

                                masterengine = ITSRestAPIDB.get_db_engine_connection_master()
                                masterengine.execution_options(isolation_level="AUTOCOMMIT").execute('UPDATE "SecurityCompanies" SET "CurrentCreditLevel" = "CurrentCreditLevel" - '+str(totalCosts)+' where "ID" = \''+str(company_id)+'\' ')

                                if not creditunits_low:
                                    creditunits_low = localcompany.CurrentCreditLevel > localcompany.LowCreditWarningLevel and (localcompany.CurrentCreditLevel - totalCosts <= localcompany.LowCreditWarningLevel)

                            if invoicing_ok:
                                clientsessiontest.Billed = True

                    # if this is a commercial test then invoice in currency using the invoice server
                    # to do


                # score and norm the test if invoicing was successfull
                # this is done on the client. For commercial tests the complete definition is downloaded from the suppliers server.
                # please note that during test taking this information is NOT available to prevent disclosing test details to the candidates
                # this means that tests and reports CANNOT be included in the session ready mail.

                # if credit units are low send the out of credits mail
                if creditunits_low:
                    this_company = mastersession.query(ITSRestAPIORMExtensions.SecurityCompany()).filter(
                        ITSRestAPIORMExtensions.SecurityCompany().ID == company_id)
                    ITSMailer.send_mail('Master','You are almost out of credits (%s left)' % this_company.CurrentCreditLevel,
                                        "The credit level has gone below the credit warning level that you have indicated. Please add more credits to your system.",
                                        this_company.ContactEMail)

@app.route('/sessionteststaking/<sessionid>', methods=['GET'])
# copy of sessiontests point only for test taking users
def sessionteststaking_get(sessionid):
    id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, translator_user, office_user, company_id, is_password_manager = check_master_header(
        request)
    additional_where_clause = 'PersID=\'' + str(id_of_user) +"',SessionID='" + str(sessionid) + "'"
    return ITSRestAPIORMExtensions.ClientSessionTest().common_paginated_read_request(request,
                                                                                     ITR_minimum_access_levels.test_taking_user,
                                                                                     additional_where_clause)


@app.route('/sessionteststaking/<sessionid>/<identity>', methods=['GET', 'POST'])
def sessionteststaking_get_id(sessionid, identity):
    id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, translator_user, office_user, company_id, is_password_manager = check_master_header(
        request)
    if request.method == 'GET':
        to_return = ITSRestAPIORMExtensions.ClientSessionTest().return_single_object(request,
                                                                                ITR_minimum_access_levels.test_taking_user,
                                                                                identity)
        try:
            if str(to_return["PersID"]) != str(id_of_user):
                return 404, "Session cannot be accessed as test taking user"
        except:
            pass
        return to_return
    elif request.method == 'POST':
        #check if the request is for this person
        request.get_data()
        data = request.data
        data_dict = json.loads(data)
        if str(data_dict["PersID"]) != str(id_of_user):
            return 404, "Session cannot be updated as test taking user"
        #check if the session in the database is also for this person
        to_check = ITSRestAPIORMExtensions.ClientSessionTest().return_single_object(request,
                                                                                 ITR_minimum_access_levels.test_taking_user,
                                                                                 identity)
        jsonObj = json.loads(to_check.data)
        if str(jsonObj["PersID"]) != str(id_of_user) or str(jsonObj["SessionID"]) != str(sessionid):
            return 404, "Session cannot be updated as test taking user"


        to_return = ITSRestAPIORMExtensions.ClientSessionTest().change_single_object(request,
                                                                                ITR_minimum_access_levels.test_taking_user,
                                                                                identity,
                                                                                'Results,Scores,TestStart,TestEnd,PercentageOfQuestionsAnswered,TotalTestTime,Status,CurrentPage,TotalPages,PluginData')

        sessionTestPostTrigger(company_id, id_of_user, identity)

        return to_return

@app.route('/sessions', methods=['GET'])
def sessions_get():
    id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, translator_user, office_user, company_id, is_password_manager = check_master_header(request)

    additional_where_clause = ""
    if test_taking_user and not office_user :
        additional_where_clause = 'PersonID=\'' + str(id_of_user) + '\''
    return ITSRestAPIORMExtensions.ClientSession().common_paginated_read_request(request,
                                                                          ITR_minimum_access_levels.test_taking_user,
                                                                                 additional_where_clause)


@app.route('/sessions/<identity>/groupmembers', methods=['GET'])
def sessions_groupmembers(identity):
    id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, translator_user, office_user, company_id, is_password_manager = check_master_header(request)

    additional_where_clause = 'parentsessionid=\'' + str(identity) + '\''
    return ITSRestAPIORMExtensions.ViewClientGroupSessionCandidates().common_paginated_read_request(request,
                                                                     ITR_minimum_access_levels.regular_office_user,
                                                                                 additional_where_clause)


@app.route('/sessions/<identity>/deletealltests', methods=['DELETE'])
def sessions_delete_tests(identity):
    # delete all tests from this session that have not been started yet
    id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, translator_user, office_user, company_id, is_password_manager = check_master_header(request)
    if request.method == 'DELETE':
        if office_user:
            with ITSRestAPIDB.session_scope(company_id) as qry_session:
                qry_session.query(ITSRestAPIORMExtensions.ClientSessionTest).filter(
                    ITSRestAPIORMExtensions.ClientSessionTest.SessionID == identity).filter(
                    ITSRestAPIORMExtensions.ClientSessionTest.Status == 10).delete()
            return "OK", 200
        else:
            return 403, "you do not have the rights to delete tests from the session"


@app.route('/sessions/<identity>', methods=['GET', 'POST', 'DELETE'])
def sessions_get_id(identity):
    app_log.info('Sessions %s ',  identity)
    id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, translator_user, office_user, company_id, is_password_manager = check_master_header(request)
    if request.method == 'GET':
        # test taking user may read their own data (to do : make sure they can only read their own data!)
        to_return = ITSRestAPIORMExtensions.ClientSession().return_single_object(request,
                                                                            ITR_minimum_access_levels.test_taking_user,
                                                                            identity)
        if test_taking_user and not office_user:
            try:
                if str(to_return["PersonID"]) != str(id_of_user):
                    return 404, "Session cannot be accessed as test taking user"
            except:
                pass
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
            #check if the offered session is for this person
            if str(data_dict["PersonID"]) != str(id_of_user) :
                return 404, "Session cannot be updated as test taking user"
            #check if the session in the database is also for this person
            to_return = ITSRestAPIORMExtensions.ClientSession().return_single_object(request,
                                                                                     ITR_minimum_access_levels.test_taking_user,
                                                                                     identity)

            try:
                if to_return["PersonID"] != id_of_user or to_return["ID"] !=  data_dict["ID"]:
                    return 404, "Session cannot be updated as test taking user"
            except:
                pass

            allowed_fields_to_update = 'Status,SessionState,AllowedStartDateTime,AllowedEndDateTime,StartedAt,EndedAt,PluginData'

        to_return = ITSRestAPIORMExtensions.ClientSession().change_single_object(request,
                                                                            ITR_minimum_access_levels.test_taking_user,
                                                                            identity, allowed_fields_to_update)

        # perform the session post trigger
        sessionPostTrigger(company_id, id_of_user, identity, data_dict, request)

        return to_return
    elif request.method == 'DELETE':
        # get the person id for this session first
        #qry_session = sessionmaker(bind=ITSRestAPIDB.get_db_engine_connection_client(company_id))()
        with ITSRestAPIDB.session_scope(company_id) as qry_session:
            sess = qry_session.query(ITSRestAPIORMExtensions.ClientSession).filter(
                ITSRestAPIORMExtensions.ClientSession.ID == identity).first()

            # then delete it
            to_return = ITSRestAPIORMExtensions.ClientSession().delete_single_object(request,
                                                                                ITR_minimum_access_levels.regular_office_user,
                                                                                identity)

            sessionPostTriggerDelete(company_id, sess.PersonID)

            return to_return
    # to do : remove the user if no open or active sessions are left, only for POST and DELETE

def sessionPostTrigger(company_id, id_of_user, identity, data_dict, request):
    # send the end session e-mail
    if int(data_dict["Status"]) == 30:
        #clientengine = ITSRestAPIDB.get_db_engine_connection_client(company_id)
        #clientsession = sessionmaker(bind=clientengine)()
        with ITSRestAPIDB.session_scope(company_id) as clientsession:
            temp_session = clientsession.query(ITSRestAPIORMExtensions.ClientSession).filter(
                        ITSRestAPIORMExtensions.ClientSession.ID == data_dict["ID"] ).first()
            temp_session.Status =31
            #clientsession.commit()
            url_to_click = request.url_root
            url_to_click = url_to_click.split("api/")[0] + "default.htm"
            if temp_session.EMailNotificationAdresses.strip() != "":
                ITSMailer.send_mail('Master','Session %s is ready for reporting' % temp_session.Description,
                                "The following session has completed : \r\n%s" % temp_session.Description +
                                "\r\n\r\n%s" % url_to_click,
                                temp_session.EMailNotificationAdresses, jsonify(temp_session.__dict__))
            removeUnnecessaryUserLogins(company_id, temp_session.PersonID)
    else:
        with ITSRestAPIDB.session_scope(company_id) as qry_session:
            sess = qry_session.query(ITSRestAPIORMExtensions.ClientSession).filter(
                ITSRestAPIORMExtensions.ClientSession.ID == identity).first()
            if sess:
                removeUnnecessaryUserLogins(company_id, sess.PersonID)

def sessionPostTriggerDelete(company_id, id_of_user):
    removeUnnecessaryUserLogins(company_id, id_of_user)

def removeUnnecessaryUserLogins(company_id, id_of_user):
    with ITSRestAPIDB.session_scope(company_id) as clientsession:
        with ITSRestAPIDB.session_scope("") as mastersession:
            temp_sessions = clientsession.query(ITSRestAPIORMExtensions.ClientSession).filter(
                ITSRestAPIORMExtensions.ClientSession.PersonID == id_of_user).filter(
                ITSRestAPIORMExtensions.ClientSession.Active).count()
            temp_session_tests = clientsession.query(ITSRestAPIORMExtensions.ClientSessionTest).filter(
                ITSRestAPIORMExtensions.ClientSessionTest.PersID == id_of_user).filter(
                ITSRestAPIORMExtensions.ClientSessionTest.Status < 30).count()
            if temp_session_tests == 0 or temp_sessions == 0:
                # no tests to take for this person any more, remove the login
                mastersession.query(ITSRestAPIORMExtensions.SecurityUser).filter(
                    ITSRestAPIORMExtensions.SecurityUser.ID == id_of_user).delete()

                person = clientsession.query(ITSRestAPIORMExtensions.ClientPerson).filter(
                    ITSRestAPIORMExtensions.ClientPerson.ID == id_of_user).first()
                if person is not None:
                    person.Active = False


@app.route('/reportdefinitions', methods=['GET'])
def reportdefinition_get():
    return ITSRestAPIORMExtensions.Report().common_paginated_read_request(request,
                                                                          ITR_minimum_access_levels.regular_office_user)


@app.route('/reportdefinitions/<identity>', methods=['GET', 'POST', 'DELETE'])
def reportdefinition_get_id(identity):
    basepathname = os.path.dirname(os.path.join(os.sep, app.instance_path, 'cache'))
    pathname = os.path.dirname(os.path.join(os.sep, app.instance_path, 'cache', ITSHelpers.string_split_to_filepath(identity)))
    include_master = False
    try:
        include_master = request.headers['IncludeMaster'] == "Y"
    except:
        pass
    cachedfilename = os.path.join(os.sep, pathname, "master_report.json") if include_master else os.path.join(os.sep, pathname, "report.json")

    if request.method == 'GET':
        if os.path.isfile(cachedfilename):
             return (open(cachedfilename, 'r').read()), 200
        else:
            to_return = ITSRestAPIORMExtensions.Report().return_single_object(request,
                                                                         ITR_minimum_access_levels.regular_office_user,
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
        check_master_header(request)
        if os.path.exists(pathname):
            ITSHelpers.remove_folder(pathname, basepathname)
        return ITSRestAPIORMExtensions.Report().change_single_object(request,
                                                                     ITR_minimum_access_levels.report_author,
                                                                     identity)
    elif request.method == 'DELETE':
        check_master_header(request)
        if os.path.exists(pathname):
            ITSHelpers.remove_folder(pathname, basepathname)
        return ITSRestAPIORMExtensions.Report().delete_single_object(request,
                                                                     ITR_minimum_access_levels.report_author,
                                                                     identity)

@app.route('/companies', methods=['GET'])
def companies_get():
    check_master_header(request)

    return ITSRestAPIORMExtensions.SecurityCompany().common_paginated_read_request(request,
                                                                                   ITR_minimum_access_levels.master_user,
                                                                                   "","",
                                                                                   True)


@app.route('/companies/<identity>', methods=['GET', 'POST', 'DELETE'])
def companies_get_id(identity):
    allowTestTakingUser = false
    token = request.headers['SessionID']
    if identity == "currentcompany":
        company_id, user_id, token_validated = ITSRestAPILogin.get_info_with_session_token(token)
        identity = company_id
        allowTestTakingUser = true
    else:
        check_master_header(request)

    if request.method == 'GET':
        if allowTestTakingUser:
            return ITSRestAPIORMExtensions.SecurityCompany().return_single_object(request,
                                                                              ITR_minimum_access_levels.test_taking_user,
                                                                              identity, True)
        else:
            return ITSRestAPIORMExtensions.SecurityCompany().return_single_object(request,
                                                                              ITR_minimum_access_levels.regular_office_user,
                                                                              identity, True)
    elif request.method == 'POST':
        check_master_header(request)
        return ITSRestAPIORMExtensions.SecurityCompany().change_single_object(request,
                                                                              ITR_minimum_access_levels.master_user,
                                                                              identity, "", True)
    elif request.method == 'DELETE':
        check_master_header(request)
        company_id, user_id, token_validated = ITSRestAPILogin.get_info_with_session_token(token)

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

        # delete any stored files
        folder_to_delete = os.path.join(os.sep, app.instance_path, 'media', str(identity) )
        shutil.rmtree(folder_to_delete, ignore_errors=True)

        return ITSRestAPIORMExtensions.SecurityCompany().delete_single_object(request,
                                                                              ITR_minimum_access_levels.master_user,
                                                                              identity, True)


@app.route('/creditgrants', methods=['GET'])
def creditgrants_get():
    check_master_header(request)

    return ITSRestAPIORMExtensions.SecurityCreditGrant().common_paginated_read_request(request,
                                                                                       ITR_minimum_access_levels.regular_office_user,
                                                                                       "", "", True)


@app.route('/creditgrants/<identity>', methods=['GET', 'POST', 'DELETE'])
def creditgrants_get_id(identity):
    check_master_header(request)
    if request.method == 'GET':
        return ITSRestAPIORMExtensions.SecurityCreditGrant().return_single_object(request,
                                                                                  ITR_minimum_access_levels.regular_office_user,
                                                                                  identity, True)
    elif request.method == 'POST':
        # increase the companies credit level with the saved credit grant
        token = request.headers['SessionID']
        company_id, user_id, token_validated = ITSRestAPILogin.get_info_with_session_token(token)
        id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, author_report_user, author_test_screen_templates_user, translator_user, office_user, is_password_manager = ITSRestAPILogin.get_id_of_user_with_token_and_company_id(
            user_id, company_id)

        if master_user:
            request.get_data()
            data = request.data
            data_dict = json.loads(data)

            masterengine = ITSRestAPIDB.get_db_engine_connection_master()
            masterengine.execution_options(isolation_level="AUTOCOMMIT").execute(
                'UPDATE "SecurityCompanies" SET "CurrentCreditLevel" = "CurrentCreditLevel" + ' + data_dict["CreditsGranted"] + ' where "ID" = \'' + data_dict["CompanyID"] + '\' ')

        return ITSRestAPIORMExtensions.SecurityCreditGrant().change_single_object(request,
                                                                                  ITR_minimum_access_levels.master_user,
                                                                                  identity,"",True)
    elif request.method == 'DELETE':
        return ITSRestAPIORMExtensions.SecurityCreditGrant().delete_single_object(request,
                                                                                  ITR_minimum_access_levels.master_user,
                                                                                  identity, True)


@app.route('/creditusages', methods=['GET'])
def creditusage_get():
    check_master_header(request)
    return ITSRestAPIORMExtensions.SecurityCreditUsage().common_paginated_read_request(request,
                                                                                       ITR_minimum_access_levels.regular_office_user)


@app.route('/creditusagespermonth', methods=['GET'])
def creditusagespermonth_get():
    token = request.headers['SessionID']
    company_id, user_id, token_validated = ITSRestAPILogin.get_info_with_session_token(token)

    if company_id != "":
        qry_session = ITSRestAPIDB.get_db_engine_connection_client(company_id)
        try:
            a = []
            a = qry_session.execute(
                'select date_part( \'year\', "UsageDateTime") as Year, date_part( \'month\', "UsageDateTime") as Month, sum("TotalTicks") as Ticks, sum("DiscountedTicks") as DiscountedTicks ' +
                'from "SecurityCreditUsage"' +
                'group by date_part( \'year\', "UsageDateTime"), date_part( \'month\', "UsageDateTime") ' +
                'order by date_part( \'year\', "UsageDateTime") desc, date_part( \'month\', "UsageDateTime") desc ').fetchall()
            if a == []:
                a.append({'Year': '2000', 'Month': '1', 'Ticks': '0', 'DiscountedTicks': '0'})
        finally:
            qry_session.dispose()
        return ITSRestAPIDB.query_array_to_jsonify(a)
    else:
        return "404", "No valid session token"


@app.route('/creditusages/<identity>', methods=['GET', 'POST', 'DELETE'])
def creditusage_get_id(identity):
    check_master_header(request)
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
    check_master_header(request)
    return ITSRestAPIORMExtensions.SecurityCreditUsage().common_paginated_read_request(request,
                                                                                       ITR_minimum_access_levels.regular_office_user)


@app.route('/datagathering/<identity>', methods=['GET', 'POST', 'DELETE'])
def datagathering_get_id(identity):
    if request.method == 'GET':
        check_master_header(request)
        return ITSRestAPIORMExtensions.SecurityCreditUsage().return_single_object(request,
                                                                                  ITR_minimum_access_levels.regular_office_user,
                                                                                  identity)
    elif request.method == 'POST':
        return ITSRestAPIORMExtensions.SecurityCreditUsage().change_single_object(request,
                                                                                  ITR_minimum_access_levels.regular_office_user,
                                                                                  identity)
    elif request.method == 'DELETE':
        check_master_header(request)
        return ITSRestAPIORMExtensions.SecurityCreditUsage().delete_single_object(request,
                                                                                  ITR_minimum_access_levels.regular_office_user,
                                                                                  identity)


@app.route('/rightstemplates', methods=['GET'])
def rightstemplates_get():
    check_master_header(request)

    return ITSRestAPIORMExtensions.SecurityTemplate().common_paginated_read_request(request,
                                                                                    ITR_minimum_access_levels.regular_office_user)


@app.route('/rightstemplates/<identity>', methods=['GET', 'POST', 'DELETE'])
def rightstemplates_get_id(identity):
    check_master_header(request)
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
    return ITSRestAPIORMExtensions.SecurityUser().common_paginated_read_request(request,
                                                                                ITR_minimum_access_levels.regular_office_user)


@app.route('/logins/<identity>', methods=['GET', 'POST', 'DELETE'])
def logins_get_id(identity):
    # get the session id and the user id from the token
    master_db_query = False
    token = request.headers['SessionID']
    company_id, user_id, token_validated = ITSRestAPILogin.get_info_with_session_token(token)
    id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, author_report_user, author_test_screen_templates_user, translator_user, office_user, is_password_manager = ITSRestAPILogin.get_id_of_user_with_token_and_company_id(
        user_id, company_id)
    if identity == 'currentuser':
        identity = id_of_user
        #master_db_query = True
    else:
        check_master_header(request)

    if request.method == 'GET':
        to_return = ITSRestAPIORMExtensions.SecurityUser().return_single_object(request,
                                                                           ITR_minimum_access_levels.test_taking_user,
                                                                           identity)
        #if not found then try the master database as well, candidates will NOT be created in the local company database
        try:
            if to_return[1] == 404:
                to_return = ITSRestAPIORMExtensions.SecurityUser().return_single_object(request,
                                                                                        ITR_minimum_access_levels.test_taking_user,
                                                                                    identity, True)
        except:
            pass

        #decrypt the API key if present
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
            #clientsession = sessionmaker(bind=ITSRestAPIDB.get_db_engine_connection_client(company_id))()
            # make sure that a new account cannot be added when the system is already at the maximum amount of consultants
            max_number_of_consultants = ITSRestAPISettings.get_setting_for_customer(company_id, 'MAXNUMBEROFCONSULTANTS', True, "")
            if max_number_of_consultants != "":
                max_number_of_consultants = int(max_number_of_consultants)
                if max_number_of_consultants >= 0:
                    consultant_count = clientsession.query(ITSRestAPIORMExtensions.SecurityUser).count()
                    if (consultant_count >= max_number_of_consultants):
                        # check if this is a new account, in that case abort
                        consultant_to_add_check =  clientsession.query(ITSRestAPIORMExtensions.SecurityUser).filter(
                                    ITSRestAPIORMExtensions.SecurityUser.ID == identity ).count()
                        if (consultant_to_add_check == 0):
                            return "Maximum number of consultants reached", 404
            # make sure the current user cannot grant more rights than the user itself owns
            consultant = clientsession.query(ITSRestAPIORMExtensions.SecurityUser).filter(
                ITSRestAPIORMExtensions.SecurityUser.ID == id_of_user).first()
            AllowedFieldsToChange = [col.name for col in ITSRestAPIORMExtensions.SecurityUser.__table__.columns]
            if not consultant.IsMasterUser:
                AllowedFieldsToChange.remove('IsMasterUser')
                if not consultant.IsTestTakingUser :
                    AllowedFieldsToChange.remove('IsTestTakingUser')
                if not consultant.IsOfficeUser :
                    AllowedFieldsToChange.remove('IsOfficeUser')
                if not consultant.IsOrganisationSupervisor :
                    AllowedFieldsToChange.remove('IsOrganisationSupervisor')
                if not consultant.IsTestAuthor :
                    AllowedFieldsToChange.remove('IsTestAuthor')
                if not consultant.IsReportAuthor :
                    AllowedFieldsToChange.remove('IsReportAuthor')
                if not consultant.IsTestScreenTemplateAuthor :
                    AllowedFieldsToChange.remove('IsTestScreenTemplateAuthor')
                if not consultant.IsPasswordManager:
                    AllowedFieldsToChange.remove('IsPasswordManager')
                if not consultant.IsTranslator :
                    AllowedFieldsToChange.remove('IsTranslator')
                if not consultant.MayOrderCredits :
                    AllowedFieldsToChange.remove('MayOrderCredits')
                if consultant.MayWorkWithBatteriesOnly :
                    AllowedFieldsToChange.remove('MayWorkWithBatteriesOnly')

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

            #never save the password in the clients database
            try:
                AllowedFieldsToChange.remove('Password')
            except:
                pass

            # save the user to the clients database
            return ITSRestAPIORMExtensions.SecurityUser().change_single_object(request,
                                                                           ITR_minimum_access_levels.regular_office_user,
                                                                           identity, ",".join(AllowedFieldsToChange) )
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
    company_id, user_id, token_validated = ITSRestAPILogin.get_info_with_session_token(token)

    if user_id != "":
        user_id = user_id.replace("'", "''")

        return ITSRestAPIORMExtensions.SecurityCompany().common_paginated_read_request(request,
                                                                                       ITR_minimum_access_levels.test_taking_user,
                                                                                       'a."ID" in (select distinct b."CompanyID" from "SecurityUsers" as b where b."Email" = \'+ user_id +\')')
    else:
        return "User not found or no known token linked to this user", 404

@app.route('/logins/currentuser/changepassword', methods=['POST'])
def login_change_password():
    # this is only available to the user him/herself
    # get the session id and the user id from the token
    token = request.headers['SessionID']
    company_id, user_id, token_validated = ITSRestAPILogin.get_info_with_session_token(token)
    id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, author_report_user, author_test_screen_templates_user, translator_user, office_user, is_password_manager = ITSRestAPILogin.get_id_of_user_with_token_and_company_id(
        user_id, company_id)

    if user_id != "":
        user_id = user_id.replace("'", "''")

        if not office_user:
            return "You do not have sufficient rights to change your password", 404
        else:
            request.get_data()
            temp_param = ITSHelpers.Empty()
            temp_param = json.loads(request.data)
            oldPW = temp_param["old_password"]
            newPW = temp_param["new_password"]

            if ITSRestAPILogin.login_user(user_id, oldPW, company_id) in (ITSRestAPILogin.LoginUserResult.ok, ITSRestAPILogin.LoginUserResult.multiple_companies_found):
                ITSRestAPILogin.update_user_password(user_id, newPW)
                return "The password has been changed", 200
            else:
                return "Your old password is not correct, please retry", 404
    else:
        return "User not found or no known token linked to this user", 404

@app.route('/tokens', methods=['GET'])
def tokens_get():
    check_master_header(request)

    return ITSRestAPIORMExtensions.SecurityWebSessionToken().common_paginated_read_request(request,
                                                                                           ITR_minimum_access_levels.master_user)


@app.route('/tokens/<identity>', methods=['GET', 'POST', 'DELETE'])
def tokens_get_id(identity):
    check_master_header(request)
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
    id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, translator_user, office_user, company_id, is_password_manager = check_master_header(
        request)

    if master_user:
        try:
            token = request.headers['SessionID']
            company_id, user_id, token_validated = ITSRestAPILogin.get_info_with_session_token(token)

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
        return "You are not authorised to make this call ",404

@app.route('/systemsettings', methods=['GET'])
def systemsettings_get():
    additional_where_clause = "ParProtected = false"
    return ITSRestAPIORMExtensions.SystemParam().common_paginated_read_request(request,
                                                                               ITR_minimum_access_levels.regular_office_user,
                                                                               additional_where_clause)


@app.route('/systemsettings/<identity>', methods=['GET', 'POST', 'DELETE'])
def systemsettings_get_id(identity):
    id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, translator_user, office_user, company_id, is_password_manager = check_master_header(request)

    if not office_user:
        return "You do not have sufficient rights to make this call", 404

    include_master_header = "N"
    try:
        include_master_header = request.headers['IncludeMaster']
    except:
        pass

    if include_master_header == "Y":
        if not master_user and request.method != 'GET':
            return "You do not have sufficient rights to make this call", 404
        #session = sessionmaker(bind=ITSRestAPIDB.get_db_engine_connection_master())()
        sessionid = ""
    else:
        if not organisation_supervisor_user and request.method != 'GET':
            return "You do not have sufficient rights to make this call", 404
        #session = sessionmaker(bind=ITSRestAPIDB.get_db_engine_connection_client(company_id))()
        sessionid = company_id

    with ITSRestAPIDB.session_scope(sessionid) as session:
        if request.method == 'GET':
            param = session.query(ITSRestAPIORMExtensions.SystemParam).filter(
                ITSRestAPIORMExtensions.SystemParam.ParameterName == identity).first()
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
            param = session.query(ITSRestAPIORMExtensions.SystemParam).filter(
                ITSRestAPIORMExtensions.SystemParam.ParameterName == identity).first()
            request.get_data()
            if param is None:
                param2 = ITSRestAPIORMExtensions.SystemParam()
                param2.ParameterName = identity
                param2.ParValue = request.data.decode('utf-8')
                #check if this parameter is protected
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
    basepathname = os.path.dirname(os.path.join(os.sep, app.instance_path, 'cache'))
    pathname = os.path.dirname(os.path.join(os.sep, app.instance_path, 'cache', ITSHelpers.string_split_to_filepath(identity)))
    try:
        include_master = request.headers['IncludeMaster'] == "Y"
    except:
        pass
    cachedfilename = os.path.join(os.sep, pathname, "master_template.json") if include_master else os.path.join(os.sep, pathname, "template.json")

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
        check_master_header(request)
        if os.path.exists(pathname):
            ITSHelpers.remove_folder(pathname, basepathname)
        temp = ITSRestAPIORMExtensions.TestScreenTemplate().change_single_object(request,
                                                                                 ITR_minimum_access_levels.test_screen_template_author,
                                                                                 identity)
        return temp
    elif request.method == 'DELETE':
        check_master_header(request)
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
    basepathname = os.path.dirname(os.path.join(os.sep, app.instance_path, 'cache'))
    pathname = os.path.dirname(os.path.join(os.sep, app.instance_path, 'cache', ITSHelpers.string_split_to_filepath(identity)))
    if request.method == 'GET':
        cachefilename = "test.json"
        # test taking users may request all test definition since they need them for test taking, but will get limited fields back to protect scoring and norming rules
        token = request.headers['SessionID']
        company_id, user_id, token_validated = ITSRestAPILogin.get_info_with_session_token(token)
        id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, author_report_user, author_test_screen_templates_user, translator_user, office_user, is_password_manager = ITSRestAPILogin.get_id_of_user_with_token_and_company_id(
            user_id, company_id)
        ITSRestAPIORMExtensions.Test().__class__.fields_to_be_removed = {}
        if (not office_user) and test_taking_user:
            # limit the amount of fields returned
            ITSRestAPIORMExtensions.Test().__class__.fields_to_be_removed = {
                "norms", "documents", "scoreRules", "graphs",
                "RequiredParsPerson", "RequiredParsSession", "RequiredParsGroup",
                "RequiredParsOrganisation"
            }
            cachefilename = "test_limited.json"

        # return the object
        try:
            include_master = request.headers['IncludeMaster'] == "Y"
        except:
            pass
        cachedfilefull = os.path.join(os.sep, pathname, "master_" + cachefilename) if include_master else os.path.join(os.sep, pathname, cachefilename)
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
                    text_file.write(json.dumps(to_return.json))
                    text_file.close()
            except:
                pass

            return to_return
    elif request.method == 'POST':
        check_master_header(request)
        if os.path.exists(pathname):
            ITSHelpers.remove_folder(pathname, basepathname)
        return ITSRestAPIORMExtensions.Test().change_single_object(request,
                                                                   ITR_minimum_access_levels.test_author,
                                                                   identity)
    elif request.method == 'DELETE':
        check_master_header(request)
        if os.path.exists(pathname):
            ITSHelpers.remove_folder(pathname, basepathname)
        return ITSRestAPIORMExtensions.Test().delete_single_object(request,
                                                                   ITR_minimum_access_levels.test_author,
                                                                   identity)


@app.route('/files/<company_id>/<maintainingObjectIdentity>/<fileType>', methods=['GET', 'DELETE'])
def files_get_id(company_id, maintainingObjectIdentity,fileType):
    masterFiles = False
    if company_id == "master":
        masterFiles = True
    token = request.headers['SessionID']
    company_id, user_id, token_validated = ITSRestAPILogin.get_info_with_session_token(token)
    id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, author_report_user, author_test_screen_templates_user, translator_user, office_user, is_password_manager = ITSRestAPILogin.get_id_of_user_with_token_and_company_id(
        user_id, company_id)
    pathname = os.path.dirname(
        os.path.join(os.sep, app.instance_path, 'media', str(company_id),
                     ITSHelpers.string_split_to_filepath(maintainingObjectIdentity)))
    basepathname = os.path.dirname(
        os.path.join(os.sep, app.instance_path, 'media', str(company_id)))
    # check if path exists, if not try the master path
    if (not os.path.isdir(pathname)) or masterFiles:
        pathname = os.path.dirname(
            os.path.join(os.sep, app.instance_path, 'media', 'master',
                     ITSHelpers.string_split_to_filepath(maintainingObjectIdentity)))
        basepathname = os.path.dirname(
            os.path.join(os.sep, app.instance_path, 'media', 'master'))
    if fileType != "all":
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
def files_copy_folder(maintainingObjectIdentity_src, maintainingObjectIdentity_dst):
    token = request.headers['SessionID']
    company_id, user_id, token_validated = ITSRestAPILogin.get_info_with_session_token(token)
    id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, author_report_user, author_test_screen_templates_user, translator_user, office_user, is_password_manager = ITSRestAPILogin.get_id_of_user_with_token_and_company_id(
        user_id, company_id)
    pathname_src = os.path.dirname(
        os.path.join(os.sep, app.instance_path, 'media', str(company_id),
                     ITSHelpers.string_split_to_filepath(maintainingObjectIdentity_src)))
    if maintainingObjectIdentity_dst.upper() == "MASTER":
        pathname_dst = os.path.dirname(os.path.join(os.sep, app.instance_path, 'media', 'master',
                         ITSHelpers.string_split_to_filepath(maintainingObjectIdentity_src) ))
    else:
        pathname_dst = os.path.dirname(
            os.path.join(os.sep, app.instance_path, 'media', str(company_id),
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
        company_id, user_id, token_validated = ITSRestAPILogin.get_info_with_session_token(token)
        id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, author_report_user, author_test_screen_templates_user, translator_user, office_user, is_password_manager = ITSRestAPILogin.get_id_of_user_with_token_and_company_id(
                user_id, company_id)
    fileType = fileType.upper()
    pathname = os.path.dirname(
        os.path.join(os.sep, app.instance_path, 'media', str(company_id),
                     ITSHelpers.string_split_to_filepath(maintainingObjectIdentity))) + os.sep + fileType
    filename = pathname + os.sep + ITSHelpers.to_filename(fileId)

    if request.method == 'GET':
        # if the file is not found try the master folder
        if not os.path.exists(filename):
            pathname = os.path.dirname(
                os.path.join(os.sep, app.instance_path, 'media', 'master',
                             ITSHelpers.string_split_to_filepath(maintainingObjectIdentity))) + os.sep + fileType
            filename = pathname + os.sep + ITSHelpers.to_filename(fileId)

        ip_address = getIP(request) # we need to check for ip in the future
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

            f = open(filename,"wb")
            try :
                tempStr = request.data
                f.write(tempStr)
            except Exception as e:
                app_log.error('File uploading failed %s',str(e))
                return "File uploading failed" , 500
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
    pathname = os.path.dirname(os.path.join(app.instance_path, 'translations/'))
    # check for master database existence. if not init the system for a smoother first time user experience
    #session = sessionmaker(bind=ITSRestAPIDB.get_db_engine_connection_master())()
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
def translations(langcode):
    if langcode == "":
        langcode = "en"
    langcode = langcode.lower()
    filename = os.path.join(app.instance_path, 'translations/', langcode + '.json')
    if request.method == 'GET':
        if os.path.isfile(filename):
            old_data = json.load(open(filename, 'r'))
            new_data = {}
            for line in old_data:
                new_data[line] = old_data[line]
                #print(old_data[line])
            with open(filename, 'r') as translationFile:
                return translationFile.read(), 200
        else:
            return "[]", 200
    elif request.method == 'POST':
        token = request.headers['SessionID']
        company_id, user_id, token_validated = ITSRestAPILogin.get_info_with_session_token(token)
        id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, author_report_user, author_test_screen_templates_user, translator_user, office_user, is_password_manager = ITSRestAPILogin.get_id_of_user_with_token_and_company_id(
            user_id, company_id)

        if (master_user or translator_user) and ITSTranslate.translation_available():
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
                translatedText = ITSTranslate.get_translation(langcode, new_data[line]['value'])
                if translatedText is not None :
                    old_data[line] = new_data[line]
                    old_data[line]['originalValue'] = new_data[line]['value']
                    old_data[line]['value'] = translatedText
                    old_data[line]['valueAsOriginal'] = 'N'
                    if old_data[line]['originalValue'] == old_data[line]['value']:
                        old_data[line]['valueAsOriginal'] = 'Y'
                    linesChanged = linesChanged + 1

                    if linesChanged > 0 and linesChanged % 25 == 0:
                        with open(filename, 'w') as translationFile: # make sure to save every 25 translations
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
    company_id, user_id, token_validated = ITSRestAPILogin.get_info_with_session_token(token)
    id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, author_report_user, author_test_screen_templates_user, translator_user, office_user, is_password_manager = ITSRestAPILogin.get_id_of_user_with_token_and_company_id(
        user_id, company_id)

    if (master_user or translator_user or author_user or author_report_user) and ITSTranslate.translation_available():
        request.get_data()
        x = request.headers['ToTranslate']
        text_to_translate = urllib.parse.unquote(x)

        translated_text = ITSTranslate.get_translation_with_source_language(sourcelangcode, targetlangcode, text_to_translate)
        return translated_text, 200
    else:
        return "Translations not available, check the azure translate string and the user's rights", 404

@app.route('/sendmail', methods=['POST'])
def send_mail():
    id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, translator_user, office_user, company_id, is_password_manager = check_master_header(request)

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
                            data_dict["From"], [] ,
                            data_dict["ReplyTo"])

            return "An email is sent", 200
        except Exception as e:
            return str(e), 500
    else:
        return "You are not authorised to sent emails",404

@app.route('/refreshpublics', methods=['POST'])
def refresh_publics():
    id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, translator_user, office_user, company_id, is_password_manager = check_master_header(
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
              param.ParameterName  = "LASTREPOREFRESH"
              session.add(param)
              newinstall = True
            else:
                lastrefreshday = int(param.ParValue)
            if lastrefreshday != currentrefreshday:
                param.ParValue = currentrefreshday
                clone_needed = True

        if clone_needed:
            ITSGit.clone_or_refresh_repo(app.instance_path,'https://github.com/Quopt/itr-reporttemplates')
            ITSGit.clone_or_refresh_repo(app.instance_path,'https://github.com/Quopt/itr-testtemplates')
            ITSGit.clone_or_refresh_repo(app.instance_path,'https://github.com/Quopt/itr-testscreentemplates')
            ITSGit.clone_or_refresh_repo(app.instance_path,'https://github.com/Quopt/itr-plugins')
            ITSGit.clone_or_refresh_repo(app.instance_path,'https://github.com/Quopt/itr-translations')
            ITSGit.clone_or_refresh_repo(app.instance_path,'https://github.com/Quopt/ITR-API')
            ITSGit.clone_or_refresh_repo(app.instance_path,'https://github.com/Quopt/ITR-webclient')
            ITSGit.clone_or_refresh_repo(app.instance_path,'https://github.com/Quopt/ITR-Public-API')

        return "OK", 200

    else:
        return "You are not authorised to refresh the public repositories", 404

@app.route('/listpublics/<reponame>', methods=['GET'])
def list_publics(reponame):
    id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, translator_user, office_user, company_id, is_password_manager = check_master_header(
        request)
    if master_user:
        tempfile =  ITSGit.list_repo_files(app.instance_path, reponame)
        return tempfile , 200

@app.route('/listpublics/<reponame>/<filename>', methods=['GET'])
def list_publics_file(reponame, filename):
    id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, translator_user, office_user, company_id, is_password_manager = check_master_header(
        request)
    if master_user:
        short_repo_name = reponame.split('/')[-1]
        newfilename = os.path.join(os.sep, app.instance_path, 'cache', 'git', short_repo_name, filename)
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

@app.route('/installpublics/itr-translations/<filename>', methods=['POST','DELETE'])
def install_publics_file( filename):
    id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, translator_user, office_user, company_id, is_password_manager = check_master_header(
        request)
    if master_user:
        srcfilename = os.path.join(os.sep, app.instance_path, 'cache', 'git', 'itr-translations', filename)
        newfilename = os.path.join(os.sep, app.instance_path, 'translations', filename)
        if request.method == "POST":
            try:
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

@app.errorhandler(500)
def internal_error(error):
    app_log.error("Internal server error 500 : %s", error)
    return "500 error"


if __name__ == '__main__':
    # app.debug = True
    # MET FLASK app.run()
    # app.run(debug=True)
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

    serve(app.wsgi_app, threads = itrthreads, listen="*:" + itrport)