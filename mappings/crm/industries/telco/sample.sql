-- CRM telecommunications mapping sample
-- PostgreSQL 14+
--
-- Demonstrates source tables and columns used by generic-mapping.ttl.
-- The values are synthetic and intentionally small.
--
-- Mapping:
--   CustomerParty -> SubscriberRelationship -> CustomerAccount
--   -> Subscription -> Subscriber/ServiceLine
--   -> MobileNumber + SIMProfile + Device
--   -> BillingAccount + ChargingAccount
--   -> Opportunity -> ServiceOrderHandoff -> ServiceOrder
--   -> ChurnRisk -> RetentionJourney

CREATE SCHEMA IF NOT EXISTS telco_crm_sample;
SET search_path TO telco_crm_sample, public;

-----------------------------------------------------------------
-- Customer party and relationship
-----------------------------------------------------------------

CREATE TABLE IF NOT EXISTS customer_parties (
    customer_party_id       varchar(64) PRIMARY KEY,
    party_role              varchar(32) NOT NULL,
    identity_verified       boolean NOT NULL DEFAULT false,
    full_name               varchar(200),
    organisation_name       varchar(200),
    email                   varchar(320),
    phone                   varchar(32),
    CONSTRAINT customer_party_role_ck
        CHECK (party_role IN ('person', 'organisation')),
    CONSTRAINT customer_party_name_ck
        CHECK (full_name IS NOT NULL OR organisation_name IS NOT NULL)
);

CREATE TABLE IF NOT EXISTS authorised_contacts (
    authorised_contact_id   varchar(64) PRIMARY KEY,
    customer_party_ref      varchar(64) NOT NULL
        REFERENCES customer_parties(customer_party_id),
    authority_type          varchar(40) NOT NULL,
    authority_start         date NOT NULL,
    authority_end           date,
    full_name               varchar(200) NOT NULL,
    email                   varchar(320),
    phone                   varchar(32),
    CONSTRAINT contact_authority_dates_ck
        CHECK (authority_end IS NULL OR authority_end >= authority_start)
);

CREATE TABLE IF NOT EXISTS subscriber_relationships (
    subscriber_relationship_id       varchar(64) PRIMARY KEY,
    relationship_customer_party_ref  varchar(64) NOT NULL
        REFERENCES customer_parties(customer_party_id),
    relationship_segment             varchar(40),
    relationship_status              varchar(24) NOT NULL,
    relationship_start_date          date NOT NULL,
    CONSTRAINT subscriber_relationship_status_ck
        CHECK (relationship_status IN
            ('prospect', 'onboarding', 'active', 'suspended', 'ended'))
);

CREATE TABLE IF NOT EXISTS relationship_authorised_contacts (
    subscriber_relationship_ref          varchar(64) NOT NULL
        REFERENCES subscriber_relationships(subscriber_relationship_id),
    relationship_authorised_contact_ref  varchar(64) NOT NULL
        REFERENCES authorised_contacts(authorised_contact_id),
    PRIMARY KEY (
        subscriber_relationship_ref,
        relationship_authorised_contact_ref
    )
);

-----------------------------------------------------------------
-- Commercial account, plan, subscription, and service identity
-----------------------------------------------------------------

CREATE TABLE IF NOT EXISTS customer_accounts (
    customer_account_id            varchar(64) PRIMARY KEY,
    relationship_customer_account_ref varchar(64) NOT NULL
        REFERENCES subscriber_relationships(subscriber_relationship_id),
    account_status                 varchar(24) NOT NULL,
    payment_type                   varchar(20) NOT NULL,
    currency_code                  char(3) NOT NULL,
    CONSTRAINT customer_account_status_ck
        CHECK (account_status IN ('pending', 'active', 'suspended', 'closed')),
    CONSTRAINT payment_type_ck
        CHECK (payment_type IN ('prepaid', 'postpaid', 'hybrid'))
);

CREATE TABLE IF NOT EXISTS rate_plans (
    rate_plan_id          varchar(64) PRIMARY KEY,
    plan_code             varchar(64) NOT NULL UNIQUE,
    plan_name             varchar(200) NOT NULL,
    recurring_fee         numeric(18,2) NOT NULL DEFAULT 0,
    commitment_months     integer NOT NULL DEFAULT 0,
    CONSTRAINT recurring_fee_ck CHECK (recurring_fee >= 0),
    CONSTRAINT commitment_months_ck CHECK (commitment_months >= 0)
);

