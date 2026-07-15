# OMS — Order Management System

An Order Management System ingests orders from channels, allocates inventory, fulfills, and
handles returns so operations teams fulfill omnichannel orders without manual reconciliation.

Industry overlays specialize this domain for vertical terminology and regulatory constraints without forking the base model.

## Concepts

- **Order** — a customer's purchase request received via a channel and tracked through fulfillment.
- **OrderLine** — a single product and quantity within an order, allocated and fulfilled individually.
- **Channel** — a sales touchpoint (web store, marketplace, retail) through which orders are received.
- **Allocation** — a reservation of available inventory against an order line before fulfillment.
- **Fulfillment** — the pick, pack, and ship execution that dispatches an order to the customer.
- **Return** — a customer-initiated reversal of one or more order lines after delivery.

## Taxonomy

- Order is a kind of CommercialDocument.
- OrderLine is a kind of DocumentLine.
- Channel is a kind of SalesTouchpoint.
- Return is a kind of ReverseTransaction.

## Attributes

- Order: orderNumber (string), orderedAt (dateTime), orderTotal (decimal), orderStatus (string)
- OrderLine: lineNumber (integer), productSku (string), quantity (integer), linePrice (decimal)
- Channel: channelName (string), channelType (string)
- Allocation: allocatedQuantity (integer), allocatedAt (dateTime)
- Fulfillment: fulfillmentNumber (string), shippedAt (dateTime), trackingNumber (string)
- Return: returnNumber (string), returnReason (string), receivedBackAt (dateTime)

## Relationships

- Order receivedViaChannel Channel (many-to-one)
- Order composedOfOrderLine OrderLine (one-to-many)
- Allocation reservesForOrderLine OrderLine (one-to-one)
- Fulfillment shipsOrder Order (many-to-one)
- Return reversesOrderLine OrderLine (many-to-one)

## Lifecycle

- Order: received → allocated → fulfilled → shipped | returned

## Roles

- **OrderManagerRole** (bearer: person) — monitors incoming orders, resolves allocation exceptions, and releases fulfillments; permissions: Order:read, Order:write, OrderLine:read, OrderLine:write, Allocation:read, Allocation:write, Fulfillment:read, Fulfillment:write
- **CustomerServiceAgentRole** (bearer: person) — answers order status inquiries and initiates returns on behalf of customers; permissions: Order:read, OrderLine:read, Fulfillment:read, Return:read, Return:write

## Primary workflow

Receive order → allocate inventory → pick and pack → ship → process return if needed
