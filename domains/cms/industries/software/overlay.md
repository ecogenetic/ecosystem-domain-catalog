# Software addendum — CMS

## Additional concepts

- **DeveloperDocContent** — Content that explains a software product or API. Distinct from a configuration item.
- **ApiDocumentationPage** — A page that publishes developer documentation for an API.

## Additional relationships

- ApiDocumentationPage publishesDeveloperDoc DeveloperDocContent (many-to-one)

## Additional roles

- **Developer Doc Author** — Writes and publishes product and API documentation. Bearer: person. Permissions: Content:read, Content:write, Page:read, Page:write.

## Regulatory notes

- Published API documentation should identify the API contract version it describes.
