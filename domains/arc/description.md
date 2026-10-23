# ARC — Architecture Management

Records architecture decisions, system contexts, structural components, interface contracts, viewpoints, and the principles those decisions cite.

## Concepts

- **ArchitectureDecision** — A recorded structural choice, its rationale, and the context it governs.
- **SystemContext** — The bounded system, its users, and the external systems an architecture describes.
- **ArchitectureComponent** — A structural part of a system context. Distinct from a user-interface widget.
- **InterfaceContract** — The agreed boundary through which an architecture component is used.
- **Viewpoint** — A stakeholder view of a system context, such as context, container, or deployment.
- **ArchitecturePrinciple** — A standing rule that architecture decisions are expected to cite.

## Taxonomy

- ArchitectureComponent is a kind of System part.
- InterfaceContract is a kind of Architecture boundary.
- Viewpoint is a kind of Architecture description.

## Relationships

- ArchitectureDecision appliesToSystemContext SystemContext (many-to-one)
- ArchitectureComponent belongsToSystemContext SystemContext (many-to-one)
- InterfaceContract exposesArchitectureComponent ArchitectureComponent (many-to-one)
- Viewpoint describesSystemContext SystemContext (many-to-one)
- ArchitectureDecision citesArchitecturePrinciple ArchitecturePrinciple (many-to-many)

## Attributes

- ArchitectureDecision: architectureDecisionId (string), architectureDecisionStatus (string), decisionTitle (string), rationale (string)
- SystemContext: systemContextId (string), contextName (string)
- ArchitectureComponent: architectureComponentId (string), componentName (string), applicationReference (string)
- InterfaceContract: interfaceContractId (string), contractName (string), apiContractReference (string)
- Viewpoint: viewpointId (string), viewpointName (string)
- ArchitecturePrinciple: architecturePrincipleId (string), principleName (string)

## Lifecycle

- ArchitectureDecision: proposed → accepted → superseded | rejected

## Roles

- **Enterprise Architect** (bearer: person) — owns architecture decisions, system contexts, and interface contracts; permissions: ArchitectureDecision:read, ArchitectureDecision:write, SystemContext:read, SystemContext:write, InterfaceContract:read

## Primary workflow

Describe system context → propose decision → define components → publish interface contracts → accept or supersede
