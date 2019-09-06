alter table "TestScreenTemplates"
add column generator_summary_snippet text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text

update "SystemParam"
set "ParValue" = '13'
where "ParameterName" = 'DBVersion'

// end of file