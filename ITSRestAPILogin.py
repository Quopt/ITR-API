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

# this python file contains all logic to login users and send/reset passwords and other single user account
# related functions
import ITSRestAPIDB
import ITSRestAPIORMExtensions
from sqlalchemy.orm import *
from enum import Enum
import hashlib, uuid
from copy import deepcopy
import datetime

from ITSLogging import *


class LoginUserResult(Enum):
    ok = 1
    user_not_found = 2
    multiple_companies_found = 3


class LoginTokenType(Enum):
    regular_session = 1
    password_reset = 2


last_logged_in_user_id = ''
last_logged_in_company_id = ''


def login_user(user_id, user_password, company_id=""):
    # check if this is correct according to the database
    global last_logged_in_user_id
    global last_logged_in_company_id
    user_guid = ""
    password = ""
    connection = ITSRestAPIDB.get_db_engine_connection_master()
    number_of_companies = 0

    # check user id and password against the database
    try:
        if company_id != "":
            app_log.info('Verifying company ids for  %s', user_id)
            result = connection.execute(
                'select "CompanyID", "ID", "Password" from "SecurityUsers" where "Email" = %s and "CompanyID" = %s and "EndDateLicense" > now()',
                user_id, company_id)
        else:
            app_log.info('Fetching company ids for  %s', user_id)
            result = connection.execute(
                'select "CompanyID", "ID", "Password"  from "SecurityUsers" where "Email" = %s and "EndDateLicense" > now()',
                user_id)
        for recs in result:
            temp_user_guid = recs[1]
            temp_password = recs[2]
            hashed_password = hashlib.sha512((user_password + str(temp_user_guid)).encode('utf-8')).hexdigest()
            if hashed_password == temp_password or temp_password == user_password:
                number_of_companies = number_of_companies + 1
                last_logged_in_user_id = user_id
                last_logged_in_company_id = recs[0]
                user_guid = recs[1]
                password = recs[2]

    except:
        pass

    app_log.info('Number of companies found : %s', str(number_of_companies))
    if number_of_companies == 1:
        # check the password
        password_ok = False
        if password == user_password:
            password_ok = True
        hashed_password = hashlib.sha512((user_password + str(user_guid)).encode('utf-8')).hexdigest()
        if hashed_password == password:
            password_ok = True
        if password_ok :
            result = connection.execution_options(isolation_level="AUTOCOMMIT").execute('update "SecurityUsers" set "LastLoginDateTime" = now() where "Email" = %s and "Password" = %s and "CompanyID" = %s',
                    user_id, user_password, last_logged_in_company_id)
            connection.dispose()
            connection = ITSRestAPIDB.get_db_engine_connection_client(last_logged_in_company_id)
            result = connection.execution_options(isolation_level="AUTOCOMMIT").execute(
                'update "SecurityUsers" set "LastLoginDateTime" = now() where "Email" = %s ', user_id)
            connection.dispose()
            return LoginUserResult.ok
        else:
            connection.dispose()
            return LoginUserResult.user_not_found
    if number_of_companies > 1:
        connection.dispose()
        return LoginUserResult.multiple_companies_found

    connection.dispose()
    return LoginUserResult.user_not_found


def check_if_user_account_is_valid(user_id):
    # check if this is correct according to the database
    global last_logged_in_user_id
    global last_logged_in_company_id
    connection = ITSRestAPIDB.get_db_engine_connection()
    number_of_companies = 0

    # check user id and password against the database
    try:
        result = connection.execute(
            'select "CompanyID" from "SecurityUsers" where "Email" = %s and "EndDateLicense" > now()',
            user_id)
        for recs in result:
            last_logged_in_user_id = user_id
            last_logged_in_company_id = recs[0]
            number_of_companies = number_of_companies + 1
    finally:
        connection.dispose()

    if number_of_companies == 1:
        return LoginUserResult.ok
    if number_of_companies > 1:
        return LoginUserResult.multiple_companies_found

    return LoginUserResult.user_not_found


