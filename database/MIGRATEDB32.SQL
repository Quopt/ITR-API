alter table "Reports"
add column "Generation" integer NOT NULL DEFAULT 1

update "SystemParam"
set "ParValue" = '33'
where "ParameterName" = 'DBVersion'

// end of file