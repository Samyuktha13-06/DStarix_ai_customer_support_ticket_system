from sqlalchemy import inspect
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from app.database.database import engine


def main() -> None:
    inspector = inspect(engine)

    tables = inspector.get_table_names()

    print("Database tables:")

    for table in tables:
        print(f"- {table}")


if __name__ == "__main__":
    main()