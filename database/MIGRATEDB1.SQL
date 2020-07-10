SET TIME ZONE 'UTC';

-- Table: public."ClientAuditLog"

-- DROP TABLE public."ClientAuditLog";

CREATE TABLE public."ClientAuditLog"
(
    "ID" uuid NOT NULL,
    "ObjectID" uuid NOT NULL,
    "CompanyID" uuid NOT NULL,
    "UserID" uuid NOT NULL,
    "ObjectType" integer NOT NULL DEFAULT 0,
    "OldData" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "NewData" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "AuditMessage" character varying(250) COLLATE pg_catalog."default" NOT NULL DEFAULT ''::character varying,
    "MessageID" smallint NOT NULL DEFAULT 0,
    "CreateDate" timestamp with time zone NOT NULL DEFAULT '2000-01-01 06:00:00+01'::timestamp with time zone,
    "SessionID" uuid,
    CONSTRAINT "ClientAuditLog_pkey" PRIMARY KEY ("ID")
)
WITH (
    OIDS = FALSE
)
TABLESPACE %TABLESPACE%;

ALTER TABLE public."ClientAuditLog"
    OWNER to postgres;

-- Index: IX_CAL_CreateDate

-- DROP INDEX public."IX_CAL_CreateDate";

CREATE INDEX "IX_CAL_CreateDate"
    ON public."ClientAuditLog" USING btree
    ("CreateDate")
    TABLESPACE %TABLESPACE%;

-- Index: IX_CAL_ObjectType

-- DROP INDEX public."IX_CAL_ObjectType";

CREATE INDEX "IX_CAL_ObjectType"
    ON public."ClientAuditLog" USING btree
    ("ObjectType")
    TABLESPACE %TABLESPACE%;

-- Table: public."ClientBatteries"

-- DROP TABLE public."ClientBatteries";

CREATE TABLE public."ClientBatteries"
(
    "ID" uuid NOT NULL,
    "BatteryName" character varying(200) COLLATE pg_catalog."default" NOT NULL,
    "Description" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "InvoiceCode" character varying(20) COLLATE pg_catalog."default" NOT NULL DEFAULT ''::character varying,
    "BeforeBatteryScript" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "AfterBatteryScript" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "ReportMailAdress" character varying(200) COLLATE pg_catalog."default" NOT NULL DEFAULT ''::character varying,
    "BatteryCosts" smallint NOT NULL DEFAULT 0,
    "BatteryReports" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "BatteryTests" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "Active" boolean NOT NULL DEFAULT true,
    "NotifyAfterBatteryCompletes" boolean NOT NULL DEFAULT false,
    "MailReportsWhenBatteryCompletes" boolean NOT NULL DEFAULT true,
    "MailReportToCandidate" boolean NOT NULL DEFAULT true,
    "BatteryType" smallint,
    "PluginData" text COLLATE pg_catalog."default" NOT NULL DEFAULT '{}'::text,
    "Remarks" text COLLATE pg_catalog."default",
    "ManagedByUserID" uuid NOT NULL DEFAULT '00000000-0000-0000-0000-000000000000'::uuid,
    CONSTRAINT "ClientBatteries_pkey" PRIMARY KEY ("ID")
)
WITH (
    OIDS = FALSE
)
TABLESPACE %TABLESPACE%;

ALTER TABLE public."ClientBatteries"
    OWNER to postgres;

-- Index: IX_CB_ManagedByUserID

-- DROP INDEX public."IX_CB_ManagedByUserID";

CREATE INDEX "IX_CB_ManagedByUserID"
    ON public."ClientBatteries" USING btree
    ("ManagedByUserID")
    TABLESPACE %TABLESPACE%;

-- Table: public."ClientEducations"

-- DROP TABLE public."ClientEducations";

CREATE TABLE public."ClientEducations"
(
    "ID" uuid NOT NULL,
    "Name" character varying(200) COLLATE pg_catalog."default" NOT NULL,
    "EducationGroup" character varying(200) COLLATE pg_catalog."default" NOT NULL DEFAULT ''::character varying,
    "Remarks" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "Active" boolean NOT NULL DEFAULT true,
    CONSTRAINT "ClientEducations_pkey" PRIMARY KEY ("ID")
)
WITH (
    OIDS = FALSE
)
TABLESPACE %TABLESPACE%;

ALTER TABLE public."ClientEducations"
    OWNER to postgres;

-- Index: IX_CE_Name

-- DROP INDEX public."IX_CE_Name";

CREATE INDEX "IX_CE_Name"
    ON public."ClientEducations" USING btree
    ("Name" COLLATE pg_catalog."default")
    TABLESPACE %TABLESPACE%;

-- Table: public."ClientGeneratedReports"

-- DROP TABLE public."ClientGeneratedReports";

CREATE TABLE public."ClientGeneratedReports"
(
    "ID" uuid NOT NULL,
    "ReportID" uuid NOT NULL,
    "LinkedObjectID" uuid NOT NULL,
    "ReportText" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "ReportTitle" character varying(200) COLLATE pg_catalog."default" NOT NULL DEFAULT ''::character varying,
    "PluginData" text COLLATE pg_catalog."default" NOT NULL DEFAULT '{}'::text,
    CONSTRAINT "ClientGeneratedReports_pkey" PRIMARY KEY ("ID")
)
WITH (
    OIDS = FALSE
)
TABLESPACE %TABLESPACE%;

ALTER TABLE public."ClientGeneratedReports"
    OWNER to postgres;

-- Index: IX_CGR_LinkedObjectID

-- DROP INDEX public."IX_CGR_LinkedObjectID";

CREATE INDEX "IX_CGR_LinkedObjectID"
    ON public."ClientGeneratedReports" USING btree
    ("LinkedObjectID")
    TABLESPACE %TABLESPACE%;

-- Table: public."ClientGroups"

-- DROP TABLE public."ClientGroups";

CREATE TABLE public."ClientGroups"
(
    "ID" uuid NOT NULL,
    "Description" character varying(200) COLLATE pg_catalog."default" NOT NULL DEFAULT ''::character varying,
    "Remarks" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "PluginData" text COLLATE pg_catalog."default" NOT NULL DEFAULT '{}'::text,
    "UserDefinedFields" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "Active" boolean NOT NULL DEFAULT true,
    "ManagedByUserID" uuid NOT NULL DEFAULT '00000000-0000-0000-0000-000000000000'::uuid,
    CONSTRAINT "ClientGroups_pkey" PRIMARY KEY ("ID")
)
WITH (
    OIDS = FALSE
)
TABLESPACE %TABLESPACE%;

ALTER TABLE public."ClientGroups"
    OWNER to postgres;

-- Index: IX_CG_Description

-- DROP INDEX public."IX_CG_Description";

CREATE INDEX "IX_CG_Description"
    ON public."ClientGroups" USING btree
    ("Description" COLLATE pg_catalog."default")
    TABLESPACE %TABLESPACE%;

-- Index: IX_CG_ManagedByUserID

-- DROP INDEX public."IX_CG_ManagedByUserID";

CREATE INDEX "IX_CG_ManagedByUserID"
    ON public."ClientGroups" USING btree
    ("ManagedByUserID")
    TABLESPACE %TABLESPACE%;

-- Table: public."ClientNationalities"

-- DROP TABLE public."ClientNationalities";

CREATE TABLE public."ClientNationalities"
(
    "ID" uuid NOT NULL,
    "NationalityName" character varying(200) COLLATE pg_catalog."default" NOT NULL DEFAULT ''::character varying,
    "NationalityCode" character varying(10) COLLATE pg_catalog."default" NOT NULL,
    "Translations" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "Remarks" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    CONSTRAINT "ClientNationalities_pkey" PRIMARY KEY ("ID")
)
WITH (
    OIDS = FALSE
)
TABLESPACE %TABLESPACE%;

