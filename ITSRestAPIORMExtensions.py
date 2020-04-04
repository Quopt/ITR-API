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

# if you want to extend the ITSRestAPIORM classes please do so here ...
# for all ORM objects the concurrency strategy is 'last write wins!'
import ITSRestAPIORM
import ITSRestAPIDB
import ITSRestAPILogin
import ITSRestAPIORMExtendedFunctions
import ITSXMLConversionSupport
from flask import jsonify
from enum import Enum

from sqlalchemy import *
from sqlalchemy.orm import *
import json
from xml.etree import ElementTree
import optparse


class ClientAuditLog(ITSRestAPIORM.ClientAuditLog, ITSRestAPIORMExtendedFunctions.ORMExtendedFunctions):
    # add additional fields
    identity_field = "ID"
    default_order_by_field = "CreateDate"
    select_fields = {"ID"
        , "ObjectID"
        , "CompanyID"
        , "UserID"
        , "ObjectType"
        , "AuditMessage"
        , "MessageID"
        , "CreateDate"
        , "SessionID"
        , "NewData"}
    sort_fields = {}
    order_fields = {}
    unified_search_fields = {"ObjectType", "OldData", "NewData", "AuditMessage"}
    archive_field = {}
    user_limit_select_field = {}
    may_work_with_own_objects_field = ""
    fields_to_be_removed = {}


class ClientBatteries(ITSRestAPIORM.ClientBattery, ITSRestAPIORMExtendedFunctions.ORMExtendedFunctions):
    # add additional fields
    identity_field = "ID"
    default_order_by_field = "BatteryName"
    select_fields = {"ID"
        , "BatteryName"
        , "InvoiceCode"
        , "ReportMailAdress"
        , "BatteryCosts"
        , "Active"
        , "NotifyAfterBatteryCompletes"
        , "MailReportsWhenBatteryCompletes"
        , "MailReportToCandidate"
        , "BatteryType"
        , "ManagedByUserID"}
    sort_fields = {}
    order_fields = {}
    unified_search_fields = {"BatteryName", "Description", "InvoiceCode", "ReportMailAdress", "Remarks"}
    archive_field = "Active"
    user_limit_select_field = {}
    may_work_with_own_objects_field = ""
    fields_to_be_removed = {}
    pass_through_fields = {"BatteryTests", "BatteryReports", "PluginData"}
    fields_to_be_removed = {}


class ClientEducation(ITSRestAPIORM.ClientEducation, ITSRestAPIORMExtendedFunctions.ORMExtendedFunctions):
    # add additional fields
    identity_field = "ID"
    default_order_by_field = "Name"
    select_fields = {"ID"
        , "Name"
        , "EducationGroup"
        , "Active"}
    sort_fields = {}
    order_fields = {}
    unified_search_fields = {"Name", "EducationGroup", "Remarks"}
    archive_field = {}
    user_limit_select_field = {}
    may_work_with_own_objects_field = ""
    fields_to_be_removed = {}


class ClientGeneratedReport(ITSRestAPIORM.ClientGeneratedReport, ITSRestAPIORMExtendedFunctions.ORMExtendedFunctions):
    # add additional fields
    identity_field = "ID"
    default_order_by_field = "ReportTitle"
    select_fields = {"ID"
        , "ReportID"
        , "LinkedObjectID"
        , "ReportTitle"}
    sort_fields = {}
    order_fields = {}
    unified_search_fields = {"ReportTitle", "ReportText"}
    archive_field = {}
    user_limit_select_field = {}
    may_work_with_own_objects_field = ""
    pass_through_fields = {"PluginData"}
    fields_to_be_removed = {}


