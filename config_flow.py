import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN

class EldomConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Eldom Smart Boiler."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            boiler_id = user_input["boiler_id"]

            await self.async_set_unique_id(boiler_id)
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=f"Eldom Boiler {boiler_id}",
                data={"boiler_id": boiler_id}
            )

        data_schema = vol.Schema({
            vol.Required("boiler_id"): str,
        })

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )
