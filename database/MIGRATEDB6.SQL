alter table public."SecurityUsers"
add column "APIKey" character varying(400) COLLATE pg_catalog."default" NOT NULL DEFAULT ''::character varying

update "SystemParam"
set "ParValue" = '7'
where "ParameterName" = 'DBVersion'

// end of file