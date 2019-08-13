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

import ITSRestAPIDB
import ITSRestAPILogin
import ITSRestAPIORMExtensions
from ITSLogging import *

from sqlalchemy import *
from sqlalchemy.orm import *
from flask import *
import traceback

class ITR_minimum_access_levels(Enum):
    test_taking_user = 1
    regular_office_user = 2
    organisation_supervisor = 3
    test_author = 4
    master_user = 5
    translator = 6
    report_author = 7
    test_screen_template_author = 8
    password_manager = 9
    data_researcher = 10


class ORMExtendedFunctions:
    def paginated_query_no_orm(self, client_database_id="", start_page=1, page_size=25, filter_expression="",
                               record_filter=[],
                               sort_fields=[],
                               include_archived=None, include_master=False, limit_by_user_id="",
                               additional_unchecked_where_clause="", include_client = True):
        filter_expression = filter_expression.strip()
        # print("X1")

        if start_page < -1:  # first page is 0, -1 means return all
            start_page = 0
        # print("X3")

        start_nr = (start_page) * page_size
        end_nr = (start_page + 1) * page_size
        start_nr = str(start_nr)
        end_nr = str(end_nr)
        # print("X4")

        # start building the where clauses
        where_clause = ""
        # archived or not
        if (include_archived is True) and len(self.archive_field) > 0:
            where_clause = "A.\"" + self.archive_field + "\" = False "
        if (include_archived is False) and len(self.archive_field) > 0:
            where_clause = "A.\"" + self.archive_field + "\" = True "
        # filter_expression for all indicated filter fields
        filter_where = ""
        if filter_expression != "":
            if len(self.unified_search_fields) > 0:
                for c in self.unified_search_fields:
                    if filter_where == "":
                        filter_where = filter_where + "(cast(A.\"" + c + "\" as varchar(100)) "
                    else:
                        filter_where = filter_where + " || cast(A.\"" + c + "\" as varchar(100)) "
            else:
                for c in inspect(self).mapper.column_attrs:
                    if filter_where == "":
                        filter_where = filter_where + "(cast(A.\"" + c.key + "\" as varchar(100)) "
                    else:
                        filter_where = filter_where + " || cast(A.\"" + c.key + "\" as varchar(100)) "
            filter_where = filter_where + " ilike \'%%" + filter_expression.replace("'", "'+char(39)+'") + "%%\' )"
        # print("X5")

        # single field filter expression.
        filter_where_single = ""
        if len(record_filter) > 0:
            last_field_in_filter_line = ""
            for filter_line in record_filter:
                field_in_filter_line = filter_line.split('=')[0]
                value_in_filter_line = filter_line.split('=')[1]
                field_in_filter_line = field_in_filter_line.strip()
                value_in_filter_line = value_in_filter_line.strip()
                # now strip the first and last char of the value_in_filterline
                if value_in_filter_line[0] == "'":
                    value_in_filter_line = value_in_filter_line[1:]
                if value_in_filter_line[len(value_in_filter_line) - 1] == "'":
                    value_in_filter_line = value_in_filter_line[:len(value_in_filter_line) - 1]

                separator = "="
                if field_in_filter_line.endswith(">") or field_in_filter_line.endswith("<"):
                    separator = field_in_filter_line[-1:] + separator
                    field_in_filter_line = field_in_filter_line[:-1]
                if field_in_filter_line.endswith("%"):
                    separator = "like"
                    field_in_filter_line = field_in_filter_line[:-1]
                if field_in_filter_line in inspect(self).mapper.column_attrs:
                    if filter_where_single == "":
                        filter_where_single = "A.\"" + field_in_filter_line + "\" "+separator+" '" + value_in_filter_line.replace(
                            "'", "''") + "' "
                    else:
                        if last_field_in_filter_line == field_in_filter_line :
                            filter_where_single = "(" +  filter_where_single + " or A.\"" + field_in_filter_line + "\" "+separator+" '" + value_in_filter_line.replace(
                                "'", "''") + "' )"
                        else:
                            filter_where_single = filter_where_single + " and A.\"" + field_in_filter_line + "\" "+separator+" '" + value_in_filter_line.replace("'", "''") + "' "
                    last_field_in_filter_line = field_in_filter_line
        # print("X6")
        if limit_by_user_id != "":
            if filter_where_single == "":
                filter_where_single = "A.\"" + self.may_work_with_own_objects_field + "\" = '" + limit_by_user_id + "'"
            else:
                filter_where_single = filter_where_single + " and A.\"" + self.may_work_with_own_objects_field + "\" = '" + limit_by_user_id + "'"

        # construct order by
        order_by = ""
        if len(sort_fields) > 0:
            for sort_line in sort_fields:
                sort_line = sort_line.strip()
                if sort_line != "":
                    if len(sort_line.split(' ')) > 1:
                        sort_line_field_only = sort_line.split(' ')[0]
                    else:
                        sort_line_field_only = sort_line
                    if order_by == "":
                        order_by = "A.\"" + sort_line_field_only + "\""
                    else:
                        order_by = order_by + ", A.\"" + sort_line_field_only + "\""
                    if len(sort_line.split(' ')) > 1:
                        order_by  = order_by + " DESC "
        if order_by == "":
            if self.default_order_by_field != "":
                for line in self.default_order_by_field.split(','):
                    if order_by != "":
                        order_by = order_by + ","
                    order_by = order_by + "A.\"" + line.strip() + "\""
        # print("X7")

        # construct select
        select_fields_text = ""
        if len(self.select_fields) > 0:
            for line in self.select_fields:
                if select_fields_text == "":
                    select_fields_text = "\"" + line + "\""
                else:
                    select_fields_text = select_fields_text + ", \"" + line + "\""
        else:
            select_fields_text = "*"
        # print("X8")

        if self.identity_field != "":
            select_fields_text = "\"" + self.identity_field + "\" as ID, " + select_fields_text
        # print("X9 ")

        temp_orderby = ""
        if order_by != "":
            temp_orderby = "OVER ( ORDER BY " + order_by + ") "
        # print("X9A " + temp_orderby)
        # print("X9A " + filter_where)
        # print("X9A " + select_fields_text)
        # print("X9A " + start_nr)
        # print("X9A " + end_nr)
        # print("X9A " + filter_where_single)

        # determine if paging is needed
        row_selector = ""
        if start_page >= 0:
            row_selector = "where (RowNumber BETWEEN " + str(int(start_nr) + 1) + " AND " + end_nr + ") "

        # filter where total construction
        filter_where_total = ""
        if filter_where_single != "":
            if filter_where != "":
                filter_where_total = "where " + filter_where
            else:
                filter_where_total = "where " + filter_where_single
        else:
            if filter_where != "":
                filter_where_total = "where " + filter_where

        if additional_unchecked_where_clause != "":
            if filter_where_total != "":
                filter_where_total = filter_where_total + " and (" + additional_unchecked_where_clause + ")"
            else:
                filter_where_total = "where (" + additional_unchecked_where_clause + ")"
        if filter_where_total == "":
            if where_clause != "":
                filter_where_total =  " where " +where_clause
        else:
            if where_clause != "" :
                filter_where_total = filter_where_total + " and " + where_clause

        # construct the final query
        temp_table_name = self.__tablename__
        final_select = "with TempTable as  ( select ROW_NUMBER() " + temp_orderby + " AS RowNumber, A.* from \"" + temp_table_name + "\" as A " + filter_where_total + ")  select " + \
                       select_fields_text + ", 0 as dbsource from TempTable " + row_selector
        # print("X10")
        # this string is a copy of final_select but with the master database name included
        final_select_master = "with TempTable as  ( select ROW_NUMBER() " + temp_orderby + " AS RowNumber, A.* from \"" + temp_table_name + "\" as A " + filter_where_total + ")  select " + \
                              select_fields_text + ", 1 as dbsource from TempTable " + row_selector
        # print("X11")
        # now construct the total query
        if client_database_id == "":
            qry_session = ITSRestAPIDB.get_db_engine_connection_master()
        else:
            qry_session = ITSRestAPIDB.get_db_engine_connection_client(client_database_id)

        a = []
        if include_master:
            try:
                if include_client:
                    try:
                        stmt = text(final_select)
                        qry = qry_session.execute(stmt)
                        a = qry.fetchall()
                    finally:
                        qry_session.dispose()
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
                app_log.info('Query on client failed :  %s', ''.join(' ' + line for line in lines))
            qry_session_master = ITSRestAPIDB.get_db_engine_connection_master()
            try:
                b = []
                stmt = text(final_select_master)
                qry = qry_session_master.execute(stmt)
                b = qry.fetchall()
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
                app_log.info('Query on master failed :  %s', ''.join(' ' + line for line in lines))
            qry_session_master.dispose()
            c = a + b
            return c
        else:
            try:
                stmt = text(final_select)
                qry = qry_session.execute(stmt)
                #qry = qry_session.execute(text(final_select)).fetchall()
                a = qry.fetchall()
            except:
                app_log.error("Query could not be executed : %s", final_select)
            finally:
                qry_session.dispose()
            return a

    def common_paginated_read_request(self, request, required_minimum_access_level, additional_filter="",
                                      additional_unchecked_where_clause="", force_masterdb=False):
        # Other supported parameters as host headers are :
        # MASTER -  Set to Y if this is a master database call.
        # SessionID - a unique number that identifies the session. This is the only number stored server side, together with the user id and company id.
        #             the rest of the information is completely transparent. If someone logs in twice with different users this means that data for example
        #             can be copied between customers and so forth. The Session ID is required and must be issued
        # UserID - the user name of this user
        # CompanyID - the id of the company this user is linked to
        # IncludeArchived - set to Y to include archived information when requesting data
        # IncludeMaster - set to Y to include information from the master database (if supported on that specific path)
        # StartPage - pagination support - the first page to return information for
        # PageSize - the size (number of records) to return
        # Filter - the filter that needs to be applied to the returned records (SQL style so field=value. This will be converted to a sql LIKE search)
        # Sort - the sort order (SQL style, so field names seperated by commas and DESC when you need to sort the other way around)
        # SearchField - if you want to search but not on a specific field then set this string. It will be applied as generic search term (not on all paths)

        # get the settings from the request header
        object_to_query = self

        company_id, filter_expression, include_archived, include_master, limit_by_user_id, master_only, page_size, proceed, record_filter, sort_fields, start_page, include_client, is_test_taking_user, user_id = self.check_and_parse_request_parameters(
            additional_filter, object_to_query, request, required_minimum_access_level)

        # and now take action
        if proceed and company_id != "":
            # and now execute the query
            if master_only or force_masterdb:
                company_id = ""

            qry_result = object_to_query.paginated_query_no_orm(company_id, start_page, page_size, filter_expression,
                                                                record_filter, sort_fields, include_archived,
                                                                include_master, limit_by_user_id,
                                                                additional_unchecked_where_clause, include_client)
            return ITSRestAPIDB.query_array_to_jsonify(qry_result)
        else:
            return "Invalid or expired token", 404

    @staticmethod
    def check_and_parse_request_parameters(additional_filter, object_to_query, request,
                                           required_minimum_access_level):
        start_page = 0
        page_size = 20
        filter_expression = ""
        record_filter = []
        sort_fields = []
        include_archived = False
        include_master = False
        include_client = True
        master_only = False
        try:
            start_page = int(request.headers['StartPage'])
        except:
            pass
        try:
            page_size = int(request.headers['PageSize'])
        except:
            pass
        try:
            filter_expression = request.headers['SearchField']
        except:
            pass
        try:
            record_filter = str(request.headers['Filter']).split(',')
        except:
            pass
        try:
            sort_fields = str(request.headers['Sort']).split(',')
        except:
            pass
        try:
            include_archived = None
            if request.headers['IncludeArchived'] == "Y":
                include_archived = True
            if request.headers['IncludeArchived'] == "N":
                include_archived = False
        except:
            pass
        try:
            include_master = request.headers['IncludeMaster'] == "Y"
        except:
            pass
        try:
            include_client = request.headers['IncludeClient'] != "N"
        except:
            pass
        try:
            if include_master and not include_client:
                master_only = True
            master_only = request.headers['MASTER'] == "Y"
        except:
            pass
        if additional_filter != "":
            if additional_filter.find(',') > 0:
                record_filter = record_filter + additional_filter.split(',')
            else:
                record_filter.append(additional_filter)

        # find out the user settings and if they may work with own objects only
        token = request.headers['SessionID']
        company_id, user_id, token_validated = ITSRestAPILogin.get_info_with_session_token(token)
        company_id = ITSRestAPILogin.get_company_with_session_token(token)
        # load the user via the ORM
        user_object = ITSRestAPIORMExtensions.SecurityUser()
        #qry_session = sessionmaker(bind=ITSRestAPIDB.get_db_engine_connection_master())()
        with ITSRestAPIDB.session_scope("") as qry_session:
            user_object = qry_session.query(ITSRestAPIORMExtensions.SecurityUser).filter(
                ITSRestAPIORMExtensions.SecurityUser.Email == user_id).filter(
                ITSRestAPIORMExtensions.SecurityUser.CompanyID == company_id).order_by(ITSRestAPIORMExtensions.SecurityUser.IsTestTakingUser).first()

            proceed = True
            if required_minimum_access_level == ITR_minimum_access_levels.master_user:
                proceed = user_object.IsMasterUser == True
            if required_minimum_access_level == ITR_minimum_access_levels.test_taking_user:
                pass  # accessible to any logged in user
            if required_minimum_access_level == ITR_minimum_access_levels.regular_office_user:
                proceed = not user_object.IsTestTakingUser == True  # accessible to anybody that is no test taking user
            if required_minimum_access_level == ITR_minimum_access_levels.organisation_supervisor:
                proceed = user_object.IsOrganisationSupervisor == True
            if required_minimum_access_level == ITR_minimum_access_levels.test_author:
                proceed = user_object.IsTestAuthor == True
            if required_minimum_access_level == ITR_minimum_access_levels.password_manager:
                proceed = user_object.IsPasswordManager == True
            if required_minimum_access_level == ITR_minimum_access_levels.report_author:
                proceed = user_object.IsReportAuthor == True
            if required_minimum_access_level == ITR_minimum_access_levels.data_researcher:
                proceed = user_object.IsResearcher == True
            if required_minimum_access_level == ITR_minimum_access_levels.test_screen_template_author:
                proceed = user_object.IsTestScreenTemplateAuthor == True
            if required_minimum_access_level == ITR_minimum_access_levels.translator:
                proceed = user_object.IsTranslator == True
            if master_only:
                master_only = user_object.IsMasterUser == True  # master database can only be queried directly by master users
            limit_by_user_id = ""
            if user_object.MayWorkWithOwnObjectsOnly == True and object_to_query.may_work_with_own_objects_field != "":
                limit_by_user_id = str(user_object.ID)

            return company_id, filter_expression, include_archived, include_master, limit_by_user_id, master_only, \
                   page_size, proceed, record_filter, sort_fields, start_page, include_client, \
                   user_object.IsTestTakingUser and not user_object.IsOfficeUser, user_object.ID

    def return_single_object(self, request, required_minimum_access_level, id_to_find, master_database_query = False):
        # get the settings from the request header
        object_to_query = self

        company_id, filter_expression, include_archived, include_master, limit_by_user_id, master_only, page_size, proceed, record_filter, sort_fields, start_page, include_client, is_test_taking_user, user_id = self.check_and_parse_request_parameters(
            "", object_to_query, request, required_minimum_access_level)

        # and now take action
        if proceed and company_id != "":
            # and now execute the query
            if master_only or master_database_query:
                company_id = ""

            with ITSRestAPIDB.session_scope(company_id) as qry_session:
                temp_object = object_to_query.__class__
                temp_column = temp_object.__table__._columns[object_to_query.identity_field]
                located_object = qry_session.query(temp_object).filter(temp_column == id_to_find).first()

                if limit_by_user_id != "" and located_object is not None:
                    if str(eval("located_object." + object_to_query.may_work_with_own_objects_field)) != limit_by_user_id:
                        located_object = None
                if located_object is None:
                    return "Object not found or not accessible with user's rights (%s)" % id_to_find, 404
                else:
                    try:
                        located_object.before_get()
                    except:
                        pass

                    temp_dict = located_object.__dict__
                    for line in object_to_query.fields_to_be_removed:
                        try:
                            if line in temp_dict:
                                del temp_dict[line]
                        except:
                            pass

                    # process pass through fields
                    temp_json = {}
                    try:
                        for line in object_to_query.pass_through_fields:
                            try:
                                temp_json[line] = eval("located_object." + line)
                            except:
                                pass
                    except:
                        pass

                    fields_with_additional_info = {
                        "_sa_instance_state",
                        "identity_field",
                        "default_order_by_field",
                        "select_fields",
                        "sort_fields",
                        "order_fields",
                        "unified_search_fields",
                        "archive_field",
                        "user_limit_select_field",
                        "may_work_with_own_objects_field",
                        "fields_to_be_removed",
                        "pass_through_fields"
                    }
                    for line in fields_with_additional_info:
                        try:
                            if line in temp_dict:
                                del temp_dict[line]
                        except:
                            pass

                    try:
                        located_object.after_get()
                    except:
                        pass

                    for line in temp_json:
                        try:
                            temp_dict[line] = json.loads( temp_json[line] )
                        except:
                            pass


                    return jsonify(temp_dict)
        else:
            return "This action is not allowed", 403

    def change_single_object(self, request, required_minimum_access_level, id_to_find, allowed_fields_to_change = "", force_master = False):
        # get the settings from the request header
        object_to_query = self

        company_id, filter_expression, include_archived, include_master, limit_by_user_id, master_only, page_size, proceed, record_filter, sort_fields, start_page, include_client, is_test_taking_user, user_id = self.check_and_parse_request_parameters(
            "", object_to_query, request, required_minimum_access_level)

        # and now take action
        if proceed and company_id != "":
            # and now execute the query
            if master_only or force_master:
                company_id = ""

            #qry_session = sessionmaker(bind=ITSRestAPIDB.get_db_engine_connection_client(company_id))()
            with ITSRestAPIDB.session_scope(company_id) as qry_session:
                temp_object = object_to_query.__class__
                temp_column = temp_object.__table__._columns[object_to_query.identity_field]
                located_object = qry_session.query(temp_object).filter(temp_column == id_to_find).first()

                if located_object is None:
                    located_object = object_to_query.__class__() # create new object
                    qry_session.add(located_object)

                if located_object is not None and limit_by_user_id != "" and object_to_query.may_work_with_own_objects_field != "":
                    if str(getattr(located_object,object_to_query.may_work_with_own_objects_field)) != limit_by_user_id and getattr(located_object,object_to_query.may_work_with_own_objects_field) != None:
                        located_object = None
                if located_object is None:
                    return "Object not found or not accessible with user's rights (%s)" % id_to_find, 404
                else:
                    try:
                        located_object.before_post(request, required_minimum_access_level, id_to_find)
                    except:
                        pass

                    request.get_data()
                    data = request.data
                    data_dict = json.loads(data)

                    # process the pass through fields and convert those objects back to strings
                    try:
                        for line in object_to_query.pass_through_fields:
                            try:
                                data_dict[line] = json.dumps(data_dict[line])
                            except:
                                pass
                    except:
                        pass

                    #check for fields that we are allowed to change and remove the rest
                    if allowed_fields_to_change != "":
                        allowed_fields_to_change = allowed_fields_to_change.upper()
                        allowed_fields = allowed_fields_to_change.split(',')
                        new_dict = {}
                        for data_line in data_dict:
                            try :
                                index = allowed_fields.index(data_line.upper())
                                new_dict[data_line] = data_dict[data_line]
                            except:
                                pass
                        data_dict = new_dict

                    for data_line in data_dict:
                        try:
                            setattr(located_object,data_line,data_dict[data_line])
                        except:
                            pass

                    try:
                        qry_session.commit()
                    except Exception as error:
                        # log the message
                        app_log.error("Internal server error 500 test could not be saved : %s", error)
                        return "Test could not be saved : " + str(error), 500
                    qry_session.close()

                    try:
                        located_object.after_post(request, required_minimum_access_level, id_to_find)
                    except:
                        pass

                    return "OK", 200
        else:
            return "This action is not allowed", 403

    def delete_single_object(self, request, required_minimum_access_level, id_to_find, force_master = False):
        # get the settings from the request header
        object_to_query = self

        company_id, filter_expression, include_archived, include_master, limit_by_user_id, master_only, page_size, proceed, record_filter, sort_fields, start_page, include_client, is_test_taking_user, user_id  = self.check_and_parse_request_parameters(
            "", object_to_query, request, required_minimum_access_level)

        # and now take action
        if proceed and company_id != "":
            # and now execute the query
            if master_only or force_master:
                company_id = ""

            #qry_session = sessionmaker(bind=ITSRestAPIDB.get_db_engine_connection_client(company_id))()
            with ITSRestAPIDB.session_scope(company_id) as qry_session:
                temp_object = object_to_query.__class__
                temp_column = temp_object.__table__._columns[object_to_query.identity_field]
                located_object = qry_session.query(temp_object).filter(temp_column == id_to_find).first()

                if located_object is not None and limit_by_user_id != "":
                    if str(getattr(located_object,object_to_query.may_work_with_own_objects_field)) != limit_by_user_id and getattr(located_object,object_to_query.may_work_with_own_objects_field) != None:
                        located_object = None
                if located_object is None:
                    return "Object not found or not accessible with user's rights (%s)" % id_to_find, 404
                else:
                    try:
                        located_object.before_delete(request, required_minimum_access_level, id_to_find)
                    except:
                        pass

                    # delete the object
                    try:
                        qry_session.delete(located_object)
                        qry_session.commit()
                    finally:
                        qry_session.close()

                    try:
                        located_object.after_delete(request, required_minimum_access_level, id_to_find)
                    except:
                        pass

                    return "OK", 200
        else:
            return "This action is not allowed", 403