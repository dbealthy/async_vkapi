import enum


class ApiError(Exception):
    def __init__(self, vk_api, method, values, raw, error, message=""):
        self.vk_api = vk_api
        self.method = method
        self.values = values
        self.raw = raw
        self.error = error
        self.message = message
        self.code = ErrorCodes(error["error_code"])
        super().__init__(self.message)

    async def retry(self):
        return await self.vk_api.method(self.method, self.values, raw=False)

    def __str__(self):
        return f"[{self.error['error_code']}] {self.error['error_msg']} {self.message}"


class ErrorCodes(enum.Enum):
    HTTP_ERROR = -1
    UNKNOWN_ERROR = 1
    APP_DOWN = 2
    UNKNOWN_METHOD = 3
    AUTH_FAIL = 5
    TOO_MANY_RPS = 6
    SERVER_ERROR = 10
    TOO_BIG_RESPONSE = 14
    ACCESS_DENIED = 15
    WALL_BANNED_DELETED = 18
    UNAVALIABLE_APP = 28
    METHOD_LIMIT = 29
    PRIVATE_PROFILE = 30


class ErrorGroups:
    WALL_NOT_ACCESSABLE = {
        ErrorCodes.ACCESS_DENIED,
        ErrorCodes.WALL_BANNED_DELETED,
        ErrorCodes.PRIVATE_PROFILE,
    }
