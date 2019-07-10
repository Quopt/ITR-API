CREATE INDEX "IX_SC_AdministrativeID"
    ON public."SecurityCompanies" USING btree
    ("AdministrativeID" COLLATE pg_catalog."default")
    TABLESPACE %TABLESPACE%;

update "SystemParam"
set "ParValue" = '8'
where "ParameterName" = 'DBVersion'

// end of file