class ClientGroupMember(ITSRestAPIORM.ClientGroupMember, ITSRestAPIORMExtendedFunctions.ORMExtendedFunctions):
    # add additional fields
    identity_field = "ID"
    default_order_by_field = "EMail"
    select_fields = {"ID"
        , "PersonID"
        , "Name"
        , "EMail"
        , "BirthDate"
        , "Age"}
    sort_fields = {}
    order_fields = {}
    unified_search_fields = {"Name", "EMail"}
    archive_field = {}
    user_limit_select_field = {}
    may_work_with_own_objects_field = ""
    pass_through_fields = {"PluginData"}
    fields_to_be_removed = {}


class ClientGroup(ITSRestAPIORM.ClientGroup, ITSRestAPIORMExtendedFunctions.ORMExtendedFunctions):
    # add additional fields
    identity_field = "ID"
    default_order_by_field = "Description"
    select_fields = {"ID"
        , "Description"
        , "UserDefinedFields"
        , "Active"
        , "ManagedByUserID"}
    sort_fields = {}
    order_fields = {}
    unified_search_fields = {"Description", "UserDefinedFields", "Remarks"}
    archive_field = {}
    user_limit_select_field = {}
    may_work_with_own_objects_field = "ManagedByUserID"
    pass_through_fields = {"PluginData"}
    fields_to_be_removed = {}


class ClientNationality(ITSRestAPIORM.ClientNationality, ITSRestAPIORMExtendedFunctions.ORMExtendedFunctions):
    # add additional fields
    identity_field = "ID"
    default_order_by_field = "NationalityName"
    select_fields = {"ID"
        , "NationalityName"
        , "NationalityCode"
        , "Translations"}
    sort_fields = {}
    order_fields = {}
    unified_search_fields = {"NationalityName", "NationalityCode", "Translations", "Remarks"}
    archive_field = {}
    user_limit_select_field = {}
    may_work_with_own_objects_field = ""
    fields_to_be_removed = {}


class ClientOrganisation(ITSRestAPIORM.ClientOrganisation, ITSRestAPIORMExtendedFunctions.ORMExtendedFunctions):
    # add additional fields
    identity_field = "ID"
    default_order_by_field = "Name"
    select_fields = {"ID"
        , "Name"
        , "Address"
        , "Logo", "ContactPerson", "ContactPhone", "ContactEMail", "Active"}
    sort_fields = {}
    order_fields = {}
    unified_search_fields = {"Name", "Address", "Logo", "ContactPerson", "ContactPhone", "ContactEMail", "Remarks"}
    archive_field = {}
    user_limit_select_field = {}
    may_work_with_own_objects_field = ""
    pass_through_fields = {"PluginData"}
    fields_to_be_removed = {}


class ClientPerson(ITSRestAPIORM.ClientPerson, ITSRestAPIORMExtendedFunctions.ORMExtendedFunctions):
    # add additional fields
    identity_field = "ID"
    default_order_by_field = "EMail"
    select_fields = {"ID"
        , "EMail"
                     #        , "Password"  passwords can only be stored, not retrieved for reasons of safety
        , "FirstName"
        , "Initials"
        , "LastName"
        , "TitlesBefore"
        , "TitlesAfter"
        , "EducationID"
        , "UserDefinedFields"
        , "OrganisationID"
        , "NationalityID"
        , "PreferredLanguage"
        , "Sex"
        , "DateOfLastTest"
        , "BirthDate"
        , "Age"
        , "CompanyID"
        , "Active"
        , "ManagedByUserID"}
    sort_fields = {}
    order_fields = {}
    unified_search_fields = {"EMail", "FirstName"
        , "Initials"
        , "LastName"
        , "TitlesBefore"
        , "TitlesAfter"
        , "EducationID"
        , "UserDefinedFields"
        , "PreferredLanguage"
        , "Sex"
        , "Remarks"}
    archive_field = "Active"
    user_limit_select_field = {}
    may_work_with_own_objects_field = "ManagedByUserID"

    pass_through_fields = {"PluginData"}

    fields_to_be_removed = {"Password"}


