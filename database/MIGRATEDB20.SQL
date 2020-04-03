CREATE INDEX IF NOT EXISTS "IX_CAL_ObjectID"
    ON public."ClientAuditLog"  ("ObjectID")
    TABLESPACE %TABLESPACE%;

CREATE INDEX IF NOT EXISTS "IX_CAL_CompanyID"
    ON public."ClientAuditLog"  ("CompanyID")
    TABLESPACE %TABLESPACE%;

CREATE INDEX IF NOT EXISTS "IX_CAL_UserID"
    ON public."ClientAuditLog"  ("UserID")
    TABLESPACE %TABLESPACE%;

CREATE INDEX IF NOT EXISTS "IX_CAL_AuditMessage"
    ON public."ClientAuditLog"  ("AuditMessage")
    TABLESPACE %TABLESPACE%;

CREATE INDEX IF NOT EXISTS "IX_CAL_MessageID"
    ON public."ClientAuditLog"  ("MessageID")
    TABLESPACE %TABLESPACE%;

CREATE INDEX IF NOT EXISTS "IX_CAL_SessionID"
    ON public."ClientAuditLog"  ("SessionID")
    TABLESPACE %TABLESPACE%;

update "SystemParam"
set "ParValue" = '21'
where "ParameterName" = 'DBVersion'

// end of file

