alter table "TestScreenTemplates"
add column get_value_as_html_snippet text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text;

update "SystemParam"
set "ParValue" = '24'
where "ParameterName" = 'DBVersion'

// end of file