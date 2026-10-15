# dataquality_demo

Kurze CLI-Demo zur Datenqualitätsprüfung mit Python 3.10 oder neuer.
Das Tool nutzt ausschließlich die Standardbibliothek und liest die Eingabe nur.

## Aufruf

```console
python dq_check.py examples/kunden.csv
```

Die Eingabe ist eine UTF-8-CSV mit Komma als Trennzeichen und exakt dem Header
`id,name,age`. Jeder Datensatz muss drei Spalten enthalten.

- `id` und `name` dürfen weder leer sein noch nur Leerzeichen enthalten.
- Nichtleere IDs müssen eindeutig sein; umgebende Leerzeichen werden entfernt.
- `age` muss eine ganze Zahl von 0 bis 120 sein; umgebende Leerzeichen sind erlaubt.
- Die erste Datenzeile ist Datensatz 1. Ein Datensatz kann mehrere Probleme haben.

Pro Problem erscheint eine Zeile, am Ende die Anzahl. Exit-Codes:

| Code | Bedeutung |
| --- | --- |
| 0 | Keine Datenqualitätsprobleme |
| 1 | Mindestens ein Datenqualitätsproblem |
| 2 | Ungültiger Aufruf, Dateifehler, ungültiges UTF-8, falscher Header oder falsche Spaltenanzahl; Fehler auf stderr |

## Demo-Testlauf

Die Beispieldatei enthält sieben Datensätze: zwei gültige und fünf mit je einem Problem.

```console
> python dq_check.py examples/kunden.csv
Datensatz 3: doppelte ID '2'
Datensatz 4: Name fehlt
Datensatz 5: Alter ist keine ganze Zahl
Datensatz 6: Alter liegt nicht zwischen 0 und 120
Datensatz 7: ID fehlt
Probleme: 5
```

Der Exit-Code ist 1. Eine saubere Datei mit folgendem Inhalt liefert
`Probleme: 0` und Exit-Code 0:

```csv
id,name,age
1,Anna,32
```

Die automatisierten Tests einschließlich CLI-Demo laufen mit:

```console
python -m unittest discover -s tests -v
```
