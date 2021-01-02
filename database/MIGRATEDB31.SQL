alter table "SecurityCompanies"
add column "PricePerCreditUnit" double precision NOT NULL DEFAULT 0.1

update "SystemParam"
set "ParValue" = '32'
where "ParameterName" = 'DBVersion'

// end of file