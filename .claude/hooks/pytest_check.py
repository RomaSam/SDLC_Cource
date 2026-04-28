#!/usr/bin/env python3
import json
import subprocess
import sys

result = subprocess.run(
    [sys.executable, "-m", "pytest", "--tb=short", "-q"],
    capture_output=True,
    text=True,
)

output = (result.stdout + result.stderr).strip()
if output:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": output,
        }
    }))

# Exit code 5 means "no tests collected" — treat as success
sys.exit(0 if result.returncode in (0, 5) else result.returncode)
