DROP INDEX "IX_SU_SecurityUsers";

CREATE INDEX "IX_SU_SecurityUsers"
    ON public."SecurityUsers" USING btree
    ("CompanyID", "Email" COLLATE pg_catalog."default")
    TABLESPACE %TABLESPACE%;

update "SystemParam"
set "ParValue" = '3'
where "ParameterName" = 'DBVersion'

// end of file