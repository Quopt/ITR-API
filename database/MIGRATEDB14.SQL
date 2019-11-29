alter table "SecurityWebSessionTokens"
add column "IsTestTakingUser" boolean NOT NULL DEFAULT false

CREATE INDEX IF NOT EXISTS "IX_SWST_IsTestTakingUser"
    ON public."SecurityWebSessionTokens"  ("IsTestTakingUser")
    TABLESPACE %TABLESPACE%;

update "SystemParam"
set "ParValue" = '15'
where "ParameterName" = 'DBVersion'

// end of file