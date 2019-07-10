CREATE INDEX IF NOT EXISTS "IX_SC_AdministrativeID"
    ON public."SecurityCompanies" USING btree
    ("AdministrativeID" COLLATE pg_catalog."default")
    TABLESPACE %TABLESPACE%;

update "SystemParam"
set "ParValue" = '9'
where "ParameterName" = 'DBVersion'

// end of file