ALTER TABLE public."ClientNationalities"
    OWNER to postgres;

-- Index: IX_CN_NationalityCode

-- DROP INDEX public."IX_CN_NationalityCode";

CREATE INDEX "IX_CN_NationalityCode"
    ON public."ClientNationalities" USING btree
    ("NationalityCode" COLLATE pg_catalog."default")
    TABLESPACE %TABLESPACE%;

-- Index: IX_CN_NationalityName

-- DROP INDEX public."IX_CN_NationalityName";

CREATE INDEX "IX_CN_NationalityName"
    ON public."ClientNationalities" USING btree
    ("NationalityName" COLLATE pg_catalog."default")
    TABLESPACE %TABLESPACE%;

-- Table: public."ClientOrganisations"

-- DROP TABLE public."ClientOrganisations";

CREATE TABLE public."ClientOrganisations"
(
    "ID" uuid NOT NULL,
    "Name" character varying(200) COLLATE pg_catalog."default" NOT NULL DEFAULT ''::character varying,
    "Address" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "Logo" character varying(200) COLLATE pg_catalog."default" NOT NULL DEFAULT ''::character varying,
    "ContactPerson" character varying(200) COLLATE pg_catalog."default" NOT NULL DEFAULT ''::character varying,
    "ContactPhone" character varying(200) COLLATE pg_catalog."default" NOT NULL DEFAULT ''::character varying,
    "ContactEMail" character varying(200) COLLATE pg_catalog."default" NOT NULL DEFAULT ''::character varying,
    "Remarks" text COLLATE pg_catalog."default" NOT NULL,
    "Active" boolean NOT NULL DEFAULT true,
    "PluginData" text COLLATE pg_catalog."default" NOT NULL DEFAULT '{}'::text,
    CONSTRAINT "ClientOrganisations_pkey" PRIMARY KEY ("ID")
)
WITH (
    OIDS = FALSE
)
TABLESPACE %TABLESPACE%;

ALTER TABLE public."ClientOrganisations"
    OWNER to postgres;

-- Index: IX_CO_Name

-- DROP INDEX public."IX_CO_Name";

CREATE INDEX "IX_CO_Name"
    ON public."ClientOrganisations" USING btree
    ("Name" COLLATE pg_catalog."default")
    TABLESPACE %TABLESPACE%;

-- Table: public."ClientPersons"

-- DROP TABLE public."ClientPersons";

CREATE TABLE public."ClientPersons"
(
    "ID" uuid NOT NULL,
    "EMail" character varying(200) COLLATE pg_catalog."default" NOT NULL DEFAULT ''::character varying,
    "Password" character varying(200) COLLATE pg_catalog."default" NOT NULL DEFAULT ''::character varying,
    "FirstName" character varying(200) COLLATE pg_catalog."default" NOT NULL DEFAULT ''::character varying,
    "Initials" character varying(200) COLLATE pg_catalog."default" NOT NULL DEFAULT ''::character varying,
    "LastName" character varying(200) COLLATE pg_catalog."default" NOT NULL DEFAULT ''::character varying,
    "TitlesBefore" character varying(200) COLLATE pg_catalog."default" NOT NULL DEFAULT ''::character varying,
    "TitlesAfter" character varying(200) COLLATE pg_catalog."default" NOT NULL DEFAULT ''::character varying,
    "EducationID" uuid NOT NULL DEFAULT '00000000-0000-0000-0000-000000000000'::uuid,
    "UserDefinedFields" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "OrganisationID" uuid NOT NULL DEFAULT '00000000-0000-0000-0000-000000000000'::uuid,
    "NationalityID" uuid NOT NULL DEFAULT '00000000-0000-0000-0000-000000000000'::uuid,
    "Remarks" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "PreferredLanguage" character varying(10) COLLATE pg_catalog."default" NOT NULL DEFAULT 'E'::character varying,
    "Sex" integer NOT NULL DEFAULT 3,
    "DateOfLastTest" timestamp with time zone NOT NULL DEFAULT '2000-01-01 06:00:00+01'::timestamp with time zone,
    "BirthDate" date NOT NULL DEFAULT '2000-01-01'::date,
    "Active" boolean NOT NULL DEFAULT true,
    "CompanyID" uuid NOT NULL DEFAULT '00000000-0000-0000-0000-000000000000'::uuid,
    "PluginData" text COLLATE pg_catalog."default" NOT NULL DEFAULT '{}'::text,
    "ManagedByUserID" uuid NOT NULL DEFAULT '00000000-0000-0000-0000-000000000000'::uuid,
    CONSTRAINT "ClientPersons_pkey" PRIMARY KEY ("ID")
)
WITH (
    OIDS = FALSE
)
TABLESPACE %TABLESPACE%;

ALTER TABLE public."ClientPersons"
    OWNER to postgres;

-- Index: IX_CP_BirthDate

-- DROP INDEX public."IX_CP_BirthDate";

CREATE INDEX "IX_CP_BirthDate"
    ON public."ClientPersons" USING btree
    ("BirthDate")
    TABLESPACE %TABLESPACE%;

-- Index: IX_CP_CompanyID

-- DROP INDEX public."IX_CP_CompanyID";

CREATE INDEX "IX_CP_CompanyID"
    ON public."ClientPersons" USING btree
    ("CompanyID")
    TABLESPACE %TABLESPACE%;

-- Index: IX_CP_DateOfLastTest

-- DROP INDEX public."IX_CP_DateOfLastTest";

CREATE INDEX "IX_CP_DateOfLastTest"
    ON public."ClientPersons" USING btree
    ("DateOfLastTest")
    TABLESPACE %TABLESPACE%;

-- Index: IX_CP_EMail

-- DROP INDEX public."IX_CP_EMail";

CREATE INDEX "IX_CP_EMail"
    ON public."ClientPersons" USING btree
    ("EMail" COLLATE pg_catalog."default")
    TABLESPACE %TABLESPACE%;

-- Index: IX_CP_EducationID

-- DROP INDEX public."IX_CP_EducationID";

CREATE INDEX "IX_CP_EducationID"
    ON public."ClientPersons" USING btree
    ("EducationID")
    TABLESPACE %TABLESPACE%;

-- Index: IX_CP_ManagedByUserID

-- DROP INDEX public."IX_CP_ManagedByUserID";

CREATE INDEX "IX_CP_ManagedByUserID"
    ON public."ClientPersons" USING btree
    ("ManagedByUserID")
    TABLESPACE %TABLESPACE%;

-- Index: IX_CP_NationalityID

-- DROP INDEX public."IX_CP_NationalityID";

CREATE INDEX "IX_CP_NationalityID"
    ON public."ClientPersons" USING btree
    ("NationalityID")
    TABLESPACE %TABLESPACE%;

-- Index: IX_CP_OrganisationID

-- DROP INDEX public."IX_CP_OrganisationID";

CREATE INDEX "IX_CP_OrganisationID"
    ON public."ClientPersons" USING btree
    ("OrganisationID")
    TABLESPACE %TABLESPACE%;

-- Index: IX_CP_PreferredLanguage

-- DROP INDEX public."IX_CP_PreferredLanguage";

CREATE INDEX "IX_CP_PreferredLanguage"
    ON public."ClientPersons" USING btree
    ("PreferredLanguage" COLLATE pg_catalog."default")
    TABLESPACE %TABLESPACE%;

-- Index: IX_CP_Sex

-- DROP INDEX public."IX_CP_Sex";