class ClientSessionTest(ITSRestAPIORM.ClientSessionTest, ITSRestAPIORMExtendedFunctions.ORMExtendedFunctions):
    # add additional fields
    identity_field = "ID"
    default_order_by_field = "SessionID, Sequence"
    select_fields = {"ID"
        , "SessionID"
        , "TestID"
        , "PersID"
        , "Sequence"
        , "TestLanguage"
        , "NormID1"
        , "NormID2"
        , "NormID3"
        , "TestStart"
        , "TestEnd"
        , "PercentageOfQuestionsAnswered"
        , "TotalTestTime"
        , "Status"
        , "HowTheTestIsTaken"
        , "WarningMessage"
        , "WarningTime"
        , "CurrentPage"
        , "TotalPages"
                     }
    sort_fields = {}
    order_fields = {}
    unified_search_fields = { "HowTheTestIsTaken", "WarningMessage"}
    archive_field = {}
    user_limit_select_field = {}
    may_work_with_own_objects_field = ""
    fields_to_be_removed = {}
    pass_through_fields = {"Results", "Scores", "PluginData"}


class ClientSession(ITSRestAPIORM.ClientSession, ITSRestAPIORMExtendedFunctions.ORMExtendedFunctions):
    # add additional fields
    identity_field = "ID"
    default_order_by_field = "Description"
    select_fields = {"ID"
        , "GroupSessionID"
        , "GroupID"
        , "PersonID"
        , "SessionType"
        , "Description"
        , "Goal"
        , "UsedBatteryIDs"
        , "UserDefinedFields"
        , "SessionState"
        , "AllowedStartDateTime"
        , "AllowedEndDateTime"
        , "StartedAt"
        , "EndedAt"
        , "Status"
        , "Active"
        , "EMailNotificationAdresses"
        , "EnforceSessionEndDateTime"
        , "EmailNotificationIncludeResults"
        , "ManagedByUserID"
        , "CreateDate"}
    sort_fields = {}
    order_fields = {}
    unified_search_fields = {"Description"
        , "Goal"
        , "SessionState"
        , "Status"
        , "EMailNotificationAdresses"
        , "Remarks"}
    archive_field = "Active"
    user_limit_select_field = {}
    may_work_with_own_objects_field = "ManagedByUserID"
    pass_through_fields = {"PluginData"}
    fields_to_be_removed = {}


class Report(ITSRestAPIORM.Report, ITSRestAPIORMExtendedFunctions.ORMExtendedFunctions):
    # add additional fields
    identity_field = "ID"
    default_order_by_field = "Description"
    select_fields = {"ID"
        , "ReportType"
        , "Description"
        , "InvoiceCode", "CostsInTicks", "ReportLanguage", "DefaultReport", "Active", "TestID", "TestIDs"}
    sort_fields = {}
    order_fields = {}
    unified_search_fields = {"ReportType", "Description", "InvoiceCode", "CostsInTicks", "ReportLanguage", "Remarks", "Explanation"}
    archive_field = {}
    user_limit_select_field = {}
    may_work_with_own_objects_field = ""
    pass_through_fields = {"PluginData", "ReportGraphs"}
    fields_to_be_removed = {}


class SecurityCompany(ITSRestAPIORM.SecurityCompany, ITSRestAPIORMExtendedFunctions.ORMExtendedFunctions):
    # add additional fields
    identity_field = "ID"
    default_order_by_field = "CompanyName"
    select_fields = {"ID", "CompanyName", "CompanyCountry", "InternationalVATNr", "VATPercentage", "MailAddress", "VisitingAddress", "InvoiceAddress"
        , "VATPercentage", "CompanyLogo", "ContactPerson", "ContactPhone", "ContactEMail"
        , "TestTakingDiscount", "CostsPerTestInUnits", "YearlyLicenseDiscount", "YearlyLicenseFee", "InvoiceCurrency"
        , "CurrentCreditLevel", "ConcurrentOpenSessions", "AllowNegativeCredits", "Active", "LicenseStartDate"
        , "LicenseEndDate", "NoPublicTests", "ExitURL"}
    sort_fields = {}
    order_fields = {}
    unified_search_fields = {"CompanyName"
        , "CompanyCountry"
        , "InternationalVATNr", "MailAddress", "VisitingAddress", "InvoiceAddress"
        , "ContactPerson", "ContactPhone", "ContactEMail" }
    archive_field = {}
    user_limit_select_field = {}
    may_work_with_own_objects_field = ""

    fields_to_be_removed = {}
    pass_through_fields = {"AdditionalPersonFields", "AdditionalGroupFields", "AdditionalSessionFields", "PluginData"}


