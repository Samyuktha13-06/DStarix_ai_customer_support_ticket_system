from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from app.database.database import Base, engine
from app.database import models


def main() -> None:
    Path("data").mkdir(
        parents=True,
        exist_ok=True,
    )

    Base.metadata.create_all(bind=engine)

    print("Customer Support database initialized successfully.")


if __name__ == "__main__":
    main()