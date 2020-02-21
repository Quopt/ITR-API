alter table "SecurityCompanies"
add column "CCEMail" character varying(200) COLLATE pg_catalog."default" NOT NULL DEFAULT ''::character varying

update "SystemParam"
set "ParValue" = '19'
where "ParameterName" = 'DBVersion'

// end of file