CREATE INDEX "IX_CP_Sex"
    ON public."ClientPersons" USING btree
    ("Sex")
    TABLESPACE %TABLESPACE%;

-- Table: public."ClientSessions"

-- DROP TABLE public."ClientSessions";

CREATE TABLE public."ClientSessions"
(
    "ID" uuid NOT NULL,
    "GroupSessionID" uuid NOT NULL,
    "GroupID" uuid NOT NULL,
    "PersonID" uuid NOT NULL,
    "SessionType" smallint NOT NULL DEFAULT 0,
    "Description" character varying(200) COLLATE pg_catalog."default" NOT NULL DEFAULT ''::character varying,
    "Goal" character varying(200) COLLATE pg_catalog."default" NOT NULL DEFAULT ''::character varying,
    "UsedBatteryIDs" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "UserDefinedFields" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "Remarks" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "SessionState" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "AllowedStartDateTime" timestamp with time zone NOT NULL DEFAULT '2000-01-01 06:00:00+01'::timestamp with time zone,
    "AllowedEndDateTime" timestamp with time zone NOT NULL DEFAULT '2100-01-01 09:00:00+01'::timestamp with time zone,
    "StartedAt" timestamp with time zone NOT NULL DEFAULT '2000-01-01 06:00:00+01'::timestamp with time zone,
    "EndedAt" timestamp with time zone NOT NULL DEFAULT '2000-01-01 06:00:00+01'::timestamp with time zone,
    "Status" integer NOT NULL DEFAULT 1,
    "Active" boolean NOT NULL DEFAULT true,
    "EMailNotificationAdresses" character varying(200) COLLATE pg_catalog."default" NOT NULL DEFAULT ''::character varying,
    "EnforceSessionEndDateTime" boolean NOT NULL DEFAULT false,
    "ManagedByUserID" uuid NOT NULL DEFAULT '00000000-0000-0000-0000-000000000000'::uuid,
    "EmailNotificationIncludeResults" boolean NOT NULL DEFAULT false,
    "PluginData" text COLLATE pg_catalog."default" NOT NULL DEFAULT '{}'::text,
    CONSTRAINT "ClientSessions_pkey" PRIMARY KEY ("ID")
)
WITH (
    OIDS = FALSE
)
TABLESPACE %TABLESPACE%;

ALTER TABLE public."ClientSessions"
    OWNER to postgres;

-- Index: IX_CS_AllowedEndDateTime

-- DROP INDEX public."IX_CS_AllowedEndDateTime";

CREATE INDEX "IX_CS_AllowedEndDateTime"
    ON public."ClientSessions" USING btree
    ("AllowedEndDateTime")
    TABLESPACE %TABLESPACE%;

-- Index: IX_CS_AllowedStartDateTime

-- DROP INDEX public."IX_CS_AllowedStartDateTime";

CREATE INDEX "IX_CS_AllowedStartDateTime"
    ON public."ClientSessions" USING btree
    ("AllowedStartDateTime")
    TABLESPACE %TABLESPACE%;

-- Index: IX_CS_Description

-- DROP INDEX public."IX_CS_Description";

CREATE INDEX "IX_CS_Description"
    ON public."ClientSessions" USING btree
    ("Description" COLLATE pg_catalog."default")
    TABLESPACE %TABLESPACE%;

-- Index: IX_CS_Goal

-- DROP INDEX public."IX_CS_Goal";

CREATE INDEX "IX_CS_Goal"
    ON public."ClientSessions" USING btree
    ("Goal" COLLATE pg_catalog."default")
    TABLESPACE %TABLESPACE%;

-- Index: IX_CS_GroupID

-- DROP INDEX public."IX_CS_GroupID";

CREATE INDEX "IX_CS_GroupID"
    ON public."ClientSessions" USING btree
    ("GroupID")
    TABLESPACE %TABLESPACE%;

-- Index: IX_CS_GroupSessionID

-- DROP INDEX public."IX_CS_GroupSessionID";

CREATE INDEX "IX_CS_GroupSessionID"
    ON public."ClientSessions" USING btree
    ("GroupSessionID")
    TABLESPACE %TABLESPACE%;

-- Index: IX_CS_ManagedByUserID

-- DROP INDEX public."IX_CS_ManagedByUserID";

CREATE INDEX "IX_CS_ManagedByUserID"
    ON public."ClientSessions" USING btree
    ("ManagedByUserID")
    TABLESPACE %TABLESPACE%;

-- Index: IX_CS_PersonID

-- DROP INDEX public."IX_CS_PersonID";

CREATE INDEX "IX_CS_PersonID"
    ON public."ClientSessions" USING btree
    ("PersonID")
    TABLESPACE %TABLESPACE%;

-- Index: IX_CS_SessionState

-- DROP INDEX public."IX_CS_SessionState";

CREATE INDEX "IX_CS_SessionState"
    ON public."ClientSessions" USING btree
    ("SessionState" COLLATE pg_catalog."default")
    TABLESPACE %TABLESPACE%;

-- Index: IX_CS_SessionType

-- DROP INDEX public."IX_CS_SessionType";

CREATE INDEX "IX_CS_SessionType"
    ON public."ClientSessions" USING btree
    ("SessionType")
    TABLESPACE %TABLESPACE%;

-- Index: IX_CS_Status

-- DROP INDEX public."IX_CS_Status";

CREATE INDEX "IX_CS_Status"
    ON public."ClientSessions" USING btree
    ("Status")
    TABLESPACE %TABLESPACE%;

-- Table: public."ClientSessionTests"

-- DROP TABLE public."ClientSessionTests";

CREATE TABLE public."ClientSessionTests"
(
    "ID" uuid NOT NULL,
    "SessionID" uuid NOT NULL,
    "TestID" uuid NOT NULL,
    "PersID" uuid NOT NULL,
    "Sequence" smallint NOT NULL DEFAULT 0,
    "TestLanguage" character varying(10) COLLATE pg_catalog."default" NOT NULL,
    "Results" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "Scores" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "NormID1" uuid,
    "NormID2" uuid,
    "NormID3" uuid,
    "TestStart" timestamp with time zone NOT NULL DEFAULT '2000-01-01 06:00:00+01'::timestamp with time zone,
    "TestEnd" timestamp with time zone NOT NULL DEFAULT '2000-01-01 06:00:00+01'::timestamp with time zone,
    "PercentageOfQuestionsAnswered" integer NOT NULL DEFAULT 0,
    "TotalTestTime" bigint NOT NULL DEFAULT 0,
    "Status" integer NOT NULL DEFAULT 1,
    "CurrentPage" integer NOT NULL DEFAULT 0,
    "TotalPages" integer NOT NULL DEFAULT 0,
    "HowTheTestIsTaken" integer NOT NULL DEFAULT 1,
    "WarningMessage" character varying(200) COLLATE pg_catalog."default" NOT NULL DEFAULT ''::character varying,
    "WarningTime" timestamp with time zone NOT NULL DEFAULT '2000-01-01 06:00:00+01'::timestamp with time zone,
    "Billed" boolean NOT NULL DEFAULT false,
    "PluginData" text COLLATE pg_catalog."default" NOT NULL DEFAULT '{}'::text,
    CONSTRAINT "ClientSessionTests_pkey" PRIMARY KEY ("ID"),
    CONSTRAINT "ClientSessionTests_SessionID_fkey" FOREIGN KEY ("SessionID")
        REFERENCES public."ClientSessions" ("ID") MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)
WITH (
    OIDS = FALSE
)
TABLESPACE %TABLESPACE%;

ALTER TABLE public."ClientSessionTests"
    OWNER to postgres;

-- Index: IX_CST_HowTheTestIsTaken

-- DROP INDEX public."IX_CST_HowTheTestIsTaken";

