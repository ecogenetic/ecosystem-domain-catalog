-- CRM software-company mapping sample
-- PostgreSQL 14+
-- Synthetic rows showing how a software customer links to a license,
-- applications, a release, and a deployment.
-- Operational state stays in the owning table.

CREATE SCHEMA IF NOT EXISTS software_crm_sample;
SET search_path TO software_crm_sample, public;

CREATE TABLE IF NOT EXISTS software_accounts (
    software_account_id varchar(64) PRIMARY KEY,
    account_name        varchar(200) NOT NULL,
    party_id            varchar(64) NOT NULL
);

CREATE TABLE IF NOT EXISTS product_subscription_opportunities (
    product_subscription_opportunity_id varchar(64) PRIMARY KEY,
    software_account_id varchar(64) NOT NULL REFERENCES software_accounts(software_account_id),
    product_edition_code varchar(64) NOT NULL,
    opportunity_status  varchar(32) NOT NULL
);

CREATE TABLE IF NOT EXISTS license_agreements (
    license_agreement_id varchar(64) PRIMARY KEY,
    software_account_id  varchar(64) NOT NULL REFERENCES software_accounts(software_account_id),
    product_edition_code varchar(64) NOT NULL,
    license_agreement_status varchar(32) NOT NULL
);

CREATE TABLE IF NOT EXISTS entitlements (
    entitlement_id varchar(64) PRIMARY KEY,
    license_agreement_id varchar(64) NOT NULL REFERENCES license_agreements(license_agreement_id),
    seat_count integer NOT NULL
);

CREATE TABLE IF NOT EXISTS client_applications (
    client_application_id varchar(64) PRIMARY KEY,
    application_name varchar(200) NOT NULL,
    client_application_status varchar(32) NOT NULL
);

CREATE TABLE IF NOT EXISTS backend_services (
    backend_service_id varchar(64) PRIMARY KEY,
    service_name varchar(200) NOT NULL
);

CREATE TABLE IF NOT EXISTS releases (
    release_id varchar(64) PRIMARY KEY,
    product_edition_code varchar(64) NOT NULL,
    release_status varchar(32) NOT NULL
);

CREATE TABLE IF NOT EXISTS release_targets (
    release_target_id varchar(64) PRIMARY KEY,
    environment_code varchar(64) NOT NULL
);

CREATE TABLE IF NOT EXISTS deployments (
    deployment_id varchar(64) PRIMARY KEY,
    release_id varchar(64) NOT NULL REFERENCES releases(release_id),
    release_target_id varchar(64) NOT NULL REFERENCES release_targets(release_target_id)
);

CREATE TABLE IF NOT EXISTS cloud_environments (
    cloud_environment_id varchar(64) PRIMARY KEY,
    environment_code varchar(64) NOT NULL,
    cloud_account_id varchar(64) NOT NULL
);
