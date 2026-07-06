# PLM — Product Lifecycle Management

A Product Lifecycle Management system manages product revisions, bills of material, and
engineering change orders so engineering and manufacturing build from approved product
definitions.

## Concepts

- **Product** — a designed item the business develops, manufactures, and maintains over its lifecycle.
- **Part** — a discrete component or raw material that can appear on a bill of materials.
- **BillOfMaterials** — the structured list of parts and quantities required to build a Product.
- **Revision** — a versioned snapshot of a Product definition at a point in time.
- **EngineeringChange** — a controlled request to modify a product definition, tracked from draft to release.
- **Workflow** — the approval process that governs how an EngineeringChange moves to release.

## Taxonomy

- Part is a kind of Component.
- BillOfMaterials is a kind of ProductStructure.
- EngineeringChange is a kind of ChangeRequest.

## Relationships

- Product definedByBillOfMaterials BillOfMaterials (one-to-many)
- BillOfMaterials composedOfPart Part (many-to-many)
- Revision versionOfProduct Product (many-to-one)
- EngineeringChange modifiesRevision Revision (many-to-one)
- Workflow governsEngineeringChange EngineeringChange (one-to-many)

## Attributes

- Product: productName (string), productNumber (string), description (string)
- Part: partNumber (string), partName (string), unitOfMeasure (string)
- BillOfMaterials: bomName (string), quantity (decimal), effectiveFrom (date)
- Revision: revisionCode (string), releasedAt (dateTime)
- EngineeringChange: changeNumber (string), reason (string), engineeringChangeStatus (string)
- Workflow: workflowName (string), stepCount (integer)

## Lifecycle

- EngineeringChange: draft → review → approved → released

## Roles

- **EngineerRole** (bearer: person) — creates parts, defines bills of material, and drafts engineering changes; permissions: Part:read, Part:write, BillOfMaterials:read, BillOfMaterials:write, EngineeringChange:read, EngineeringChange:write
- **ChangeApproverRole** (bearer: person) — reviews and approves engineering changes and releases revisions; permissions: EngineeringChange:read, EngineeringChange:write, Revision:read, Revision:write

## Primary workflow

Create part → define BOM → submit engineering change → review → release revision
