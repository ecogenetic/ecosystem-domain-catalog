# Software addendum — GRC

## Additional concepts

- **SecurityControl** — A control that protects software, customer data, or the production platform.
- **SocEvidence** — Evidence collected to show a security control operated for a stated period.

## Additional relationships

- SocEvidence evidencesSecurityControl SecurityControl (many-to-one)

## Additional roles

- **Security Compliance Officer** — Maps security controls and collects operating evidence. Bearer: person. Permissions: Control:read, Control:write, Evidence:read, Evidence:write, Policy:read.

## Regulatory notes

- Control evidence should name the system or product edition it covers and the period it covers.