def create_session_token(user_id, company_id, login_token_type):
    # first create the token and then store it in the database
    # the token is returned as a string
    if login_token_type == LoginTokenType.regular_session:  # regular internet session
        token = 'W' + uuid.uuid4().hex
    else:  # password reset token
        token = 'P' + uuid.uuid4().hex
    connection = ITSRestAPIDB.get_db_engine_connection()
    check_for_dead_tokens(connection)
    try:
        connection.execution_options(isolation_level="AUTOCOMMIT").execute('insert into "SecurityWebSessionTokens" ("Token", "UserID", "CompanyID") values (%s,%s,%s)',
                       token, user_id, company_id)
    finally:
        connection.dispose()

    return token


def check_session_token(token_id):
    # Please note that the company id may change once on a token. This is currently not validated.
    # We only validate the combination of user_id and token_id for this token. IP addresses et cetera are ignored as well
    # this function returns True if the token is present and false if it is not
    connection = ITSRestAPIDB.get_db_engine_connection()
    number_of_tokens = 0
    try:
        check_for_dead_tokens(connection)
        for recs in connection.execute(
                'select count(*) from "SecurityWebSessionTokens" where "Token" = %s and "TokenValidated" > now() - interval \'10 minutes\' ',
                token_id):
            number_of_tokens = recs[0]

        if number_of_tokens == 1:
            connection.execution_options(isolation_level="AUTOCOMMIT").execute(
                'update "SecurityWebSessionTokens" set "TokenValidated" = now() where "Token" = %s',
                token_id)
    finally:
        connection.dispose()
    return number_of_tokens == 1


def check_for_dead_tokens(connection):
    connection.execute(
        'delete from "SecurityWebSessionTokens" where "TokenValidated" < now() - interval \'10 minutes\' ');


def get_company_with_session_token(token_id):
    # Please note that the company id may change once on a token. This is currently not validated.
    # We only validate the combination of user_id and token_id for this token. IP addresses et cetera are ignored as well
    # this function returns True if the token is present and false if it is not
    connection = ITSRestAPIDB.get_db_engine_connection()
    number_of_tokens = 0
    company_id = ""

    try:
        check_for_dead_tokens(connection)
        for recs in connection.execute(
                'select "CompanyID", "UserID" from "SecurityWebSessionTokens" where "Token" = %s and "TokenValidated" > now() - interval \'10 minutes\' ',
                token_id):
            company_id = recs[0]
            user_id = recs[1]

        if company_id != "":
            connection.execution_options(isolation_level="AUTOCOMMIT").execute(
                'update "SecurityWebSessionTokens" set "TokenValidated" = now() where "Token" = %s and "UserID" = %s',
                token_id,
                user_id)
    finally:
        connection.dispose()

    return company_id


def get_info_with_session_token(token_id):
    # get the user name as stored with the session token
    connection = ITSRestAPIDB.get_db_engine_connection()
    company_id = ""
    user_id = ""
    token_validated = ""

    try:
        check_for_dead_tokens(connection)
        for recs in connection.execute(
                'select "CompanyID", "UserID", "TokenValidated" from "SecurityWebSessionTokens" where "Token" = %s ',
                token_id):
            company_id = recs[0]
            user_id = recs[1]
            token_validated = recs[2]
    finally:
        connection.dispose()

    return company_id, user_id, token_validated


def get_id_of_user_with_token_and_company_id(user_id, company_id):
    # get the id of the user name with the company id and the user id
    connection = ITSRestAPIDB.get_db_engine_connection()
    id_of_user = ""
    master_user = ""
    test_taking_user = ""
    organisation_supervisor_user = ""
    author_user = ""
    translator_user = ""
    author_report_user = ""
    author_test_screen_templates_user = ""
    office_user = ""

    try:
        for recs in connection.execute(
                'select "ID", "IsMasterUser", "IsTestTakingUser", "IsOrganisationSupervisor", "IsTestAuthor", "IsReportAuthor", "IsTestScreenTemplateAuthor", "IsTranslator", "IsOfficeUser" from "SecurityUsers" where "CompanyID" = %s and "Email" = %s order by "IsOfficeUser"',
                company_id, user_id):
            id_of_user = recs[0]
            master_user = recs[1]
            test_taking_user = recs[2]
            organisation_supervisor_user = recs[3]
            author_user = recs[4]
            author_report_user = recs[5]
            author_test_screen_templates_user = recs[6]
            translator_user = recs[7]
            office_user = recs[8]
    finally:
        try:
         connection.dispose()
        except:
         pass

    return id_of_user, master_user, test_taking_user, organisation_supervisor_user, author_user, author_report_user, author_test_screen_templates_user, translator_user, office_user


