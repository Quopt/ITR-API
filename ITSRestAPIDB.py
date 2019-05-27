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

# this python file contains all database related functions
import sqlalchemy
import urllib
import os
import sys
import traceback
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import Pool, NullPool
import sqlalchemy_utils
from flask import *
import uuid
import threading
import time

import application
import ITSRestAPISettings
import ITSRestAPIORM
import ITSRestAPIORMExtensions
from ITSLogging import *
from contextlib import contextmanager

@contextmanager
def session_scope(company_id, create_db_if_it_does_not_exist = True):
    """Provide a transactional scope around a series of operations."""
    session = sessionmaker(bind=get_db_engine_connection_client(company_id, create_db_if_it_does_not_exist))()
    #session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

database_version_checked = False
version_checked_databases = []
db_engines_created = {}
sem = threading.Semaphore()

def get_db_engine_connection_master():
    return get_db_engine_connection('')


def get_db_engine_connection_client(client_db, create_db_if_it_does_not_exist = True):
    return get_db_engine_connection(client_db, create_db_if_it_does_not_exist)


def get_orm_client_master():
    session = sessionmaker(bind=get_db_engine_connection())
    return session()


def get_orm_client_session(client_db):
    session = sessionmaker(bind=get_db_engine_connection(client_db))
    return session()


def get_master_db_name():
    return ITSRestAPISettings.get_setting('DBPREFIX') + 'Master'


def get_db_engine_connection(db_name="", create_db_if_it_does_not_exist = True):
    global database_version_checked
    global last_database_version_checked
    global orm_session

    if db_name == "" or db_name == "Master":
        db_name = 'Master'
    else:
        db_name = '{' + str(db_name) + '}'
    if db_name not in version_checked_databases:
        database_version_checked = False
    else:
        database_version_checked = True

    # gets a connection to the master database
    db_prefix = ITSRestAPISettings.get_setting('DBPREFIX')
    db_base_connect_string = ITSRestAPISettings.get_setting('DBCONNECTSTRING')
    db_connect_string = db_base_connect_string + db_prefix + db_name
    db_engine = ITSRestAPISettings.get_setting('DBENGINE')
    db_connectionpoolsize = int(ITSRestAPISettings.get_setting('CONNECTIONPOOLSIZE', '0'))
    db_connectionlogging = ITSRestAPISettings.get_setting('CONNECTIONLOGGING', 'N')
    db_full_connect_string = ""

    if db_connect_string is None:
        raise Exception('Database connection setting not present in the application.cfg file')

    # connect to the database
    if len(db_engine) > 0:
        params = db_connect_string  # urllib.parse.quote_plus(db_connect_string)
        db_full_connect_string = "%s%s" % (db_engine, params)
    else:
        db_full_connect_string = db_connect_string
    if db_full_connect_string not in db_engines_created:
        if db_connectionpoolsize <= 0:
            db_engine_object = sqlalchemy.create_engine(db_full_connect_string, poolclass=NullPool)
        else:
            db_engine_object = sqlalchemy.create_engine(db_full_connect_string, max_overflow=db_connectionpoolsize, pool_size=db_connectionpoolsize)
        db_engines_created[db_full_connect_string] = db_engine_object
        # enable sql alchemy query logging
        if db_connectionlogging == "INFO":
            logging.basicConfig()
            logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
        if db_connectionlogging == "WARNING":
            logging.basicConfig()
            logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
        if db_connectionlogging == "ERROR":
            logging.basicConfig()
            logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)
    else:
        db_engine_object = db_engines_created[db_full_connect_string]

    # check for correct database version
    if not database_version_checked:
        try:
            useTableSpace = ITSRestAPISettings.get_setting("USETABLESPACE")
            if useTableSpace == "Y":
                db_engine_object.execute("SET default_tablespace = ITR" + ITSRestAPISettings.get_setting("USETABLESPACEPOSTFIX"));
            db_version_check = db_engine_object.execute(
                'select "SystemParam"."ParValue" from "SystemParam" where "ParameterName" = \'DBVersion\' ')
            db_version = 1
            for row in db_version_check:
                db_version = row['ParValue']

            # database is there so do not create it any more
            create_db_if_it_does_not_exist = False

            migrate_db(db_engine_object, db_prefix + db_name, db_version, db_name)

            version_checked_databases.append(db_name)
        except Exception as e:
            # database is not there, create it
            #sem.acquire()
            try:
                if create_db_if_it_does_not_exist:
                    # sqlalchemy_utils.create_database(db_full_connect_string)
                    create_db(db_prefix + db_name)
                    #ITSRestAPIORM.metadata.create_all(db_engine_object)
                    migrate_db(db_engine_object, db_prefix + db_name, 1, db_name)
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
                app_log.info('Exception on db version check %s', ''.join(' ' + line for line in lines))
            #sem.release()

    db_engine_object.dispose()

    return db_engine_object


