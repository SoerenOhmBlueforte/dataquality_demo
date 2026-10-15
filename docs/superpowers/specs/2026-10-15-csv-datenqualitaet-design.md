# CSV-Datenqualität: Design

## Ziel

Eine kurze CLI-Demo prüft eine CSV-Datei und zeigt konkrete Datenqualitätsprobleme. Die vorhandene `examples/kunden.csv` dient als vorführbarer Testfall.

## Eingabe und Regeln

- Aufruf: `python dq_check.py <datei.csv>`.
- UTF-8-CSV mit Komma als Trennzeichen und exakt dem Header `id,name,age`.
- Ein leerer oder nur aus Leerzeichen bestehender Wert für `id` oder `name` ist ein Problem.
- Jede nichtleere `id` muss innerhalb der Datei eindeutig sein. Für den Vergleich werden umgebende Leerzeichen entfernt.
- `age` muss eine ganze Zahl von 0 bis 120 einschließlich sein. Umgebende Leerzeichen sind erlaubt.
- Die erste Datenzeile ist Datensatz 1; eine Zeile kann mehrere Probleme melden.
- Die mitgelieferte CSV enthält sieben Datensätze: zwei gültige und fünf mit je einem Problem.

## Ausgabe und Fehler

- Pro Problem eine verständliche Zeile mit Datensatznummer; am Ende die Anzahl der Probleme.
- Exit-Code 0: keine Probleme. Exit-Code 1: mindestens ein Datenqualitätsproblem.
- Exit-Code 2: ungültiger Aufruf, unlesbare Datei, falscher Header oder falsche Spaltenanzahl. Fehlermeldung auf stderr.
- Die Datei wird nur gelesen; das Tool korrigiert keine Daten.

## Umsetzung und Nachweis

Ein Skript `dq_check.py` nutzt nur die Python-Standardbibliothek (`argparse`, `csv`). `unittest` prüft die Regeln und die Exit-Codes. Ein CLI-Test gegen `examples/kunden.csv` weist fünf Meldungen und Exit-Code 1 nach; ein sauberer Testfall weist Exit-Code 0 nach.
