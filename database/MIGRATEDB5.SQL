alter table public."SecurityUsers"
add column "IsPasswordManager" boolean NOT NULL DEFAULT false;

update "SystemParam"
set "ParValue" = '6'
where "ParameterName" = 'DBVersion'

// end of file