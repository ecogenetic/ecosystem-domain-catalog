# Software addendum — SRV

## Additional concepts

- **ApplicationComputeHost** — A compute host assigned to run one software application.

## Additional relationships

- ApplicationComputeHost hostsProductEdition ProductEdition (many-to-one)

## Additional roles

- **Application Platform Engineer** — Assigns compute hosts to a product edition. Bearer: person. Permissions: ComputeHost:read, ComputeHost:write, ComputeCluster:read.

## Regulatory notes

- Decommissioning a host that ran customer workloads should retain the image version and the time the host was drained.
