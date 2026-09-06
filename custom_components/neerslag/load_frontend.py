from homeassistant.core import HomeAssistant
from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.const import CONF_ID, CONF_TYPE, CONF_URL
from homeassistant.loader import async_get_integration
from aiohttp import web
import logging
import os
from .const import DOMAIN, FRONTEND_SCRIPT_URL, DATA_EXTRA_MODULE_URL
import time

_LOGGER = logging.getLogger(__name__)

RESOURCE_TYPE_MODULE = "module"


async def _async_register_card_resource(hass: HomeAssistant, url: str) -> bool:
    """Register the card as a Lovelace resource. Returns True on success.

    add_extra_js_url() hands the card to the frontend during its own bootstrap,
    which is also when Home Assistant swaps window.customElements for the
    scoped-custom-element-registry polyfill. A card whose customElements.define()
    runs before that swap registers in the native registry and is invisible to
    the frontend afterwards, which surfaces as the card reporting
    "Custom element doesn't exist: neerslag-card".

    It is a race, not a consistent failure: on a normal load the card bundle and
    the frontend's own core/app bundles finish within about 3ms of each other, so
    which side wins varies per page load. Lovelace loads its resources after the
    frontend is up, so a resource always reaches the registry the frontend reads.
    """
    try:
        from homeassistant.components.lovelace.const import (
            CONF_RESOURCE_TYPE_WS,
            LOVELACE_DATA,
            MODE_STORAGE,
        )
    except ImportError:  # Home Assistant moved these internals
        _LOGGER.debug("Neerslag frontend: Lovelace resource API unavailable")
        return False

    lovelace = hass.data.get(LOVELACE_DATA)

    if lovelace is None:
        _LOGGER.debug("Neerslag frontend: Lovelace is not set up")
        return False

    if lovelace.resource_mode != MODE_STORAGE:
        # YAML-mode resources are read-only; the user maintains that list.
        _LOGGER.debug("Neerslag frontend: Lovelace resources are in YAML mode")
        return False

    resources = lovelace.resources
    await resources.async_get_info()  # loads the collection if it isn't yet

    path = url.split("?")[0]

    for item in resources.async_items() or []:
        if str(item.get(CONF_URL, "")).split("?")[0] != path:
            continue

        # Adopt an entry that already points at the card - including one added
        # by hand - and keep its version query in step with the installed
        # integration instead of adding a second copy.
        if item.get(CONF_URL) != url or item.get(CONF_TYPE) != RESOURCE_TYPE_MODULE:
            await resources.async_update_item(
                item[CONF_ID],
                {CONF_RESOURCE_TYPE_WS: RESOURCE_TYPE_MODULE, CONF_URL: url},
            )
            _LOGGER.info("Neerslag frontend: updated Lovelace resource to %s", url)

        return True

    await resources.async_create_item(
        {CONF_RESOURCE_TYPE_WS: RESOURCE_TYPE_MODULE, CONF_URL: url}
    )
    _LOGGER.info("Neerslag frontend: registered Lovelace resource %s", url)

    return True


async def setup_view(hass: HomeAssistant):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    path_to_file = os.path.join(
        dir_path,
        "home-assistant-neerslag-card",
        "neerslag-card.js",
    )

    should_cache = False

    _LOGGER.debug(
        "Neerslag frontend: registering static path %s -> %s",
        FRONTEND_SCRIPT_URL,
        path_to_file,
    )

    await hass.http.async_register_static_paths(
        [
            StaticPathConfig(
                FRONTEND_SCRIPT_URL,
                path_to_file,
                should_cache,
            )
        ]
    )

    # The version query gives the browser a fresh module when the integration is
    # updated; the static route matches on path, so it is ignored server-side.
    integration = await async_get_integration(hass, DOMAIN)
    version = str(integration.version) if integration.version else str(int(time.time()))
    module_url = f"{FRONTEND_SCRIPT_URL}?v={version}"

    if await _async_register_card_resource(hass, module_url):
        return

    # Fall back to the extra module URL when there is no storage-mode Lovelace to
    # register a resource with. This is the racy path described above, but losing
    # the race some of the time beats never loading the card at all.
    _LOGGER.debug(
        "Neerslag frontend: falling back to extra JS module URL %s",
        FRONTEND_SCRIPT_URL,
    )

    add_extra_js_url(hass, FRONTEND_SCRIPT_URL, es5=False)
