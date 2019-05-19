import json

def pretty(json_to_print):
    return json.dumps(json_to_print, indent=4, sort_keys=True)

def response_code_valid(code):
    return code >= 200 and code < 300