# E-Commerce — Digital Commerce & Retail

A digital commerce system lets shoppers browse products, manage carts, check out, pay, and
track order fulfillment, so purchases complete smoothly with visibility into order status.

## Concepts

- **Product** — a sellable item with price, description, and stock availability.
- **Cart** — the shopper's working collection of products before checkout.
- **Order** — a confirmed purchase created from a cart at checkout.
- **Payment** — the settlement of an order through a payment method.
- **Review** — a shopper's rating and commentary about a product.
- **Fulfilment** — the picking, packing, shipping, and delivery of an order.

## Taxonomy

- Cart is a kind of Container.
- Order is a kind of CommercialTransaction.

## Relationships

- Cart containsProduct Product (many-to-many)
- Order createdFromCart Cart (one-to-one)
- Payment settlesOrder Order (many-to-one)
- Fulfilment shipsOrder Order (one-to-one)
- Review writtenAboutProduct Product (many-to-one)

## Attributes

- Product: productName (string), price (decimal), stockAvailable (integer)
- Cart: createdAt (dateTime), cartTotal (decimal)
- Order: orderNumber (string), orderStatus (string), orderTotal (decimal)
- Payment: paymentMethod (string), paidAmount (decimal), paidAt (dateTime)
- Review: rating (integer), comment (string)
- Fulfilment: trackingNumber (string), shippedAt (dateTime), deliveredAt (dateTime)

## Lifecycle

- Order: cart → paid → fulfilled → delivered

## Roles

- **ShopperRole** (bearer: person) — browses products, manages a cart, places orders, writes reviews; permissions: Product:read, Cart:read, Cart:write, Order:read, Review:read, Review:write
- **StoreAdministratorRole** (bearer: person) — maintains the catalog, monitors orders, and manages fulfilment; permissions: Product:read, Product:write, Order:read, Order:write, Fulfilment:read, Fulfilment:write

## Primary workflow

Browse catalog → add to cart → checkout → pay → fulfill order → confirm delivery
