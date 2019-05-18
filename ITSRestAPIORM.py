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

# The contents of this file are generated using sqlacodegen and will be replaced when the database migrates to a new scheme
# class extensions can be put in ITSRestAPIORMExtensions
# coding: utf-8

from sqlalchemy import BigInteger, Column, DateTime, Date, Float, ForeignKey, Index, Integer, LargeBinary, SmallInteger, \
    String, Table, Unicode, UnicodeText, text, Boolean
from sqlalchemy_utils import UUIDType
import uuid
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref

Base = declarative_base()
metadata = Base.metadata


class ClientAuditLog(Base):
    __tablename__ = 'ClientAuditLog'
    __table_args__ = (
        Index('IX_CAL_CreateDate', 'CreateDate', unique=False),
        Index('IX_CAL_ObjectType', 'ObjectType', unique=False),
        #{'schema': 'ITR'}
    )

    ID = Column(UUIDType(binary=False), primary_key=True)
    ObjectID = Column(UUIDType(binary=False), nullable=False)
    CompanyID = Column(UUIDType(binary=False), nullable=False)
    UserID = Column(UUIDType(binary=False), nullable=False)
    ObjectType = Column(Integer, nullable=False, server_default=text("((0))"))
    OldData = Column(UnicodeText, nullable=False, server_default=text("('')"))
    NewData = Column(UnicodeText, nullable=False, server_default=text("('')"))
    AuditMessage = Column(Unicode(250), nullable=False, server_default=text("('')"))
    MessageID = Column(SmallInteger, nullable=False, server_default=text("((0))"))
    CreateDate = Column(DateTime(timezone=True), nullable=False, server_default=text("('2000-01-01 04:00:00 -1:00')"))
    SessionID = Column(UUIDType(binary=False))


class ClientBattery(Base):
    __tablename__ = 'ClientBatteries'
    __table_args__ = (
        Index('IX_CB_ManagedByUserID', 'ManagedByUserID', unique=False),
        #{'schema': 'ITR'}
    )

    ID = Column(UUIDType(binary=False), primary_key=True)
    BatteryName = Column(Unicode(200), nullable=False)
    Description = Column(UnicodeText, nullable=False, server_default=text("('')"))
    InvoiceCode = Column(Unicode(20), nullable=False, server_default=text("('')"))
    BeforeBatteryScript = Column(UnicodeText, nullable=False, server_default=text("('')"))
    AfterBatteryScript = Column(UnicodeText, nullable=False, server_default=text("('')"))
    ReportMailAdress = Column(Unicode(200), nullable=False, server_default=text("('')"))
    BatteryCosts = Column(SmallInteger, nullable=False, server_default=text("((0))"))
    BatteryReports = Column(UnicodeText, nullable=False, server_default=text("('')"))
    BatteryTests = Column(UnicodeText, nullable=False, server_default=text("('')"))
    Active = Column(Boolean, nullable=False, server_default=text("True"))
    NotifyAfterBatteryCompletes = Column(Boolean, nullable=False,
                                         server_default=text("False"))
    MailReportsWhenBatteryCompletes = Column(Boolean, nullable=False,
                                             server_default=text("True"))
    MailReportToCandidate = Column(Boolean, nullable=False, server_default=text("True"))
    BatteryType = Column(SmallInteger)
    PluginData = Column(UnicodeText, nullable=False, server_default=text("('{}')"))
    Remarks = Column(UnicodeText)
    ManagedByUserID = Column(UUIDType(binary=False), nullable=False,
                             server_default=text("('{00000000-0000-0000-0000-000000000000}')"))


class ClientEducation(Base):
    __tablename__ = 'ClientEducations'
    __table_args__ = (
        Index('IX_CE_Name', 'Name', unique=False),
        #{'schema': 'ITR'}
    )

    ID = Column(UUIDType(binary=False), primary_key=True)
    Name = Column(Unicode(200), nullable=False)
    EducationGroup = Column(Unicode(200), nullable=False, server_default=text("('')"))
    Remarks = Column(UnicodeText, nullable=False, server_default=text("('')"))
    Active = Column(Boolean, nullable=False, server_default=text("True"))
    PluginData = Column(UnicodeText, nullable=False, server_default=text("('{}')"))


class ClientGeneratedReport(Base):
    __tablename__ = 'ClientGeneratedReports'
    __table_args__ = (
        Index('IX_CGR_LinkedObjectID', 'LinkedObjectID', unique=False),
        #{'schema': 'ITR'}
    )

    ID = Column(UUIDType(binary=False), primary_key=True)
    ReportID = Column(UUIDType(binary=False), nullable=False)
    LinkedObjectID = Column(UUIDType(binary=False), nullable=False)
    ReportText = Column(UnicodeText, nullable=False, server_default=text("('')"))
    ReportTitle = Column(Unicode(200), nullable=False, server_default=text("('')"))
    PluginData = Column(UnicodeText, nullable=False, server_default=text("('{}')"))


class ClientGroupMember(Base):
    __tablename__ = 'ClientGroupMember'
    __table_args__ = (
        Index('IX_CGM_Name', 'Name', unique=False),
        Index('IX_CGM_EMail', 'EMail', unique=False),
        Index('IX_CGM_BirthDate', 'BirthDate', unique=False),
        #{'schema': 'ITR'}
    )

    ID = Column(ForeignKey('ClientGroups.ID'), primary_key=True, nullable=False)
    PersonID = Column(ForeignKey('ClientPersons.ID'), primary_key=True, nullable=False)
    Name = Column(Unicode(200), nullable=False)
    EMail = Column(Unicode(200), nullable=False)
    BirthDate = Column(DateTime, nullable=False)
    PluginData = Column(UnicodeText, nullable=False, server_default=text("('{}')"))

    ClientGroup = relationship('ITSRestAPIORMExtensions.ClientGroup', single_parent=True, backref=backref("children", cascade="all,delete"))
    ClientPerson = relationship('ITSRestAPIORMExtensions.ClientPerson')


class ClientGroup(Base):
    __tablename__ = 'ClientGroups'
    __table_args__ = (
        Index('IX_CG_Description', 'Description', unique=False),
        Index('IX_CG_ManagedByUserID', 'ManagedByUserID', unique=False),
        Index('IX_CG_ReportType', 'ReportType', unique=False),
        #{'schema': 'ITR'}
    )

    ID = Column(UUIDType(binary=False), primary_key=True)
    Description = Column(Unicode(200), nullable=False, server_default=text("('')"))
    Remarks = Column(UnicodeText, nullable=False, server_default=text("('')"))
    PluginData = Column(UnicodeText, nullable=False, server_default=text("('{}')"))
    UserDefinedFields = Column(UnicodeText, nullable=False, server_default=text("('')"))
    Active = Column(Boolean, nullable=False, server_default=text("True"))
    ManagedByUserID = Column(UUIDType(binary=False), nullable=False,
                             server_default=text("('{00000000-0000-0000-0000-000000000000}')"))
    ReportType = Column(SmallInteger, nullable=False, server_default=text("((10))"))


