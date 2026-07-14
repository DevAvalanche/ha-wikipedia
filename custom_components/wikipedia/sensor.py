"""Sensor platform for Wikipedia integration."""
from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    CONF_FEATURED_ARTICLE,
    CONF_IMAGE_OF_DAY,
    CONF_ON_THIS_DAY,
    CONF_MOST_READ,
    CONF_IN_THE_NEWS,
    CONF_DID_YOU_KNOW,
    DATA_FEATURED_ARTICLE,
    DATA_IMAGE_OF_DAY,
    DATA_ON_THIS_DAY,
    DATA_MOST_READ,
    DATA_IN_THE_NEWS,
    DATA_DID_YOU_KNOW,
)
from .coordinator import WikipediaDataUpdateCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: WikipediaDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    opts = {**entry.data, **entry.options}
    entities = []

    if opts.get(CONF_FEATURED_ARTICLE, False):
        entities.append(WikipediaSensor(coordinator, entry, DATA_FEATURED_ARTICLE, "Featured Article", "mdi:book-open-page-variant"))
    if opts.get(CONF_IMAGE_OF_DAY, True):
        entities.append(WikipediaSensor(coordinator, entry, DATA_IMAGE_OF_DAY, "Image of the Day", "mdi:image"))
    if opts.get(CONF_ON_THIS_DAY, True):
        entities.append(WikipediaSensor(coordinator, entry, DATA_ON_THIS_DAY, "On This Day", "mdi:calendar-today"))
    if opts.get(CONF_MOST_READ, False):
        entities.append(WikipediaSensor(coordinator, entry, DATA_MOST_READ, "Most Read", "mdi:trending-up"))
    if opts.get(CONF_IN_THE_NEWS, True):
        entities.append(WikipediaSensor(coordinator, entry, DATA_IN_THE_NEWS, "In the News", "mdi:newspaper"))
    if opts.get(CONF_DID_YOU_KNOW, True):
        entities.append(WikipediaSensor(coordinator, entry, DATA_DID_YOU_KNOW, "Did You Know", "mdi:lightbulb-on"))

    async_add_entities(entities)


class WikipediaSensor(CoordinatorEntity, SensorEntity):
    """A single Wikipedia sensor."""

    def __init__(self, coordinator, entry, key, name, icon):
        super().__init__(coordinator)
        self._key = key
        self._attr_name = f"Wikipedia {name}"
        self._attr_icon = icon
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": f"Wikipedia ({coordinator.language.upper()})",
            "manufacturer": "Wikimedia Foundation",
            "model": "Wikipedia Feed API",
            "entry_type": "service",
        }

    @property
    def _data(self) -> dict | None:
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self._key)

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success and self._data is not None

    @property
    def state(self) -> str | None:
        data = self._data
        if not data:
            return None
        for field in ("title", "top_title", "count", "story"):
            val = data.get(field)
            if val is not None:
                return str(val)[:255]
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return self._data or {}
