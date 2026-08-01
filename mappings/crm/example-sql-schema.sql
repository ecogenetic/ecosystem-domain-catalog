-- ============================================================================
-- mappings/crm/example-sql-schema.sql
--
-- Example legacy CRM database schema demonstrating how common SQL tables,
-- columns, and foreign keys map to the canonical CRM ontology.
--
-- This is a product-agnostic reference schema. Real-world systems will vary
-- in naming conventions, but the structural patterns (PKs, FKs, status enums,
-- monetary/decimal columns, datetime columns) are nearly universal.
-- ============================================================================

-- ---------------------------------------------------------------------------
-- 1. CUSTOMER MASTER
-- ---------------------------------------------------------------------------

CREATE TABLE accounts (
    account_id       VARCHAR(36) PRIMARY KEY,  -- :Account / :id
    account_name     VARCHAR(255) NOT NULL,    -- :accountName
    industry         VARCHAR(100),             -- :industry
    annual_revenue   DECIMAL(15,2),            -- :annualRevenue
    website          VARCHAR(255),             -- :website
    account_type     VARCHAR(50),              -- :accountType (prospect, customer, partner)
    employee_count   INTEGER,                  -- :employeeCount
    territory_id     VARCHAR(36),              -- :assignedToTerritory (FK → territories)
    created_at       TIMESTAMP DEFAULT NOW(),  -- :createdAt
    updated_at       TIMESTAMP DEFAULT NOW()
);

CREATE TABLE territories (
    territory_id     VARCHAR(36) PRIMARY KEY,  -- :Territory / :id
    territory_name   VARCHAR(100) NOT NULL,    -- :territoryName
    region           VARCHAR(50)               -- :region
);

CREATE TABLE contacts (
    contact_id       VARCHAR(36) PRIMARY KEY,  -- :Contact / :id
    account_id       VARCHAR(36) NOT NULL,     -- :belongsToAccount (FK → accounts)
    full_name        VARCHAR(255) NOT NULL,    -- :fullName
    email            VARCHAR(255),             -- :email
    phone            VARCHAR(50),              -- :phone
    job_title        VARCHAR(100),             -- :jobTitle
    department       VARCHAR(100),             -- :department
    marketing_opt_in BOOLEAN DEFAULT FALSE,    -- :marketingOptIn
    preferred_channel VARCHAR(20)              -- :preferredChannel (email, phone, sms)
);

-- ---------------------------------------------------------------------------
-- 2. MARKETING & LEAD MANAGEMENT
-- ---------------------------------------------------------------------------

CREATE TABLE campaigns (
    campaign_id          VARCHAR(36) PRIMARY KEY, -- :Campaign / :id
    campaign_name        VARCHAR(255) NOT NULL,   -- :campaignName
    campaign_type        VARCHAR(50),              -- :campaignType (event, email, ads, webinar)
    campaign_start_date  DATE,                     -- :campaignStartDate
    campaign_end_date    DATE,                     -- :campaignEndDate
    budgeted_cost        DECIMAL(12,2),            -- :budgetedCost
    campaign_status      VARCHAR(20) DEFAULT 'planned' -- :campaignStatus (planned, active, completed)
);

CREATE TABLE leads (
    lead_id          VARCHAR(36) PRIMARY KEY,   -- :Lead / :id
    campaign_id      VARCHAR(36),                -- :generatesLead (FK → campaigns)
    lead_source      VARCHAR(50) NOT NULL,       -- :leadSource
    captured_at      TIMESTAMP DEFAULT NOW(),    -- :capturedAt
    company          VARCHAR(255),               -- :company
    lead_score       INTEGER DEFAULT 0,          -- :leadScore
    lead_status      VARCHAR(20) DEFAULT 'new',  -- :leadStatus (new, contacted, qualified, converted, disqualified)
    -- Conversion foreign keys (populated when lead is qualified)
    opportunity_id   VARCHAR(36),                -- :convertsToOpportunity (FK → opportunities)
    contact_id       VARCHAR(36),                -- :convertsToContact (FK → contacts)
    account_id       VARCHAR(36)                 -- :convertsToAccount (FK → accounts)
);

-- ---------------------------------------------------------------------------
-- 3. SALES EXECUTION
-- ---------------------------------------------------------------------------

