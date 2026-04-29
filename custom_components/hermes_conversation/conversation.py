"""Hermes Conversation Entity."""
from __future__ import annotations

import logging

import aiohttp
from homeassistant.components import conversation
from homeassistant.components.conversation import (
    ConversationEntity,
    ConversationInput,
    ConversationResult,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_HERMES_URL, CONF_TIMEOUT, DEFAULT_TIMEOUT, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Hermes conversation entity from config entry."""
    async_add_entities([HermesConversationAgent(hass, entry)])


class HermesConversationAgent(ConversationEntity):
    """Hermes Agent conversation entity."""

    _attr_has_entity_name = True
    _attr_name = "Hermes"

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        self.hass = hass
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_conversation"

    @property
    def supported_languages(self) -> list[str]:
        """Return supported languages."""
        return ["fr", "en"]

    async def async_process(self, user_input: ConversationInput) -> ConversationResult:
        """Process a sentence."""
        config = self.hass.data[DOMAIN][self._entry.entry_id]
        hermes_url = config[CONF_HERMES_URL]
        timeout = config.get(CONF_TIMEOUT, DEFAULT_TIMEOUT)

        payload = {
            "text": user_input.text,
            "conversation_id": user_input.conversation_id or "",
            "language": user_input.language or "fr",
        }
        if user_input.device_id:
            payload["device_id"] = user_input.device_id

        try:
            async with (
                aiohttp.ClientSession() as session,
                session.post(
                    hermes_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=timeout),
                ) as response,
            ):
                response.raise_for_status()
                data = await response.json()
        except Exception:
            _LOGGER.exception("Hermes request failed: %s", hermes_url)
            intent_response = conversation.IntentResponse(
                language=user_input.language or "fr"
            )
            intent_response.async_set_speech("Hermes n'est pas joignable.")
            return ConversationResult(
                response=intent_response,
                conversation_id=user_input.conversation_id,
            )

        speech = data.get("speech") or data.get("response") or "Je n'ai pas de reponse."
        intent_response = conversation.IntentResponse(
            language=user_input.language or "fr"
        )
        intent_response.async_set_speech(speech)
        return ConversationResult(
            response=intent_response,
            conversation_id=data.get("conversation_id") or user_input.conversation_id,
        )