class ClientNationality(Base):
    __tablename__ = 'ClientNationalities'
    __table_args__ = (
        Index('IX_CN_NationalityName', 'NationalityName', unique=False),
        Index('IX_CN_NationalityCode', 'NationalityCode', unique=False),
        #{'schema': 'ITR'}
    )

    ID = Column(UUIDType(binary=False), primary_key=True)
    NationalityName = Column(Unicode(200), nullable=False, server_default=text("('')"))
    NationalityCode = Column(Unicode(10), nullable=False)
    Translations = Column(UnicodeText, nullable=False, server_default=text("('')"))
    PluginData = Column(UnicodeText, nullable=False, server_default=text("('{}')"))
    Remarks = Column(UnicodeText, nullable=False, server_default=text("('')"))


class ClientOrganisation(Base):
    __tablename__ = 'ClientOrganisations'
    __table_args__ = (
        Index('IX_CO_Name', 'Name', unique=False),
        #{'schema': 'ITR'}
    )

    ID = Column(UUIDType(binary=False), primary_key=True)
    Name = Column(Unicode(200), nullable=False, server_default=text("('')"))
    Address = Column(UnicodeText, nullable=False, server_default=text("('')"))
    Logo = Column(Unicode(200), nullable=False, server_default=text("('')"))
    ContactPerson = Column(Unicode(200), nullable=False, server_default=text("('')"))
    ContactPhone = Column(Unicode(200), nullable=False, server_default=text("('')"))
    ContactEMail = Column(Unicode(200), nullable=False, server_default=text("('')"))
    Remarks = Column(UnicodeText, nullable=False)
    Active = Column(Boolean, nullable=False, server_default=text("True"))
    PluginData = Column(UnicodeText, nullable=False, server_default=text("('{}')"))

class ClientPerson(Base):
    __tablename__ = 'ClientPersons'
    __table_args__ = (
        Index('IX_CP_EMail', 'EMail', unique=False),
        Index('IX_CP_EducationID', 'EducationID', unique=False),
        Index('IX_CP_OrganisationID', 'OrganisationID', unique=False),
        Index('IX_CP_NationalityID', 'NationalityID', unique=False),
        Index('IX_CP_PreferredLanguage', 'PreferredLanguage', unique=False),
        Index('IX_CP_Sex', 'Sex', unique=False),
        Index('IX_CP_DateOfLastTest', 'DateOfLastTest', unique=False),
        Index('IX_CP_BirthDate', 'BirthDate', unique=False),
        Index('IX_CP_CompanyID', 'CompanyID', unique=False),
        Index('IX_CP_ManagedByUserID', 'ManagedByUserID', unique=False),
        #{'schema': 'ITR'}
    )

    ID = Column(UUIDType(binary=False), primary_key=True)
    EMail = Column(Unicode(200), nullable=False, server_default=text("('')"))
    Password = Column(Unicode(200), nullable=False, server_default=text("('')"))
    FirstName = Column(Unicode(200), nullable=False, server_default=text("('')"))
    Initials = Column(Unicode(200), nullable=False, server_default=text("('')"))
    LastName = Column(Unicode(200), nullable=False, server_default=text("('')"))
    TitlesBefore = Column(Unicode(200), nullable=False, server_default=text("('')"))
    TitlesAfter = Column(Unicode(200), nullable=False, server_default=text("('')"))
    EducationID = Column(UUIDType(binary=False), nullable=False,
                             server_default=text("('{00000000-0000-0000-0000-000000000000}')"))
    UserDefinedFields = Column(UnicodeText, nullable=False, server_default=text("('')"))
    OrganisationID = Column(UUIDType(binary=False), nullable=False,
                             server_default=text("('{00000000-0000-0000-0000-000000000000}')"))
    NationalityID = Column(UUIDType(binary=False), nullable=False,
                             server_default=text("('{00000000-0000-0000-0000-000000000000}')"))
    Remarks = Column(UnicodeText, nullable=False, server_default=text("('')"))
    PreferredLanguage = Column(Unicode(10), nullable=False, server_default=text("('E')"))
    Sex = Column(Integer, nullable=False, server_default=text("((3))"))
    DateOfLastTest = Column(DateTime(timezone=True), nullable=False, server_default=text("('2000-01-01 04:00:00 -1:00')"))
    BirthDate = Column(Date, nullable=False, server_default=text("('2000-01-01')"))
    Active = Column(Boolean, nullable=False, server_default=text("True"))
    CompanyID = Column(UUIDType(binary=False), nullable=False,
                             server_default=text("('{00000000-0000-0000-0000-000000000000}')"))
    PluginData = Column(UnicodeText, nullable=False, server_default=text("('{}')"))
    ManagedByUserID = Column(UUIDType(binary=False), nullable=False,
                             server_default=text("('{00000000-0000-0000-0000-000000000000}')"))


