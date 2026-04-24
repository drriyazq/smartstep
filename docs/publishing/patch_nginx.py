#!/usr/bin/env python3
"""Patch /etc/nginx/sites-enabled/areafair to add static /smartstep/privacy/
and /smartstep/terms/ locations. Writes to /tmp/areafair.new — the caller
copies it into place with sudo.
"""
import sys

CONFIG_PATH = "/etc/nginx/sites-enabled/areafair"
OUT_PATH = "/tmp/areafair.new"

BLOCK = """    location = /smartstep/privacy/ {
        root /home/drriyazq/static-pages;
        try_files /smartstep-privacy.html =404;
        default_type text/html;
    }

    location = /smartstep/terms/ {
        root /home/drriyazq/static-pages;
        try_files /smartstep-terms.html =404;
        default_type text/html;
    }

"""

ANCHOR = "    location /smartstep-admin/"


def main():
    with open(CONFIG_PATH) as f:
        config = f.read()

    if "/smartstep/privacy/" in config:
        # Remove old patch so we can rewrite cleanly
        import re
        config = re.sub(
            r"    location = /smartstep/privacy/ \{.*?    \}\n\n    location = /smartstep/terms/ \{.*?    \}\n\n",
            "",
            config,
            count=1,
            flags=re.DOTALL,
        )

    if ANCHOR not in config:
        print(f"ERROR: anchor {ANCHOR!r} not found in {CONFIG_PATH}")
        return 1

    patched = config.replace(ANCHOR, BLOCK + ANCHOR, 1)
    with open(OUT_PATH, "w") as f:
        f.write(patched)
    print(f"Wrote {OUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
