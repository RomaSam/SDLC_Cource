#!/usr/bin/env python3
import json
import re
import sys

PATTERNS = [
    (r'AKIA[0-9A-Z]{16}', 'AWS Access Key ID'),
    (r'sk-ant-[A-Za-z0-9_\-]{32,}', 'Anthropic API Key'),
    (r'sk-[A-Za-z0-9]{32,}', 'OpenAI-style API Key'),
    (r'gh[pousr]_[A-Za-z0-9_]{36,}', 'GitHub Token'),
    (r'(?i)(?:api[_-]?key|api[_-]?secret|access[_-]?token|auth[_-]?token|secret[_-]?key)\s*[=:]\s*[\'"][A-Za-z0-9+/=_\-]{16,}[\'"]', 'API Key/Token assignment'),
    (r'(?i)(?:password|passwd|pwd)\s*[=:]\s*[\'"][^\s\'"]{8,}[\'"]', 'Password assignment'),
]

SAFE_PATTERNS = [
    r'(?i)your[_-]?',
    r'<[A-Z_]{3,}>',
    r'\$\{[A-Z_]+\}',
    r'(?i)example',
    r'(?i)placeholder',
    r'x{4,}',
    r'(?i)changeme',
    r'(?i)dummy',
    r'\*{4,}',
    r'os\.environ',
    r'getenv',
    r'environ\[',
]


def is_safe_value(text):
    return any(re.search(p, text) for p in SAFE_PATTERNS)


def check_secrets(content):
    findings = []
    for pattern, name in PATTERNS:
        for match in re.finditer(pattern, content):
            val = match.group(0)
            if not is_safe_value(val):
                findings.append(name)
                break
    return findings


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    tool = data.get('tool_name', '')
    content = ''

    if tool == 'Write':
        content = data.get('tool_input', {}).get('content', '') or ''
    elif tool == 'Edit':
        content = data.get('tool_input', {}).get('new_string', '') or ''

    if not content:
        sys.exit(0)

    findings = check_secrets(content)

    if findings:
        unique = list(dict.fromkeys(findings))
        print(json.dumps({
            'continue': False,
            'stopReason': f"Potential secret detected ({', '.join(unique)}). Remove hardcoded secrets before writing."
        }))

    sys.exit(0)


if __name__ == '__main__':
    main()