class ClientSessionTest(Base):
    __tablename__ = 'ClientSessionTests'
    __table_args__ = (
        Index('IX_CST_SessionID', 'SessionID', unique=False),
        Index('IX_CST_TestID', 'TestID', unique=False),
        Index('IX_CST_PersID', 'PersID', unique=False),
        Index('IX_CST_Status', 'Status', unique=False),
        Index('IX_CST_NormID1', 'NormID1', unique=False),
        Index('IX_CST_NormID2', 'NormID2', unique=False),
        Index('IX_CST_NormID3', 'NormID3', unique=False),
        Index('IX_CST_HowTheTestIsTaken', 'HowTheTestIsTaken', unique=False),
        #{'schema': 'ITR'}
    )

    ID = Column(UUIDType(binary=False), primary_key=True)
    SessionID = Column(ForeignKey('ClientSessions.ID'), nullable=False)
    TestID = Column(UUIDType(binary=False), nullable=False)
    PersID = Column(UUIDType(binary=False), nullable=False)
    Sequence = Column(SmallInteger, nullable=False, server_default=text("((0))"))
    TestLanguage = Column(Unicode(10), nullable=False)
    Results = Column(UnicodeText, nullable=False, server_default=text("('')"))
    Scores = Column(UnicodeText, nullable=False, server_default=text("('')"))
    NormID1 = Column(UUIDType(binary=False))
    NormID2 = Column(UUIDType(binary=False))
    NormID3 = Column(UUIDType(binary=False))
    TestStart = Column(DateTime(timezone=True), nullable=False, server_default=text("('2000-01-01 04:00:00 -1:00')"))
    TestEnd = Column(DateTime(timezone=True), nullable=False, server_default=text("('2000-01-01 04:00:00 -1:00')"))
    PercentageOfQuestionsAnswered = Column(Integer, nullable=False, server_default=text("((0))"))
    TotalTestTime = Column(BigInteger, nullable=False, server_default=text("((0))"))
    Status = Column(Integer, nullable=False, server_default=text("((1))"))
    CurrentPage = Column(Integer, nullable=False, server_default=text("((0))"))
    TotalPages = Column(Integer, nullable=False, server_default=text("((0))"))
    HowTheTestIsTaken = Column(Integer, nullable=False, server_default=text("((1))"))
    WarningMessage = Column(Unicode(200), nullable=False, server_default=text("('')"))
    WarningTime = Column(DateTime(timezone=True), nullable=False, server_default=text("('2000-01-01 04:00:00 -1:00')"))
    Billed = Column(Boolean, nullable=False, server_default=text("False"))
    PluginData = Column(UnicodeText, nullable=False, server_default=text("('{}')"))

    ClientSession = relationship('ITSRestAPIORMExtensions.ClientSession', single_parent=True, backref=backref("children", cascade="all,delete"))
    #ClientSession = relationship('ITSRestAPIORMExtensions.ClientSession', single_parent=True, cascade='all, delete-orphan') xxx


class ClientSession(Base):
    __tablename__ = 'ClientSessions'
    __table_args__ = (
        Index('IX_CS_GroupSessionID', 'GroupSessionID', unique=False),
        Index('IX_CS_GroupID', 'GroupID', unique=False),
        Index('IX_CS_PersonID', 'PersonID', unique=False),
        Index('IX_CS_SessionType', 'SessionType', unique=False),
        Index('IX_CS_Description', 'Description', unique=False),
        Index('IX_CS_Goal', 'Goal', unique=False),
        Index('IX_CS_SessionState', 'SessionState', unique=False),
        Index('IX_CS_AllowedStartDateTime', 'AllowedStartDateTime', unique=False),
        Index('IX_CS_AllowedEndDateTime', 'AllowedEndDateTime', unique=False),
        Index('IX_CS_Status', 'Status', unique=False),
        Index('IX_CS_ManagedByUserID', 'ManagedByUserID', unique=False),
        #{'schema': 'ITR'}
    )

    ID = Column(UUIDType(binary=False), primary_key=True)
    GroupSessionID = Column(UUIDType(binary=False), nullable=False)
    GroupID = Column(UUIDType(binary=False), nullable=False)
    PersonID = Column(UUIDType(binary=False), nullable=False)
    SessionType = Column(SmallInteger, nullable=False, server_default=text("((0))"))
    Description = Column(Unicode(200), nullable=False, server_default=text("('')"))
    Goal = Column(Unicode(200), nullable=False, server_default=text("('')"))
    UsedBatteryIDs = Column(UnicodeText, nullable=False, server_default=text("('')"))
    UserDefinedFields = Column(UnicodeText, nullable=False, server_default=text("('')"))
    Remarks = Column(UnicodeText, nullable=False, server_default=text("('')"))
    SessionState = Column(UnicodeText, nullable=False, server_default=text("('')"))
    AllowedStartDateTime = Column(DateTime(timezone=True), nullable=False, server_default=text("('2000-01-01 04:00:00 -1:00')"))
    AllowedEndDateTime = Column(DateTime(timezone=True), nullable=False, server_default=text("('1-1-2100 9:00:00')"))
    StartedAt = Column(DateTime(timezone=True), nullable=False, server_default=text("('2000-01-01 04:00:00 -1:00')"))
    EndedAt = Column(DateTime(timezone=True), nullable=False, server_default=text("('2000-01-01 04:00:00 -1:00')"))
    Status = Column(Integer, nullable=False, server_default=text("((1))"))
    Active = Column(Boolean, nullable=False, server_default=text("True"))
    EMailNotificationAdresses = Column(Unicode(200), nullable=False, server_default=text("('')"))
    EnforceSessionEndDateTime = Column(Boolean, nullable=False, server_default=text("False"))
    ManagedByUserID = Column(UUIDType(binary=False), nullable=False,
                             server_default=text("('{00000000-0000-0000-0000-000000000000}')"))
    EmailNotificationIncludeResults = Column(Boolean, nullable=False, server_default=text("False"))
    PluginData = Column(UnicodeText, nullable=False, server_default=text("('{}')"))

class Report(Base):
    __tablename__ = 'Reports'
    __table_args__ = (
        Index('IX_R_InvoiceCode', 'InvoiceCode', unique=False),
        Index('IX_R_Description', 'Description', unique=False),
        Index('IX_R_ReportType', 'ReportType', unique=False),
        Index('IX_R_TestID', 'TestID', unique=False),
        #{'schema': 'ITR'}
    )

    ID = Column(UUIDType(binary=False), primary_key=True)
    TestID = Column(UUIDType(binary=False), nullable=False, server_default=text("('{00000000-0000-0000-0000-000000000000}')"))
    ReportType = Column(SmallInteger, nullable=False, server_default=text("((10))"))
    Description = Column(Unicode(200), nullable=False, server_default=text("('')"))
    Explanation = Column(UnicodeText, nullable=False, server_default=text("('')"))
    InvoiceCode = Column(Unicode(50), nullable=False, server_default=text("('')"))
    CostsInTicks = Column(SmallInteger, nullable=False, server_default=text("((0))"))
    Remarks = Column(UnicodeText, nullable=False, server_default=text("('')"))
    ReportLanguage = Column(Unicode(50), nullable=False, server_default=text("('')"))
    Active = Column(Boolean, nullable=False, server_default=text("True"))
    DefaultReport = Column(Boolean, nullable=False, server_default=text("False"))
    PluginData = Column(UnicodeText, nullable=False, server_default=text("('')"))
    BeforeReportScript = Column(UnicodeText, nullable=False, server_default=text("('')"))
    AfterReportScript = Column(UnicodeText, nullable=False, server_default=text("('')"))
    PerCandidateReportScript = Column(UnicodeText, nullable=False, server_default=text("('')"))
    ReportText = Column(UnicodeText, nullable=False, server_default=text("('')"))
    ReportGraphs = Column(UnicodeText, nullable=False, server_default=text("('{}')"))
    PluginData = Column(UnicodeText, nullable=False, server_default=text("('{}')"))
    TestIDs = Column(UnicodeText, nullable=False, server_default=text("('')"))

    # note : relationship to test with testID is optional
    # to do : delete the reports linked to the test if the test is deleted since this is not done using referential integrity

