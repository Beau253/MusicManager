# [1.2.0](https://github.com/Beau253/MusicManager/compare/v1.1.0...v1.2.0) (2025-10-28)


### Features

* **spotify:** Add 'fields' option to get_playlist_tracks ([63ff7eb](https://github.com/Beau253/MusicManager/commit/63ff7eb92e49a8daf6c762cce2338f22b56b85bf))

# [1.1.0](https://github.com/Beau253/MusicManager/compare/v1.0.3...v1.1.0) (2025-10-28)


### Bug Fixes

* **api:** correct database connection shutdown in lifespan ([7b4f1d6](https://github.com/Beau253/MusicManager/commit/7b4f1d61658088ab857f3719a0c282f67da7b82f))


### Features

* add lidarr and spotify API endpoints ([d9e879c](https://github.com/Beau253/MusicManager/commit/d9e879c7262f13b5b9a36244ab84f32cf736516a))
* add plex, downloader API endpoints and api launch command ([409fbff](https://github.com/Beau253/MusicManager/commit/409fbffecc6c1e175900701d72975f05ccff901b))
* **api:** convert downloader run to a background task ([746f3d1](https://github.com/Beau253/MusicManager/commit/746f3d1bb7b5e4a2b543d741b5c2c81f53592be6))
* **api:** improve lidarr router with consistent models ([925775c](https://github.com/Beau253/MusicManager/commit/925775c03d54bd8dd3398aaf4fde6e5042133631))
* implement centralized validation service and API endpoint ([8e9eb76](https://github.com/Beau253/MusicManager/commit/8e9eb760852ed8c1fcb29dc51f2b064c9fd2d907))
* implement database logic and API response models ([527a09c](https://github.com/Beau253/MusicManager/commit/527a09c81eb2bdfa63500f9356084714e14e857c))
* implement remaining database placeholder methods ([5521f24](https://github.com/Beau253/MusicManager/commit/5521f24cd20fe37295ec34b1b306041bc0443b69))
* scaffold FastAPI application for web frontend ([56adbf8](https://github.com/Beau253/MusicManager/commit/56adbf81731ea0412b27429b3d54f55197c149b1))

## [1.0.3](https://github.com/Beau253/MusicManager/compare/v1.0.2...v1.0.3) (2025-10-24)


### Bug Fixes

* **deps:** correct format of requirements.txt ([008f519](https://github.com/Beau253/MusicManager/commit/008f5195edda894afcc177a3c46bc95d91adacfd))

## [1.0.2](https://github.com/Beau253/MusicManager/compare/v1.0.1...v1.0.2) (2025-10-24)


### Bug Fixes

* **ci:** add build-essential to Dockerfile for pip compilation ([dcb47c7](https://github.com/Beau253/MusicManager/commit/dcb47c70cdd519fa5c1be28ea7dcaafd408df267))

## [1.0.1](https://github.com/Beau253/MusicManager/compare/v1.0.0...v1.0.1) (2025-10-24)


### Bug Fixes

* **ci:** correct chromaprint package name for ubuntu base image ([903ffe8](https://github.com/Beau253/MusicManager/commit/903ffe8661e675961ab9da6ada95d2eb6fc2b118))

# 1.0.0 (2025-10-24)


### Features

* **ci:** add Dockerfile for containerized builds ([d766ffd](https://github.com/Beau253/MusicManager/commit/d766ffd51ae27e9f6d39e641a0a6ca3c1551c541))
