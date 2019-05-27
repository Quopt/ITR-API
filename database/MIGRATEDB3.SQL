CREATE OR REPLACE VIEW viewclientgroupsessions AS
 select
  A."ID", A."GroupSessionID", A."GroupID", A."SessionType", A."Description", A."Goal", A."UsedBatteryIDs", A."Remarks", A."SessionState", A."AllowedStartDateTime", A."AllowedEndDateTime", A."StartedAt", A."EndedAt", A."Status", A."Active" as Active, A."EMailNotificationAdresses", A."EnforceSessionEndDateTime", A."ManagedByUserID", A."EmailNotificationIncludeResults",
  count(*) FILTER (WHERE b."Status" <= 10) AS ReadyCount,
  count(*) FILTER (WHERE b."Status" > 10 and b."Status" < 30) AS InProgressCount,
  count(*) FILTER (WHERE b."Status" >= 30) AS DoneCount
 from "ClientSessions" A left outer join "ClientSessions" B on A."ID" = B."GroupSessionID" where A."SessionType" = 100
 group by A."ID", A."GroupSessionID", A."GroupID", A."SessionType", A."Description", A."Goal", A."UsedBatteryIDs", A."Remarks", A."SessionState", A."AllowedStartDateTime", A."AllowedEndDateTime", A."StartedAt", A."EndedAt", A."Status", A."Active", A."EMailNotificationAdresses", A."EnforceSessionEndDateTime", A."ManagedByUserID", A."EmailNotificationIncludeResults"
 ;

update "SystemParam"
set "ParValue" = '4'
where "ParameterName" = 'DBVersion'

// end of file