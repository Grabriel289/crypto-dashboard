"""Shared aiohttp session factory with Windows-compatible DNS resolver.

aiodns is broken on some Windows setups (cannot contact DNS servers).
Force ThreadedResolver so aiohttp uses the OS DNS stack instead.
"""
import aiohttp


def create_session(**kwargs) -> aiohttp.ClientSession:
    """Create an aiohttp ClientSession with ThreadedResolver."""
    resolver = aiohttp.ThreadedResolver()
    connector = kwargs.pop("connector", None)
    if connector is None:
        connector = aiohttp.TCPConnector(resolver=resolver)
    return aiohttp.ClientSession(connector=connector, **kwargs)
