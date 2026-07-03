"""Config flow for Wikipedia integration."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import (
    DOMAIN,
    DEFAULT_LANGUAGE,
    DEFAULT_UPDATE_INTERVAL,
    DEFAULT_ON_THIS_DAY_COUNT,
    DEFAULT_IN_THE_NEWS_COUNT,
    CONF_LANGUAGE,
    CONF_UPDATE_INTERVAL,
    CONF_FEATURED_ARTICLE,
    CONF_IMAGE_OF_DAY,
    CONF_ON_THIS_DAY,
    CONF_ON_THIS_DAY_COUNT,
    CONF_MOST_READ,
    CONF_IN_THE_NEWS,
    CONF_IN_THE_NEWS_COUNT,
    SUPPORTED_LANGUAGES,
)


def _schema(defaults: dict) -> vol.Schema:
    return vol.Schema({
        vol.Required(CONF_LANGUAGE, default=defaults.get(CONF_LANGUAGE, DEFAULT_LANGUAGE)):
            vol.In(SUPPORTED_LANGUAGES),
        vol.Required(CONF_UPDATE_INTERVAL, default=defaults.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)):
            vol.All(vol.Coerce(int), vol.Range(min=1, max=24)),
        vol.Required(CONF_FEATURED_ARTICLE, default=defaults.get(CONF_FEATURED_ARTICLE, False)):
            bool,
        vol.Required(CONF_IMAGE_OF_DAY, default=defaults.get(CONF_IMAGE_OF_DAY, True)):
            bool,
        vol.Required(CONF_ON_THIS_DAY, default=defaults.get(CONF_ON_THIS_DAY, True)):
            bool,
        vol.Required(CONF_ON_THIS_DAY_COUNT, default=defaults.get(CONF_ON_THIS_DAY_COUNT, DEFAULT_ON_THIS_DAY_COUNT)):
            vol.All(vol.Coerce(int), vol.Range(min=1, max=3)),
        vol.Required(CONF_MOST_READ, default=defaults.get(CONF_MOST_READ, False)):
            bool,
        vol.Required(CONF_IN_THE_NEWS, default=defaults.get(CONF_IN_THE_NEWS, True)):
            bool,
        vol.Required(CONF_IN_THE_NEWS_COUNT, default=defaults.get(CONF_IN_THE_NEWS_COUNT, DEFAULT_IN_THE_NEWS_COUNT)):
            vol.All(vol.Coerce(int), vol.Range(min=1, max=3)),
    })


class WikipediaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")
        if user_input is not None:
            return self.async_create_entry(
                title=f"Wikipedia ({user_input[CONF_LANGUAGE].upper()})",
                data=user_input,
            )
        return self.async_show_form(step_id="user", data_schema=_schema({}))

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return WikipediaOptionsFlow(config_entry)


class WikipediaOptionsFlow(config_entries.OptionsFlow):
    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        defaults = {**self.config_entry.data, **self.config_entry.options}
        return self.async_show_form(step_id="init", data_schema=_schema(defaults))