CREATE INDEX "IX_CST_HowTheTestIsTaken"
    ON public."ClientSessionTests" USING btree
    ("HowTheTestIsTaken")
    TABLESPACE %TABLESPACE%;

-- Index: IX_CST_NormID1

-- DROP INDEX public."IX_CST_NormID1";

CREATE INDEX "IX_CST_NormID1"
    ON public."ClientSessionTests" USING btree
    ("NormID1")
    TABLESPACE %TABLESPACE%;

-- Index: IX_CST_NormID2

-- DROP INDEX public."IX_CST_NormID2";

CREATE INDEX "IX_CST_NormID2"
    ON public."ClientSessionTests" USING btree
    ("NormID2")
    TABLESPACE %TABLESPACE%;

-- Index: IX_CST_NormID3

-- DROP INDEX public."IX_CST_NormID3";

CREATE INDEX "IX_CST_NormID3"
    ON public."ClientSessionTests" USING btree
    ("NormID3")
    TABLESPACE %TABLESPACE%;

-- Index: IX_CST_PersID

-- DROP INDEX public."IX_CST_PersID";

CREATE INDEX "IX_CST_PersID"
    ON public."ClientSessionTests" USING btree
    ("PersID")
    TABLESPACE %TABLESPACE%;

-- Index: IX_CST_SessionID

-- DROP INDEX public."IX_CST_SessionID";

CREATE INDEX "IX_CST_SessionID"
    ON public."ClientSessionTests" USING btree
    ("SessionID")
    TABLESPACE %TABLESPACE%;

-- Index: IX_CST_Status

-- DROP INDEX public."IX_CST_Status";

CREATE INDEX "IX_CST_Status"
    ON public."ClientSessionTests" USING btree
    ("Status")
    TABLESPACE %TABLESPACE%;

-- Index: IX_CST_TestID

-- DROP INDEX public."IX_CST_TestID";

CREATE INDEX "IX_CST_TestID"
    ON public."ClientSessionTests" USING btree
    ("TestID")
    TABLESPACE %TABLESPACE%;

-- Table: public."Reports"

-- DROP TABLE public."Reports";

CREATE TABLE public."Reports"
(
    "ID" uuid NOT NULL,
    "TestID" uuid NOT NULL DEFAULT '00000000-0000-0000-0000-000000000000'::uuid,
    "ReportType" smallint NOT NULL DEFAULT 10,
    "Description" character varying(200) COLLATE pg_catalog."default" NOT NULL DEFAULT ''::character varying,
    "Explanation" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "InvoiceCode" character varying(50) COLLATE pg_catalog."default" NOT NULL DEFAULT ''::character varying,
    "CostsInTicks" smallint NOT NULL DEFAULT 0,
    "Remarks" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "ReportLanguage" character varying(50) COLLATE pg_catalog."default" NOT NULL DEFAULT ''::character varying,
    "Active" boolean NOT NULL DEFAULT true,
    "DefaultReport" boolean NOT NULL DEFAULT false,
    "BeforeReportScript" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "AfterReportScript" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "PerCandidateReportScript" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "ReportText" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "ReportGraphs" text COLLATE pg_catalog."default" NOT NULL DEFAULT '{}'::text,
    "PluginData" text COLLATE pg_catalog."default" NOT NULL DEFAULT '{}'::text,
    "TestIDs" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    CONSTRAINT "Reports_pkey" PRIMARY KEY ("ID")
)
WITH (
    OIDS = FALSE
)
TABLESPACE %TABLESPACE%;

ALTER TABLE public."Reports"
    OWNER to postgres;

-- Index: IX_R_Description

-- DROP INDEX public."IX_R_Description";

CREATE INDEX "IX_R_Description"
    ON public."Reports" USING btree
    ("Description" COLLATE pg_catalog."default")
    TABLESPACE %TABLESPACE%;

-- Index: IX_R_InvoiceCode

-- DROP INDEX public."IX_R_InvoiceCode";

CREATE INDEX "IX_R_InvoiceCode"
    ON public."Reports" USING btree
    ("InvoiceCode" COLLATE pg_catalog."default")
    TABLESPACE %TABLESPACE%;

-- Index: IX_R_ReportType

-- DROP INDEX public."IX_R_ReportType";

CREATE INDEX "IX_R_ReportType"
    ON public."Reports" USING btree
    ("ReportType")
    TABLESPACE %TABLESPACE%;

-- Index: IX_R_TestID

-- DROP INDEX public."IX_R_TestID";

CREATE INDEX "IX_R_TestID"
    ON public."Reports" USING btree
    ("TestID")
    TABLESPACE %TABLESPACE%;

-- Table: public."SecurityCompanies"

-- DROP TABLE public."SecurityCompanies";

CREATE TABLE public."SecurityCompanies"
(
    "ID" uuid NOT NULL,
    "CompanyName" character varying(200) COLLATE pg_catalog."default" NOT NULL,
    "CompanyCountry" character varying(200) COLLATE pg_catalog."default" NOT NULL,
    "InternationalVATNr" character varying(200) COLLATE pg_catalog."default" NOT NULL,
    "VATPercentage" double precision NOT NULL DEFAULT 0,
    "MailAddress" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "VisitingAddress" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "InvoiceAddress" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "AdministrativeID" character varying(200) COLLATE pg_catalog."default" NOT NULL DEFAULT ''::character varying,
    "CompanyLogo" character varying(200) COLLATE pg_catalog."default" NOT NULL,
    "ContactPerson" character varying(200) COLLATE pg_catalog."default" NOT NULL,
    "ContactPhone" character varying(50) COLLATE pg_catalog."default" NOT NULL,
    "ContactEMail" character varying(200) COLLATE pg_catalog."default" NOT NULL,
    "TestTakingDiscount" integer NOT NULL DEFAULT 0,
    "CostsPerTestInUnits" integer NOT NULL DEFAULT 0,
    "YearlyLicenseDiscount" integer NOT NULL DEFAULT 0,
    "YearlyLicenseFee" integer NOT NULL,
    "InvoiceCurrency" character varying(50) COLLATE pg_catalog."default" NOT NULL,
    "CurrentCreditLevel" bigint NOT NULL DEFAULT 0,
    "LowCreditWarningLevel" bigint NOT NULL DEFAULT 500,
    "ConcurrentOpenSessions" integer NOT NULL DEFAULT 0,
    "CompanyVariables" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "AdditionalPersonFields" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "AdditionalGroupFields" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "AdditionalSessionFields" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "AllowNegativeCredits" boolean NOT NULL DEFAULT true,
    "Active" boolean NOT NULL DEFAULT true,
    "LicenseStartDate" timestamp with time zone NOT NULL DEFAULT '2000-01-01 06:00:00+01'::timestamp with time zone,
    "LicenseEndDate" timestamp with time zone NOT NULL DEFAULT '2100-01-01 00:00:00+01'::timestamp with time zone,
    "NoPublicTests" boolean NOT NULL DEFAULT false,
    "ExitURL" character varying(255) COLLATE pg_catalog."default",
    "PluginData" text COLLATE pg_catalog."default" NOT NULL DEFAULT '{}'::text,
    "Generation" integer NOT NULL DEFAULT 1,
    CONSTRAINT "SecurityCompanies_pkey" PRIMARY KEY ("ID")
)
WITH (
    OIDS = FALSE
)
TABLESPACE %TABLESPACE%;

ALTER TABLE public."SecurityCompanies"
    OWNER to postgres;

-- Index: IX_SC_CompanyCountry

-- DROP INDEX public."IX_SC_CompanyCountry";