class SecurityCompany(Base):
    __tablename__ = 'SecurityCompanies'
    __table_args__ = (
        Index('IX_SC_CompanyName', 'CompanyName', unique=False),
        Index('IX_SC_CompanyCountry', 'CompanyCountry', unique=False),
        Index('IX_SC_InvoiceCurrency', 'InvoiceCurrency', unique=False),
        #{'schema': 'ITR'}
    )

    ID = Column(UUIDType(binary=False), primary_key=True)
    CompanyName = Column(Unicode(200), nullable=False)
    CompanyCountry = Column(Unicode(200), nullable=False)
    InternationalVATNr = Column(Unicode(200), nullable=False)
    VATPercentage = Column(Float(53), nullable=False, server_default=text("((0))"))
    MailAddress = Column(UnicodeText, nullable=False, server_default=text("('')"))
    VisitingAddress = Column(UnicodeText, nullable=False, server_default=text("('')"))
    InvoiceAddress = Column(UnicodeText, nullable=False, server_default=text("('')"))
    AdministrativeID = Column(Unicode(200), nullable=False, server_default=text("('')"))
    CompanyLogo = Column(Unicode(200), nullable=False)
    ContactPerson = Column(Unicode(200), nullable=False)
    ContactPhone = Column(Unicode(50), nullable=False)
    ContactEMail = Column(Unicode(200), nullable=False)
    TestTakingDiscount = Column(Integer, nullable=False, server_default=text("((0))"))
    CostsPerTestInUnits = Column(Integer, nullable=False, server_default=text("((0))"))
    YearlyLicenseDiscount = Column(Integer, nullable=False, server_default=text("((0))"))
    YearlyLicenseFee = Column(Integer, nullable=False)
    InvoiceCurrency = Column(Unicode(50), nullable=False)
    CurrentCreditLevel = Column(BigInteger, nullable=False, server_default=text("((0))"))
    LowCreditWarningLevel = Column(BigInteger, nullable=False, server_default=text("((500))"))
    ConcurrentOpenSessions = Column(Integer, nullable=False, server_default=text("((0))"))
    CompanyVariables = Column(UnicodeText, nullable=False, server_default=text("('')"))
    AdditionalPersonFields = Column(UnicodeText, nullable=False, server_default=text("('')"))
    AdditionalGroupFields = Column(UnicodeText, nullable=False, server_default=text("('')"))
    AdditionalSessionFields = Column(UnicodeText, nullable=False, server_default=text("('')"))
    AllowNegativeCredits = Column(Boolean, nullable=False, server_default=text("True"))
    Active = Column(Boolean, nullable=False, server_default=text("True"))
    LicenseStartDate = Column(DateTime(timezone=True), nullable=False, server_default=text("('2000-01-01 04:00:00 -1:00')"))
    LicenseEndDate = Column(DateTime(timezone=True), nullable=False, server_default=text("('1-1-2100')"))
    NoPublicTests = Column(Boolean, nullable=False, server_default=text("False"))
    ExitURL = Column(Unicode(255))
    PluginData = Column(UnicodeText, nullable=False, server_default=text("('{}')"))
    Generation = Column(Integer, nullable=False, server_default=text("((1))"))


class SecurityCreditGrant(Base):
    __tablename__ = 'SecurityCreditGrants'
    __table_args__ = (
        Index('IX_SCG_UserID', 'UserID', unique=False),
        Index('IX_SCG_CompanyID', 'CompanyID', unique=False),
        Index('IX_SCG_GrantedWhen', 'GrantedWhen', unique=False),
        #{'schema': 'ITR'}
    )

    ID = Column(UUIDType(binary=False), primary_key=True)
    UserID = Column(UUIDType(binary=False), nullable=False)
    CompanyID = Column(ForeignKey('SecurityCompanies.ID'), nullable=False)
    GrantedWhen = Column(DateTime(timezone=True), nullable=False, server_default=text("('2000-01-01 04:00:00 -1:00')"))
    Remarks = Column(UnicodeText, nullable=False, server_default=text("('')"))
    UserDescription = Column(Unicode(200), nullable=False, server_default=text("('')"))
    CreditsGranted = Column(SmallInteger, nullable=False, server_default=text("((0))"))
    Paid = Column(Boolean, nullable=False, server_default=text("True"))

    SecurityCompany = relationship('ITSRestAPIORMExtensions.SecurityCompany', single_parent=True, cascade="all,delete")


class SecurityCreditUsage(Base):
    __tablename__ = 'SecurityCreditUsage'
    __table_args__ = (
        Index('IX_SCU_UserID', 'UserID', unique=False),
        Index('IX_SCU_CompanyID', 'CompanyID', unique=False),
        Index('IX_SCU_InvoiceCode', 'InvoiceCode', unique=False),
        Index('IX_SCU_UsageDateTime', 'UsageDateTime', unique=False),
        Index('IX_SCU_SessionID', 'SessionID', unique=False),
        #{'schema': 'ITR'}
    )

    ID = Column(UUIDType(binary=False), primary_key=True)
    UserID = Column(UUIDType(binary=False), nullable=False)
    CompanyID = Column(ForeignKey('SecurityCompanies.ID'), nullable=False)
    InvoiceCode = Column(Unicode(50), nullable=False)
    SessionName = Column(Unicode(200), nullable=False)
    UserName = Column(Unicode(200), nullable=False)
    OriginalTicks = Column(SmallInteger, nullable=False)
    DiscountedTicks = Column(SmallInteger, nullable=False)
    TotalTicks = Column(SmallInteger, nullable=False)
    UsageDateTime = Column(DateTime(timezone=True), nullable=False)
    SessionID = Column(UUIDType(binary=False), nullable=False,
                       server_default=text("('{00000000-0000-0000-0000-000000000000}')"))

    SecurityCompany = relationship('ITSRestAPIORMExtensions.SecurityCompany', single_parent=True, cascade="all,delete" )

