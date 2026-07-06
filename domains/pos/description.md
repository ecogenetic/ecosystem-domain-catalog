# POS — Point of Sale System

A Point of Sale System rings up sales, applies tenders, manages register shifts, and prints
receipts so store staff checkout customers quickly with accurate cash control.

## Concepts

- **Register** — a checkout terminal where sale transactions are rung up and tenders taken.
- **Transaction** — a sale rung up at a register, comprising scanned line items settled by tenders.
- **LineItem** — a single scanned product line on a transaction with quantity and price.
- **Tender** — a payment instrument (cash, card, voucher) applied to settle a transaction.
- **Shift** — a cashier's working session on a register, opened and closed with a cash count.
- **Receipt** — the printed or digital proof of purchase documenting a completed transaction.

## Taxonomy

- Transaction is a kind of Sale.
- Tender is a kind of Payment.
- Receipt is a kind of Document.

## Relationships

- Register hostsTransaction Transaction (one-to-many)
- Transaction comprisesLineItem LineItem (one-to-many)
- Tender settlesTransaction Transaction (many-to-one)
- Shift openedOnRegister Register (many-to-one)
- Receipt documentsTransaction Transaction (one-to-one)

## Attributes

- Register: registerNumber (string), storeLocation (string)
- Transaction: transactionNumber (string), totalAmount (decimal), transactedAt (dateTime), transactionStatus (string)
- LineItem: sku (string), quantity (integer), unitPrice (decimal)
- Tender: tenderType (string), tenderAmount (decimal)
- Shift: openedAt (dateTime), closedAt (dateTime), openingFloat (decimal), closingCount (decimal)
- Receipt: receiptNumber (string), printedAt (dateTime)

## Lifecycle

- Transaction: open → items scanned → tendered → receipt printed → reconciled

## Roles

- **CashierRole** (bearer: person) — opens shifts, scans items, applies tenders, and prints receipts; permissions: Transaction:read, Transaction:write, LineItem:read, LineItem:write, Tender:read, Tender:write, Shift:read, Shift:write
- **StoreManagerRole** (bearer: person) — manages registers, reviews shifts, and reconciles cash counts; permissions: Register:read, Register:write, Shift:read, Shift:write, Transaction:read, Receipt:read

## Primary workflow

Open shift → scan items → apply tender → print receipt → close shift and reconcile
