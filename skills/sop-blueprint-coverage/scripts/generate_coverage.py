#!/usr/bin/env python3
"""Process one combined SOP/Blueprint page and return one Markdown report."""
DEFAULT_OUTPUT_NAME = "coverage.md"

import sys
sys.dont_write_bytecode = True
from coverage import main


if __name__ == "__main__":
    sys.exit(main())