class SecurityDataGathering(Base):
    __tablename__ = 'SecurityDataGathering'
    __table_args__ = (
        Index('IX_SDG_CompanyID', 'CompanyID', unique=False),
        Index('IX_SDG_SessionID', 'SessionID', unique=False),
        Index('IX_SDG_TestID', 'TestID', unique=False),
        #{'schema': 'ITR'}
    )

    ID = Column(UUIDType(binary=False), primary_key=True)
    CompanyID = Column(UUIDType(binary=False), nullable=False)
    SessionID = Column(UUIDType(binary=False), nullable=False)
    TestID = Column(UUIDType(binary=False), nullable=False)
    PersonData = Column(UnicodeText, nullable=False, server_default=text("('')"))
    GroupData = Column(UnicodeText, nullable=False, server_default=text("('')"))
    SessionData = Column(UnicodeText, nullable=False, server_default=text("('')"))
    TestData = Column(UnicodeText, nullable=False, server_default=text("('')"))
    PluginData = Column(UnicodeText, nullable=False, server_default=text("('{}')"))


class SecurityTemplate(Base):
    __tablename__ = 'SecurityTemplates'
    __table_args__ = (
        Index('IX_ST_Description', 'Description', unique=False),
        #{'schema': 'ITR'}
    )

    ID = Column(UUIDType(binary=False), primary_key=True)
    Description = Column(Unicode(200), nullable=False, server_default=text("('')"))
    Comments = Column(UnicodeText, nullable=False, server_default=text("('')"))
    Contents = Column(UnicodeText, nullable=False, server_default=text("('')"))
    PluginData = Column(UnicodeText, nullable=False, server_default=text("('{}')"))


class SecurityUser(Base):
    __tablename__ = 'SecurityUsers'
    __table_args__ = (
        Index('IX_SU_SecurityUsers', 'CompanyID', 'Email', unique=True),
        Index('IX_SU_Email', 'Email', unique=False),
        Index('IX_SU_CompanyID', 'CompanyID', unique=False),
        Index('IX_SU_PasswordExpirationDate', 'PasswordExpirationDate', unique=False),
        Index('IX_SU_StartDateLicense', 'StartDateLicense', unique=False),
        Index('IX_SU_EndDateLicense', 'EndDateLicense', unique=False),
        Index('IX_SU_LastLoginDateTime', 'LastLoginDateTime', unique=False),
        Index('IX_SU_LastRefreshDateTime', 'LastRefreshDateTime', unique=False),
        Index('IX_SU_SecurityTemplateID', 'SecurityTemplateID', unique=False),
        #{'schema': 'ITR'}
    )

    ID = Column(UUIDType(binary=False), primary_key=True)
    CompanyID = Column(ForeignKey('SecurityCompanies.ID'), nullable=False)
    Email = Column(Unicode(200), nullable=False, server_default=text("('')"))
    Password = Column(Unicode(200), nullable=False, server_default=text("('')"))
    UserOpeningsScreen = Column(Unicode(200), nullable=False, server_default=text("('')"))
    UserName = Column(Unicode(200), nullable=False)
    UserRights = Column(UnicodeText, nullable=False, server_default=text("('')"))
    UserParameters = Column(UnicodeText, nullable=False, server_default=text("('')"))
    PreferredLanguage = Column(Unicode(10), nullable=False, server_default=text("('E')"))
    MailAddress = Column(UnicodeText, nullable=False, server_default=text("('')"))
    VisitingAddress = Column(UnicodeText, nullable=False, server_default=text("('')"))
    InvoiceAddress = Column(UnicodeText, nullable=False, server_default=text("('')"))
    InformationAddress = Column(UnicodeText, nullable=False, server_default=text("('')"))
    Remarks = Column(UnicodeText, nullable=False, server_default=text("('')"))
    PasswordExpirationDate = Column(DateTime(timezone=True), nullable=False, server_default=text("('2000-01-01 04:00:00 -1:00')"))
    StartDateLicense = Column(DateTime(timezone=True), nullable=False, server_default=text("('2000-01-01 04:00:00 -1:00')"))
    EndDateLicense = Column(DateTime(timezone=True), nullable=False, server_default=text("('1-1-2100 9:00:00')"))
    LastLoginDateTime = Column(DateTime(timezone=True), nullable=False, server_default=text("('2000-01-01 04:00:00 -1:00')"))
    LastRefreshDateTime = Column(DateTime(timezone=True), nullable=False, server_default=text("('2000-01-01 04:00:00 -1:00')"))
    IsMasterUser = Column(Boolean, nullable=False, server_default=text("False"))
    IsTestTakingUser = Column(Boolean, nullable=False, server_default=text("False"))
    IsOfficeUser = Column(Boolean, nullable=False, server_default=text("False"))
    IsOrganisationSupervisor = Column(Boolean, nullable=False, server_default=text("False"))
    IsTestAuthor = Column(Boolean, nullable=False, server_default=text("False"))
    IsReportAuthor = Column(Boolean, nullable=False, server_default=text("False"))
    IsTestScreenTemplateAuthor = Column(Boolean, nullable=False, server_default=text("False"))
    IsTranslator = Column(Boolean, nullable=False, server_default=text("False"))
    MayOrderCredits = Column(Boolean, nullable=False, server_default=text("False"))
    MayWorkWithBatteriesOnly = Column(Boolean, nullable=False, server_default=text("False"))
    DoNotRenewLicense = Column(Boolean, nullable=False, server_default=text("False"))
    Active = Column(Boolean, nullable=False, server_default=text("True"))
    UserCulture = Column(Unicode(20), nullable=False, server_default=text("('en')"))
    SessionPool = Column(Integer, nullable=False, server_default=text("((1))"))
    MayWorkWithOwnObjectsOnly = Column(Boolean, nullable=False, server_default=text("False"))
    SecurityTemplateID = Column(UUIDType(binary=False), server_default=text("'{00000000-0000-0000-0000-000000000000}'"))
    HasPersonalCreditPool = Column(Boolean, nullable=False, server_default=text("False"))
    CurrentPersonalCreditLevel = Column(Integer, nullable=False, server_default=text("((0))"))
    PluginData = Column(UnicodeText, nullable=False, server_default=text("('{}')"))

class SecurityWebSessionToken(Base):
    __tablename__ = 'SecurityWebSessionTokens'
    __table_args__ = (
        Index('IX_SWST_TokenValidated', 'TokenValidated', unique=False),
        Index('IX_SWST_UserID', 'UserID', unique=False),
        Index('IX_SWST_CompanyID', 'CompanyID', unique=False),
        #{'schema': 'ITR'}
    )

    Token = Column(Unicode(50), primary_key=True)
    UserID = Column(Unicode(50), nullable=False)
    CompanyID = Column(UUIDType(binary=False), nullable=False)
    TokenValidated = Column(DateTime(timezone=True), nullable=False, server_default=text("(NOW())"))


