"""Config flow for Neerslag Sensor (Buienalarm / Buienradar) integration."""
import logging
from typing import Optional

import voluptuous as vol
from homeassistant.core import callback

from homeassistant import config_entries, core, exceptions
from homeassistant.config_entries import ConfigEntry


from .const import DOMAIN  # pylint:disable=unused-import

_LOGGER = logging.getLogger(__name__)

def _user_data_schema(hass: core.HomeAssistant) -> vol.Schema:
    """Build the initial setup schema.

    Suggest the Home Assistant location rather than a fixed point. The old
    55.000/5.000 default sits in the North Sea, and Buienradar now answers
    anything outside the Netherlands or Belgium with a 404, so accepting the
    suggestion produced a sensor that could never return data.
    """
    lat = hass.config.latitude
    lon = hass.config.longitude

    return vol.Schema({vol.Optional("buienalarm", default=False): bool,
                       vol.Optional("buienalarmLatitude", description={"suggested_value": f"{lat:.3f}"}): str,
                       vol.Optional("buienalarmLongitude", description={"suggested_value": f"{lon:.3f}"}): str,
                       vol.Optional("buienradar", default=False): bool,
                       vol.Optional("buienradarLatitude", description={"suggested_value": f"{lat:.2f}"}): str,
                       vol.Optional("buienradarLongitude", description={"suggested_value": f"{lon:.2f}"}): str,
                       vol.Optional("NeerslagSensorUseHAforLocation", default=True): bool
                       })


async def validate_input(hass: core.HomeAssistant, data):
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    # TODO validate the data can be used to set up a connection.

    # If your PyPI package is not built with async, pass your methods
    # to the executor:
    # await hass.async_add_executor_job(
    #     your_validate_func, data["username"], data["password"]
    # )

    # hub = PlaceholderHub(data["host"])

    # if not await hub.authenticate(data["username"], data["password"]):
    #     raise InvalidAuth

    # If you cannot connect:
    # throw CannotConnect
    # If the authentication is wrong:
    # InvalidAuth

    # Return info that you want to store in the config entry.
    return {"title": "Neerslag"}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Neerslag Sensor (Buienalarm / Buienradar)."""

    VERSION = 1
    # TODO pick one of the available connection classes in homeassistant/config_entries.py
    CONNECTION_CLASS = config_entries.CONN_CLASS_UNKNOWN

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""

        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")
        if self.hass.data.get(DOMAIN):
            return self.async_abort(reason="single_instance_allowed")

        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=_user_data_schema(self.hass)
            )

        errors = {}

        try:
            # info = await validate_input(self.hass, user_input)
            title = "Neerslag App"
            data = user_input
            # _LOGGER.info("Dit wordt nu uitgevoerd...........")
            # _LOGGER.info(data)

        except CannotConnect:
            errors["base"] = "cannot_connect"
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            return self.async_create_entry(title=title, data=data)

        return self.async_show_form(
            step_id="user", data_schema=_user_data_schema(self.hass), errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return OptionsFlowHandler()


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle Neerslag options."""

    def __init__(self) -> None:
        """Initialize options flow."""
        # eigen state kun je die hier initialiseren
        pass

    async def async_step_init(self, user_input=None):

        # _LOGGER.info("HIER>>>")
        # _LOGGER.info(self.config_entry.data.get("buienalarmLatitude"))
        # _LOGGER.info(self.config_entry.data.get("buienalarm"))
        # _LOGGER.info(self.config_entry.data.get("NeerslagSensorUseHAforLocation"))
        data = self.config_entry.data
        lat = self.hass.config.latitude
        lon = self.hass.config.longitude

        testtest = vol.Schema({vol.Optional("buienalarm", default=bool(data.get("buienalarm", False))): bool,
                               vol.Optional("buienalarmLatitude", default=data.get("buienalarmLatitude") or f"{lat:.3f}"): str,
                               vol.Optional("buienalarmLongitude", default=data.get("buienalarmLongitude") or f"{lon:.3f}"): str,
                               vol.Optional("buienradar", default=bool(data.get("buienradar", False))): bool,
                               vol.Optional("buienradarLatitude", default=data.get("buienradarLatitude") or f"{lat:.2f}"): str,
                               vol.Optional("buienradarLongitude", default=data.get("buienradarLongitude") or f"{lon:.2f}"): str,
                               vol.Optional("NeerslagSensorUseHAforLocation", default=bool(data.get("NeerslagSensorUseHAforLocation", True))): bool
                               })

        # _LOGGER.info("----->>>>---------------")
        # _LOGGER.info(self.config_entry.options)
        # _LOGGER.info(self.config_entry.data)
        # _LOGGER.info("------<<<<--------------")
        """Manage the options."""
        if user_input is not None:
            # _LOGGER.info(user_input)
            # _LOGGER.info("<><><><><><><><><><>")
            # self.config_entry.data = user_input
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=testtest,
        )


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(exceptions.HomeAssistantError):
    """Error to indicate there is invalid auth."""