CREATE INDEX "IX_SC_CompanyCountry"
    ON public."SecurityCompanies" USING btree
    ("CompanyCountry" COLLATE pg_catalog."default")TABLESPACE %TABLESPACE%;

-- Index: IX_SC_CompanyName

-- DROP INDEX public."IX_SC_CompanyName";

CREATE INDEX "IX_SC_CompanyName"
    ON public."SecurityCompanies" USING btree
    ("CompanyName" COLLATE pg_catalog."default")
    TABLESPACE %TABLESPACE%;

-- Index: IX_SC_InvoiceCurrency

-- DROP INDEX public."IX_SC_InvoiceCurrency";

CREATE INDEX "IX_SC_InvoiceCurrency"
    ON public."SecurityCompanies" USING btree
    ("InvoiceCurrency" COLLATE pg_catalog."default")
    TABLESPACE %TABLESPACE%;

-- Table: public."SecurityCreditGrants"

-- DROP TABLE public."SecurityCreditGrants";

CREATE TABLE public."SecurityCreditGrants"
(
    "ID" uuid NOT NULL,
    "UserID" uuid NOT NULL,
    "CompanyID" uuid NOT NULL,
    "GrantedWhen" timestamp with time zone NOT NULL DEFAULT '2000-01-01 06:00:00+01'::timestamp with time zone,
    "Remarks" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "UserDescription" character varying(200) COLLATE pg_catalog."default" NOT NULL DEFAULT ''::character varying,
    "CreditsGranted" smallint NOT NULL DEFAULT 0,
    "Paid" boolean NOT NULL DEFAULT true,
    CONSTRAINT "SecurityCreditGrants_pkey" PRIMARY KEY ("ID"),
    CONSTRAINT "SecurityCreditGrants_CompanyID_fkey" FOREIGN KEY ("CompanyID")
        REFERENCES public."SecurityCompanies" ("ID") MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)
WITH (
    OIDS = FALSE
)
TABLESPACE %TABLESPACE%;

ALTER TABLE public."SecurityCreditGrants"
    OWNER to postgres;

-- Index: IX_SCG_CompanyID

-- DROP INDEX public."IX_SCG_CompanyID";

CREATE INDEX "IX_SCG_CompanyID"
    ON public."SecurityCreditGrants" USING btree
    ("CompanyID")
    TABLESPACE %TABLESPACE%;

-- Index: IX_SCG_GrantedWhen

-- DROP INDEX public."IX_SCG_GrantedWhen";

CREATE INDEX "IX_SCG_GrantedWhen"
    ON public."SecurityCreditGrants" USING btree
    ("GrantedWhen")
    TABLESPACE %TABLESPACE%;

-- Index: IX_SCG_UserID

-- DROP INDEX public."IX_SCG_UserID";

CREATE INDEX "IX_SCG_UserID"
    ON public."SecurityCreditGrants" USING btree
    ("UserID")
    TABLESPACE %TABLESPACE%;

-- Table: public."SecurityCreditUsage"

-- DROP TABLE public."SecurityCreditUsage";

CREATE TABLE public."SecurityCreditUsage"
(
    "ID" uuid NOT NULL,
    "UserID" uuid NOT NULL,
    "CompanyID" uuid NOT NULL,
    "InvoiceCode" character varying(50) COLLATE pg_catalog."default" NOT NULL,
    "OriginalTicks" smallint NOT NULL,
    "DiscountedTicks" smallint NOT NULL,
    "TotalTicks" smallint NOT NULL,
    "UsageDateTime" timestamp with time zone NOT NULL,
    "SessionID" uuid NOT NULL DEFAULT '00000000-0000-0000-0000-000000000000'::uuid,
    "UserName" character varying(200) COLLATE pg_catalog."default" NOT NULL,
    "SessionName" character varying(200) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT "SecurityCreditUsage_pkey" PRIMARY KEY ("ID"),
    CONSTRAINT "SecurityCreditUsage_CompanyID_fkey" FOREIGN KEY ("CompanyID")
        REFERENCES public."SecurityCompanies" ("ID") MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)
WITH (
    OIDS = FALSE
)
TABLESPACE %TABLESPACE%;

ALTER TABLE public."SecurityCreditUsage"
    OWNER to postgres;

-- Index: IX_SCU_CompanyID

-- DROP INDEX public."IX_SCU_CompanyID";

CREATE INDEX "IX_SCU_CompanyID"
    ON public."SecurityCreditUsage" USING btree
    ("CompanyID")
    TABLESPACE %TABLESPACE%;

-- Index: IX_SCU_InvoiceCode

-- DROP INDEX public."IX_SCU_InvoiceCode";

CREATE INDEX "IX_SCU_InvoiceCode"
    ON public."SecurityCreditUsage" USING btree
    ("InvoiceCode" COLLATE pg_catalog."default")
    TABLESPACE %TABLESPACE%;

-- Index: IX_SCU_SessionID

-- DROP INDEX public."IX_SCU_SessionID";

CREATE INDEX "IX_SCU_SessionID"
    ON public."SecurityCreditUsage" USING btree
    ("SessionID")
    TABLESPACE %TABLESPACE%;

-- Index: IX_SCU_UsageDateTime

-- DROP INDEX public."IX_SCU_UsageDateTime";

CREATE INDEX "IX_SCU_UsageDateTime"
    ON public."SecurityCreditUsage" USING btree
    ("UsageDateTime")
    TABLESPACE %TABLESPACE%;

-- Index: IX_SCU_UserID

-- DROP INDEX public."IX_SCU_UserID";

CREATE INDEX "IX_SCU_UserID"
    ON public."SecurityCreditUsage" USING btree
    ("UserID")
    TABLESPACE %TABLESPACE%;

-- Table: public."SecurityDataGathering"

-- DROP TABLE public."SecurityDataGathering";

CREATE TABLE public."SecurityDataGathering"
(
    "ID" uuid NOT NULL,
    "CompanyID" uuid NOT NULL,
    "SessionID" uuid NOT NULL,
    "TestID" uuid NOT NULL,
    "PersonData" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "GroupData" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "SessionData" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "TestData" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "PluginData" text COLLATE pg_catalog."default" NOT NULL DEFAULT '{}'::text,
    CONSTRAINT "SecurityDataGathering_pkey" PRIMARY KEY ("ID")
)
WITH (
    OIDS = FALSE
)
TABLESPACE %TABLESPACE%;

ALTER TABLE public."SecurityDataGathering"
    OWNER to postgres;

-- Index: IX_SDG_CompanyID

-- DROP INDEX public."IX_SDG_CompanyID";

CREATE INDEX "IX_SDG_CompanyID"
    ON public."SecurityDataGathering" USING btree
    ("CompanyID")
    TABLESPACE %TABLESPACE%;

-- Index: IX_SDG_SessionID

-- DROP INDEX public."IX_SDG_SessionID";

CREATE INDEX "IX_SDG_SessionID"
    ON public."SecurityDataGathering" USING btree
    ("SessionID")
    TABLESPACE %TABLESPACE%;

-- Index: IX_SDG_TestID

-- DROP INDEX public."IX_SDG_TestID";

CREATE INDEX "IX_SDG_TestID"
    ON public."SecurityDataGathering" USING btree
    ("TestID")
    TABLESPACE %TABLESPACE%;

-- Table: public."SecurityTemplates"

-- DROP TABLE public."SecurityTemplates";

CREATE TABLE public."SecurityTemplates"
(
    "ID" uuid NOT NULL,
    "Description" character varying(200) COLLATE pg_catalog."default" NOT NULL DEFAULT ''::character varying,
    "Comments" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "Contents" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "PluginData" text COLLATE pg_catalog."default" NOT NULL DEFAULT '{}'::text,
    CONSTRAINT "SecurityTemplates_pkey" PRIMARY KEY ("ID")
)
WITH (
    OIDS = FALSE
)
TABLESPACE %TABLESPACE%;

