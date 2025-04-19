from pathlib import Path
from pygscholar.api.local_db import LocalNavigator


def main():
    db = Path("local_db.json")
    driver = LocalNavigator(dbname=db)
    driver.populate_author("Henrik Nicolay Finsberg")
    driver.populate_author("Jørgen Dokken")


if __name__ == "__main__":
    main()
