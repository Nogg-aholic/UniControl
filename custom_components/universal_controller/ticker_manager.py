"""Ticker management system for Universal Controller entities."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_time_interval

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class TickerManager:
    """Manages execution tickers for Universal Controller entities."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the ticker manager."""
        self.hass = hass
        self._tickers: Dict[str, TickerInstance] = {}
        self._entities: Dict[str, Any] = {}  # Reference to entities

    def register_entity(self, entity_id: str, entity) -> None:
        """Register an entity with the ticker manager."""
        self._entities[entity_id] = entity
        _LOGGER.debug("Registered entity %s with ticker manager", entity_id)

    def unregister_entity(self, entity_id: str) -> None:
        """Unregister an entity from the ticker manager."""
        # Stop any running ticker
        if entity_id in self._tickers:
            self.stop_ticker(entity_id)
        
        # Remove entity reference
        if entity_id in self._entities:
            del self._entities[entity_id]
            
        _LOGGER.debug("Unregistered entity %s from ticker manager", entity_id)

    def start_ticker(self, entity_id: str, interval: int) -> None:
        """Start a ticker for an entity."""
        if interval <= 0:
            _LOGGER.warning("Invalid interval %s for entity %s", interval, entity_id)
            return

        # Stop existing ticker if running
        self.stop_ticker(entity_id)

        # Create new ticker
        ticker = TickerInstance(
            entity_id=entity_id,
            interval=interval,
            hass=self.hass,
            manager=self
        )
        
        self._tickers[entity_id] = ticker
        ticker.start()
        
        _LOGGER.info("Started ticker for entity %s with interval %s seconds", entity_id, interval)

    def stop_ticker(self, entity_id: str) -> None:
        """Stop a ticker for an entity."""
        if entity_id in self._tickers:
            ticker = self._tickers[entity_id]
            ticker.stop()
            del self._tickers[entity_id]
            _LOGGER.info("Stopped ticker for entity %s", entity_id)

    def restart_ticker(self, entity_id: str, interval: int) -> None:
        """Restart a ticker with a new interval."""
        self.stop_ticker(entity_id)
        self.start_ticker(entity_id, interval)

    def is_ticker_running(self, entity_id: str) -> bool:
        """Check if a ticker is running for an entity."""
        return entity_id in self._tickers and self._tickers[entity_id].is_running

    def get_ticker_info(self, entity_id: str) -> Dict[str, Any] | None:
        """Get information about a ticker."""
        if entity_id not in self._tickers:
            return None
        
        ticker = self._tickers[entity_id]
        return {
            "entity_id": entity_id,
            "interval": ticker.interval,
            "is_running": ticker.is_running,
            "last_execution": ticker.last_execution,
            "next_execution": ticker.next_execution,
            "execution_count": ticker.execution_count,
            "error_count": ticker.error_count,
            "last_error": ticker.last_error,
        }

    async def execute_entity(self, entity_id: str) -> None:
        """Execute an entity's code immediately."""
        if entity_id not in self._entities:
            _LOGGER.error("Entity %s not found in ticker manager", entity_id)
            return

        entity = self._entities[entity_id]
        try:
            await entity._execute_typescript()
            _LOGGER.debug("Manual execution completed for entity %s", entity_id)
        except Exception as err:
            _LOGGER.error("Manual execution failed for entity %s: %s", entity_id, err)

    def stop_all_tickers(self) -> None:
        """Stop all running tickers."""
        for entity_id in list(self._tickers.keys()):
            self.stop_ticker(entity_id)
        _LOGGER.info("Stopped all tickers")

    def get_all_ticker_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all tickers."""
        return {
            entity_id: self.get_ticker_info(entity_id)
            for entity_id in self._tickers
        }


class TickerInstance:
    """Individual ticker instance for an entity."""

    def __init__(
        self,
        entity_id: str,
        interval: int,
        hass: HomeAssistant,
        manager: TickerManager
    ) -> None:
        """Initialize the ticker instance."""
        self.entity_id = entity_id
        self.interval = interval
        self.hass = hass
        self.manager = manager
        
        self.is_running = False
        self.last_execution: datetime | None = None
        self.next_execution: datetime | None = None
        self.execution_count = 0
        self.error_count = 0
        self.last_error: str | None = None
        
        self._cancel_callback = None
        self._execution_lock = asyncio.Lock()

    def start(self) -> None:
        """Start the ticker."""
        if self.is_running:
            return

        self.is_running = True
        self.next_execution = datetime.now() + timedelta(seconds=self.interval)
        
        # Schedule periodic execution
        self._cancel_callback = async_track_time_interval(
            self.hass,
            self._execute_callback,
            timedelta(seconds=self.interval)
        )
        
        _LOGGER.debug("Ticker started for entity %s", self.entity_id)

    def stop(self) -> None:
        """Stop the ticker."""
        if not self.is_running:
            return

        self.is_running = False
        
        if self._cancel_callback:
            self._cancel_callback()
            self._cancel_callback = None
        
        self.next_execution = None
        _LOGGER.debug("Ticker stopped for entity %s", self.entity_id)

    @callback
    def _execute_callback(self, _: datetime) -> None:
        """Callback for scheduled execution."""
        if not self.is_running:
            return
        
        # Schedule the execution
        self.hass.async_create_task(self._execute())
        
        # Update next execution time
        self.next_execution = datetime.now() + timedelta(seconds=self.interval)

    async def _execute(self) -> None:
        """Execute the entity's code."""
        async with self._execution_lock:
            try:
                self.last_execution = datetime.now()
                await self.manager.execute_entity(self.entity_id)
                self.execution_count += 1
                self.last_error = None
                
                _LOGGER.debug(
                    "Ticker execution completed for entity %s (count: %d)",
                    self.entity_id,
                    self.execution_count
                )
                
            except Exception as err:
                self.error_count += 1
                self.last_error = str(err)
                
                _LOGGER.error(
                    "Ticker execution failed for entity %s (error count: %d): %s",
                    self.entity_id,
                    self.error_count,
                    err
                )
                
                # Stop ticker if too many consecutive errors
                if self.error_count >= 5:
                    _LOGGER.error(
                        "Stopping ticker for entity %s due to excessive errors",
                        self.entity_id
                    )
                    self.stop()
