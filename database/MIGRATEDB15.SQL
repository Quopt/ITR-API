alter table "ClientSessions"
add column "CreateDate" timestamp with time zone NOT NULL DEFAULT '2000-01-01 06:00:00+01'::timestamp with time zone

update "SystemParam"
set "ParValue" = '16'
where "ParameterName" = 'DBVersion'

// end of file