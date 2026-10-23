# REL — Release and Deployment

Tracks source repositories, builds, change sets, releases, release targets, and the deployments that place a release on a target.

## Concepts

- **SourceRepository** — A version-control repository that holds the source of a software application. Distinct from a supply-chain shipment.
- **Build** — A produced artefact built from a source repository.
- **Release** — A named set of builds and change sets intended for deployment.
- **Deployment** — The placement of a release onto a release target.
- **ReleaseTarget** — The environment a deployment is aimed at. Distinct from a cloud environment, and correlated with it by environment identifier.
- **ChangeSet** — A bounded set of source changes included in a release.

## Taxonomy

- Deployment is a kind of Release activity.
- ReleaseTarget is a kind of Deployment destination.
- Build is a kind of Release artefact.

## Relationships

- Build producedFromSourceRepository SourceRepository (many-to-one)
- Release packagesBuild Build (one-to-many)
- Release includesChangeSet ChangeSet (one-to-many)
- Deployment deploysRelease Release (many-to-one)
- Deployment targetsReleaseTarget ReleaseTarget (many-to-one)

## Attributes

- SourceRepository: sourceRepositoryId (string), repositoryName (string), applicationReference (string)
- Build: buildId (string), buildNumber (string)
- Release: releaseId (string), releaseStatus (string), releaseName (string), applicationReference (string)
- Deployment: deploymentId (string), deployedAt (dateTime)
- ReleaseTarget: releaseTargetId (string), targetName (string), environmentCode (string)
- ChangeSet: changeSetId (string), changeSummary (string)

## Lifecycle

- Release: planned → built → deployed → rolledBack | retired

## Roles

- **Release Manager** (bearer: person) — assembles releases and approves deployments to a release target; permissions: Release:read, Release:write, Deployment:read, Deployment:write, ReleaseTarget:read

## Primary workflow

Commit repository → build → assemble release → choose release target → deploy → roll back or retire
