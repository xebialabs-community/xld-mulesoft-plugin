# Mulesoft integration for XL Deploy

[![License MIT][license-image]][license-url]
[![standard-readme compliant](https://img.shields.io/badge/readme%20style-standard-blue.svg)](https://github.com/RichardLitt/standard-readme)

## Preface

This document describes the functionality provided by the XL Deploy Cassandra plugin.

See the [XL Deploy reference manual](https://docs.xebialabs.com/xl-Deploy) for background information on XL Deploy and release automation concepts.

## Overview

The `xld-mulesoft-plugin` is an [XL Deploy](https://docs.xebialabs.com/v.9.5/xl-deploy) plugin that enables deploying to Mulesoft.

## Installation

### Building the Plugin

You can use the gradle wrapper to build the plugin. Use the following command to build
using [Gradle](https://gradle.org/):

```
./gradlew clean assemble

```
The built plugin, along with other files from the build, can then be found in the _build_ folder.

### Adding the Plugin to XL Deploy

For the latest instructions on installing XL Deploy plugins, consult the [associated documentation on docs.xebialabs.com](https://docs.xebialabs.com/xl-deploy/how-to/install-or-remove-xl-deploy-plugins.html).

## Contributing

Please review the contributing guidelines for _xebialabs-community_ at [http://xebialabs-community.github.io/](http://xebialabs-community.github.io/)

## License

This community plugin is licensed under the [MIT license][license-url].

See license in [LICENSE.md](LICENSE.md)

[license-image]: https://img.shields.io/badge/license-MIT-yellow.svg
[license-url]: https://opensource.org/licenses/MIT
