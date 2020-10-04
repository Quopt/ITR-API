CREATE OR REPLACE VIEW ViewClientSessionsWithPerson AS
 select
  A."ID", "GroupSessionID", "GroupID", "PersonID", "SessionType", "Description", "Goal", "UsedBatteryIDs", A."Remarks", "SessionState", "AllowedStartDateTime", "AllowedEndDateTime", "StartedAt", "EndedAt", "Status", A."Active" as Active, "EMailNotificationAdresses", "EnforceSessionEndDateTime", A."ManagedByUserID", "EmailNotificationIncludeResults",
  "EMail", "FirstName", "Initials", "LastName", "TitlesBefore", "TitlesAfter", "EducationID", "OrganisationID", "NationalityID", "PreferredLanguage", "Sex", "DateOfLastTest", "BirthDate", B."Active" as PersonActive, A."CreateDate", "Age",
  B."PersonType"
 from "ClientSessions" A inner join "ClientPersons" B on A."PersonID" = B."ID";

CREATE OR REPLACE VIEW ViewClientSessionTestsWithPerson AS
 select
  A."ID", "SessionID", "TestID", "PersID", "Sequence", "TestLanguage", "NormID1", "NormID2", "NormID3", "TestStart", "TestEnd", "PercentageOfQuestionsAnswered", "TotalTestTime", A."Status" as Status, "CurrentPage", "TotalPages", "HowTheTestIsTaken", "WarningMessage", "WarningTime", "Billed",
    "EMail", "FirstName", "Initials", "LastName", "TitlesBefore", "TitlesAfter", "EducationID", "OrganisationID", "NationalityID", "PreferredLanguage", "Sex", "DateOfLastTest", "BirthDate", B."Active" as PersonActive,
	C."Description", C."SessionType", C."Status" as SessionStatus, C."Active", C."CreateDate", "Age",
    B."PersonType"
 from "ClientSessionTests" A inner join "ClientPersons" as B on A."PersID" = B."ID"
  inner join "ClientSessions" C on A."SessionID" = C."ID";

CREATE OR REPLACE VIEW viewclientgroupsessioncandidates AS
 SELECT c."ID",
    a."ID" AS parentsessionid,
    b."ID" AS sessionid,
    b."Status" AS sessionstatus,
    b."SessionType" AS sessiontype,
    c."EMail",
    c."FirstName",
    c."Initials",
    c."LastName",
    c."TitlesBefore",
    c."TitlesAfter",
    c."EducationID",
    c."OrganisationID",
    c."NationalityID",
    c."PreferredLanguage",
    c."Sex",
    c."DateOfLastTest",
    c."BirthDate",
    c."Active",
    c."CompanyID",
    c."ManagedByUserID",
    a."CreateDate",
    c."Age",
    c."PersonType"
   FROM "ClientSessions" a
     JOIN "ClientSessions" b ON a."ID" = b."GroupSessionID"
     JOIN "ClientPersons" c ON b."PersonID" = c."ID"
  WHERE a."SessionType" in (100,200,300,400,500,600,700,800,900,1000,1100,1200,1300,1400,1500,1600,1700,1800,1900);

update "SystemParam"
set "ParValue" = '28'
where "ParameterName" = 'DBVersion'

// end of file