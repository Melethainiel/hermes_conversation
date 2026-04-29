"""Tests for Hermes conversation entity."""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock

from custom_components.hermes_conversation.conversation import HermesConversationAgent
from custom_components.hermes_conversation.const import DOMAIN, CONF_HERMES_URL, CONF_TIMEOUT


@pytest.fixture
def agent():
    """Create a HermesConversationAgent instance."""
    hass = MagicMock()
    hass.data = {
        DOMAIN: {
            "test-entry": {
                CONF_HERMES_URL: "http://localhost:8000/voice",
                CONF_TIMEOUT: 60,
            }
        }
    }
    entry = MagicMock()
    entry.entry_id = "test-entry"
    return HermesConversationAgent(hass, entry)


def test_supported_languages(agent):
    """Test supported languages."""
    assert "fr" in agent.supported_languages
    assert "en" in agent.supported_languages


@pytest.mark.asyncio
async def test_process_success(agent):
    """Test successful conversation processing."""
    user_input = MagicMock()
    user_input.text = "Bonjour"
    user_input.conversation_id = "conv-1"
    user_input.language = "fr"
    user_input.device_id = None

    mock_resp = AsyncMock()
    mock_resp.status = 200
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json = AsyncMock(return_value={"speech": "Salut!", "conversation_id": "conv-1"})
    mock_resp.__aenter__ = AsyncMock(return_value=mock_resp)
    mock_resp.__aexit__ = AsyncMock(return_value=False)

    mock_session = AsyncMock()
    mock_session.post = MagicMock(return_value=mock_resp)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)

    with patch("aiohttp.ClientSession", return_value=mock_session):
        result = await agent.async_process(user_input)

    assert result.response.speech["plain"]["speech"] == "Salut!"


@pytest.mark.asyncio
async def test_process_error(agent):
    """Test error handling when Hermes is unreachable."""
    user_input = MagicMock()
    user_input.text = "Hello"
    user_input.conversation_id = "conv-2"
    user_input.language = "fr"
    user_input.device_id = None

    with patch("aiohttp.ClientSession", side_effect=Exception("Connection refused")):
        result = await agent.async_process(user_input)

    assert "joignable" in result.response.speech["plain"]["speech"]
