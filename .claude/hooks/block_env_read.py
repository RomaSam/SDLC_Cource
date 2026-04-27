#!/usr/bin/env python3
import json
import os
import re
import sys

_BLOCKED = re.compile(r'^\.env($|\.[^.]+$)', re.IGNORECASE)
_SAFE = re.compile(r'^\.env\.(example|sample|template|dist)$', re.IGNORECASE)

BLOCKED_TOOLS = {
    'Read': lambda d: d.get('tool_input', {}).get('file_path', ''),
    'Edit': lambda d: d.get('tool_input', {}).get('file_path', ''),
}


def is_env_file(path):
    name = os.path.basename(path)
    return bool(_BLOCKED.match(name)) and not bool(_SAFE.match(name))


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    tool = data.get('tool_name', '')
    extractor = BLOCKED_TOOLS.get(tool)
    if not extractor:
        sys.exit(0)

    path = extractor(data)
    if path and is_env_file(path):
        print(json.dumps({
            'continue': False,
            'stopReason': 'Access to env. is restricted by Policy'
        }))

    sys.exit(0)


if __name__ == '__main__':
    main()
