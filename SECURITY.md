# Security Policy

## Reporting a vulnerability

Do **not** open a public GitHub issue for security-sensitive reports.

Email the maintainers via the contact listed in the GitHub organization
[ecogenetic](https://github.com/ecogenetic) profile, or open a private security advisory
on this repository if enabled.

Please include:

- Description of the issue and impact
- Steps to reproduce (if applicable)
- Affected paths (e.g. overlay that embeds unsafe assumptions)

## Scope

This repository contains domain language, ontologies, and documentation — not runtime
services. Security concerns typically involve:

- Misleading regulatory/compliance language that could cause unsafe generated workflows
- Accidental inclusion of secrets or personal data in commits
- Supply-chain issues in CI workflows

We will acknowledge reports and remediate as appropriate.
