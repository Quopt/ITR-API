alter table public."SecurityUsers"
add column "HasTestingOfficeAccess" boolean NOT NULL DEFAULT true;

alter table public."SecurityUsers"
add column "HasEducationalOfficeAccess" boolean NOT NULL DEFAULT false;

update "SystemParam"
set "ParValue" = '25'
where "ParameterName" = 'DBVersion'

// end of file