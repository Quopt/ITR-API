CREATE OR REPLACE VIEW viewclientgroupsessions AS
 SELECT a."ID",
    a."GroupSessionID",
    a."GroupID",
    a."SessionType",
    a."Description",
    a."Goal",
    a."UsedBatteryIDs",
    a."Remarks",
    a."SessionState",
    a."AllowedStartDateTime",
    a."AllowedEndDateTime",
    a."StartedAt",
    a."EndedAt",
    a."Status",
    a."Active" AS active,
    a."EMailNotificationAdresses",
    a."EnforceSessionEndDateTime",
    a."ManagedByUserID",
    a."EmailNotificationIncludeResults",
    count(*) FILTER (WHERE b."Status" <= 10) AS readycount,
    count(*) FILTER (WHERE b."Status" > 10 AND b."Status" < 30) AS inprogresscount,
    count(*) FILTER (WHERE b."Status" >= 30) AS donecount
   FROM "ClientSessions" a
     LEFT JOIN "ClientSessions" b ON a."ID" = b."GroupSessionID"
  WHERE a."SessionType" in (100,200,300,400,500)
  GROUP BY a."ID", a."GroupSessionID", a."GroupID", a."SessionType", a."Description", a."Goal", a."UsedBatteryIDs", a."Remarks", a."SessionState", a."AllowedStartDateTime", a."AllowedEndDateTime", a."StartedAt", a."EndedAt", a."Status", a."Active", a."EMailNotificationAdresses", a."EnforceSessionEndDateTime", a."ManagedByUserID", a."EmailNotificationIncludeResults";

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
    c."Age"
   FROM "ClientSessions" a
     JOIN "ClientSessions" b ON a."ID" = b."GroupSessionID"
     JOIN "ClientPersons" c ON b."PersonID" = c."ID"
  WHERE a."SessionType" in (100,200,300,400,500);

update "SystemParam"
set "ParValue" = '23'
where "ParameterName" = 'DBVersion'

// end of file