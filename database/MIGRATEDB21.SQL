alter table "SecurityWebSessionTokens"
add column "TokenSessionID" uuid NULL

update "SystemParam"
set "ParValue" = '22'
where "ParameterName" = 'DBVersion'

// end of file