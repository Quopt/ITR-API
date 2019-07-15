ALTER TABLE public."SecurityDataGathering"
    add column "SessionDescription" character varying (200) COLLATE pg_catalog."default" NOT NULL DEFAULT ''::character varying,
    add column "TestDescription" character varying (200) COLLATE pg_catalog."default" NOT NULL DEFAULT ''::character varying,
    add column "CompanyDescription" character varying (200) COLLATE pg_catalog."default" NOT NULL DEFAULT ''::character varying,
    add column "GroupDescription" character varying (200) COLLATE pg_catalog."default" NOT NULL DEFAULT ''::character varying,
    add column "SessionEndData" timestamp with time zone NOT NULL DEFAULT '2000-01-01 06:00:00+01'::timestamp with time zone
;

CREATE INDEX IF NOT EXISTS "IX_SDG_SessionDescription"
    ON public."SecurityDataGathering" USING btree
    ("SessionDescription" COLLATE pg_catalog."default")
    TABLESPACE %TABLESPACE%;

CREATE INDEX IF NOT EXISTS "IX_SDG_TestDescription"
    ON public."SecurityDataGathering" USING btree
    ("TestDescription" COLLATE pg_catalog."default")
    TABLESPACE %TABLESPACE%;

CREATE INDEX IF NOT EXISTS "IX_SDG_CompanyDescription"
    ON public."SecurityDataGathering" USING btree
    ("CompanyDescription" COLLATE pg_catalog."default")
    TABLESPACE %TABLESPACE%;

CREATE INDEX IF NOT EXISTS "IX_SDG_GroupDescription"
    ON public."SecurityDataGathering" USING btree
    ("GroupDescription" COLLATE pg_catalog."default")
    TABLESPACE %TABLESPACE%;

CREATE INDEX IF NOT EXISTS "IX_SDG_SessionEndData"
    ON public."SecurityDataGathering" USING btree
    ("SessionEndData")
    TABLESPACE %TABLESPACE%;

update "SystemParam"
set "ParValue" = '10'
where "ParameterName" = 'DBVersion'

// end of file