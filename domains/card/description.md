# CARD — Cards and Payment Instrument Management

Cards and Payment Instrument Management controls payment instruments from issuance through activation, authorisation, tokenisation, clearing, disputes, blocking, replacement, and closure.

## Concepts
- **PaymentInstrument** — a reusable instrument used to initiate a payment.
- **CardInstrument** — a physical or virtual card instrument issued under an account or card agreement.
- **PaymentToken** — a tokenised representation of a payment instrument used in a wallet or merchant context.
- **CardAuthorization** — a decision to approve or decline a requested card transaction amount.
- **CardClearingRecord** — a clearing record received after authorisation for posting and settlement.
- **CardDispute** — a customer or bank dispute raised against a card transaction or clearing record.
- **CardLimit** — a monetary or usage limit applied to a card instrument.
- **CardLifecycleEvent** — an immutable event recording issuance, activation, blocking, replacement, or closure.

## Taxonomy
- CardInstrument is a kind of PaymentInstrument.
- PaymentToken is a kind of PaymentInstrument.

## Relationships
- CardInstrument tokenizedAs PaymentToken (one-to-many)
- CardAuthorization authorizesInstrument CardInstrument (many-to-one)
- CardClearingRecord clearsAuthorization CardAuthorization (many-to-one)
- CardDispute disputesClearingRecord CardClearingRecord (many-to-one)
- CardLimit limitsInstrument CardInstrument (many-to-one)
- CardLifecycleEvent recordsLifecycleFor CardInstrument (many-to-one)

## Attributes
- PaymentInstrument: instrumentReference (string), instrumentStatus (string)
- CardInstrument: maskedPan (string), expiryDate (date)
- PaymentToken: tokenReference (string), tokenStatus (string)
- CardAuthorization: authorizationReference (string), amount (decimal), authorizationStatus (string), authorizedAt (dateTime)
- CardClearingRecord: clearingReference (string), clearingAmount (decimal), clearedAt (dateTime)
- CardDispute: disputeReference (string), disputeStatus (string), disputedAmount (decimal)
- CardLimit: limitType (string), limitAmount (decimal)
- CardLifecycleEvent: eventType (string), occurredAt (dateTime)

## Lifecycle
- CardInstrument: requested → issued → active → blocked → replaced | closed
- CardDispute: opened → investigating → resolved → closed | rejected

## Roles
- **Card Operations Role** (bearer: person) — issues, activates, blocks, replaces, and closes card instruments; permissions: CardInstrument:read, CardInstrument:write, CardLifecycleEvent:read, CardLifecycleEvent:write
- **Dispute Analyst Role** (bearer: person) — investigates and resolves card disputes; permissions: CardDispute:read, CardDispute:write, CardClearingRecord:read

## Primary workflow
Request instrument → issue card → activate → authorise usage → clear transaction → handle dispute if raised → block or replace when required → close instrument
