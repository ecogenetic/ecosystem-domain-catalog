# E-Commerce — Digital Commerce & Retail

A digital commerce system lets shoppers browse products, manage carts, check out, pay, and
track order fulfillment, so purchases complete smoothly with visibility into order status.

## Concepts

- **Customer** — the registered shopper who owns carts, places orders, and writes reviews.
- **Product** — a sellable item with price, description, and stock availability; may be a physical good, a digital product, a service, or a subscription.
- **Category** — a named grouping that organises the catalog for browsing; categories can nest.
- **Cart** — the shopper's working collection of products before checkout.
- **Order** — a confirmed purchase created from a cart at checkout.
- **OrderLine** — one product within an order with its quantity, unit price, and line total.
- **Promotion** — a discount or promotional offer applied to an order at checkout via a code or rule.
- **Payment** — the settlement of an order through a payment method.
- **Review** — a shopper's rating and commentary about a product.
- **Fulfilment** — the delivery of an order: shipping for physical goods, digital delivery or provisioning for digital products and services, or in-store pickup.

## Taxonomy

- Cart is a kind of Container.
- Order is a kind of CommercialTransaction.
- OrderLine is a kind of TransactionLine.

## Relationships

- Cart ownedByCustomer Customer (many-to-one)
- Cart containsProduct Product (many-to-many)
- Order createdFromCart Cart (one-to-one)
- Order placedByCustomer Customer (many-to-one)
- OrderLine partOfOrder Order (many-to-one)
- OrderLine forProduct Product (many-to-one)
- Product inCategory Category (many-to-many)
- Promotion appliedToOrder Order (many-to-many)
- Payment settlesOrder Order (many-to-one)
- Fulfilment shipsOrder Order (one-to-one)
- Review writtenAboutProduct Product (many-to-one)
- Review writtenByCustomer Customer (many-to-one)

## Attributes

- Customer: customerName (string), email (string), registeredAt (dateTime)
- Product: productName (string), price (decimal), stockAvailable (integer), productType (string)
- Category: categoryName (string)
- Cart: createdAt (dateTime), cartTotal (decimal)
- Order: orderNumber (string), orderStatus (string), orderTotal (decimal)
- OrderLine: quantity (integer), unitPrice (decimal), lineTotal (decimal)
- Promotion: promoCode (string), discountValue (decimal), validFrom (date), validTo (date)
- Payment: paymentMethod (string), paidAmount (decimal), paidAt (dateTime)
- Review: rating (integer), comment (string)
- Fulfilment: trackingNumber (string), fulfilmentType (string), shippedAt (dateTime), deliveredAt (dateTime)

## Lifecycle

- Order: cart → paid → fulfilled → delivered

## Roles

- **ShopperRole** (bearer: person) — browses products, manages a cart, places orders, writes reviews; permissions: Product:read, Cart:read, Cart:write, Order:read, Review:read, Review:write
- **StoreAdministratorRole** (bearer: person) — maintains the catalog, monitors orders, and manages fulfilment; permissions: Product:read, Product:write, Order:read, Order:write, Fulfilment:read, Fulfilment:write

## Primary workflow

Browse catalog → add to cart → checkout → pay → fulfill order → confirm delivery