class SecurityCreditGrant(ITSRestAPIORM.SecurityCreditGrant, ITSRestAPIORMExtendedFunctions.ORMExtendedFunctions):
    # add additional fields
    identity_field = "ID"
    default_order_by_field = "GrantedWhen"
    select_fields = {"ID", "UserID", "CompanyID", "GrantedWhen", "UserDescription", "Paid", "CreditsGranted", "Remarks"}
    sort_fields = {}
    order_fields = {}
    unified_search_fields = {"UserDescription", "CreditsGranted", "Remarks"}
    archive_field = {}
    user_limit_select_field = {}
    may_work_with_own_objects_field = ""
    fields_to_be_removed = {}


class SecurityCreditUsage(ITSRestAPIORM.SecurityCreditUsage, ITSRestAPIORMExtendedFunctions.ORMExtendedFunctions):
    # add additional fields
    identity_field = "ID"
    default_order_by_field = "UsageDateTime"
    select_fields = {"ID"
        , "UserID"
        , "CompanyID"
        , "InvoiceCode", "OriginalTicks", "DiscountedTicks", "TotalTicks", "UsageDateTime", "SessionID",
                     "SessionName", "UserName"}
    sort_fields = {}
    order_fields = {}
    unified_search_fields = {"InvoiceCode", "OriginalTicks", "DiscountedTicks", "TotalTicks", "SessionName", "UserName"}
    archive_field = {}
    user_limit_select_field = {}
    may_work_with_own_objects_field = ""
    fields_to_be_removed = {}


class SecurityDataGathering(ITSRestAPIORM.SecurityDataGathering, ITSRestAPIORMExtendedFunctions.ORMExtendedFunctions):
    # add additional fields
    identity_field = "ID"
    default_order_by_field = "ID"
    select_fields = {"ID"
         , "CompanyID"
         , "SessionID"
         ,"TestID"
         ,"PersonData"
         ,"GroupData"
         ,"SessionData"
         ,"TestData"
         ,"PluginData"
         ,"TestDescription"
         ,"SessionDescription"
         ,"CompanyDescription"
         ,"GroupDescription"
         ,"SessionEndData"}
    sort_fields = {}
    order_fields = {}
    unified_search_fields = {"ID"}
    archive_field = {}
    user_limit_select_field = {}
    may_work_with_own_objects_field = ""
    pass_through_fields = {"PluginData"}
    fields_to_be_removed = {}

class SecurityTemplate(ITSRestAPIORM.SecurityTemplate, ITSRestAPIORMExtendedFunctions.ORMExtendedFunctions):
    # add additional fields
    identity_field = "ID"
    default_order_by_field = "Description"
    select_fields = {"ID"
        , "Description"}
    sort_fields = {}
    order_fields = {}
    unified_search_fields = {"Description", "Comments", "Contents"}
    archive_field = {}
    user_limit_select_field = {}
    may_work_with_own_objects_field = ""
    pass_through_fields = {"PluginData"}
    fields_to_be_removed = {}


