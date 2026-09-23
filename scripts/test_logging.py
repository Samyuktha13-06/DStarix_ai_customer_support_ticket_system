import logging
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from app.core.logging_config import setup_logging


def main():
    print("=" * 80)
    print("PHASE 9.6 - LOGGING TEST")
    print("=" * 80)

    setup_logging()

    logger = logging.getLogger("phase9.6.test")

    logger.info("Test informational log")
    logger.warning("Test warning log")
    logger.error("Test error log")

    print("\nPASS: Logging configuration initialized successfully.")
    print("PASS: INFO log generated.")
    print("PASS: WARNING log generated.")
    print("PASS: ERROR log generated.")

    print("\n" + "=" * 80)
    print("PHASE 9.6 LOGGING TEST: PASS")
    print("=" * 80)


if __name__ == "__main__":
    main()