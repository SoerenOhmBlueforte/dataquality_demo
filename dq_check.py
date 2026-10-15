import argparse
import csv
from pathlib import Path
import sys


def check_csv(path: Path) -> list[str]:
    problems = []
    seen_ids = set()
    with path.open(encoding="utf-8", newline="") as source:
        reader = csv.reader(source)
        if next(reader, None) != ["id", "name", "age"]:
            raise ValueError("Header muss exakt id,name,age sein")

        for number, row in enumerate(reader, start=1):
            if len(row) != 3:
                raise ValueError(f"Datensatz {number}: erwartet werden 3 Spalten")
            record_id, name, age = (value.strip() for value in row)
            prefix = f"Datensatz {number}: "

            if not record_id:
                problems.append(prefix + "ID fehlt")
            elif record_id in seen_ids:
                problems.append(prefix + f"doppelte ID '{record_id}'")
            else:
                seen_ids.add(record_id)

            if not name:
                problems.append(prefix + "Name fehlt")

            try:
                age_number = int(age)
            except ValueError:
                problems.append(prefix + "Alter ist keine ganze Zahl")
            else:
                if not 0 <= age_number <= 120:
                    problems.append(prefix + "Alter liegt nicht zwischen 0 und 120")

    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="CSV-Datenqualitaet pruefen")
    parser.add_argument("datei", type=Path, help="UTF-8-CSV mit Header id,name,age")
    try:
        args = parser.parse_args(argv)
    except SystemExit as error:
        return error.code

    try:
        problems = check_csv(args.datei)
    except (OSError, ValueError, csv.Error) as error:
        print(f"Fehler: {error}", file=sys.stderr)
        return 2

    for problem in problems:
        print(problem)
    print(f"Probleme: {len(problems)}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
