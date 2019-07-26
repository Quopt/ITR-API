alter table public."SecurityUsers"
add column "IsResearcher" boolean NOT NULL DEFAULT false;

update "SystemParam"
set "ParValue" = '11'
where "ParameterName" = 'DBVersion'

// end of file