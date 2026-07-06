# ERP — Enterprise Resource Planning

An Enterprise Resource Planning system integrates procure-to-pay, order-to-cash, inventory,
light manufacturing, and general-ledger accounting so finance and operations work from a single
source of enterprise truth. Purchasing commitments, goods movements, sales fulfilment, and
payments all resolve to balanced journal entries in the ledger, giving controllers a real-time,
auditable view of the business.

## Concepts

### Master data

- **Product** — a good or material the business purchases, stocks, sells, or manufactures, identified by SKU.
- **Vendor** — an external organisation that supplies products or services to the business.
- **Customer** — an organisation or person the business sells products to on agreed terms.
- **Warehouse** — a physical facility where products are received, stored, picked, and shipped.
- **GLAccount** — a general-ledger account in the chart of accounts against which journal lines are posted.
- **CostCenter** — an organisational unit that absorbs costs for management reporting and budget control.
- **TaxCode** — a configured tax treatment (rate and jurisdiction) applied to purchase and sales documents.
- **FiscalPeriod** — an accounting period (month or quarter) that is opened for posting and closed at period end.
- **Ledger** — the financial book of record where journal entries are recorded per fiscal period.

### Procure-to-pay

- **Requisition** — an internal request to purchase products, raised by a department before any vendor commitment.
- **PurchaseOrder** — a formal commitment to buy specified products from a vendor at agreed terms.
- **PurchaseOrderLine** — a single product line on a purchase order with ordered quantity and negotiated price.
- **GoodsReceipt** — the recorded arrival of ordered products at a warehouse, confirming quantities against the purchase order.
- **Invoice** — a vendor's demand for payment, three-way matched against the purchase order and goods receipt before posting.
- **Payment** — a settlement of one or more invoices, executed through a bank and reconciled against the ledger.

### Order-to-cash

- **SalesOrder** — a customer's confirmed commitment to buy specified products at agreed prices.
- **SalesOrderLine** — a single product line on a sales order with ordered quantity and selling price.
- **Shipment** — an outbound delivery that fulfils sales order lines from warehouse stock.
- **CustomerInvoice** — the business's demand for payment issued to a customer for shipped goods.

### Inventory

- **InventoryLevel** — the on-hand, reserved, and available quantity of one product in one warehouse.
- **StockMovement** — a recorded change of stock (receipt, issue, transfer, or adjustment) that keeps inventory levels auditable.

### Manufacturing

- **BillOfMaterials** — the component structure defining which products and quantities are consumed to make a finished product.
- **WorkOrder** — an instruction to manufacture a quantity of a product, consuming components per its bill of materials.

### Financial accounting

- **JournalEntry** — a balanced accounting document (debits equal credits) recorded in the ledger for a fiscal period.
- **JournalLine** — a single debit or credit line of a journal entry, posted to a GL account and optionally a cost center.
- **Budget** — a planned spend amount for a cost center in a fiscal period, monitored against actual postings.

## Taxonomy

- Vendor is a kind of Organisation.
- Customer is a kind of Organisation.
- Requisition is a kind of CommercialDocument.
- PurchaseOrder is a kind of CommercialDocument.
- GoodsReceipt is a kind of CommercialDocument.
- Invoice is a kind of CommercialDocument.
- SalesOrder is a kind of CommercialDocument.
- CustomerInvoice is a kind of CommercialDocument.
- Shipment is a kind of CommercialDocument.
- JournalEntry is a kind of AccountingRecord.
- JournalLine is a kind of AccountingRecord.
- Warehouse is a kind of Facility.
- StockMovement is a kind of InventoryTransaction.

## Attributes