ALTER TABLE public."SecurityTemplates"
    OWNER to postgres;

-- Index: IX_ST_Description

-- DROP INDEX public."IX_ST_Description";

CREATE INDEX "IX_ST_Description"
    ON public."SecurityTemplates" USING btree
    ("Description" COLLATE pg_catalog."default")
    TABLESPACE %TABLESPACE%;

-- Table: public."SecurityUsers"

-- DROP TABLE public."SecurityUsers";

CREATE TABLE public."SecurityUsers"
(
    "ID" uuid NOT NULL,
    "CompanyID" uuid NOT NULL,
    "Email" character varying(200) COLLATE pg_catalog."default" NOT NULL DEFAULT ''::character varying,
    "Password" character varying(200) COLLATE pg_catalog."default" NOT NULL DEFAULT ''::character varying,
    "UserOpeningsScreen" character varying(200) COLLATE pg_catalog."default" NOT NULL DEFAULT ''::character varying,
    "UserName" character varying(200) COLLATE pg_catalog."default" NOT NULL,
    "UserRights" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "UserParameters" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "PreferredLanguage" character varying(10) COLLATE pg_catalog."default" NOT NULL DEFAULT 'E'::character varying,
    "MailAddress" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "VisitingAddress" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "InvoiceAddress" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "InformationAddress" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "Remarks" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "PasswordExpirationDate" timestamp with time zone NOT NULL DEFAULT '2000-01-01 06:00:00+01'::timestamp with time zone,
    "StartDateLicense" timestamp with time zone NOT NULL DEFAULT '2000-01-01 06:00:00+01'::timestamp with time zone,
    "EndDateLicense" timestamp with time zone NOT NULL DEFAULT '2100-01-01 09:00:00+01'::timestamp with time zone,
    "LastLoginDateTime" timestamp with time zone NOT NULL DEFAULT '2000-01-01 06:00:00+01'::timestamp with time zone,
    "LastRefreshDateTime" timestamp with time zone NOT NULL DEFAULT '2000-01-01 06:00:00+01'::timestamp with time zone,
    "IsMasterUser" boolean NOT NULL DEFAULT false,
    "IsTestTakingUser" boolean NOT NULL DEFAULT false,
    "IsOfficeUser" boolean NOT NULL DEFAULT false,
    "IsOrganisationSupervisor" boolean NOT NULL DEFAULT false,
    "IsTestAuthor" boolean NOT NULL DEFAULT false,
    "IsReportAuthor" boolean NOT NULL DEFAULT false,
    "IsTestScreenTemplateAuthor" boolean NOT NULL DEFAULT false,
    "IsTranslator" boolean NOT NULL DEFAULT false,
    "MayOrderCredits" boolean NOT NULL DEFAULT false,
    "MayWorkWithBatteriesOnly" boolean NOT NULL DEFAULT false,
    "DoNotRenewLicense" boolean NOT NULL DEFAULT false,
    "Active" boolean NOT NULL DEFAULT true,
    "UserCulture" character varying(20) COLLATE pg_catalog."default" NOT NULL DEFAULT 'en'::character varying,
    "SessionPool" integer NOT NULL DEFAULT 1,
    "MayWorkWithOwnObjectsOnly" boolean NOT NULL DEFAULT false,
    "SecurityTemplateID" uuid DEFAULT '00000000-0000-0000-0000-000000000000'::uuid,
    "HasPersonalCreditPool" boolean NOT NULL DEFAULT false,
    "CurrentPersonalCreditLevel" integer NOT NULL DEFAULT 0,
    "PluginData" text COLLATE pg_catalog."default" NOT NULL DEFAULT '{}'::text,
    CONSTRAINT "SecurityUsers_pkey" PRIMARY KEY ("ID"),
    CONSTRAINT "SecurityUsers_CompanyID_fkey" FOREIGN KEY ("CompanyID")
        REFERENCES public."SecurityCompanies" ("ID") MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)
WITH (
    OIDS = FALSE
)
TABLESPACE %TABLESPACE%;

ALTER TABLE public."SecurityUsers"
    OWNER to postgres;

-- Index: IX_SU_CompanyID

-- DROP INDEX public."IX_SU_CompanyID";

CREATE INDEX "IX_SU_CompanyID"
    ON public."SecurityUsers" USING btree
    ("CompanyID")
    TABLESPACE %TABLESPACE%;

-- Index: IX_SU_Email

-- DROP INDEX public."IX_SU_Email";

CREATE INDEX "IX_SU_Email"
    ON public."SecurityUsers" USING btree
    ("Email" COLLATE pg_catalog."default")
    TABLESPACE %TABLESPACE%;

-- Index: IX_SU_EndDateLicense

-- DROP INDEX public."IX_SU_EndDateLicense";

CREATE INDEX "IX_SU_EndDateLicense"
    ON public."SecurityUsers" USING btree
    ("EndDateLicense")
    TABLESPACE %TABLESPACE%;

-- Index: IX_SU_LastLoginDateTime

-- DROP INDEX public."IX_SU_LastLoginDateTime";

CREATE INDEX "IX_SU_LastLoginDateTime"
    ON public."SecurityUsers" USING btree
    ("LastLoginDateTime")
    TABLESPACE %TABLESPACE%;

-- Index: IX_SU_LastRefreshDateTime

-- DROP INDEX public."IX_SU_LastRefreshDateTime";

CREATE INDEX "IX_SU_LastRefreshDateTime"
    ON public."SecurityUsers" USING btree
    ("LastRefreshDateTime")
    TABLESPACE %TABLESPACE%;

-- Index: IX_SU_PasswordExpirationDate

-- DROP INDEX public."IX_SU_PasswordExpirationDate";

CREATE INDEX "IX_SU_PasswordExpirationDate"
    ON public."SecurityUsers" USING btree
    ("PasswordExpirationDate")
    TABLESPACE %TABLESPACE%;

-- Index: IX_SU_SecurityTemplateID

-- DROP INDEX public."IX_SU_SecurityTemplateID";

CREATE INDEX "IX_SU_SecurityTemplateID"
    ON public."SecurityUsers" USING btree
    ("SecurityTemplateID")
    TABLESPACE %TABLESPACE%;

-- Index: IX_SU_SecurityUsers

-- DROP INDEX public."IX_SU_SecurityUsers";

CREATE UNIQUE INDEX "IX_SU_SecurityUsers"
    ON public."SecurityUsers" USING btree
    ("CompanyID", "Email" COLLATE pg_catalog."default")
    TABLESPACE %TABLESPACE%;

-- Index: IX_SU_StartDateLicense

-- DROP INDEX public."IX_SU_StartDateLicense";

CREATE INDEX "IX_SU_StartDateLicense"
    ON public."SecurityUsers" USING btree
    ("StartDateLicense")
    TABLESPACE %TABLESPACE%;

-- Table: public."SecurityWebSessionTokens"

-- DROP TABLE public."SecurityWebSessionTokens";

CREATE TABLE public."SecurityWebSessionTokens"
(
    "Token" character varying(50) COLLATE pg_catalog."default" NOT NULL,
    "UserID" character varying(50) COLLATE pg_catalog."default" NOT NULL,
    "CompanyID" uuid NOT NULL,
    "TokenValidated" timestamp with time zone NOT NULL DEFAULT now(),
    CONSTRAINT "SecurityWebSessionTokens_pkey" PRIMARY KEY ("Token")
)
WITH (
    OIDS = FALSE
)
TABLESPACE %TABLESPACE%;