CREATE TABLE IF NOT EXISTS subscriptions (
    subscription_id                 varchar(64) PRIMARY KEY,
    relationship_subscription_ref  varchar(64) NOT NULL
        REFERENCES subscriber_relationships(subscriber_relationship_id),
    customer_account_ref           varchar(64) NOT NULL
        REFERENCES customer_accounts(customer_account_id),
    subscription_rate_plan_ref     varchar(64) NOT NULL
        REFERENCES rate_plans(rate_plan_id),
    subscription_type              varchar(32) NOT NULL,
    subscription_status            varchar(24) NOT NULL,
    contract_start_date            date,
    contract_end_date              date,
    CONSTRAINT subscription_status_ck
        CHECK (subscription_status IN
            ('pending', 'active', 'suspended', 'terminated')),
    CONSTRAINT subscription_dates_ck
        CHECK (
            contract_end_date IS NULL
            OR contract_start_date IS NULL
            OR contract_end_date >= contract_start_date
        )
);

CREATE TABLE IF NOT EXISTS subscribers (
    subscriber_id               varchar(64) PRIMARY KEY,
    subscription_subscriber_ref varchar(64) NOT NULL
        REFERENCES subscriptions(subscription_id),
    service_status              varchar(24) NOT NULL,
    service_activated_at        timestamptz,
    CONSTRAINT subscriber_service_status_ck
        CHECK (service_status IN
            ('reserved', 'pending_activation', 'active', 'suspended', 'ceased'))
);

-----------------------------------------------------------------
-- Number, SIM, and device
-----------------------------------------------------------------

CREATE TABLE IF NOT EXISTS mobile_numbers (
    mobile_number_id       varchar(64) PRIMARY KEY,
    msisdn                 varchar(20) NOT NULL UNIQUE,
    number_status          varchar(24) NOT NULL,
    CONSTRAINT msisdn_format_ck CHECK (msisdn ~ '^\+[1-9][0-9]{7,14}$')
);

CREATE TABLE IF NOT EXISTS sim_profiles (
    sim_profile_id         varchar(64) PRIMARY KEY,
    iccid                  varchar(24) NOT NULL UNIQUE,
    imsi                   varchar(20) UNIQUE,
    sim_type               varchar(16) NOT NULL,
    CONSTRAINT sim_type_ck CHECK (sim_type IN ('physical', 'esim'))
);

CREATE TABLE IF NOT EXISTS devices (
    device_id               varchar(64) PRIMARY KEY,
    device_identifier       varchar(64) NOT NULL UNIQUE,
    device_type             varchar(32) NOT NULL,
    device_model            varchar(120),
    device_eligibility_date date
);

CREATE TABLE IF NOT EXISTS subscriber_identifiers (
    subscriber_ref             varchar(64) PRIMARY KEY
        REFERENCES subscribers(subscriber_id),
    subscriber_mobile_number_ref varchar(64) NOT NULL
        REFERENCES mobile_numbers(mobile_number_id),
    subscriber_sim_profile_ref varchar(64) NOT NULL
        REFERENCES sim_profiles(sim_profile_id),
    valid_from                 timestamptz NOT NULL,
    valid_to                   timestamptz,
    CONSTRAINT subscriber_identifier_dates_ck
        CHECK (valid_to IS NULL OR valid_to >= valid_from)
);

CREATE TABLE IF NOT EXISTS subscriber_devices (
    subscriber_ref        varchar(64) NOT NULL
        REFERENCES subscribers(subscriber_id),
    subscriber_device_ref varchar(64) NOT NULL
        REFERENCES devices(device_id),
    associated_from       timestamptz NOT NULL,
    associated_to         timestamptz,
    PRIMARY KEY (subscriber_ref, subscriber_device_ref, associated_from)
);

-----------------------------------------------------------------
-- Billing and charging references
-----------------------------------------------------------------

CREATE TABLE IF NOT EXISTS billing_accounts (
    billing_account_id                 varchar(64) PRIMARY KEY,
    relationship_billing_account_ref   varchar(64) NOT NULL
        REFERENCES subscriber_relationships(subscriber_relationship_id),
    bill_cycle_day                     integer NOT NULL,
    invoice_delivery_channel           varchar(20) NOT NULL,
    CONSTRAINT bill_cycle_day_ck CHECK (bill_cycle_day BETWEEN 1 AND 28)
);

