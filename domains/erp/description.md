# ERP — Enterprise Resource Planning

An Enterprise Resource Planning system manages products, vendors, purchase orders, inventory,
and financial postings so finance and operations work from a single source of enterprise truth.

## Concepts

- **Product** — a good or material the business purchases, stocks, or sells, identified by SKU.
- **Vendor** — an external organisation that supplies products or services to the business.
- **PurchaseOrder** — a formal commitment to buy specified products from a vendor at agreed terms.
- **Invoice** — a vendor's demand for payment, matched against a purchase order before posting.
- **Warehouse** — a physical facility where purchased products are received and stored.
- **Ledger** — the financial book of record where matched invoices are posted as accounting entries.

## Taxonomy

- Vendor is a kind of Organisation.
- PurchaseOrder is a kind of CommercialDocument.
- Invoice is a kind of CommercialDocument.
- Warehouse is a kind of Facility.

## Attributes

- Product: sku (string), productName (string), unitCost (decimal)
- Vendor: vendorName (string), taxId (string), paymentTerms (string)
- PurchaseOrder: orderNumber (string), orderDate (date), totalAmount (decimal), purchaseOrderStatus (string)
- Invoice: invoiceNumber (string), invoiceDate (date), invoiceAmount (decimal)
- Warehouse: warehouseCode (string), address (string)
- Ledger: ledgerCode (string), fiscalYear (integer)

## Relationships

- Vendor supplies Product (many-to-many)
- PurchaseOrder orderedFromVendor Vendor (many-to-one)
- PurchaseOrder containsProduct Product (many-to-many)
- Invoice matchedToPurchaseOrder PurchaseOrder (many-to-one)
- Warehouse storesProduct Product (many-to-many)
- Invoice postedToLedger Ledger (many-to-one)

## Lifecycle

- PurchaseOrder: draft → approved → received → invoiced → closed

## Roles

- **BuyerRole** (bearer: person) — creates requisitions and purchase orders, selects vendors; permissions: PurchaseOrder:read, PurchaseOrder:write, Vendor:read, Product:read
- **FinanceClerkRole** (bearer: person) — matches invoices to purchase orders and posts entries to the ledger; permissions: Invoice:read, Invoice:write, Ledger:read, Ledger:write, PurchaseOrder:read
- **ApproverRole** (bearer: person) — reviews and approves purchase orders before commitment; permissions: PurchaseOrder:read, PurchaseOrder:write, Vendor:read

## Primary workflow

Create requisition → approve purchase order → receive goods → match invoice → post to ledger