ALTER TABLE public."SecurityWebSessionTokens"
    OWNER to postgres;

-- Index: IX_SWST_CompanyID

-- DROP INDEX public."IX_SWST_CompanyID";

CREATE INDEX "IX_SWST_CompanyID"
    ON public."SecurityWebSessionTokens" USING btree
    ("CompanyID")
    TABLESPACE %TABLESPACE%;

-- Index: IX_SWST_TokenValidated

-- DROP INDEX public."IX_SWST_TokenValidated";

CREATE INDEX "IX_SWST_TokenValidated"
    ON public."SecurityWebSessionTokens" USING btree
    ("TokenValidated")
    TABLESPACE %TABLESPACE%;

-- Index: IX_SWST_UserID

-- DROP INDEX public."IX_SWST_UserID";

CREATE INDEX "IX_SWST_UserID"
    ON public."SecurityWebSessionTokens" USING btree
    ("UserID" COLLATE pg_catalog."default")
    TABLESPACE %TABLESPACE%;

-- Table: public."SystemParam"

-- DROP TABLE public."SystemParam";

CREATE TABLE public."SystemParam"
(
    "ParameterName" character varying(50) COLLATE pg_catalog."default" NOT NULL,
    "ParValue" character varying COLLATE pg_catalog."default",
    "ParProtected" boolean not null default false,
    CONSTRAINT "SystemParam_pkey" PRIMARY KEY ("ParameterName")
)
WITH (
    OIDS = FALSE
)
TABLESPACE %TABLESPACE%;

ALTER TABLE public."SystemParam"
    OWNER to postgres;

-- Table: public."SystemTranslations"

-- DROP TABLE public."SystemTranslations";

CREATE TABLE public."SystemTranslations"
(
    "ID" uuid NOT NULL,
    "FormName" character varying(250) COLLATE pg_catalog."default" NOT NULL DEFAULT ''::character varying,
    "StringName" character varying(250) COLLATE pg_catalog."default" NOT NULL DEFAULT ''::character varying,
    "LanguageCode" character varying(10) COLLATE pg_catalog."default" NOT NULL DEFAULT ''::character varying,
    "TranslatedString" character varying(4000) COLLATE pg_catalog."default" NOT NULL DEFAULT ''::character varying,
    "IsTranslated" boolean NOT NULL DEFAULT true,
    CONSTRAINT "SystemTranslations_pkey" PRIMARY KEY ("ID")
)
WITH (
    OIDS = FALSE
)
TABLESPACE %TABLESPACE%;

ALTER TABLE public."SystemTranslations"
    OWNER to postgres;

-- Index: IX_ST_FormName

-- DROP INDEX public."IX_ST_FormName";

CREATE INDEX "IX_ST_FormName"
    ON public."SystemTranslations" USING btree
    ("FormName" COLLATE pg_catalog."default")
    TABLESPACE %TABLESPACE%;

-- Index: IX_ST_IsTranslated

-- DROP INDEX public."IX_ST_IsTranslated";

CREATE INDEX "IX_ST_IsTranslated"
    ON public."SystemTranslations" USING btree
    ("IsTranslated")
    TABLESPACE %TABLESPACE%;

-- Index: IX_ST_LanguageCode

-- DROP INDEX public."IX_ST_LanguageCode";

CREATE INDEX "IX_ST_LanguageCode"
    ON public."SystemTranslations" USING btree
    ("LanguageCode" COLLATE pg_catalog."default")
    TABLESPACE %TABLESPACE%;

-- Index: IX_ST_StringName

-- DROP INDEX public."IX_ST_StringName";

CREATE INDEX "IX_ST_StringName"
    ON public."SystemTranslations" USING btree
    ("StringName" COLLATE pg_catalog."default")
    TABLESPACE %TABLESPACE%;

-- Table: public."TestScreenTemplates"

-- DROP TABLE public."TestScreenTemplates";

CREATE TABLE public."TestScreenTemplates"
(
    "ID" uuid NOT NULL,
    "HTMLContent" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "HTMLContentPnP" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "PluginData" text COLLATE pg_catalog."default" NOT NULL DEFAULT '{}'::text,
    "Description" character varying(200) COLLATE pg_catalog."default" NOT NULL DEFAULT ''::character varying,
    "TemplateType" smallint NOT NULL DEFAULT 0,
    "Explanation" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "Remarks" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "ScreenDefinitionFrozen" boolean NOT NULL DEFAULT false,
    "ScreenDefinitionIsReleased" boolean NOT NULL DEFAULT false,
    "TemplateVariables" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    get_value_snippet text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    get_value_as_html_snippet text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    set_value_snippet text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    init_value_snippet text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    generator_snippet text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    generator_pnp_snippet text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    validation_snippet text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    isanswered_snippet text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    CONSTRAINT "TestScreenTemplates_pkey" PRIMARY KEY ("ID")
)
WITH (
    OIDS = FALSE
)
TABLESPACE %TABLESPACE%;

ALTER TABLE public."TestScreenTemplates"
    OWNER to postgres;

-- Index: IX_TST_Description

-- DROP INDEX public."IX_TST_Description";

CREATE INDEX "IX_TST_Description"
    ON public."TestScreenTemplates" USING btree
    ("Description" COLLATE pg_catalog."default")
    TABLESPACE %TABLESPACE%;

-- Table: public."Tests"

-- DROP TABLE public."Tests";

CREATE TABLE public."Tests"
(
    "ID" uuid NOT NULL,
    "TestName" character varying(50) COLLATE pg_catalog."default" NOT NULL DEFAULT ''::character varying,
    "Description" character varying(200) COLLATE pg_catalog."default" NOT NULL DEFAULT ''::character varying,
    "Explanation" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "CatalogInformation" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "Copyrights" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "Costs" smallint NOT NULL DEFAULT 0,
    "TestType" smallint NOT NULL DEFAULT 0,
    "AuthorInfo" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "InvoiceCode" character varying(50) COLLATE pg_catalog."default" NOT NULL DEFAULT ''::character varying,
    "Remarks" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "TestStartDate" timestamp with time zone NOT NULL DEFAULT '2000-01-01 06:00:00+01'::timestamp with time zone,
    "TestEndDate" timestamp with time zone NOT NULL DEFAULT '2100-01-01 09:00:00+01'::timestamp with time zone,
    "TestDefinitionFrozen" boolean NOT NULL DEFAULT false,
    "TestDefinitionIsReleased" boolean NOT NULL DEFAULT false,
    "TestDefinitionIsOpenSource" boolean NOT NULL DEFAULT false,
    "TestDefinitionIsCommercial" boolean NOT NULL DEFAULT false,
    "TestDefinitionIsExternal" boolean NOT NULL DEFAULT false,
    "TestDefinitionIsBanned" boolean NOT NULL DEFAULT false,
    "Active" boolean NOT NULL DEFAULT true,
    "SupportsTestTaking" boolean NOT NULL DEFAULT true,
    "SupportsTestScoring" boolean NOT NULL DEFAULT true,
    "SupportsOnlyRenorming" boolean NOT NULL DEFAULT true,
    "IsRestartable" boolean NOT NULL DEFAULT true,
    "Supports360Degrees" boolean NOT NULL DEFAULT true,
    "CandidateCanDo360Too" boolean NOT NULL DEFAULT true,
    "ShowTestClosureScreen" boolean NOT NULL DEFAULT true,
    "TotalTimeAvailableForThisTest" smallint NOT NULL,
    "MinPercentageOfAnswersRequired" integer NOT NULL DEFAULT 0,
    "TotalNumberOfExperiments" smallint NOT NULL DEFAULT 0,
    "BeforeScript" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "AfterScript" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "BeforeNormingScript" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "AfterNormingScript" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "ScoringScript" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "Pre360" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "Per360" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "Post360" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "RequiredParsPerson" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "RequiredParsSession" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "RequiredParsGroup" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "RequiredParsOrganisation" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "PluginData" text COLLATE pg_catalog."default" NOT NULL DEFAULT '{}'::text,
    screens text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    scales text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    norms text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    documents text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "scoreRules" text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    graphs text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    media text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    files text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
    "LanguageSupport" character varying(200) COLLATE pg_catalog."default" NOT NULL DEFAULT ''::character varying,
    "Generation" integer NOT NULL DEFAULT 1,
    CONSTRAINT "Tests_pkey" PRIMARY KEY ("ID")
)
WITH (
    OIDS = FALSE
)
TABLESPACE %TABLESPACE%;

