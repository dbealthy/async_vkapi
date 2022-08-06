from async_vkapi.execute import VkScript

repeat_method = VkScript(
    args=("method", "key", "values"),
    clean_args=("method", "key"),
    return_raw=False,
    code="""
    var params = %(values)s,
        idx = 0,
        responses = [];

    while (idx < params.length) {
        var response = API.%(method)s(params[idx]);
        if (!response) {
            var val = {"%(key)s": params[idx]["%(key)s"]};
            return response;
        }
        response.%(key)s = params[idx]["%(key)s"];
        responses.push(response);
        idx = idx + 1;
    }
    return responses;
    """,
)


get_all_items = VkScript(
    args=("method", "key", "values", "count", "offset", "offset_mul"),
    clean_args=("method", "key", "offset", "offset_mul"),
    return_raw=True,
    code="""
    var params = %(values)s,
        calls = 0,
        items = [],
        count = %(count)s,
        offset = %(offset)s,
        ri;
    while(calls < 25) {
        calls = calls + 1;
        params.offset = offset * %(offset_mul)s;
        var response = API.%(method)s(params),
            new_count = response.count,
            count_diff = (count == null ? 0 : new_count - count);
        if (!response) {
            return {"_error": 1};
        }
        if (count_diff < 0) {
            offset = offset + count_diff;
        } else {
            ri = response.%(key)s;
            items = items + ri.slice(count_diff);
            offset = offset + params.count + count_diff;
            if (ri.length < params.count) {
                calls = 99;
            }
        }
        count = new_count;
        if (count != null && offset >= count) {
            calls = 99;
        }
    };
    return {
        count: count,
        items: items,
        offset: offset,
        more: calls != 99
    };
""",
)
