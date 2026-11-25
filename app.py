import argparse
import logging
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Count non-empty lines in a file.")
    parser.add_argument("path", type=Path)
    parser.add_argument("--debug", action="store_true")
    parser.add_argument('--save-to-db', action='store_true')
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(levelname)s %(message)s",
    )
    logger = logging.getLogger(__name__)
    logger.debug("Reading %s", args.path)

    try:
        with args.path.open(encoding="utf-8") as source:
            count = sum(1 for line in source if line.strip())
    except (OSError, UnicodeError) as error:
        logger.error("Cannot read %s: %s", args.path, error)
        return 1

    logger.info("Non-empty lines: %d", count)
    if args.save_to_db:
        import psycopg

        try:
            with psycopg.connect(connect_timeout=5) as connection:
                connection.execute(
                    "INSERT INTO line_counts (file_name, non_empty_lines) VALUES (%s, %s)",
                    (args.path.name, count),
                )
        except psycopg.Error as error:
            logger.error("Cannot save result to PostgreSQL: %s", error)
            return 1

        logger.info("Result saved to PostgreSQL")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
