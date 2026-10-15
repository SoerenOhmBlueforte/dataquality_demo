# CSV-Datenqualität Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ein kleines Python-CLI meldet Datenqualitätsprobleme in der Beispiel-CSV und lässt sich mit einem Testlauf vorführen.

**Architecture:** `dq_check.py` liest die CSV und gibt Prüfergebnisse als Meldungen zurück. Dieselbe Datei enthält einen dünnen CLI-Einstiegspunkt für Ausgabe und Exit-Codes. `tests/test_dq_check.py` prüft Regeln und CLI mit `unittest`.

**Tech Stack:** Python 3, Standardbibliothek (`argparse`, `csv`, `unittest`)

**Spec:** `docs/superpowers/specs/2026-10-15-csv-datenqualitaet-design.md`

## Global Constraints

- Eingabe: UTF-8, Komma, exakt `id,name,age`; keine Konfiguration oder zusätzlichen Pakete.
- Regeln: `id` und `name` erforderlich, `id` eindeutig, `age` ganzzahlig in 0..120.
- Exit-Codes: 0 sauber, 1 Qualitätsprobleme, 2 Aufruf-, Datei- oder Strukturfehler.
- Keine Änderung an der Eingabedatei.

## Review Focus

- Ein Name mit Komma in Anführungszeichen bleibt ein einzelnes CSV-Feld (Task 1).
- Werte mit nur Leerzeichen gelten als leer (Task 1).
- IDs mit umgebenden Leerzeichen gelten als gleich (Task 1).
- Eine Zeile mit zu vielen oder zu wenigen Feldern führt zu Exit-Code 2 (Tasks 1–2).
- Eine leere Datei führt zu Exit-Code 2 (Tasks 1–2).

---

### Task 1: CSV-Prüfung

**Files:**
- Create: `dq_check.py`
- Create: `tests/test_dq_check.py`
- Read: `examples/kunden.csv`

**Interfaces:**
- Produces: `check_csv(path: Path) -> list[str]`; `ValueError` bei falschem Header oder falscher Spaltenanzahl, `OSError` bei Dateifehlern.
- Meldungsformat: `Datensatz N: <problem>`; Datensatznummer beginnt nach dem Header bei 1.

- [ ] **Step 1: Failing tests schreiben.** `unittest` prüft für `examples/kunden.csv` genau fünf Meldungen: doppelte ID in Datensatz 3, fehlender Name in 4, ungültiges Alter in 5, Alter außerhalb des Bereichs in 6, fehlende ID in 7. Ein sauberer CSV-Test liefert `[]`. Weitere Tests prüfen die fünf Fälle unter „Review Focus“ für `check_csv`.
- [ ] **Step 2: Fehlerzustand prüfen.** `python -m unittest discover -s tests -v` ausführen; die neuen Tests müssen wegen der noch fehlenden Funktion fehlschlagen.
- [ ] **Step 3: Minimal implementieren.** In `dq_check.py` `check_csv(path: Path) -> list[str]` mit `csv.reader` ergänzen: Header und Spaltenzahl prüfen, Werte mit `strip()` auswerten, nichtleere IDs in einem Set sammeln, jede Regel separat melden.
- [ ] **Step 4: Tests erneut ausführen.** `python -m unittest discover -s tests -v`; alle Task-1-Tests müssen bestehen.
- [ ] **Step 5: Task committen.** `git add dq_check.py tests/test_dq_check.py` und `git commit -m "feat: check CSV data quality"` ausführen.

### Task 2: CLI und Demo-Test

**Files:**
- Modify: `dq_check.py`
- Modify: `tests/test_dq_check.py`
- Modify: `README.md`

**Interfaces:**
- Consumes: `check_csv(path: Path) -> list[str]` aus Task 1.
- Produces: `main(argv: list[str] | None = None) -> int`; `if __name__ == "__main__": raise SystemExit(main())`.

- [ ] **Step 1: Failing CLI-Tests schreiben.** `main()` mit erfasster stdout/stderr prüfen: Beispiel-CSV meldet fünf Probleme und gibt 1 zurück; saubere CSV meldet null und gibt 0 zurück; fehlende Datei, leere Datei und falsche Spaltenanzahl geben 2 zurück und schreiben einen Fehler auf stderr.
- [ ] **Step 2: Fehlerzustand prüfen.** `python -m unittest discover -s tests -v` ausführen; die neuen CLI-Tests müssen wegen des fehlenden Einstiegspunkts fehlschlagen.
- [ ] **Step 3: CLI implementieren und dokumentieren.** `main()` mit einem positionalen Dateipfad, verständlicher Ausgabe und den drei Exit-Codes ergänzen. In `README.md` Aufruf, Regeln und einen kurzen Demo-Testlauf dokumentieren.
- [ ] **Step 4: Vollständig prüfen.** `python -m unittest discover -s tests -v` muss bestehen. `python dq_check.py examples/kunden.csv` muss fünf Probleme ausgeben und Exit-Code 1 liefern; einen sauberen CSV-Fall mit Exit-Code 0 prüfen.
- [ ] **Step 5: Task committen.** `git add dq_check.py tests/test_dq_check.py README.md` und `git commit -m "feat: add CSV quality CLI demo"` ausführen.