class SecurityUser(ITSRestAPIORM.SecurityUser, ITSRestAPIORMExtendedFunctions.ORMExtendedFunctions):
    # add additional fields
    identity_field = "ID"
    default_order_by_field = "Email"
    select_fields = {"ID", "CompanyID", "Email", "UserName", "MailAddress", "VisitingAddress", "InvoiceAddress",
                     "InformationAddress", "LastLoginDateTime", "EndDateLicense", "StartDateLicense",
                     "UserOpeningsScreen", "PreferredLanguage", "PasswordExpirationDate", "LastLoginDateTime",
                     "IsMasterUser", "IsTestTakingUser", "IsOrganisationSupervisor", "IsTestAuthor", "IsReportAuthor",
                     "IsTestScreenTemplateAuthor", "IsResearcher",
                     "IsTranslator", "IsPasswordManager", "MayOrderCredits", "MayWorkWithBatteriesOnly", "DoNotRenewLicense",
                     "Active", "UserCulture", "SessionPool", "MayWorkWithOwnObjectsOnly",
                     "SecurityTemplateID", "HasPersonalCreditPool", "CurrentPersonalCreditLevel"}
    sort_fields = {}
    order_fields = {}
    unified_search_fields = {"Email", "UserName", "MailAddress", "VisitingAddress", "InvoiceAddress",
                             "InformationAddress", "Remarks",
                             "CurrentPersonalCreditLevel"}
    archive_field = {}
    user_limit_select_field = {}
    may_work_with_own_objects_field = ""
    fields_to_be_removed = {"Password"}
    pass_through_fields = {"PluginData"}


class SecurityWebSessionToken(ITSRestAPIORM.SecurityWebSessionToken,
                              ITSRestAPIORMExtendedFunctions.ORMExtendedFunctions):
    # add additional fields
    identity_field = "Token"
    default_order_by_field = "Token"
    select_fields = { # "Token", do not include the token. Never send this back to the client for security reasons
        "UserID", "CompanyID", "TokenValidated", "IsTestTakingUser"}
    sort_fields = {}
    order_fields = {}
    unified_search_fields = {"Token"}
    archive_field = {}
    user_limit_select_field = {}
    may_work_with_own_objects_field = ""
    fields_to_be_removed = {}


class SystemParam(ITSRestAPIORM.SystemParam, ITSRestAPIORMExtendedFunctions.ORMExtendedFunctions):
    # add additional fields
    identity_field = "ParameterName"
    default_order_by_field = "ParameterName"
    select_fields = {"ParameterName"
        , "ParValue"}
    sort_fields = {}
    order_fields = {}
    unified_search_fields = {"ParameterName", "ParValue"}
    archive_field = {}
    user_limit_select_field = {}
    may_work_with_own_objects_field = ""
    fields_to_be_removed = {}


class TestScreenTemplate(ITSRestAPIORM.TestScreenTemplate, ITSRestAPIORMExtendedFunctions.ORMExtendedFunctions):
    # add additional fields
    identity_field = "ID"
    default_order_by_field = "Description"
    select_fields = {"ID"
        , "Description"
        , "Explanation"
                     }
    sort_fields = {}
    order_fields = {}
    unified_search_fields = {"Description", "Explanation", "Remarks"}
    archive_field = {}
    user_limit_select_field = {}
    may_work_with_own_objects_field = ""

    fields_to_be_removed = {}
    pass_through_fields = {"TemplateVariables", "PluginData"}

    # extra properties for Json supported fields
    TemplateVariablesJson = ""
    GeneratorScriptJson = ""
    ValidationScriptJson = ""


class Test(ITSRestAPIORM.Test, ITSRestAPIORMExtendedFunctions.ORMExtendedFunctions):
    # add additional fields
    identity_field = "ID"
    default_order_by_field = "TestName"
    select_fields = {"ID"
        , "TestName"
        , "Description"
        , "Costs"
        , "InvoiceCode"
        , "Active"
        , "TestType"
        , "SupportsTestTaking"
        , "SupportsTestScoring"
        , "SupportsOnlyRenorming"
        , "IsRestartable"
        , "Supports360Degrees"
        , "CandidateCanDo360Too"
        , "ShowTestClosureScreen"
        , "TotalTimeAvailableForThisTest"
        , "MinPercentageOfAnswersRequired"
        , "TotalNumberOfExperiments"
        , "LanguageSupport"
        , "Generation"}
    sort_fields = {}
    order_fields = {}
    unified_search_fields = {"TestName", "Description", "Costs", "TestType", "Generation", "CatalogInformation", "Remarks"}
    archive_field = {}
    user_limit_select_field = {}
    may_work_with_own_objects_field = ""

    fields_to_be_removed = {}
    pass_through_fields = {"screens", "scales", "norms", "documents", "scoreRules", "graphs", "media", "files",
                           "PluginData", "RequiredParsPerson", "RequiredParsSession", "RequiredParsGroup",
                           "RequiredParsOrganisation"}


