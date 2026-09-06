[![hacs_badge](https://img.shields.io/badge/HACS-Custom_repository-41BDF5.svg)](https://github.com/hacs/integration)
# Neerslag App

> ### This is a fork
>
> The Neerslag App was created by **[@aex351](https://github.com/aex351)** and the original lives at
> **[aex351/home-assistant-neerslag-app](https://github.com/aex351/home-assistant-neerslag-app)**. All credit for the integration and the
> card belongs there.
>
> This fork exists only to develop and test fixes for
> [issue #96](https://github.com/aex351/home-assistant-neerslag-app/issues/96) (Buienradar rain data unavailable). It is **not** a
> replacement or a competing integration, and it is not listed in the HACS default store.
>
> **If you just want the integration, install the original.** Use this fork only if you
> are deliberately testing these changes.

Neerslag app for Home Assistant. All-in-one package (Sensors + Card).

Display rain forecast using Buienalarm and/or Buienradar sensor data. The Neerslag App (and the sensors) is fully configurable via the Home Assistant interface. 

> This package contains the Neerslag Card. Make sure to uninstall the Neerslag Card package from Home Assistant before using the Neerslag App to avoid unexpected behaviour. This includes manually removing the custom sensors.

## Features
* Everything from the Neerslag Card;
* Built-in Buienalarm and Buienradar sensors;
* Ability to configure this app via the GUI;
* Can use build-in Home Assistant configured location.

![Example](https://github.com/bprins/home-assistant-neerslag-app/raw/main/documentation/example.png)

## Installation overview
1) Install via HACS or manual;
2) Configure the Neerslag App (via interface);
3) Add the Neerslag Card to your dashboard.


## 1a. Install via HACS (recommended)
This fork is not in the HACS default store, so it has to be added as a custom repository.
1) Remove any existing Neerslag App install first — both write to `custom_components/neerslag`;
2) In HACS, open the menu (three dots) and choose `Custom repositories`;
3) Add `https://github.com/bprins/home-assistant-neerslag-app` with type `Integration`;
4) Open the new `Neerslag App` entry and click download;
5) Restart Home Assistant and clear the browser cache;
6) Add the Neerslag App as an Integration in Home Assistant `(menu: settings -> devices & services -> add integration)`;
7) Restart Home Assistant and clear the browser cache (optional).

For updates go to the Community Store (HACS) and click update. Note that HACS decides an
update is available from the `version` in `manifest.json`, so this fork has to bump it for
each change it ships.

## 1b. Manual install
Not recommended, you will need to track updates manually by browsing to the repository;
1) Download the latest release of the Neerslag App from this repository;
2) In Home Assistant, create a folder `config/custom_components`;
3) Add the Neerslag App to the `custom_components` folder;
4) Restart Home Assistant;
5) Add the Neerslag App as an Integration in Home Assistant `(menu: settings -> devices & services -> add integration)`;
6) Restart Home Assistant and clear the browser cache (optional).

For updates, repeat step 1 to 4. Home Assistant will not delete any configuration.

## 2. Configure the Neerslag App (via interface)
The Neerslag App is fully configurable via the interface. 
1) Go to `(menu: settings -> devices & services -> add integration)` and click on `configure`. 
2) Select which sensor you want to use and provide the location data. There is an option to use the built-in Home Assistant location data. If this checkbox is selected, it will override the location settings of the individual sensors.

## 3. Add the Neerslag Card to your Dashboard
1) Go to your dashboard, go to `configure UI`;
2) Click `add card`;
3) Find the Neerslag Card in the list of cards;
4) Add the card and configure the card.

> Note: Due to caching, The Neerslag Card might not be visible in the Home Assistant card selector directly after installing the Neerslag App. Restart Home Assistant and clear the browser cache to resolve this.

### Using one sensor:
```yaml
type: 'custom:neerslag-card'
title: Neerslag
entity: sensor.neerslag_buienalarm_regen_data
```
### Using two sensors:
```yaml
type: 'custom:neerslag-card'
title: Neerslag
entities:
  - sensor.neerslag_buienalarm_regen_data
  - sensor.neerslag_buienradar_regen_data
  ```
> Note: If Home Assistant has not yet received data from the sensors, the card can remain blank.

### Advanced configuration options:
Enable auto zoom to have the graph dynamically zoom in or out depending on the amount of rainfall. 

Note: By default auto zoom is disabled. Which gives the graph a fixed starting position displaying low, medium and heavy rainfall. Auto zoom will continue on extreme rainfall. Before version 2022.07.07.1 this setting was set to true.

```yaml
autozoom: false
```

## Changes in this fork
Everything below is a fix on top of the original; nothing else is intentionally different.

* **Buienradar endpoint.** `gps.buienradar.nl/getrr.php` is retired and now redirects to
  `gadgets.buienradar.nl/data/raintext/`, which serves only the Netherlands and Belgium and
  answers anything else with an HTTP 404 whose body is a sentence of plain English. The old
  code never checked the status and passed that sentence to the card as if it were rain
  data. It now calls the endpoint directly, checks the status, and validates the payload.
* **Error reporting.** A bare `except:` logged every failure as `timeout` at INFO level, so
  no failure was diagnosable. Failures are now logged at warning level with the URL, the
  status, and the response.
* **Availability.** `available` returned only "is this source enabled", so a source switched
  off in the options looked identical to a broken one, while a sensor whose fetch kept
  failing still reported healthy. Repeated failures now mark the sensor unavailable, and a
  disabled source says so in the log.
* **Default coordinates.** The setup form suggested `55.00 / 5.00`, a point in the North Sea,
  which Buienradar now rejects with a 404. It suggests the Home Assistant location instead.
* **Frontend.** The ~240 KB card bundle was served with caching disabled and re-downloaded on
  every page load, which can lose the frontend's 2 second custom-element registration window
  and leave `Custom element doesn't exist: neerslag-card`. It is now cached and busted by
  version. `manifest.json` also declares its `frontend` and `http` dependencies.

## Credits
The Neerslag App and the Neerslag Card are the work of
[@aex351](https://github.com/aex351) — see the original repository at
[aex351/home-assistant-neerslag-app](https://github.com/aex351/home-assistant-neerslag-app). This fork only carries the fixes listed above,
with the intention of contributing them back upstream.