CREATE TABLE pipelines (
    pipeline_id      VARCHAR(36) PRIMARY KEY,   -- :Pipeline / :id
    pipeline_name    VARCHAR(100) NOT NULL,      -- :pipelineName
    stage_count      INTEGER DEFAULT 0           -- :stageCount
);

CREATE TABLE pipeline_stages (
    stage_id           VARCHAR(36) PRIMARY KEY,  -- :PipelineStage / :id
    pipeline_id        VARCHAR(36) NOT NULL,     -- :partOfPipeline (FK → pipelines)
    stage_name         VARCHAR(50) NOT NULL,     -- :stageName
    stage_order        INTEGER NOT NULL,         -- :stageOrder
    default_probability DECIMAL(3,2) DEFAULT 0.5 -- :defaultProbability (0.00 - 1.00)
);

CREATE TABLE products (
    product_id       VARCHAR(36) PRIMARY KEY,   -- :Product / :id
    product_code     VARCHAR(50) NOT NULL,       -- :productCode
    product_name     VARCHAR(255) NOT NULL,      -- :productName
    list_price       DECIMAL(12,2)               -- :listPrice
);

CREATE TABLE opportunities (
    opportunity_id       VARCHAR(36) PRIMARY KEY, -- :Opportunity / :id
    opportunity_name     VARCHAR(255) NOT NULL,    -- :opportunityName
    account_id           VARCHAR(36) NOT NULL,     -- :pursuedWithAccount (FK → accounts)
    contact_id           VARCHAR(36),              -- :hasPrimaryContact (FK → contacts)
    pipeline_id          VARCHAR(36) NOT NULL,     -- :progressesThroughPipeline (FK → pipelines)
    stage_id             VARCHAR(36) NOT NULL,     -- :atPipelineStage (FK → pipeline_stages)
    campaign_id          VARCHAR(36),              -- :influencedByCampaign (FK → campaigns)
    amount               DECIMAL(15,2) NOT NULL,   -- :amount
    probability          DECIMAL(3,2),             -- :probability (0.00 - 1.00)
    close_date           DATE,                     -- :closeDate
    opportunity_status   VARCHAR(20) DEFAULT 'lead' -- :opportunityStatus (lead, qualified, proposal, won, lost)
);

-- Many-to-many: opportunities ↔ products (via junction table)
CREATE TABLE opportunity_products (
    opportunity_id   VARCHAR(36) NOT NULL,        -- :includesProduct
    product_id       VARCHAR(36) NOT NULL,
    PRIMARY KEY (opportunity_id, product_id)
);

-- ---------------------------------------------------------------------------
-- 4. QUOTES
-- ---------------------------------------------------------------------------

CREATE TABLE quotes (
    quote_id           VARCHAR(36) PRIMARY KEY,   -- :Quote / :id
    quote_number       VARCHAR(50) NOT NULL,       -- :quoteNumber
    opportunity_id     VARCHAR(36) NOT NULL,       -- :quotesOpportunity (FK → opportunities)
    quote_date         DATE,                       -- :quoteDate
    valid_until        DATE,                       -- :validUntil
    quote_total        DECIMAL(15,2),              -- :quoteTotal
    quote_status       VARCHAR(20) DEFAULT 'draft' -- :quoteStatus (draft, presented, accepted, rejected, expired)
);

CREATE TABLE quote_lines (
    quote_line_id      VARCHAR(36) PRIMARY KEY,   -- :QuoteLine / :id
    quote_id           VARCHAR(36) NOT NULL,       -- :partOfQuote (FK → quotes)
    product_id         VARCHAR(36) NOT NULL,       -- :forQuotedProduct (FK → products)
    quoted_quantity    DECIMAL(10,2) NOT NULL,     -- :quotedQuantity
    quoted_unit_price  DECIMAL(12,2) NOT NULL,     -- :quotedUnitPrice
    discount_percent   DECIMAL(5,2) DEFAULT 0.00   -- :discountPercent
);

-- ---------------------------------------------------------------------------
-- 5. CONTRACTS
-- ---------------------------------------------------------------------------

