# UIA — User Interface Applications

Describes client applications, screens, user-interface components, design systems, navigation flows, and accessibility requirements.

## Concepts

- **ClientApplication** — A user-interface application people use in a browser or desktop client.
- **Screen** — A page or view inside a client application.
- **UiComponent** — A reusable screen widget. Distinct from an architecture component.
- **DesignSystem** — The shared visual and interaction rules a client application adopts.
- **NavigationFlow** — A path that connects screens inside a client application.
- **AccessibilityRequirement** — A requirement a screen must meet so people can use it.

## Taxonomy

- Screen is a kind of Client surface.
- UiComponent is a kind of Screen widget.
- NavigationFlow is a kind of Client interaction.

## Relationships

- Screen belongsToClientApplication ClientApplication (many-to-one)
- UiComponent composesScreen Screen (many-to-many)
- ClientApplication adoptsDesignSystem DesignSystem (many-to-one)
- NavigationFlow connectsScreen Screen (many-to-many)
- AccessibilityRequirement constrainsScreen Screen (many-to-many)

## Attributes

- ClientApplication: clientApplicationId (string), clientApplicationStatus (string), applicationName (string), productEditionCode (string)
- Screen: screenId (string), screenName (string)
- UiComponent: uiComponentId (string), componentName (string)
- DesignSystem: designSystemId (string), systemName (string)
- NavigationFlow: navigationFlowId (string), flowName (string)
- AccessibilityRequirement: accessibilityRequirementId (string), requirementName (string)

## Lifecycle

- ClientApplication: draft → released → deprecated

## Roles

- **UI Lead** (bearer: person) — owns client applications, screens, and accessibility requirements; permissions: ClientApplication:read, ClientApplication:write, Screen:read, Screen:write, AccessibilityRequirement:read, AccessibilityRequirement:write

## Primary workflow

Define client application → adopt design system → compose screens → connect navigation → meet accessibility → release or deprecate
