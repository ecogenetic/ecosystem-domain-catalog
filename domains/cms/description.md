# CMS — Content Management System

A Content Management System lets teams author content, manage pages and media, and publish
through approval workflows so editors ship approved content to the right channels on schedule.

## Concepts

- **Content** — an authored unit of text or structured information that moves through an editorial workflow.
- **Page** — a navigable destination composed of one or more content items.
- **MediaAsset** — an uploaded file such as an image, video, or document referenced by content.
- **Taxonomy** — a controlled vocabulary of terms used to classify content for navigation and search.
- **Workflow** — the approval process that governs how content moves from draft to published.
- **Publication** — a release event that pushes an approved page to a channel at a scheduled time.

## Taxonomy

- Page is a kind of Content Container.
- MediaAsset is a kind of DigitalAsset.
- Publication is a kind of ReleaseEvent.

## Relationships

- Page composedOfContent Content (one-to-many)
- Content referencesMediaAsset MediaAsset (many-to-many)
- Taxonomy classifiesContent Content (one-to-many)
- Workflow governsContent Content (one-to-many)
- Publication releasesPage Page (many-to-one)

## Attributes

- Content: title (string), body (string), contentStatus (string)
- Page: slug (string), pageTitle (string)
- MediaAsset: fileName (string), mimeType (string)
- Taxonomy: taxonomyName (string), termCount (integer)
- Workflow: workflowName (string), approvalSteps (integer)
- Publication: channel (string), publishedAt (dateTime)

## Lifecycle

- Content: draft → review → approved → published

## Roles

- **AuthorRole** (bearer: person) — drafts content, attaches media assets, submits for review; permissions: Content:read, Content:write, MediaAsset:read, MediaAsset:write
- **EditorRole** (bearer: person) — reviews drafts, applies taxonomy terms, approves or returns content; permissions: Content:read, Content:write, Taxonomy:read, Taxonomy:write, Workflow:read
- **PublisherRole** (bearer: person) — schedules and releases approved pages to channels; permissions: Page:read, Page:write, Publication:read, Publication:write

## Primary workflow

Draft content → review → approve → publish page → archive or update
