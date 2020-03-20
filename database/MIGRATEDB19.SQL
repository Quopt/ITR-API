alter table "SecurityCompanies"
add column "MFAEnabled" boolean NOT NULL DEFAULT false

alter table "SecurityUsers"
add column "otp_secret" character varying(200) COLLATE pg_catalog."default" NOT NULL DEFAULT ''::character varying

update "SystemParam"
set "ParValue" = '20'
where "ParameterName" = 'DBVersion'

// end of file