"""
Run the evaluation suite against the live AI and print a pass/fail report.

Usage:
    python -m backend.evaluations.runner

Exits with code 0 if every check passes, 1 otherwise — so it can be used
in CI to block a change that makes the AI worse.
"""
import sys

from backend.evaluations import checks
from backend.evaluations.dataset import CASES, EvalCase
from backend.services.soap import generate_soap_note
from backend.services.suggestions import generate_clinical_suggestions

PASS = "PASS"
FAIL = "FAIL"


def _run_case(case: EvalCase) -> list[tuple[bool, str]]:
    note = generate_soap_note(case.physician_input).note
    suggestions = generate_clinical_suggestions(case.physician_input).suggestions

    return [
        checks.check_soap_sections_filled(note),
        checks.check_has_diagnoses(suggestions),
        checks.check_diagnoses_have_valid_likelihood(suggestions),
        checks.check_medications_have_dose(suggestions),
        checks.check_schedule_items_have_timeframe(suggestions),
        checks.check_mentions_expected_terms(note, suggestions, case.expected_terms),
    ]


def run() -> bool:
    total = 0
    passed = 0

    for case in CASES:
        print(f"\n=== Case: {case.name} ===")
        print(f"Input: {case.physician_input}")
        for ok, message in _run_case(case):
            total += 1
            passed += int(ok)
            print(f"  [{PASS if ok else FAIL}] {message}")

    print(f"\n{'-' * 50}")
    print(f"RESULT: {passed}/{total} checks passed")
    return passed == total


if __name__ == "__main__":
    all_passed = run()
    sys.exit(0 if all_passed else 1)
