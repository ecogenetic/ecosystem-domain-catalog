# MOB — Mobile Applications

Manages mobile applications, store listings, device platforms, mobile releases, push channels, and store reviews.

## Concepts

- **MobileApplication** — A software application built for a phone or tablet platform.
- **AppStoreListing** — The store listing that publishes a mobile application.
- **DevicePlatform** — A mobile operating platform a mobile application targets.
- **MobileRelease** — A version of a mobile application submitted to or released through a store.
- **PushChannel** — A channel used to notify a mobile application.
- **StoreReview** — The review outcome recorded against an app store listing.

## Taxonomy

- MobileRelease is a kind of Application version.
- AppStoreListing is a kind of Store presence.
- PushChannel is a kind of Notification channel.

## Relationships

- AppStoreListing publishesMobileApplication MobileApplication (many-to-one)
- MobileApplication targetsDevicePlatform DevicePlatform (many-to-one)
- MobileRelease releasesMobileApplication MobileApplication (many-to-one)
- PushChannel notifiesMobileApplication MobileApplication (many-to-one)
- StoreReview reviewsAppStoreListing AppStoreListing (many-to-one)

## Attributes

- MobileApplication: mobileApplicationId (string), applicationName (string), productEditionCode (string)
- AppStoreListing: appStoreListingId (string), listingName (string)
- DevicePlatform: devicePlatformId (string), platformName (string)
- MobileRelease: mobileReleaseId (string), mobileReleaseStatus (string), versionName (string)
- PushChannel: pushChannelId (string), channelName (string)
- StoreReview: storeReviewId (string), reviewOutcome (string)

## Lifecycle

- MobileRelease: built → submitted → released → retired

## Roles

- **Mobile Lead** (bearer: person) — owns mobile applications, store listings, and mobile releases; permissions: MobileApplication:read, MobileApplication:write, MobileRelease:read, MobileRelease:write, AppStoreListing:read

## Primary workflow

Define mobile application → target platform → build release → submit to store → release or retire
