ALTER TABLE public."ClientSessions"
ADD COLUMN "ShortLoginCode" character varying(40) COLLATE pg_catalog."default" NOT NULL DEFAULT ''::character varying;

CREATE INDEX IF NOT EXISTS "IX_CS_ShortLoginCode"
    ON public."ClientSessions"  ("ShortLoginCode")
    TABLESPACE %TABLESPACE%;

update "SystemParam"
set "ParValue" = '29'
where "ParameterName" = 'DBVersion'

// end of file