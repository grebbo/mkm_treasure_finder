import json


def pretty(json_to_print):
    return json.dumps(json_to_print, indent=4, sort_keys=True)


def response_code_valid(code):
    return 200 <= code < 300
