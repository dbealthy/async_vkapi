import asyncio

import aiohttp

from .exceptions import ApiError, ErrorCodes
from .execute import VkScript

API_V = "5.131"


class VkAPI:
    """Vk API class that allows async request and uses token manager.
    It is recommended to use this class with a context manager
    """

    API_BASE = "https://api.vk.com/method"
    # Maximum 3 requests per secod allowed
    RPS = 3

    def __init__(self, token: str, api_v: str = API_V):
        self.session = aiohttp.ClientSession()
        self.api_v = api_v
        self.token = token

        self.error_handlers = {
            ErrorCodes.TOO_MANY_RPS: try_again_error_handler,
            ErrorCodes.SERVER_ERROR: try_again_error_handler,
        }

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    async def _call(self, method: str, params: dict, token: str):
        """Basic async http call to vk api"""
        url = f"{VkAPI.API_BASE}/{method}"
        params["access_token"] = token
        params["v"] = self.api_v
        async with self.session.post(url, params=params) as response:
            # if response.ok:
            return await response.json()

    async def method(self, method: str, params: dict, raw: bool = False):
        """This is called to use vk methods
        :param method: Method name (look up in vk api docs)
        :param params: Dict that delivers params to that method
        :param raw: Whether return response['response'] or just response with errors
        """
        response = await self._call(method, params, self.token)

        if response.get("error"):
            error = ApiError(self, method, params, raw, response["error"])

            # Run error handler
            if error.code in self.error_handlers:
                response = await self.error_handlers[error.code](error)

                if response is not None:
                    return response

            raise error

        return response if raw else response["response"]

    async def execute(self, vk_script: VkScript, *args, **kwargs):
        """This methods is called to run VkScript with vk execute method
        :param vk_script: Object of type VkScript filled with VkScript code
        :param *args: Arguments that are passed to the object's script
        :param **kwargs: Keyword arguments that are passed to the object's script
        """
        response = await self.method(
            "execute", {"code": vk_script(*args, **kwargs)}, raw=vk_script.return_raw
        )
        return response

    def register_error_handler(self, error_code, handler):
        """Register new error handler with vk_api error_code and your function"""
        if not isinstance(error_code, ErrorCodes):
            raise TypeError(
                f"Error code for handler should be of type: VkErrorCodes, not {type(error_code)}"
            )
        self.error_handlers[error_code] = handler

    async def close(self):
        await self.session.close()


async def http_error_handler(session: aiohttp.ClientSession, response):
    await session.close()
    session = aiohttp.ClientSession()


async def try_again_error_handler(error: ApiError):
    """Handler that reties api call"""
    await asyncio.sleep(1)
    return await error.retry()
