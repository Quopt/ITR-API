alter table public."Tests"
add column "TestDefinitionIsProtected" boolean NOT NULL DEFAULT true;

update "SystemParam"
set "ParValue" = '8'
where "ParameterName" = 'DBVersion'

// end of file