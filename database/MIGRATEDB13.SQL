alter table "TestScreenTemplates"
add column "HTMLContentSummary" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text

update "SystemParam"
set "ParValue" = '14'
where "ParameterName" = 'DBVersion'

// end of file