# WMS — Warehouse Management System

A Warehouse Management System controls bin locations, pick lists, stock levels, receipts,
and outbound shipments so warehouse staff pick and ship orders accurately and on time.

## Concepts

- **Warehouse** — a physical facility whose storage space is organised into addressable bin locations.
- **BinLocation** — an addressable slot within a warehouse where stock is put away and picked from.
- **StockLevel** — the recorded quantity of an item at a specific bin location.
- **Receipt** — a record of inbound goods received into the warehouse that increases stock levels.
- **PickList** — an ordered set of picking instructions that reserves stock for outbound orders.
- **Shipment** — an outbound consignment that packs and dispatches completed pick lists.

## Taxonomy

- BinLocation is a kind of StorageLocation.
- Receipt is a kind of InboundTransaction.
- Shipment is a kind of OutboundTransaction.
- PickList is a kind of WorkInstruction.

## Attributes

- Warehouse: warehouseCode (string), warehouseName (string)
- BinLocation: binCode (string), zone (string), capacity (integer)
- StockLevel: itemCode (string), quantity (integer), lastCountedAt (dateTime)
- Receipt: receiptNumber (string), receivedAt (dateTime)
- PickList: pickListNumber (string), releasedAt (dateTime), pickListStatus (string)
- Shipment: shipmentNumber (string), dispatchedAt (dateTime)

## Relationships

- Warehouse containsBinLocation BinLocation (one-to-many)
- StockLevel measuredAtBinLocation BinLocation (many-to-one)
- Receipt increasesStockLevel StockLevel (many-to-many)
- PickList reservesStockLevel StockLevel (many-to-many)
- Shipment fulfillsPickList PickList (one-to-one)

## Lifecycle

- PickList: created → in progress → completed → shipped

## Roles

- **PickerRole** (bearer: person) — executes pick lists, confirms picked quantities, and reports shortages; permissions: PickList:read, PickList:write, StockLevel:read, BinLocation:read
- **WarehouseManagerRole** (bearer: person) — configures bin locations, releases pick lists, and oversees receipts and shipments; permissions: Warehouse:read, Warehouse:write, BinLocation:read, BinLocation:write, PickList:read, PickList:write, Receipt:read, Receipt:write, Shipment:read, Shipment:write

## Primary workflow

Receive stock → put away → allocate pick list → pick → pack → ship
