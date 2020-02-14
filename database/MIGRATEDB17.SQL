ALTER TABLE public."ClientPersons"
ADD COLUMN "Age" integer not null default 0;

ALTER TABLE public."ClientGroupMember"
ADD COLUMN "Age" integer not null default 0;

CREATE OR REPLACE VIEW ViewClientSessionsWithPerson AS
 select
  A."ID", "GroupSessionID", "GroupID", "PersonID", "SessionType", "Description", "Goal", "UsedBatteryIDs", A."Remarks", "SessionState", "AllowedStartDateTime", "AllowedEndDateTime", "StartedAt", "EndedAt", "Status", A."Active" as Active, "EMailNotificationAdresses", "EnforceSessionEndDateTime", A."ManagedByUserID", "EmailNotificationIncludeResults",
  "EMail", "FirstName", "Initials", "LastName", "TitlesBefore", "TitlesAfter", "EducationID", "OrganisationID", "NationalityID", "PreferredLanguage", "Sex", "DateOfLastTest", "BirthDate", B."Active" as PersonActive, A."CreateDate", "Age"
 from "ClientSessions" A inner join "ClientPersons" B on A."PersonID" = B."ID";

CREATE OR REPLACE VIEW ViewClientSessionTestsWithPerson AS
 select
  A."ID", "SessionID", "TestID", "PersID", "Sequence", "TestLanguage", "NormID1", "NormID2", "NormID3", "TestStart", "TestEnd", "PercentageOfQuestionsAnswered", "TotalTestTime", A."Status" as Status, "CurrentPage", "TotalPages", "HowTheTestIsTaken", "WarningMessage", "WarningTime", "Billed",
    "EMail", "FirstName", "Initials", "LastName", "TitlesBefore", "TitlesAfter", "EducationID", "OrganisationID", "NationalityID", "PreferredLanguage", "Sex", "DateOfLastTest", "BirthDate", B."Active" as PersonActive,
	C."Description", C."SessionType", C."Status" as SessionStatus, C."Active", C."CreateDate", "Age"
 from "ClientSessionTests" A inner join "ClientPersons" as B on A."PersID" = B."ID"
  inner join "ClientSessions" C on A."SessionID" = C."ID";

CREATE OR REPLACE VIEW ViewClientGroupSessionCandidates AS
select
 C."ID", A."ID" as parentsessionid, B."ID" as sessionid, B."Status" as sessionstatus, B."SessionType" as sessiontype, C."EMail", C."FirstName", C."Initials", C."LastName", C."TitlesBefore", C."TitlesAfter", C."EducationID", C."OrganisationID", C."NationalityID", C."PreferredLanguage", C."Sex", C."DateOfLastTest", C."BirthDate", C."Active", C."CompanyID", C."ManagedByUserID", A."CreateDate", "Age"
 from "ClientSessions" A inner join "ClientSessions" B on A."ID" = B."GroupSessionID"
   inner join "ClientPersons" C on B."PersonID" = C."ID"
 where A."SessionType" = 100;

update "SystemParam"
set "ParValue" = '18'
where "ParameterName" = 'DBVersion'

// end of file