def create_or_update_testrun_user(user_guid, company_id, user_id, new_password, active_status, delete_only):
    with ITSRestAPIDB.session_scope("") as session:
        user_query = session.query(ITSRestAPIORMExtensions.SecurityUser).filter(ITSRestAPIORMExtensions.SecurityUser.Email == user_id).\
            filter(ITSRestAPIORMExtensions.SecurityUser.CompanyID == company_id).\
            filter(ITSRestAPIORMExtensions.SecurityUser.ID == user_guid)
        user_list = user_query.all()
        old_id = ""

        if len(user_list) > 1 :
            old_id = user_list[0].ID
            user_query.delete()

        if len(user_list) == 1 :
            new_user = user_list[0]
        else :
            new_user = ITSRestAPIORMExtensions.SecurityUser()
            new_user.ID = user_guid
            new_user.CompanyID = company_id
            new_user.IsOfficeUser = False

        #insert new
        if active_status and not delete_only:
            new_user.Email = user_id
            new_user.UserName = user_id
            hashed_password = hashlib.sha512((new_password + str(user_guid)).encode('utf-8')).hexdigest()
            new_user.Password = hashed_password
            new_user.Active = active_status
            new_user.IsTestTakingUser = True
            session.add(new_user)

def delete_login(user_guid):
    with ITSRestAPIDB.session_scope("") as session:
        session.query(ITSRestAPIORMExtensions.SecurityUser).filter(ITSRestAPIORMExtensions.SecurityUser.ID == user_guid).delete()

def update_user_password(user_id, new_password, user_guid = ""):
    connection = ITSRestAPIDB.get_db_engine_connection()
    try:
        if user_guid == "":
          result = connection.execute(
                'select "CompanyID", "ID" from "SecurityUsers" where "Email" = %s',
                user_id)
        else:
            result = connection.execute(
                'select "CompanyID", "ID" from "SecurityUsers" where "ID" = %s',
                user_guid)
        for recs in result:
            company_id = recs[0]
            user_guid = recs[1]

            hashed_password = hashlib.sha512((new_password + str(user_guid)).encode('utf-8')).hexdigest()
            connection.execution_options(isolation_level="AUTOCOMMIT").execute('update "SecurityUsers" set "Password" = %s, "PasswordExpirationDate" = (NOW() + interval \'3 months\') where "Email" = %s and "ID" = %s',
                    hashed_password, user_id, user_guid)

            clientconnection = ITSRestAPIDB.get_db_engine_connection(str(company_id))
            try:
                clientconnection.execution_options(isolation_level="AUTOCOMMIT").execute(
                    'update "SecurityUsers" set "PasswordExpirationDate" = (NOW() + interval \'3 months\') where "ID" = %s',
                    user_guid)
            finally:
                clientconnection.dispose()
    finally:
        connection.dispose()


def delete_session_token(token_id):
    connection = ITSRestAPIDB.get_db_engine_connection()
    try:
        connection.execution_options(isolation_level="AUTOCOMMIT").execute('delete from "SecurityWebSessionTokens" where "Token" = %s',
                       token_id)
    finally:
        connection.dispose()

def delete_all_company_users(company_id):
    if company_id != "":
        connection = ITSRestAPIDB.get_db_engine_connection()
        try:
            connection.execution_options(isolation_level="AUTOCOMMIT").execute('delete from "SecurityUsers" where "CompanyID" = %s',
               company_id)
        finally:
            connection.dispose()

def change_token_company(token_id, company_id):
    connection = ITSRestAPIDB.get_db_engine_connection()
    try:
        connection.execution_options(isolation_level="AUTOCOMMIT").execute('update "SecurityWebSessionTokens" set "CompanyID" = %s where "Token" = %s',
            company_id, token_id)
    finally:
        connection.dispose()

    # check if the database exists, otherwise create
    connection = ITSRestAPIDB.get_db_engine_connection_client(company_id)
    connection.dispose()