class SystemParam(Base):
    __tablename__ = 'SystemParam'

    ParameterName = Column(Unicode(50), primary_key=True)
    ParValue = Column(Unicode)
    ParProtected = Column(Boolean, nullable=False, server_default=text("False"))

class SystemTranslation(Base):
    __tablename__ = 'SystemTranslations'
    __table_args__ = (
        Index('IX_ST_FormName', 'FormName', unique=False),
        Index('IX_ST_StringName', 'StringName', unique=False),
        Index('IX_ST_LanguageCode', 'LanguageCode', unique=False),
        Index('IX_ST_IsTranslated', 'IsTranslated', unique=False),
        #{'schema': 'ITR'}
    )

    ID = Column(UUIDType(binary=False), primary_key=True)
    FormName = Column(Unicode(250), nullable=False, server_default=text("('')"))
    StringName = Column(Unicode(250), nullable=False, server_default=text("('')"))
    LanguageCode = Column(Unicode(10), nullable=False, server_default=text("('')"))
    TranslatedString = Column(Unicode(4000), nullable=False, server_default=text("('')"))
    IsTranslated = Column(Boolean, nullable=False, server_default=text("True"))
    PluginData = Column(UnicodeText, nullable=False, server_default=text("('{}')"))


class TestScreenTemplate(Base):
    __tablename__ = 'TestScreenTemplates'
    __table_args__ = (
        Index('IX_TST_Description', 'Description', unique=False),
        #{'schema': 'ITR'}
    )

    ID = Column(UUIDType(binary=False), primary_key=True)
    HTMLContent = Column(UnicodeText, nullable=False, server_default=text("('')"))
    HTMLContentPnP = Column(UnicodeText, nullable=False, server_default=text("('')"))
    PluginData = Column(UnicodeText, nullable=False, server_default=text("('{}')"))
    Description = Column(Unicode(200), nullable=False, server_default=text("('')"))
    TemplateType = Column(SmallInteger, nullable=False, server_default=text("((0))"))
    Explanation = Column(UnicodeText, nullable=False, server_default=text("('')"))
    Remarks = Column(UnicodeText, nullable=False, server_default=text("('')"))
    ScreenDefinitionFrozen = Column(Boolean, nullable=False, server_default=text("False"))
    ScreenDefinitionIsReleased = Column(Boolean, nullable=False, server_default=text("False"))
    TemplateVariables = Column(UnicodeText, nullable=False, server_default=text("('')"))
    get_value_snippet = Column(UnicodeText, nullable=False, server_default=text("('')"))
    set_value_snippet = Column(UnicodeText, nullable=False, server_default=text("('')"))
    init_value_snippet = Column(UnicodeText, nullable=False, server_default=text("('')"))
    generator_snippet = Column(UnicodeText, nullable=False, server_default=text("('')"))
    generator_pnp_snippet = Column(UnicodeText, nullable=False, server_default=text("('')"))
    validation_snippet = Column(UnicodeText, nullable=False, server_default=text("('')"))
    isanswered_snippet = Column(UnicodeText, nullable=False, server_default=text("('')"))


class Test(Base):
    __tablename__ = 'Tests'
    __table_args__ = (
        Index('IX_T_TestName', 'TestName', unique=False),
        Index('IX_T_InvoiceCode', 'InvoiceCode', unique=False),
        Index('IX_T_TestStartDate', 'TestStartDate', unique=False),
        Index('IX_T_TestEndDate', 'TestEndDate', unique=False),
        #{'schema': 'ITR'}
    )

    ID = Column(UUIDType(binary=False), primary_key=True)
    TestName = Column(Unicode(50), nullable=False, server_default=text("('')"))
    Description = Column(Unicode(200), nullable=False, server_default=text("('')"))
    Explanation = Column(UnicodeText, nullable=False, server_default=text("('')"))
    CatalogInformation = Column(UnicodeText, nullable=False, server_default=text("('')"))
    Copyrights = Column(UnicodeText, nullable=False, server_default=text("('')"))
    Costs = Column(SmallInteger, nullable=False, server_default=text("((0))"))
    TestType = Column(SmallInteger, nullable=False, server_default=text("((0))"))
    AuthorInfo = Column(UnicodeText, nullable=False, server_default=text("('')"))
    InvoiceCode = Column(Unicode(50), nullable=False, server_default=text("('')"))
    Remarks = Column(UnicodeText, nullable=False, server_default=text("('')"))
    TestStartDate = Column(DateTime(timezone=True), nullable=False, server_default=text("('2000-01-01 04:00:00 -1:00')"))
    TestEndDate = Column(DateTime(timezone=True), nullable=False, server_default=text("('1-1-2100 9:00:00')"))
    TestDefinitionFrozen = Column(Boolean, nullable=False, server_default=text("False"))
    TestDefinitionIsReleased = Column(Boolean, nullable=False, server_default=text("False"))
    TestDefinitionIsOpenSource = Column(Boolean, nullable=False, server_default=text("False"))
    TestDefinitionIsCommercial = Column(Boolean, nullable=False, server_default=text("False"))
    TestDefinitionIsExternal = Column(Boolean, nullable=False, server_default=text("False"))
    TestDefinitionIsBanned = Column(Boolean, nullable=False, server_default=text("False"))
    Active = Column(Boolean, nullable=False, server_default=text("True"))
    SupportsTestTaking = Column(Boolean, nullable=False, server_default=text("True"))
    SupportsTestScoring = Column(Boolean, nullable=False, server_default=text("True"))
    SupportsOnlyRenorming = Column(Boolean, nullable=False, server_default=text("True"))
    IsRestartable = Column(Boolean, nullable=False, server_default=text("True"))
    Supports360Degrees = Column(Boolean, nullable=False, server_default=text("True"))
    CandidateCanDo360Too = Column(Boolean, nullable=False, server_default=text("True"))
    ShowTestClosureScreen = Column(Boolean, nullable=False, server_default=text("True"))
    TotalTimeAvailableForThisTest = Column(SmallInteger, nullable=False)
    MinPercentageOfAnswersRequired = Column(Integer, nullable=False, server_default=text("((0))"))
    TotalNumberOfExperiments = Column(SmallInteger, nullable=False, server_default=text("((0))"))
    BeforeScript = Column(UnicodeText, nullable=False, server_default=text("('')"))
    AfterScript = Column(UnicodeText, nullable=False, server_default=text("('')"))
    BeforeNormingScript = Column(UnicodeText, nullable=False, server_default=text("('')"))
    AfterNormingScript = Column(UnicodeText, nullable=False, server_default=text("('')"))
    ScoringScript = Column(UnicodeText, nullable=False, server_default=text("('')"))
    Pre360 = Column(UnicodeText, nullable=False, server_default=text("('')"))
    Per360 = Column(UnicodeText, nullable=False, server_default=text("('')"))
    Post360 = Column(UnicodeText, nullable=False, server_default=text("('')"))
    RequiredParsPerson = Column(UnicodeText, nullable=False, server_default=text("('')"))
    RequiredParsSession = Column(UnicodeText, nullable=False, server_default=text("('')"))
    RequiredParsGroup = Column(UnicodeText, nullable=False, server_default=text("('')"))
    RequiredParsOrganisation = Column(UnicodeText, nullable=False, server_default=text("('')"))
    PluginData = Column(UnicodeText, nullable=False, server_default=text("('{}')"))
    screens = Column(UnicodeText, nullable=False, server_default=text("('')"))
    scales = Column(UnicodeText, nullable=False, server_default=text("('')"))
    norms = Column(UnicodeText, nullable=False, server_default=text("('')"))
    documents = Column(UnicodeText, nullable=False, server_default=text("('')"))
    scoreRules = Column(UnicodeText, nullable=False, server_default=text("('')"))
    graphs = Column(UnicodeText, nullable=False, server_default=text("('')"))
    media = Column(UnicodeText, nullable=False, server_default=text("('')"))
    files = Column(UnicodeText, nullable=False, server_default=text("('')"))
    LanguageSupport = Column(Unicode(200), nullable=False, server_default=text("('')"))
    Generation = Column(Integer, nullable=False, server_default=text("((1))"))