def create_db(db_name):
    # create connect string to the master database
    app_log.info('Database not found, will create the db %s', db_name)
    db_base_connect_string = ITSRestAPISettings.get_setting('DBCONNECTSTRING')
    db_connect_string = db_base_connect_string + 'postgres'
    db_engine = ITSRestAPISettings.get_setting('DBENGINE')
    db_folder = ITSRestAPISettings.get_setting('DBFOLDER')
    if db_folder == "":
        db_folder = os.path.join(application.app.instance_path, 'db')
    else:
        if db_folder.find('/') == 0 or db_folder.find('\\') == 0:
            pass
        else:
            db_folder = os.path.join(application.app.instance_path, db_folder)
    db_full_connect_string = ""
    if len(db_engine) > 0:
        params = db_connect_string  # urllib.parse.quote_plus(db_connect_string)
        db_full_connect_string = "%s%s" % (db_engine, params)
        #app_log.info('Opening db connection for creation to %s', db_full_connect_string)
        db_engine_object = sqlalchemy.create_engine(db_full_connect_string, poolclass=NullPool)
    else:
        db_full_connect_string = db_connect_string
        #app_log.info('Opening db connection for creation to %s', db_connect_string)
        db_engine_object = sqlalchemy.create_engine(db_connect_string, poolclass=NullPool)

    # create the tablespace
    try:
        tempStr = "create tablespace ITR location '" + db_folder + "'"
        useTableSpace =  ITSRestAPISettings.get_setting("USETABLESPACE")
        if useTableSpace == "Y" :
           db_engine_object.execution_options(isolation_level="AUTOCOMMIT").execute(tempStr)
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        app_log.info('Exception on db tablespace create %s', ''.join(' ' + line for line in lines))
    # create the database by opening the script and firing off the script commands one by one
    sql_path = ITSRestAPISettings.get_setting("SQLPATH")
    if sql_path == "":
        sql_path = os.path.join(application.app.root_path, 'database')
    sql_command = ""
    file_name = os.sep + "CREATEDB.SQL"

    run_db_script(db_engine_object, db_name, file_name, sql_path)

new_company_id = uuid.uuid4()
admin_user_id = uuid.uuid4()
def run_db_script(db_engine_object, db_name, file_name, sql_path):
    sql_command = ""
    db_tablespace =  ""
    useTableSpace = ITSRestAPISettings.get_setting("USETABLESPACE")
    db_tablespace = "pg_default"
    if useTableSpace == "Y":
        db_tablespace = "ITR" + ITSRestAPISettings.get_setting("USETABLESPACEPOSTFIX")

    global new_company_id, admin_user_id

    app_log.info('Running db script %s on %s' % (file_name, db_name))
    with open(sql_path + file_name, 'r') as f:
        for line in f:
            if line.strip() == "":
                # now execute the command if any, dont care what the result is, let exceptions bubble up
                if sql_command != "":
                    sql_command_subst = sql_command.replace('%DBNAME%', db_name)
                    sql_command_subst = sql_command_subst.replace('%TABLESPACE%', db_tablespace )
                    sql_command_subst = sql_command_subst.replace('%NEWCOMPANYID%', str(new_company_id))
                    sql_command_subst = sql_command_subst.replace('%ADMINUSERID%', str(admin_user_id))
                    #app_log.info(' %s > %s' % (db_name, sql_command_subst))
                    db_engine_object.execution_options(isolation_level="AUTOCOMMIT").execute(sql_command_subst)
                sql_command = ""
            else:
                # add to the command to be executed
                if line.find('--') == 0 or line.find('//') == 0 :
                    pass
                else:
                    sql_command = sql_command + line + "\r\n"


def migrate_db(db_engine, db_name, current_version, db_id):
    global new_company_id, admin_user_id
    if db_id != 'Master':
        new_company_id = db_id
        #mc = sessionmaker(bind=get_db_engine_connection_master())()
        with session_scope("") as mc:
            admin_user = mc.query(ITSRestAPIORMExtensions.SecurityUser ).filter( ITSRestAPIORMExtensions.SecurityUser.Email == "Admin").first()
            if admin_user is not None:
                admin_user_id = admin_user.ID

    # migrate the database if a migration is known
    sql_path = ITSRestAPISettings.get_setting("SQLPATH")
    if sql_path == "":
        sql_path = os.path.join(application.app.root_path, 'database')
    # check if there is a migration file, if not abort
    file_name = os.sep + "MIGRATEDB" + str(current_version) + ".SQL"
    if os.path.isfile(sql_path + file_name):
        run_db_script(db_engine, db_name, file_name, sql_path)
        migrate_db(db_engine, db_name, current_version + 1, db_id)


def query_array_to_jsonify(qry_result):
    qry_array = []
    for result_row in qry_result:
        qry_array.append(dict(result_row))
    return jsonify(qry_array)

def drop_database(company_id):
    mconnect = get_db_engine_connection_master()
    database_name = ITSRestAPISettings.get_setting('DBPREFIX') + "{" + str(company_id) + "}"

    mconnect.execute("""SELECT pg_terminate_backend(pg_stat_activity.pid)
                    FROM pg_stat_activity
                    WHERE pg_stat_activity.datname = %s
                    AND pid <> pg_backend_pid();""", database_name);
    mconnect.execution_options(isolation_level="AUTOCOMMIT").execute("DROP DATABASE \"" +  database_name + "\"");
