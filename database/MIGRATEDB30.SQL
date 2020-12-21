insert into "SystemParam" values( 'MAX_RESULTS_LIMIT', '1000000', TRUE )

insert into "SystemParam" values( 'MAX_SCORES_LIMIT', '100000', TRUE )

insert into "SystemParam" values( 'MAX_PLUGINDATA_LIMIT', '10000', TRUE )

insert into "SystemParam" values( 'MAX_CALL_LIMIT', '20', TRUE )

update "SystemParam"
set "ParValue" = '31'
where "ParameterName" = 'DBVersion'

// end of file