ALTER TABLE public."ClientPersons"
ADD COLUMN "PersonType" smallint NOT NULL DEFAULT 0;

ALTER TABLE public."ClientEducations"
ADD COLUMN "EducationType" smallint NOT NULL DEFAULT 0;

ALTER TABLE public."ClientGroups"
ADD COLUMN "GroupType" smallint NOT NULL DEFAULT 0;

ALTER TABLE public."ClientNationalities"
ADD COLUMN "NationalityType" smallint NOT NULL DEFAULT 0;

ALTER TABLE public."ClientOrganisations"
ADD COLUMN "OrganisationType" smallint NOT NULL DEFAULT 0;

CREATE INDEX IF NOT EXISTS "IX_CP_PersonType"
    ON public."ClientPersons"  ("PersonType")
    TABLESPACE %TABLESPACE%;

CREATE INDEX IF NOT EXISTS "IX_CE_EducationType"
    ON public."ClientEducations"  ("EducationType")
    TABLESPACE %TABLESPACE%;

CREATE INDEX IF NOT EXISTS "IX_CG_GroupType"
    ON public."ClientGroups"  ("GroupType")
    TABLESPACE %TABLESPACE%;

CREATE INDEX IF NOT EXISTS "IX_CN_NationalityType"
    ON public."ClientNationalities"  ("NationalityType")
    TABLESPACE %TABLESPACE%;

CREATE INDEX IF NOT EXISTS "IX_CO_OrganisationType"
    ON public."ClientOrganisations"  ("OrganisationType")
    TABLESPACE %TABLESPACE%;

update "SystemParam"
set "ParValue" = '27'
where "ParameterName" = 'DBVersion'

// end of file