class ViewClientSessionsWithPerson(Base):
    __tablename__ = 'viewclientsessionswithperson'

    ID=Column(UUIDType(binary=False), primary_key=True)
    GroupSessionID = Column(UUIDType(binary=False), nullable=False)
    GroupID = Column(UUIDType(binary=False), nullable=False)
    PersonID = Column(UUIDType(binary=False), nullable=False)
    SessionType = Column(SmallInteger, nullable=False, server_default=text("((0))"))
    Description = Column(Unicode(200), nullable=False, server_default=text("('')"))
    Goal = Column(Unicode(200), nullable=False, server_default=text("('')"))
    UsedBatteryIDs = Column(UnicodeText, nullable=False, server_default=text("('')"))
    UserDefinedFields = Column(UnicodeText, nullable=False, server_default=text("('')"))
    Remarks = Column(UnicodeText, nullable=False, server_default=text("('')"))
    SessionState = Column(UnicodeText, nullable=False, server_default=text("('')"))
    AllowedStartDateTime = Column(DateTime(timezone=True), nullable=False,
                                  server_default=text("('2000-01-01 04:00:00 -1:00')"))
    AllowedEndDateTime = Column(DateTime(timezone=True), nullable=False, server_default=text("('1-1-2100 9:00:00')"))
    StartedAt = Column(DateTime(timezone=True), nullable=False, server_default=text("('2000-01-01 04:00:00 -1:00')"))
    EndedAt = Column(DateTime(timezone=True), nullable=False, server_default=text("('2000-01-01 04:00:00 -1:00')"))
    Status = Column(Integer, nullable=False, server_default=text("((1))"))
    Active = Column(Boolean, nullable=False, server_default=text("True"))
    EMailNotificationAdresses = Column(Unicode(200), nullable=False, server_default=text("('')"))
    EnforceSessionEndDateTime = Column(Boolean, nullable=False, server_default=text("False"))
    ManagedByUserID = Column(UUIDType(binary=False), nullable=False,
                             server_default=text("('{00000000-0000-0000-0000-000000000000}')"))
    EmailNotificationIncludeResults = Column(Boolean, nullable=False, server_default=text("False"))

    EMail = Column(Unicode(200), nullable=False, server_default=text("('')"))
    FirstName = Column(Unicode(200), nullable=False, server_default=text("('')"))
    Initials = Column(Unicode(200), nullable=False, server_default=text("('')"))
    LastName = Column(Unicode(200), nullable=False, server_default=text("('')"))
    TitlesBefore = Column(Unicode(200), nullable=False, server_default=text("('')"))
    TitlesAfter = Column(Unicode(200), nullable=False, server_default=text("('')"))
    EducationID = Column(UUIDType(binary=False), nullable=False,
                             server_default=text("('{00000000-0000-0000-0000-000000000000}')"))
    OrganisationID = Column(UUIDType(binary=False), nullable=False,
                             server_default=text("('{00000000-0000-0000-0000-000000000000}')"))
    NationalityID = Column(UUIDType(binary=False), nullable=False,
                             server_default=text("('{00000000-0000-0000-0000-000000000000}')"))
    PreferredLanguage = Column(Unicode(10), nullable=False, server_default=text("('E')"))
    Sex = Column(Integer, nullable=False, server_default=text("((3))"))
    DateOfLastTest = Column(DateTime(timezone=True), nullable=False, server_default=text("('2000-01-01 04:00:00 -1:00')"))
    BirthDate = Column(Date, nullable=False, server_default=text("('2000-01-01')"))
    PersonActive = Column(Boolean, nullable=False, server_default=text("True"))


