# Software addendum — SIV

## Additional concepts

- **ApplicationServiceInstance** — A deployed occurrence of a software application. Distinct from the backend service definition.
- **DeployedServiceComponent** — A component running inside an application service instance.

## Additional relationships

- ApplicationServiceInstance containsDeployedServiceComponent DeployedServiceComponent (one-to-many)

## Additional roles

- **Application Inventory Manager** — Records deployed application service instances. Bearer: person. Permissions: ServiceInstance:read, ServiceInstance:write, ServiceComponent:read, ServiceComponent:write.

## Regulatory notes

- A service instance should reference the deployment and the application identifier and should not copy the API contract.
