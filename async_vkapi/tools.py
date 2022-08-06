from .exceptions import ApiError
from .vkfunctions import get_all_items


async def get_all_iter(
    api: API,
    method,
    max_count,
    values=None,
    key="items",
    limit=None,
    stop_fn=None,
    negative_offset=False,
):
    values = values.copy() if values else {}
    values["count"] = max_count

    offset = max_count if negative_offset else 0
    items_count = 0
    count = None

    while True:
        response = await api.execute(
            get_all_items,
            method,
            key,
            values,
            count,
            offset,
            offset_mul=-1 if negative_offset else 1,
        )

        if "execute_errors" in response:
            raise ApiError(
                api,
                method,
                values,
                False,
                response["execute_errors"][0]["error_code"],
                f"Failed to get_all_iter:\nCould not load items: {response['execute_errors']}",
            )

        response = response["response"]

        items = response["items"]
        items_count += len(items)

        # for item in items:
        #     yield item
        yield items

        if not response["more"]:
            break

        if limit and items_count >= limit:
            break

        if stop_fn and stop_fn(items):
            break

        count = response["count"]
        offset = response["offset"]