- Product: sku (string), productName (string), unitCost (decimal), listPrice (decimal), productType (string)
- Vendor: vendorName (string), taxId (string), paymentTerms (string), vendorRating (string)
- Customer: customerName (string), customerNumber (string), creditLimit (decimal), customerPaymentTerms (string)
- Warehouse: warehouseCode (string), address (string)
- GLAccount: accountCode (string), accountName (string), accountType (string)
- CostCenter: costCenterCode (string), costCenterName (string)
- TaxCode: taxCodeValue (string), taxRate (decimal), jurisdiction (string)
- FiscalPeriod: periodCode (string), startDate (date), endDate (date), fiscalPeriodStatus (string)
- Ledger: ledgerCode (string), fiscalYear (integer)
- Requisition: requisitionNumber (string), requestedDate (date), justification (string), requisitionStatus (string)
- PurchaseOrder: orderNumber (string), orderDate (date), totalAmount (decimal), currencyCode (string), purchaseOrderStatus (string)
- PurchaseOrderLine: lineNumber (integer), orderedQuantity (decimal), negotiatedPrice (decimal)
- GoodsReceipt: receiptNumber (string), receivedDate (date), receivedQuantity (decimal)
- Invoice: invoiceNumber (string), invoiceDate (date), invoiceAmount (decimal), dueDate (date), invoiceStatus (string)
- Payment: paymentReference (string), paymentDate (date), paymentAmount (decimal), paymentMethod (string), paymentStatus (string)
- SalesOrder: salesOrderNumber (string), salesOrderDate (date), orderTotal (decimal), salesOrderStatus (string)
- SalesOrderLine: salesLineNumber (integer), soldQuantity (decimal), sellingPrice (decimal)
- Shipment: shipmentNumber (string), shippedDate (date), carrier (string), trackingReference (string)
- CustomerInvoice: customerInvoiceNumber (string), issueDate (date), invoiceTotal (decimal), customerInvoiceStatus (string)
- InventoryLevel: onHandQuantity (decimal), reservedQuantity (decimal), availableQuantity (decimal), reorderPoint (decimal)
- StockMovement: movementReference (string), movementType (string), movementQuantity (decimal), movementDate (date)
- BillOfMaterials: bomCode (string), bomVersion (string), outputQuantity (decimal)
- WorkOrder: workOrderNumber (string), plannedQuantity (decimal), completedQuantity (decimal), workOrderStatus (string)
- JournalEntry: journalNumber (string), postingDate (date), journalDescription (string), journalEntryStatus (string)
- JournalLine: debitAmount (decimal), creditAmount (decimal), lineDescription (string)
- Budget: budgetAmount (decimal), committedAmount (decimal), actualAmount (decimal)

## Relationships

- Vendor supplies Product (many-to-many)
- Requisition requestsProduct Product (many-to-many)
- Requisition convertsToPurchaseOrder PurchaseOrder (one-to-one)
- PurchaseOrder orderedFromVendor Vendor (many-to-one)
- PurchaseOrder containsProduct Product (many-to-many)
- PurchaseOrderLine partOfPurchaseOrder PurchaseOrder (many-to-one)
- PurchaseOrderLine forProduct Product (many-to-one)
- GoodsReceipt receiptForPurchaseOrder PurchaseOrder (many-to-one)
- GoodsReceipt receivedAtWarehouse Warehouse (many-to-one)
- Invoice matchedToPurchaseOrder PurchaseOrder (many-to-one)
- Invoice matchedToGoodsReceipt GoodsReceipt (many-to-one)
- Invoice appliesTaxCode TaxCode (many-to-one)
- Invoice postedToLedger Ledger (many-to-one)
- Payment settlesInvoice Invoice (many-to-many)
- Payment settlesCustomerInvoice CustomerInvoice (many-to-many)
- SalesOrder placedByCustomer Customer (many-to-one)
- SalesOrderLine partOfSalesOrder SalesOrder (many-to-one)
- SalesOrderLine forSoldProduct Product (many-to-one)
- Shipment fulfillsSalesOrder SalesOrder (many-to-one)
- Shipment shippedFromWarehouse Warehouse (many-to-one)
- CustomerInvoice billsSalesOrder SalesOrder (many-to-one)
- CustomerInvoice issuedToCustomer Customer (many-to-one)
- CustomerInvoice appliesSalesTaxCode TaxCode (many-to-one)
- Warehouse storesProduct Product (many-to-many)
- InventoryLevel tracksProduct Product (many-to-one)
- InventoryLevel heldInWarehouse Warehouse (many-to-one)
- StockMovement movesProduct Product (many-to-one)
- StockMovement fromWarehouse Warehouse (many-to-one)
- StockMovement toWarehouse Warehouse (many-to-one)
- BillOfMaterials definesProduct Product (many-to-one)
- BillOfMaterials includesComponent Product (many-to-many)
- WorkOrder producesProduct Product (many-to-one)
- WorkOrder consumesBillOfMaterials BillOfMaterials (many-to-one)
- JournalEntry recordedInLedger Ledger (many-to-one)
- JournalEntry belongsToFiscalPeriod FiscalPeriod (many-to-one)
- JournalLine partOfJournalEntry JournalEntry (many-to-one)
- JournalLine postedToGLAccount GLAccount (many-to-one)
- JournalLine allocatedToCostCenter CostCenter (many-to-one)
- Budget plannedForCostCenter CostCenter (many-to-one)
- Budget plannedForFiscalPeriod FiscalPeriod (many-to-one)