class ViewClientSessionTestsWithPerson(Base):
    __tablename__ = 'viewclientsessiontestswithperson'

    ID = Column(UUIDType(binary=False), primary_key=True)
    SessionID = Column(ForeignKey('ClientSessions.ID'), nullable=False)
    TestID = Column(UUIDType(binary=False), nullable=False)
    PersID = Column(UUIDType(binary=False), nullable=False)
    Sequence = Column(SmallInteger, nullable=False, server_default=text("((0))"))
    TestLanguage = Column(Unicode(10), nullable=False)
    NormID1 = Column(UUIDType(binary=False))
    NormID2 = Column(UUIDType(binary=False))
    NormID3 = Column(UUIDType(binary=False))
    TestStart = Column(DateTime(timezone=True), nullable=False, server_default=text("('2000-01-01 04:00:00 -1:00')"))
    TestEnd = Column(DateTime(timezone=True), nullable=False, server_default=text("('2000-01-01 04:00:00 -1:00')"))
    PercentageOfQuestionsAnswered = Column(Integer, nullable=False, server_default=text("((0))"))
    TotalTestTime = Column(BigInteger, nullable=False, server_default=text("((0))"))
    Status = Column(Integer, nullable=False, server_default=text("((1))"))
    CurrentPage = Column(Integer, nullable=False, server_default=text("((0))"))
    TotalPages = Column(Integer, nullable=False, server_default=text("((0))"))
    HowTheTestIsTaken = Column(Integer, nullable=False, server_default=text("((1))"))
    WarningMessage = Column(Unicode(200), nullable=False, server_default=text("('')"))
    WarningTime = Column(DateTime(timezone=True), nullable=False, server_default=text("('2000-01-01 04:00:00 -1:00')"))
    Billed = Column(Boolean, nullable=False, server_default=text("False"))

    EMail = Column(Unicode(200), nullable=False, server_default=text("('')"))
    FirstName = Column(Unicode(200), nullable=False, server_default=text("('')"))
    Initials = Column(Unicode(200), nullable=False, server_default=text("('')"))
    LastName = Column(Unicode(200), nullable=False, server_default=text("('')"))
    TitlesBefore = Column(Unicode(200), nullable=False, server_default=text("('')"))
    TitlesAfter = Column(Unicode(200), nullable=False, server_default=text("('')"))
    EducationID = Column(UUIDType(binary=False), nullable=False,
                             server_default=text("('{00000000-0000-0000-0000-000000000000}')"))
    OrganisationID = Column(UUIDType(binary=False), nullable=False,
                             server_default=text("('{00000000-0000-0000-0000-000000000000}')"))
    NationalityID = Column(UUIDType(binary=False), nullable=False,
                             server_default=text("('{00000000-0000-0000-0000-000000000000}')"))
    PreferredLanguage = Column(Unicode(10), nullable=False, server_default=text("('E')"))
    Sex = Column(Integer, nullable=False, server_default=text("((3))"))
    DateOfLastTest = Column(DateTime(timezone=True), nullable=False, server_default=text("('2000-01-01 04:00:00 -1:00')"))
    BirthDate = Column(Date, nullable=False, server_default=text("('2000-01-01')"))
    PersonActive = Column(Boolean, nullable=False, server_default=text("True"))

    SessionType = Column(SmallInteger, nullable=False, server_default=text("((0))"))
    Description = Column(Unicode(200), nullable=False, server_default=text("('')"))
    SessionStatus = Column(Integer, nullable=False, server_default=text("((1))"))
    Active = Column(Boolean, nullable=False, server_default=text("True"))


class ViewClientGroupSessions(Base):
    __tablename__ = 'viewclientgroupsessions'

    ID=Column(UUIDType(binary=False), primary_key=True)
    GroupSessionID = Column(UUIDType(binary=False), nullable=False)
    GroupID = Column(UUIDType(binary=False), nullable=False)
    SessionType = Column(SmallInteger, nullable=False, server_default=text("((0))"))
    Description = Column(Unicode(200), nullable=False, server_default=text("('')"))
    Goal = Column(Unicode(200), nullable=False, server_default=text("('')"))
    UsedBatteryIDs = Column(UnicodeText, nullable=False, server_default=text("('')"))
    UserDefinedFields = Column(UnicodeText, nullable=False, server_default=text("('')"))
    Remarks = Column(UnicodeText, nullable=False, server_default=text("('')"))
    SessionState = Column(UnicodeText, nullable=False, server_default=text("('')"))
    AllowedStartDateTime = Column(DateTime(timezone=True), nullable=False,
                                  server_default=text("('2000-01-01 04:00:00 -1:00')"))
    AllowedEndDateTime = Column(DateTime(timezone=True), nullable=False, server_default=text("('1-1-2100 9:00:00')"))
    StartedAt = Column(DateTime(timezone=True), nullable=False, server_default=text("('2000-01-01 04:00:00 -1:00')"))
    EndedAt = Column(DateTime(timezone=True), nullable=False, server_default=text("('2000-01-01 04:00:00 -1:00')"))
    Status = Column(Integer, nullable=False, server_default=text("((1))"))
    Active = Column(Boolean, nullable=False, server_default=text("True"))
    EMailNotificationAdresses = Column(Unicode(200), nullable=False, server_default=text("('')"))
    EnforceSessionEndDateTime = Column(Boolean, nullable=False, server_default=text("False"))
    ManagedByUserID = Column(UUIDType(binary=False), nullable=False,
                             server_default=text("('{00000000-0000-0000-0000-000000000000}')"))
    EmailNotificationIncludeResults = Column(Boolean, nullable=False, server_default=text("False"))

    readycount = Column(Integer, nullable=False, server_default=text("((0))"))
    inprogresscount = Column(Integer, nullable=False, server_default=text("((0))"))
    donecount = Column(Integer, nullable=False, server_default=text("((0))"))



class ViewClientGroupSessionCandidates(Base):
    __tablename__ = 'viewclientgroupsessioncandidates'

    ID = Column(UUIDType(binary=False), primary_key=True)
    sessionid = Column(UUIDType(binary=False), primary_key=False)
    sessiontype = Column(SmallInteger, nullable=False)
    sessionstatus = Column(Integer, nullable=False)
    EMail = Column(Unicode(200), nullable=False, server_default=text("('')"))
    Password = Column(Unicode(200), nullable=False, server_default=text("('')"))
    FirstName = Column(Unicode(200), nullable=False, server_default=text("('')"))
    Initials = Column(Unicode(200), nullable=False, server_default=text("('')"))
    LastName = Column(Unicode(200), nullable=False, server_default=text("('')"))
    TitlesBefore = Column(Unicode(200), nullable=False, server_default=text("('')"))
    TitlesAfter = Column(Unicode(200), nullable=False, server_default=text("('')"))
    EducationID = Column(UUIDType(binary=False), nullable=False,
                             server_default=text("('{00000000-0000-0000-0000-000000000000}')"))
    OrganisationID = Column(UUIDType(binary=False), nullable=False,
                             server_default=text("('{00000000-0000-0000-0000-000000000000}')"))
    NationalityID = Column(UUIDType(binary=False), nullable=False,
                             server_default=text("('{00000000-0000-0000-0000-000000000000}')"))
    PreferredLanguage = Column(Unicode(10), nullable=False, server_default=text("('E')"))
    Sex = Column(Integer, nullable=False, server_default=text("((3))"))
    DateOfLastTest = Column(DateTime(timezone=True), nullable=False, server_default=text("('2000-01-01 04:00:00 -1:00')"))
    BirthDate = Column(Date, nullable=False, server_default=text("('2000-01-01')"))
    Active = Column(Boolean, nullable=False, server_default=text("True"))
    CompanyID = Column(UUIDType(binary=False), nullable=False,
                             server_default=text("('{00000000-0000-0000-0000-000000000000}')"))
    ManagedByUserID = Column(UUIDType(binary=False), nullable=False,
                             server_default=text("('{00000000-0000-0000-0000-000000000000}')"))

