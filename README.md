# Blueair Filter Integration for Home Assistant

A simple BlueAir sensor and fan integration for HomeAssistant that supports the [Protect](https://www.blueair.com/us/protect-family.html), [Dust Magnet](https://www.blueair.com/us/dustmagnet-family.html) or [Blue](https://www.blueair.com/us/blue-family.html) product lines. So far, only Blue Pure 311 Max is implemented.

The newer BlueAir devices connect to AWS-hosted cloud services, and the client is ported over from [homebridge-blueair](https://github.com/fjs21/homebridge-blueair/tree/master) by @fjs21.

## Installation

Only manual installation is supported. Until this version is reconciled with [aijayadams/hass-blueair](https://github.com/aijayadams/hass-blueair) and pull requests are merged, I will not be able to publish to HACS.

- Copy custom_components/blueair to your HomeAssistant base config directory (the place where configuration.yaml lives)

## Configuration

The integration is configured through the Home Assistant UI. No need to edit yaml files today.

- Configuration -> Devices and Services -> Add Integration
- Search BlueAir, and enter your username and password

![HASS BlueAir Device](https://raw.githubusercontent.com/aijayadams/hass-blueair/main/device.png)
