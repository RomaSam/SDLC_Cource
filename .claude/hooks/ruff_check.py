#!/usr/bin/env python3
import json
import subprocess
import sys


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    file_path = data.get('tool_input', {}).get('file_path', '')

    if not file_path.endswith('.py'):
        sys.exit(0)

    result = subprocess.run(
        ['py', '-3', '-m', 'ruff', 'check', file_path],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        output = (result.stdout or result.stderr).strip()
        print(json.dumps({
            'hookSpecificOutput': {
                'hookEventName': 'PostToolUse',
                'additionalContext': f'ruff check found issues in {file_path}:\n{output}'
            }
        }))

    sys.exit(0)


if __name__ == '__main__':
    main()
