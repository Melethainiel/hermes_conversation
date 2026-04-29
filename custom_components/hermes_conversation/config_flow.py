"""Config flow for Hermes Conversation Agent."""
from __future__ import annotations

import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import CONF_HERMES_URL, CONF_TIMEOUT, DEFAULT_HERMES_URL, DEFAULT_TIMEOUT, DOMAIN


class HermesConversationConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Hermes Conversation."""

    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            url = user_input[CONF_HERMES_URL]
            # Test connectivity
            try:
                async with (
                    aiohttp.ClientSession() as session,
                    session.get(
                        url.rsplit("/", 1)[0] + "/health",
                        timeout=aiohttp.ClientTimeout(total=5),
                    ) as resp,
                ):
                    if resp.status != 200:
                        errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "cannot_connect"

            if not errors:
                await self.async_set_unique_id("hermes_conversation")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title="Hermes Agent",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HERMES_URL, default=DEFAULT_HERMES_URL): str,
                    vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): int,
                }
            ),
            errors=errors,
        )
