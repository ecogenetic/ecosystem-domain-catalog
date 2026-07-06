# CPQ — Configure, Price, Quote

A Configure, Price, Quote system configures products, applies price rules, bundles offers, and
generates customer quotes so sales reps quote complex deals accurately without spreadsheet errors.

## Concepts

- **Quote** — a priced offer document presented to a customer for a configured set of products.
- **Configuration** — a valid combination of product options and features selected for a deal.
- **PriceRule** — a rule that computes or adjusts prices based on configuration, volume, or customer terms.
- **Bundle** — a predefined grouping of products and options sold together at a combined price.
- **Discount** — a reduction applied to a quote's price, subject to approval thresholds.
- **Approval** — a sign-off decision that authorizes a quote to be sent to the customer.

## Taxonomy

- Quote is a kind of CommercialDocument.
- Bundle is a kind of ProductOffering.
- Discount is a kind of PriceAdjustment.

## Relationships

- Quote containsConfiguration Configuration (one-to-many)
- Configuration selectsBundle Bundle (many-to-one)
- PriceRule pricesConfiguration Configuration (many-to-many)
- Discount adjustsQuote Quote (many-to-one)
- Approval authorizesQuote Quote (many-to-one)

## Attributes

- Quote: quoteNumber (string), totalPrice (decimal), validUntil (date), quoteStatus (string)
- Configuration: configurationName (string), optionCount (integer)
- PriceRule: ruleName (string), ruleExpression (string), priority (integer)
- Bundle: bundleName (string), listPrice (decimal)
- Discount: discountPercent (decimal), discountReason (string)
- Approval: approvedAt (dateTime), approvalDecision (string)

## Lifecycle

- Quote: configured → priced → submitted → approved | rejected

## Roles

- **SalesRepRole** (bearer: person) — configures products, applies discounts, and submits quotes; permissions: Quote:read, Quote:write, Configuration:read, Configuration:write, Discount:read, Discount:write
- **PricingApproverRole** (bearer: person) — reviews submitted quotes and approves or rejects discounts beyond threshold; permissions: Quote:read, Approval:read, Approval:write, PriceRule:read

## Primary workflow

Select product → configure options → apply pricing rules → generate quote → submit for approval
