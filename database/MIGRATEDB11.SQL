CREATE EXTENSION IF NOT EXISTS pg_trgm;

create index IF NOT EXISTS ixg_ClientAuditLog ON "ClientAuditLog" using gin(( "ObjectType" || "OldData"|| "NewData"|| "AuditMessage") gin_trgm_ops);

create index IF NOT EXISTS ixg_ClientBatteries ON "ClientBatteries" using gin(( "BatteryName"|| "Description"|| "InvoiceCode"|| "ReportMailAdress"|| "Remarks") gin_trgm_ops);


create index IF NOT EXISTS ixg_ClientEducations ON "ClientEducations" using gin(( "Name"|| "EducationGroup"|| "Remarks") gin_trgm_ops);


create index IF NOT EXISTS ixg_ClientGeneratedReports ON "ClientGeneratedReports" using gin(( "ReportTitle" || "ReportText") gin_trgm_ops);


create index IF NOT EXISTS ixg_ClientGroupMember ON "ClientGroupMember" using gin(( "Name" || "EMail") gin_trgm_ops);


create index IF NOT EXISTS ixg_ClientGroups ON "ClientGroups" using gin(( "Description" || "UserDefinedFields"|| "Remarks") gin_trgm_ops);


create index IF NOT EXISTS ixg_ClientNationalities ON "ClientNationalities" using gin(( "NationalityName" || "NationalityCode"|| "Translations"|| "Remarks") gin_trgm_ops);


create index IF NOT EXISTS ixg_ClientOrganisations ON "ClientOrganisations" using gin(( "Name"|| "Address"|| "Logo"|| "ContactPerson"|| "ContactPhone"|| "ContactEMail"|| "Remarks") gin_trgm_ops);


create index IF NOT EXISTS ixg_ClientPersons ON "ClientPersons" using gin(( "EMail"|| "FirstName"|| "Initials"|| "LastName"|| "TitlesBefore"|| "TitlesAfter"|| "EducationID"|| "UserDefinedFields"|| "PreferredLanguage"|| "Sex"||  "Remarks") gin_trgm_ops);


create index IF NOT EXISTS ixg_ClientSessionTests ON "ClientSessionTests" using gin(( "HowTheTestIsTaken"|| "WarningMessage") gin_trgm_ops);


create index IF NOT EXISTS ixg_ClientSessions ON "ClientSessions" using gin(( "Description"
        || "Goal"
        || "SessionState"
        || "Status"
        || "EMailNotificationAdresses"
        || "Remarks") gin_trgm_ops);


create index IF NOT EXISTS ixg_Reports ON "Reports" using gin(( "ReportType" || "Description"|| "InvoiceCode"|| "CostsInTicks"|| "ReportLanguage"|| "Remarks"|| "Explanation") gin_trgm_ops);


create index IF NOT EXISTS ixg_SecurityCompanies ON "SecurityCompanies" using gin(( "CompanyName"
         ||  "CompanyCountry"
         ||  "InternationalVATNr" ||  "MailAddress" ||  "VisitingAddress" ||  "InvoiceAddress"
         ||  "ContactPerson" ||  "ContactPhone" ||  "ContactEMail") gin_trgm_ops);


create index IF NOT EXISTS ixg_SecurityCreditGrants ON "SecurityCreditGrants" using gin(("UserDescription"||  "CreditsGranted"||  "Remarks") gin_trgm_ops);


create index IF NOT EXISTS ixg_SecurityCreditUsage ON "SecurityCreditUsage" using gin(( "InvoiceCode"|| "OriginalTicks"|| "DiscountedTicks"|| "TotalTicks"||  "SessionName"|| "UserName") gin_trgm_ops);


create index IF NOT EXISTS ixg_SecurityTemplates ON "SecurityTemplates" using gin(( "Description"|| "Comments"|| "Contents") gin_trgm_ops);


create index IF NOT EXISTS ixg_SecurityUsers ON "SecurityUsers" using gin(( "Email"|| "UserName"|| "MailAddress"|| "VisitingAddress"|| "InvoiceAddress"|| "InformationAddress"|| "Remarks" || "CurrentPersonalCreditLevel") gin_trgm_ops);


create index IF NOT EXISTS ixg_SecurityWebSessionTokens ON "SecurityWebSessionTokens" using gin(( "Token" ) gin_trgm_ops);


create index IF NOT EXISTS ixg_SystemParam ON "SystemParam" using gin(( "ParameterName"|| "ParValue") gin_trgm_ops);


create index IF NOT EXISTS ixg_TestScreenTemplates ON "TestScreenTemplates" using gin(( "Description"|| "Explanation"|| "Remarks") gin_trgm_ops);


create index IF NOT EXISTS ixg_Tests ON "Tests" using gin(( "TestName"|| "Description"|| "Costs"|| "TestType"|| "Generation"|| "CatalogInformation"|| "Remarks") gin_trgm_ops);




update "SystemParam"
set "ParValue" = '12'
where "ParameterName" = 'DBVersion'

// end of file