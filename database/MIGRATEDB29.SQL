alter table "TestScreenTemplates"
add column custom_template_actions_snippet text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text;

update "SystemParam"
set "ParValue" = '30'
where "ParameterName" = 'DBVersion'

// end of file