CREATE TABLE contracts (
    contract_id              VARCHAR(36) PRIMARY KEY, -- :Contract / :id
    contract_number          VARCHAR(50) NOT NULL,    -- :contractNumber
    opportunity_id           VARCHAR(36) NOT NULL,    -- :resultsFromOpportunity (FK → opportunities)
    account_id               VARCHAR(36) NOT NULL,    -- :governsAccount (FK → accounts)
    contract_start           DATE NOT NULL,           -- :contractStart
    contract_end             DATE NOT NULL,           -- :contractEnd
    contract_value           DECIMAL(15,2) NOT NULL,  -- :contractValue
    contract_status          VARCHAR(20) DEFAULT 'draft', -- :contractStatus (draft, active, expired, terminated)
    renewal_opportunity_id   VARCHAR(36)             -- :renewsIntoOpportunity (FK → opportunities)
);

-- ---------------------------------------------------------------------------
-- 6. FORECASTING
-- ---------------------------------------------------------------------------

CREATE TABLE forecasts (
    forecast_id      VARCHAR(36) PRIMARY KEY,   -- :Forecast / :id
    territory_id     VARCHAR(36) NOT NULL,       -- :coversTerritory (FK → territories)
    forecast_period  VARCHAR(20) NOT NULL,       -- :forecastPeriod (e.g., '2026-Q3')
    forecast_amount  DECIMAL(15,2) NOT NULL,     -- :forecastAmount
    commit_amount    DECIMAL(15,2) NOT NULL,     -- :commitAmount
    best_case_amount DECIMAL(15,2) NOT NULL      -- :bestCaseAmount
);

-- ---------------------------------------------------------------------------
-- 7. SERVICE & ENGAGEMENT
-- ---------------------------------------------------------------------------

CREATE TABLE activities (
    activity_id          VARCHAR(36) PRIMARY KEY, -- :Activity / :id
    activity_type        VARCHAR(50) NOT NULL,     -- :activityType (call, email, meeting, note)
    occurred_at          TIMESTAMP DEFAULT NOW(),  -- :occurredAt
    summary              TEXT,                      -- :summary
    -- Polymorphic foreign keys (only one is typically populated per row)
    opportunity_id       VARCHAR(36),               -- :loggedAgainstOpportunity (FK → opportunities)
    case_id              VARCHAR(36),               -- :loggedAgainstCase (FK → cases)
    contact_id           VARCHAR(36)                -- :involvesContact (FK → contacts)
);

CREATE TABLE cases (
    case_id          VARCHAR(36) PRIMARY KEY,   -- :Case / :id
    case_number      VARCHAR(50) NOT NULL,       -- :caseNumber
    contact_id       VARCHAR(36) NOT NULL,       -- :raisedByContact (FK → contacts)
    account_id       VARCHAR(36) NOT NULL,       -- :filedAgainstAccount (FK → accounts)
    product_id       VARCHAR(36),                -- :aboutProduct (FK → products)
    subject          VARCHAR(255) NOT NULL,      -- :subject
    priority         VARCHAR(20) DEFAULT 'medium', -- :priority (low, medium, high, critical)
    opened_at        TIMESTAMP DEFAULT NOW(),    -- :openedAt
    resolved_at      TIMESTAMP,                  -- :resolvedAt
    sla_due_at       TIMESTAMP,                  -- :slaDueAt
    escalated        BOOLEAN DEFAULT FALSE,      -- :escalated
    case_status      VARCHAR(30) DEFAULT 'new'   -- :caseStatus (new, in_progress, waiting_on_customer, resolved, closed)
);

-- ============================================================================
-- INDEXES (for performance on common FK lookups)
-- ============================================================================
CREATE INDEX idx_contacts_account ON contacts(account_id);
CREATE INDEX idx_opportunities_account ON opportunities(account_id);
CREATE INDEX idx_opportunities_stage ON opportunities(stage_id);
CREATE INDEX idx_quotes_opportunity ON quotes(opportunity_id);
CREATE INDEX idx_quote_lines_quote ON quote_lines(quote_id);
CREATE INDEX idx_contracts_opportunity ON contracts(opportunity_id);
CREATE INDEX idx_contracts_account ON contracts(account_id);
CREATE INDEX idx_forecasts_territory ON forecasts(territory_id);
CREATE INDEX idx_cases_contact ON cases(contact_id);
CREATE INDEX idx_cases_account ON cases(account_id);
CREATE INDEX idx_activities_opportunity ON activities(opportunity_id);
CREATE INDEX idx_activities_case ON activities(case_id);