def clone_user_login(user_id, user_guid, old_company_id, new_company_id):
    connection = ITSRestAPIDB.get_db_engine_connection()

    try:
        result = connection.execute(
                'select count(*) from "SecurityUsers" where "Email" = %s and "CompanyID" = %s',
                user_id, new_company_id)
        for recs in result:
            new_count = recs[0]

        if new_count == 0:
            query = """INSERT INTO
            "SecurityUsers"(
                "ID", "CompanyID", "Email", "Password", "UserOpeningsScreen", "UserName", "UserRights", "UserParameters",
                "PreferredLanguage", "MailAddress", "VisitingAddress", "InvoiceAddress", "InformationAddress", "Remarks",
                "PasswordExpirationDate", "StartDateLicense", "EndDateLicense", "LastLoginDateTime", "LastRefreshDateTime",
                "IsMasterUser", "IsTestTakingUser", "IsOfficeUser", "IsOrganisationSupervisor", "IsTestAuthor",
                "IsReportAuthor", "IsTestScreenTemplateAuthor", "IsTranslator", "MayOrderCredits",
                "MayWorkWithBatteriesOnly", "DoNotRenewLicense", "Active", "UserCulture", "SessionPool",
                "MayWorkWithOwnObjectsOnly", "SecurityTemplateID", "HasPersonalCreditPool", "CurrentPersonalCreditLevel",
                "PluginData")
            select
            %s, %s, "Email", '22CentigradeInArequipaToday' as "Password", "UserOpeningsScreen", "UserName", "UserRights", "UserParameters", "PreferredLanguage", "MailAddress", "VisitingAddress", "InvoiceAddress", "InformationAddress", "Remarks", "PasswordExpirationDate", "StartDateLicense", "EndDateLicense", "LastLoginDateTime", "LastRefreshDateTime", "IsMasterUser", "IsTestTakingUser", "IsOfficeUser", "IsOrganisationSupervisor", "IsTestAuthor", "IsReportAuthor", "IsTestScreenTemplateAuthor", "IsTranslator", "MayOrderCredits", "MayWorkWithBatteriesOnly", "DoNotRenewLicense", "Active", "UserCulture", "SessionPool", "MayWorkWithOwnObjectsOnly", "SecurityTemplateID", "HasPersonalCreditPool", "CurrentPersonalCreditLevel", "PluginData"
            from
            "SecurityUsers"
            where
            "ID" = %s """

            new_user_guid =  uuid.uuid4()
            connection.execution_options(isolation_level="AUTOCOMMIT").execute(query,
                  new_user_guid, new_company_id, user_guid)

            # now copy this login to the client database
            with ITSRestAPIDB.session_scope("") as mastersession:
                with ITSRestAPIDB.session_scope(new_company_id) as clientsession:
                    consultant = mastersession.query(ITSRestAPIORMExtensions.SecurityUser).filter(
                        ITSRestAPIORMExtensions.SecurityUser.ID == new_user_guid).first()
                    try:
                        clientsession.query(ITSRestAPIORMExtensions.SecurityUser).filter(
                          ITSRestAPIORMExtensions.SecurityUser.Email == user_id).delete()
                    except:
                        pass
                    newconsultant = ITSRestAPIORMExtensions.SecurityUser()
                    newconsultant.ID = consultant.ID
                    newconsultant.CompanyID = consultant.CompanyID
                    newconsultant.Email = consultant.Email
                    newconsultant.UserName = consultant.UserName
                    newconsultant.PasswordExpirationDate = datetime.datetime(2000, 1, 1)
                    newconsultant.Password = ""
                    newconsultant.IsMasterUser = consultant.IsMasterUser
                    newconsultant.IsOfficeUser = consultant.IsOfficeUser
                    newconsultant.IsOrganisationSupervisor = consultant.IsOrganisationSupervisor
                    newconsultant.IsTestAuthor = consultant.IsTestAuthor
                    newconsultant.IsReportAuthor = consultant.IsReportAuthor
                    newconsultant.IsTestScreenTemplateAuthor = consultant.IsTestScreenTemplateAuthor
                    newconsultant.IsTranslator = consultant.IsTranslator
                    newconsultant.MayOrderCredits = consultant.MayOrderCredits
                    newconsultant.MayWorkWithBatteriesOnly = consultant.MayWorkWithBatteriesOnly
                    newconsultant.MayWorkWithOwnObjectsOnly = consultant.MayWorkWithOwnObjectsOnly
                    newconsultant.Active = consultant.Active
                    clientsession.add(newconsultant)
                    clientsession.commit()

    except Exception as e:
        app_log.error('creating new user failed : ' + str(e))
    finally:
        connection.dispose()