# SRV — Server and Compute Management

Tracks compute hosts, clusters, runtimes, server images, capacity pools, and availability targets for software workloads.

## Concepts

- **ComputeHost** — A virtual or physical server that runs software. Distinct from an enterprise physical-asset work order.
- **ComputeCluster** — A managed group of compute hosts that run a workload together.
- **Runtime** — The execution runtime installed on a compute host, such as a container runtime or language runtime.
- **ServerImage** — A versioned image from which a compute host is built.
- **CapacityPool** — A named pool of compute capacity allocated to hosts.
- **AvailabilityTarget** — The availability commitment a compute cluster is expected to meet.

## Taxonomy

- ComputeHost is a kind of Compute resource.
- Runtime is a kind of Execution runtime.
- ServerImage is a kind of Build artefact.

## Relationships

- ComputeHost memberOfComputeCluster ComputeCluster (many-to-one)
- ComputeHost runsRuntime Runtime (many-to-one)
- ComputeHost builtFromServerImage ServerImage (many-to-one)
- CapacityPool allocatesComputeHost ComputeHost (one-to-many)
- AvailabilityTarget coversComputeCluster ComputeCluster (many-to-one)

## Attributes

- ComputeHost: computeHostId (string), computeHostStatus (string), hostName (string), environmentCode (string), applicationReference (string)
- ComputeCluster: computeClusterId (string), clusterName (string)
- Runtime: runtimeId (string), runtimeName (string)
- ServerImage: serverImageId (string), imageName (string)
- CapacityPool: capacityPoolId (string), poolName (string)
- AvailabilityTarget: availabilityTargetId (string), availabilityPercent (decimal)

## Lifecycle

- ComputeHost: provisioned → active → drained → decommissioned

## Roles

- **Platform Engineer** (bearer: person) — provisions hosts, manages images, and drains capacity; permissions: ComputeHost:read, ComputeHost:write, ComputeCluster:read, ServerImage:read, ServerImage:write

## Primary workflow

Define cluster → build image → provision host → run runtime → allocate capacity → drain or decommission