## Lifecycle

- Requisition: draft → submitted → approved → converted | rejected
- PurchaseOrder: draft → approved → received → invoiced → closed
- Invoice: received → matched → approved → posted → paid
- Payment: initiated → executed → reconciled
- SalesOrder: draft → confirmed → allocated → shipped → invoiced → closed
- CustomerInvoice: draft → issued → partially_paid → paid | written_off
- WorkOrder: planned → released → in_progress → completed → closed
- JournalEntry: draft → posted → reversed
- FiscalPeriod: open → closed

## Roles

- **BuyerRole** (bearer: person) — creates requisitions and purchase orders, selects vendors, and negotiates line prices; permissions: Requisition:read, Requisition:write, PurchaseOrder:read, PurchaseOrder:write, Vendor:read, Product:read
- **ApproverRole** (bearer: person) — reviews and approves requisitions and purchase orders before commitment; permissions: Requisition:read, Requisition:write, PurchaseOrder:read, PurchaseOrder:write, Vendor:read
- **WarehouseOperatorRole** (bearer: person) — receives goods against purchase orders, picks and ships sales orders, and records stock movements; permissions: GoodsReceipt:read, GoodsReceipt:write, Shipment:read, Shipment:write, StockMovement:read, StockMovement:write, InventoryLevel:read, PurchaseOrder:read, SalesOrder:read
- **SalesClerkRole** (bearer: person) — captures sales orders, allocates stock, and issues customer invoices; permissions: SalesOrder:read, SalesOrder:write, CustomerInvoice:read, CustomerInvoice:write, Customer:read, Product:read, InventoryLevel:read
- **FinanceClerkRole** (bearer: person) — three-way matches vendor invoices, runs payments, and posts entries to the ledger; permissions: Invoice:read, Invoice:write, Payment:read, Payment:write, Ledger:read, Ledger:write, JournalEntry:read, JournalEntry:write, PurchaseOrder:read, GoodsReceipt:read
- **ControllerRole** (bearer: person) — manages the chart of accounts, opens and closes fiscal periods, monitors budgets, and signs off period-end close; permissions: GLAccount:read, GLAccount:write, FiscalPeriod:read, FiscalPeriod:write, Budget:read, Budget:write, JournalEntry:read, Ledger:read, CostCenter:read, CostCenter:write

## Primary workflow

Create requisition → approve → raise purchase order → receive goods → three-way match vendor invoice → pay vendor → post to ledger

Supporting workflows:

- Order-to-cash: capture sales order → allocate stock → ship → issue customer invoice → collect payment → post to ledger
- Inventory control: record stock movements → maintain inventory levels → trigger replenishment at reorder point
- Manufacturing: release work order → consume components per bill of materials → receive finished goods into stock
- Period-end close: post accruals → reconcile subledgers → close fiscal period → report against budget