ALTER TABLE public."Tests"
    OWNER to postgres;

-- Index: IX_T_InvoiceCode

-- DROP INDEX public."IX_T_InvoiceCode";

CREATE INDEX "IX_T_InvoiceCode"
    ON public."Tests" USING btree
    ("InvoiceCode" COLLATE pg_catalog."default")
    TABLESPACE %TABLESPACE%;

-- Index: IX_T_TestEndDate

-- DROP INDEX public."IX_T_TestEndDate";

CREATE INDEX "IX_T_TestEndDate"
    ON public."Tests" USING btree
    ("TestEndDate")
    TABLESPACE %TABLESPACE%;

-- Index: IX_T_TestName

-- DROP INDEX public."IX_T_TestName";

CREATE INDEX "IX_T_TestName"
    ON public."Tests" USING btree
    ("TestName" COLLATE pg_catalog."default")
    TABLESPACE %TABLESPACE%;

-- Index: IX_T_TestStartDate

-- DROP INDEX public."IX_T_TestStartDate";

CREATE INDEX "IX_T_TestStartDate"
    ON public."Tests" USING btree
    ("TestStartDate")
    TABLESPACE %TABLESPACE%;


-- Table: public."ClientGroupMember"

-- DROP TABLE public."ClientGroupMember";

CREATE TABLE public."ClientGroupMember"
(
    "ID" uuid NOT NULL,
    "PersonID" uuid NOT NULL,
    "Name" character varying(200) COLLATE pg_catalog."default" NOT NULL,
    "EMail" character varying(200) COLLATE pg_catalog."default" NOT NULL,
    "BirthDate" timestamp without time zone NOT NULL,
    "PluginData" text COLLATE pg_catalog."default" NOT NULL DEFAULT '{}'::text,
    CONSTRAINT "ClientGroupMember_pkey" PRIMARY KEY ("ID", "PersonID"),
    CONSTRAINT "ClientGroupMember_ID_fkey" FOREIGN KEY ("ID")
        REFERENCES public."ClientGroups" ("ID") MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT "ClientGroupMember_PersonID_fkey" FOREIGN KEY ("PersonID")
        REFERENCES public."ClientPersons" ("ID") MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)
WITH (
    OIDS = FALSE
)
TABLESPACE %TABLESPACE%;

ALTER TABLE public."ClientGroupMember"
    OWNER to postgres;

-- Index: IX_CGM_BirthDate

-- DROP INDEX public."IX_CGM_BirthDate";

CREATE INDEX "IX_CGM_BirthDate"
    ON public."ClientGroupMember" USING btree
    ("BirthDate")
    TABLESPACE %TABLESPACE%;

-- Index: IX_CGM_EMail

-- DROP INDEX public."IX_CGM_EMail";

CREATE INDEX "IX_CGM_EMail"
    ON public."ClientGroupMember" USING btree
    ("EMail" COLLATE pg_catalog."default")
    TABLESPACE %TABLESPACE%;

-- Index: IX_CGM_Name

-- DROP INDEX public."IX_CGM_Name";

CREATE INDEX "IX_CGM_Name"
    ON public."ClientGroupMember" USING btree
    ("Name" COLLATE pg_catalog."default")
    TABLESPACE %TABLESPACE%;


CREATE OR REPLACE VIEW ViewClientSessionsWithPerson AS
 select
  A."ID", "GroupSessionID", "GroupID", "PersonID", "SessionType", "Description", "Goal", "UsedBatteryIDs", A."Remarks", "SessionState", "AllowedStartDateTime", "AllowedEndDateTime", "StartedAt", "EndedAt", "Status", A."Active" as Active, "EMailNotificationAdresses", "EnforceSessionEndDateTime", A."ManagedByUserID", "EmailNotificationIncludeResults",
  "EMail", "FirstName", "Initials", "LastName", "TitlesBefore", "TitlesAfter", "EducationID", "OrganisationID", "NationalityID", "PreferredLanguage", "Sex", "DateOfLastTest", "BirthDate", B."Active" as PersonActive
 from "ClientSessions" A inner join "ClientPersons" B on A."PersonID" = B."ID";

CREATE OR REPLACE VIEW ViewClientSessionTestsWithPerson AS
 select
  A."ID", "SessionID", "TestID", "PersID", "Sequence", "TestLanguage", "NormID1", "NormID2", "NormID3", "TestStart", "TestEnd", "PercentageOfQuestionsAnswered", "TotalTestTime", A."Status" as Status, "CurrentPage", "TotalPages", "HowTheTestIsTaken", "WarningMessage", "WarningTime", "Billed",
    "EMail", "FirstName", "Initials", "LastName", "TitlesBefore", "TitlesAfter", "EducationID", "OrganisationID", "NationalityID", "PreferredLanguage", "Sex", "DateOfLastTest", "BirthDate", B."Active" as PersonActive,
	C."Description", C."SessionType", C."Status" as SessionStatus, C."Active"
 from "ClientSessionTests" A inner join "ClientPersons" as B on A."PersID" = B."ID"
  inner join "ClientSessions" C on A."SessionID" = C."ID";

insert into "SecurityCompanies" ("ID", "CompanyName", "CompanyCountry", "InternationalVATNr", "CompanyLogo", "ContactPerson","ContactPhone","ContactEMail", "YearlyLicenseFee","YearlyLicenseDiscount","InvoiceCurrency") values ( '%NEWCOMPANYID%', 'ITRHelpdesk', 'Netherlands','','','','','',0,0,'Euro')

insert into "SecurityUsers" ("ID", "CompanyID", "Email", "UserName", "Password", "IsMasterUser", "IsOfficeUser", "IsOrganisationSupervisor", "IsTestAuthor", "IsReportAuthor", "IsTestScreenTemplateAuthor", "IsTranslator")
values('%ADMINUSERID%', '%NEWCOMPANYID%', 'Admin', 'Admin', '22CentigradeInArequipaToday', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE)

insert into "SystemParam" values( 'DBVersion','2', TRUE )

insert into "SystemParam" values( 'CreditOrderEMail', '', TRUE )

insert into "SystemParam" values( 'MAXNUMBEROFCONSULTANTS', '', TRUE )

insert into "SystemParam" values( 'SMTP_SENDER', '', TRUE )

insert into "SystemParam" values( 'SMTP_SERVER', '', TRUE )

insert into "SystemParam" values( 'SMTP_PORT', '', TRUE )

insert into "SystemParam" values( 'SMTP_USETLS', '', TRUE )

insert into "SystemParam" values( 'SMTP_USER', '', TRUE )

insert into "SystemParam" values( 'SMTP_PASSWORD', '', TRUE )

insert into "SystemParam" values( 'TRANSLATE_AZURE_KEY', '', TRUE )

insert into "SystemParam" values( 'ServerID', md5(random()::text || clock_timestamp()::text)::uuid , TRUE )

// end of file