CREATE TABLE IF NOT EXISTS charging_accounts (
    charging_account_id                varchar(64) PRIMARY KEY,
    relationship_charging_account_ref  varchar(64) NOT NULL
        REFERENCES subscriber_relationships(subscriber_relationship_id),
    balance_amount                     numeric(18,2) NOT NULL DEFAULT 0,
    data_allowance_mb                  numeric(18,2) NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS invoices (
    invoice_id              varchar(64) PRIMARY KEY,
    billing_account_ref     varchar(64) NOT NULL
        REFERENCES billing_accounts(billing_account_id),
    invoice_number          varchar(64) NOT NULL UNIQUE,
    invoice_date            date NOT NULL,
    amount_due              numeric(18,2) NOT NULL,
    invoice_status          varchar(20) NOT NULL
);

-----------------------------------------------------------------
-- Sales-to-fulfilment handoff
-----------------------------------------------------------------

CREATE TABLE IF NOT EXISTS opportunities (
    opportunity_id                varchar(64) PRIMARY KEY,
    subscriber_relationship_ref   varchar(64) NOT NULL
        REFERENCES subscriber_relationships(subscriber_relationship_id),
    opportunity_subscription_ref  varchar(64)
        REFERENCES subscriptions(subscription_id),
    opportunity_rate_plan_ref     varchar(64)
        REFERENCES rate_plans(rate_plan_id),
    opportunity_name              varchar(200) NOT NULL,
    opportunity_type              varchar(32) NOT NULL,
    opportunity_amount            numeric(18,2) NOT NULL DEFAULT 0,
    opportunity_probability       numeric(5,4) NOT NULL,
    opportunity_status            varchar(24) NOT NULL,
    opportunity_close_date        date,
    CONSTRAINT opportunity_probability_ck
        CHECK (opportunity_probability BETWEEN 0 AND 1),
    CONSTRAINT opportunity_status_ck
        CHECK (opportunity_status IN
            ('lead', 'qualified', 'proposal', 'won', 'lost'))
);

CREATE TABLE IF NOT EXISTS service_orders (
    service_order_id        varchar(64) PRIMARY KEY,
    service_order_type      varchar(24) NOT NULL,
    service_order_status    varchar(24) NOT NULL,
    submitted_at            timestamptz NOT NULL,
    completed_at            timestamptz
);

CREATE TABLE IF NOT EXISTS service_order_handoffs (
    service_order_handoff_id       varchar(64) PRIMARY KEY,
    handoff_opportunity_ref        varchar(64) NOT NULL
        REFERENCES opportunities(opportunity_id),
    handoff_service_order_ref      varchar(64) NOT NULL UNIQUE
        REFERENCES service_orders(service_order_id),
    handoff_at                     timestamptz NOT NULL,
    handoff_status                 varchar(24) NOT NULL,
    CONSTRAINT handoff_status_ck
        CHECK (handoff_status IN
            ('prepared', 'submitted', 'acknowledged', 'completed', 'failed'))
);

-----------------------------------------------------------------
-- Portability, care, and retention
-----------------------------------------------------------------

CREATE TABLE IF NOT EXISTS porting_requests (
    porting_request_id      varchar(64) PRIMARY KEY,
    mobile_number_ref       varchar(64) NOT NULL
        REFERENCES mobile_numbers(mobile_number_id),
    port_status             varchar(24) NOT NULL,
    requested_at            timestamptz NOT NULL
);

CREATE TABLE IF NOT EXISTS portability_journeys (
    portability_journey_id  varchar(64) PRIMARY KEY,
    relationship_ref        varchar(64) NOT NULL
        REFERENCES subscriber_relationships(subscriber_relationship_id),
    portability_request_ref varchar(64) NOT NULL UNIQUE
        REFERENCES porting_requests(porting_request_id),
    port_direction          varchar(16) NOT NULL,
    journey_status          varchar(24) NOT NULL,
    journey_started_at      timestamptz NOT NULL,
    journey_completed_at    timestamptz,
    CONSTRAINT port_direction_ck CHECK (port_direction IN ('port_in', 'port_out'))
);

CREATE TABLE IF NOT EXISTS churn_scores (
    churn_score_id          varchar(64) PRIMARY KEY,
    subscriber_relationship_ref varchar(64) NOT NULL
        REFERENCES subscriber_relationships(subscriber_relationship_id),
    churn_probability       numeric(5,4) NOT NULL,
    score_band              varchar(16) NOT NULL,
    scored_at               timestamptz NOT NULL,
    CONSTRAINT churn_probability_ck CHECK (churn_probability BETWEEN 0 AND 1)
);

CREATE TABLE IF NOT EXISTS retention_journeys (
    retention_journey_id       varchar(64) PRIMARY KEY,
    subscriber_relationship_ref varchar(64) NOT NULL
        REFERENCES subscriber_relationships(subscriber_relationship_id),
    retention_churn_score_ref  varchar(64) NOT NULL
        REFERENCES churn_scores(churn_score_id),
    retention_opportunity_ref  varchar(64)
        REFERENCES opportunities(opportunity_id),
    journey_status             varchar(24) NOT NULL,
    retention_reason           varchar(80) NOT NULL,
    save_outcome               varchar(32),
    journey_started_at         timestamptz NOT NULL,
    journey_completed_at       timestamptz,
    CONSTRAINT retention_status_ck
        CHECK (journey_status IN
            ('triggered', 'assessed', 'contacted', 'offered',
             'retained', 'churned', 'suppressed'))
);

CREATE TABLE IF NOT EXISTS billing_enquiries (
    billing_enquiry_id          varchar(64) PRIMARY KEY,
    subscriber_relationship_ref varchar(64) NOT NULL
        REFERENCES subscriber_relationships(subscriber_relationship_id),
    billing_enquiry_invoice_ref varchar(64)
        REFERENCES invoices(invoice_id),
    case_status                 varchar(24) NOT NULL,
    opened_at                   timestamptz NOT NULL,
    resolved_at                 timestamptz
);

-----------------------------------------------------------------
-- Synthetic example records
-----------------------------------------------------------------

INSERT INTO customer_parties (
    customer_party_id, party_role, identity_verified,
    full_name, email, phone
) VALUES (
    'PTY-1001', 'person', true,
    'Sample Customer', 'sample.customer@example.test', '+27820001001'
) ON CONFLICT DO NOTHING;

INSERT INTO subscriber_relationships (
    subscriber_relationship_id, relationship_customer_party_ref,
    relationship_segment, relationship_status, relationship_start_date
) VALUES (
    'REL-1001', 'PTY-1001',
    'consumer-value', 'active', DATE '2025-02-01'
) ON CONFLICT DO NOTHING;

INSERT INTO customer_accounts (
    customer_account_id, relationship_customer_account_ref,
    account_status, payment_type, currency_code
) VALUES (
    'ACC-1001', 'REL-1001',
    'active', 'postpaid', 'ZAR'
) ON CONFLICT DO NOTHING;

INSERT INTO rate_plans (
    rate_plan_id, plan_code, plan_name, recurring_fee, commitment_months
) VALUES (
    'PLAN-5G-20', '5G-20GB', '5G 20 GB Plan', 499.00, 24
) ON CONFLICT DO NOTHING;

INSERT INTO subscriptions (
    subscription_id, relationship_subscription_ref, customer_account_ref,
    subscription_rate_plan_ref, subscription_type, subscription_status,
    contract_start_date, contract_end_date
) VALUES (
    'SUB-1001', 'REL-1001', 'ACC-1001',
    'PLAN-5G-20', 'mobile', 'active',
    DATE '2025-02-01', DATE '2027-01-31'
) ON CONFLICT DO NOTHING;

INSERT INTO subscribers (
    subscriber_id, subscription_subscriber_ref,
    service_status, service_activated_at
) VALUES (
    'LINE-1001', 'SUB-1001',
    'active', TIMESTAMPTZ '2025-02-01 08:30:00+02'
) ON CONFLICT DO NOTHING;

INSERT INTO mobile_numbers (
    mobile_number_id, msisdn, number_status
) VALUES (
    'NUM-1001', '+27820001001', 'allocated'
) ON CONFLICT DO NOTHING;

INSERT INTO sim_profiles (
    sim_profile_id, iccid, imsi, sim_type
) VALUES (
    'SIM-1001', '89271000000000001001', '655010000001001', 'esim'
) ON CONFLICT DO NOTHING;

INSERT INTO devices (
    device_id, device_identifier, device_type,
    device_model, device_eligibility_date
) VALUES (
    'DEV-1001', '356789100001001', 'smartphone',
    'Sample 5G Device', DATE '2026-08-01'
) ON CONFLICT DO NOTHING;

INSERT INTO subscriber_identifiers (
    subscriber_ref, subscriber_mobile_number_ref,
    subscriber_sim_profile_ref, valid_from
) VALUES (
    'LINE-1001', 'NUM-1001',
    'SIM-1001', TIMESTAMPTZ '2025-02-01 08:30:00+02'
) ON CONFLICT DO NOTHING;

INSERT INTO subscriber_devices (
    subscriber_ref, subscriber_device_ref, associated_from
) VALUES (
    'LINE-1001', 'DEV-1001', TIMESTAMPTZ '2025-02-01 08:30:00+02'
) ON CONFLICT DO NOTHING;

INSERT INTO billing_accounts (
    billing_account_id, relationship_billing_account_ref,
    bill_cycle_day, invoice_delivery_channel
) VALUES (
    'BILL-1001', 'REL-1001', 15, 'email'
) ON CONFLICT DO NOTHING;

INSERT INTO charging_accounts (
    charging_account_id, relationship_charging_account_ref,
    balance_amount, data_allowance_mb
) VALUES (
    'CHG-1001', 'REL-1001', 0.00, 20480.00
) ON CONFLICT DO NOTHING;

INSERT INTO opportunities (
    opportunity_id, subscriber_relationship_ref,
    opportunity_subscription_ref, opportunity_rate_plan_ref,
    opportunity_name, opportunity_type, opportunity_amount,
    opportunity_probability, opportunity_status, opportunity_close_date
) VALUES (
    'OPP-1001', 'REL-1001',
    'SUB-1001', 'PLAN-5G-20',
    'Device and plan renewal', 'renewal', 11976.00,
    0.75, 'proposal', DATE '2026-08-15'
) ON CONFLICT DO NOTHING;

INSERT INTO service_orders (
    service_order_id, service_order_type,
    service_order_status, submitted_at
) VALUES (
    'SO-1001', 'modify', 'received',
    TIMESTAMPTZ '2026-08-01 10:00:00+02'
) ON CONFLICT DO NOTHING;

INSERT INTO service_order_handoffs (
    service_order_handoff_id, handoff_opportunity_ref,
    handoff_service_order_ref, handoff_at, handoff_status
) VALUES (
    'HO-1001', 'OPP-1001',
    'SO-1001', TIMESTAMPTZ '2026-08-01 10:00:00+02', 'acknowledged'
) ON CONFLICT DO NOTHING;

INSERT INTO churn_scores (
    churn_score_id, subscriber_relationship_ref,
    churn_probability, score_band, scored_at
) VALUES (
    'CHURN-1001', 'REL-1001',
    0.68, 'high', TIMESTAMPTZ '2026-07-31 23:00:00+02'
) ON CONFLICT DO NOTHING;

INSERT INTO retention_journeys (
    retention_journey_id, subscriber_relationship_ref,
    retention_churn_score_ref, retention_opportunity_ref,
    journey_status, retention_reason, save_outcome,
    journey_started_at
) VALUES (
    'RET-1001', 'REL-1001',
    'CHURN-1001', 'OPP-1001',
    'offered', 'contract_end_and_churn_risk', NULL,
    TIMESTAMPTZ '2026-08-01 09:00:00+02'
) ON CONFLICT DO NOTHING;

-----------------------------------------------------------------
-- Joined CRM view: no operational data is duplicated
-----------------------------------------------------------------

CREATE OR REPLACE VIEW customer_service_360 AS
SELECT
    r.subscriber_relationship_id,
    p.customer_party_id,
    COALESCE(p.full_name, p.organisation_name) AS customer_name,
    a.customer_account_id,
    s.subscription_id,
    s.subscription_status,
    rp.plan_code,
    rp.plan_name,
    line.subscriber_id,
    line.service_status,
    mn.msisdn,
    d.device_model,
    ba.billing_account_id,
    ca.charging_account_id,
    s.contract_end_date
FROM subscriber_relationships r
JOIN customer_parties p
  ON p.customer_party_id = r.relationship_customer_party_ref
JOIN customer_accounts a
  ON a.relationship_customer_account_ref = r.subscriber_relationship_id
JOIN subscriptions s
  ON s.relationship_subscription_ref = r.subscriber_relationship_id
JOIN rate_plans rp
  ON rp.rate_plan_id = s.subscription_rate_plan_ref
JOIN subscribers line
  ON line.subscription_subscriber_ref = s.subscription_id
LEFT JOIN subscriber_identifiers si
  ON si.subscriber_ref = line.subscriber_id
 AND si.valid_to IS NULL
LEFT JOIN mobile_numbers mn
  ON mn.mobile_number_id = si.subscriber_mobile_number_ref
LEFT JOIN subscriber_devices sd
  ON sd.subscriber_ref = line.subscriber_id
 AND sd.associated_to IS NULL
LEFT JOIN devices d
  ON d.device_id = sd.subscriber_device_ref
LEFT JOIN billing_accounts ba
  ON ba.relationship_billing_account_ref = r.subscriber_relationship_id
LEFT JOIN charging_accounts ca
  ON ca.relationship_charging_account_ref = r.subscriber_relationship_id;
