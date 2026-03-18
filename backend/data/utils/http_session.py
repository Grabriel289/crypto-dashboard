"""Shared aiohttp session factory with Windows-compatible DNS resolver.

aiodns is broken on some Windows setups (cannot contact DNS servers).
Force ThreadedResolver so aiohttp uses the OS DNS stack instead.
Also disable strict SSL verification for APIs with cert issues (e.g. Bybit).
"""
import ssl
import aiohttp


def create_session(**kwargs) -> aiohttp.ClientSession:
    """Create an aiohttp ClientSession with ThreadedResolver and relaxed SSL."""
    resolver = aiohttp.ThreadedResolver()
    connector = kwargs.pop("connector", None)
    if connector is None:
        ssl_ctx = ssl.create_default_context()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE
        connector = aiohttp.TCPConnector(resolver=resolver, ssl=ssl_ctx)
    return aiohttp.ClientSession(connector=connector, **kwargs)
