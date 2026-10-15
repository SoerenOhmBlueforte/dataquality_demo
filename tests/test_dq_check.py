from pathlib import Path
from contextlib import redirect_stderr, redirect_stdout
import io
import subprocess
import sys
import tempfile
import unittest

import dq_check
from dq_check import check_csv


class CheckCsvTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "kunden.csv"

    def write_csv(self, content):
        self.path.write_text(content, encoding="utf-8")
        return self.path

    def test_example_reports_five_problems_without_changing_file(self):
        path = Path(__file__).resolve().parents[1] / "examples" / "kunden.csv"
        original = path.read_bytes()
        self.assertEqual(check_csv(path), [
            "Datensatz 3: doppelte ID '2'",
            "Datensatz 4: Name fehlt",
            "Datensatz 5: Alter ist keine ganze Zahl",
            "Datensatz 6: Alter liegt nicht zwischen 0 und 120",
            "Datensatz 7: ID fehlt",
        ])
        self.assertEqual(path.read_bytes(), original)

    def test_clean_csv_accepts_age_boundaries_and_whitespace(self):
        path = self.write_csv("id,name,age\n 1 , Anna , 0 \n2,Ben,120\n")
        self.assertEqual(check_csv(path), [])

    def test_quoted_comma_is_part_of_name(self):
        path = self.write_csv('id,name,age\n1,"Müller, Anna",32\n')
        self.assertEqual(check_csv(path), [])

    def test_whitespace_only_required_values_are_missing_not_duplicates(self):
        path = self.write_csv("id,name,age\n , ,32\n,,45\n")
        self.assertEqual(check_csv(path), [
            "Datensatz 1: ID fehlt", "Datensatz 1: Name fehlt",
            "Datensatz 2: ID fehlt", "Datensatz 2: Name fehlt",
        ])

    def test_ids_are_compared_after_stripping_whitespace(self):
        path = self.write_csv("id,name,age\n1,Anna,32\n 1 ,Ben,45\n1,Clara,28\n")
        self.assertEqual(check_csv(path), [
            "Datensatz 2: doppelte ID '1'",
            "Datensatz 3: doppelte ID '1'",
        ])

    def test_invalid_ages_are_reported(self):
        for age, problem in [
            ("", "Alter ist keine ganze Zahl"),
            (" ", "Alter ist keine ganze Zahl"),
            ("1.5", "Alter ist keine ganze Zahl"),
            ("-1", "Alter liegt nicht zwischen 0 und 120"),
            ("121", "Alter liegt nicht zwischen 0 und 120"),
        ]:
            with self.subTest(age=age):
                path = self.write_csv(f"id,name,age\n1,Anna,{age}\n")
                self.assertEqual(check_csv(path), [f"Datensatz 1: {problem}"])

    def test_all_problems_in_a_record_are_reported(self):
        path = self.write_csv("id,name,age\n1,Anna,32\n1, ,abc\n")
        self.assertEqual(check_csv(path), [
            "Datensatz 2: doppelte ID '1'",
            "Datensatz 2: Name fehlt",
            "Datensatz 2: Alter ist keine ganze Zahl",
        ])

    def test_wrong_field_count_is_rejected(self):
        for row in ["1,Anna", "1,Anna,32,extra", ""]:
            with self.subTest(row=row):
                path = self.write_csv(f"id,name,age\n{row}\n")
                with self.assertRaises(ValueError):
                    check_csv(path)

    def test_empty_file_is_rejected(self):
        with self.assertRaises(ValueError):
            check_csv(self.write_csv(""))

    def test_header_must_match_exactly(self):
        for header in ["name,id,age", "id,name,years", "id, name,age"]:
            with self.subTest(header=header):
                with self.assertRaises(ValueError):
                    check_csv(self.write_csv(f"{header}\n1,Anna,32\n"))

    def test_header_without_records_has_no_problems(self):
        self.assertEqual(check_csv(self.write_csv("id,name,age\n")), [])

    def test_missing_file_raises_os_error(self):
        with self.assertRaises(OSError):
            check_csv(self.path)


class CliTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "kunden.csv"

    def run_main(self, argv):
        self.assertTrue(callable(getattr(dq_check, "main", None)), "main entry point is missing")
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = dq_check.main(argv)
        return code, stdout.getvalue(), stderr.getvalue()

    def test_example_reports_five_problems_and_returns_one(self):
        path = Path(__file__).resolve().parents[1] / "examples" / "kunden.csv"
        code, stdout, stderr = self.run_main([str(path)])
        self.assertEqual(code, 1)
        self.assertEqual(stdout.splitlines(), [
            "Datensatz 3: doppelte ID '2'",
            "Datensatz 4: Name fehlt",
            "Datensatz 5: Alter ist keine ganze Zahl",
            "Datensatz 6: Alter liegt nicht zwischen 0 und 120",
            "Datensatz 7: ID fehlt",
            "Probleme: 5",
        ])
        self.assertEqual(stderr, "")

    def test_clean_csv_reports_zero_and_returns_zero(self):
        self.path.write_text("id,name,age\n1,Anna,32\n", encoding="utf-8")
        original = self.path.read_bytes()
        code, stdout, stderr = self.run_main([str(self.path)])
        self.assertEqual((code, stdout, stderr), (0, "Probleme: 0\n", ""))
        self.assertEqual(self.path.read_bytes(), original)

    def test_missing_file_returns_two_with_error_on_stderr(self):
        code, stdout, stderr = self.run_main([str(self.path)])
        self.assertEqual(code, 2)
        self.assertEqual(stdout, "")
        self.assertIn("Fehler:", stderr)

    def test_structure_errors_return_two_with_error_on_stderr(self):
        for content in ["", "name,id,age\n", "id,name,age\n1,Anna\n"]:
            with self.subTest(content=content):
                self.path.write_text(content, encoding="utf-8")
                code, stdout, stderr = self.run_main([str(self.path)])
                self.assertEqual(code, 2)
                self.assertEqual(stdout, "")
                self.assertIn("Fehler:", stderr)

    def test_invalid_utf8_returns_two_with_error_on_stderr(self):
        self.path.write_bytes(b"id,name,age\n1,\xff,32\n")
        code, stdout, stderr = self.run_main([str(self.path)])
        self.assertEqual(code, 2)
        self.assertEqual(stdout, "")
        self.assertIn("Fehler:", stderr)

    def test_invalid_invocations_return_two_with_error_on_stderr(self):
        for argv in [[], ["one.csv", "two.csv"]]:
            with self.subTest(argv=argv):
                code, stdout, stderr = self.run_main(argv)
                self.assertEqual(code, 2)
                self.assertEqual(stdout, "")
                self.assertTrue(stderr)

    def test_script_entry_point_runs_example(self):
        root = Path(__file__).resolve().parents[1]
        result = subprocess.run(
            [sys.executable, str(root / "dq_check.py"), str(root / "examples" / "kunden.csv")],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout.splitlines()[-1], "Probleme: 5")
        self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()
