CREATE OR REPLACE VIEW viewclientgroupsessioncandidates AS
select
 C."ID", A."ID" as parentsessionid, B."ID" as sessionid, B."Status" as sessionstatus, B."SessionType" as sessiontype, C."EMail", C."FirstName", C."Initials", C."LastName", C."TitlesBefore", C."TitlesAfter", C."EducationID", C."OrganisationID", C."NationalityID", C."PreferredLanguage", C."Sex", C."DateOfLastTest", C."BirthDate", C."Active", C."CompanyID", C."ManagedByUserID"
 from "ClientSessions" A inner join "ClientSessions" B on A."ID" = B."GroupSessionID"
   inner join "ClientPersons" C on B."PersonID" = C."ID"
 where A."SessionType" = 100;

update "SystemParam"
set "ParValue" = '5'
where "ParameterName" = 'DBVersion'

// end of file