class ViewClientSessionTestsWithPerson(ITSRestAPIORM.ViewClientSessionTestsWithPerson,
                                       ITSRestAPIORMExtendedFunctions.ORMExtendedFunctions):
    identity_field = "ID"
    archive_field = "Active"
    default_order_by_field = "Description"
    unified_search_fields = {"Description"
        , "EMail"
        , "FirstName"
        , "Initials"
        , "LastName"
                             }
    select_fields = {"ID"
        , "Description"
        , "EMail"
        , "FirstName"
        , "Initials"
        , "active"
        , "AllowedStartDateTime", "AllowedEndDateTime", "StartedAt", "EndedAt", "CreateDate"}
    may_work_with_own_objects_field = ""


class ViewClientSessionsWithPerson(ITSRestAPIORM.ViewClientSessionsWithPerson,
                                   ITSRestAPIORMExtendedFunctions.ORMExtendedFunctions):
    identity_field = "ID"
    default_order_by_field = "Description"
    archive_field = "active"
    select_fields = {"ID"
        , "Description"
        , "EMail"
        , "FirstName"
        , "LastName"
        , "Initials"
        , "active"
        , "AllowedStartDateTime", "AllowedEndDateTime", "StartedAt", "EndedAt", "CreateDate"}

    unified_search_fields = {"Description", "EMail", "FirstName", "LastName", "Initials"}
    may_work_with_own_objects_field = "ManagedByUserID"


class ViewClientGroupSessions(ITSRestAPIORM.ViewClientGroupSessions,
                              ITSRestAPIORMExtendedFunctions.ORMExtendedFunctions):
    identity_field = "ID"
    default_order_by_field = "Description"
    archive_field = "active"
    select_fields = {"ID"
        , "Description"
        , "active"
        , "AllowedStartDateTime", "AllowedEndDateTime"
        , "readycount"
        , "inprogresscount"
        , "donecount"
    }

    unified_search_fields = {"Description"}
    may_work_with_own_objects_field = "ManagedByUserID"


class ViewClientGroupSessionCandidates(ITSRestAPIORM.ViewClientGroupSessionCandidates,
                                       ITSRestAPIORMExtendedFunctions.ORMExtendedFunctions):
    identity_field = "ID"
    default_order_by_field = "EMail"
    select_fields = {"ID"
        , "EMail"
        , "FirstName"
        , "Initials"
        , "LastName"
        , "TitlesBefore"
        , "TitlesAfter"
        , "EducationID"
        , "OrganisationID"
        , "NationalityID"
        , "PreferredLanguage"
        , "Sex"
        , "DateOfLastTest"
        , "BirthDate"
        , "Age"
        , "CompanyID"
        , "Active"
        , "ManagedByUserID"
        , "sessionid"
        , "sessiontype"
        , "sessionstatus"
        , "CreateDate"}
    sort_fields = {}
    order_fields = {}
    unified_search_fields = {"EMail", "FirstName"
        , "Initials"
        , "LastName"
        , "TitlesBefore"
        , "TitlesAfter"
        , "PreferredLanguage"
        , "Sex"
        , "Remarks"}
    archive_field = "Active"
    user_limit_select_field = {}
    may_work_with_own_objects_field = "ManagedByUserID"
