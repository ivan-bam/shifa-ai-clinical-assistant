"""
Quality checks for AI-generated clinical output.

Each check is a plain function that looks at the output and returns
(passed: bool, message: str). They are deterministic — no AI involved —
so they are fast, free, and reliable.
"""
from backend.services.soap import SOAPNote
from backend.services.suggestions import ClinicalSuggestions

VALID_LIKELIHOODS = {"high", "moderate", "low"}


def check_soap_sections_filled(note: SOAPNote) -> tuple[bool, str]:
    sections = {
        "subjective": note.subjective,
        "objective": note.objective,
        "assessment": note.assessment,
        "plan": note.plan,
    }
    missing = [name for name, value in sections.items() if not value or not value.strip()]
    if missing:
        return False, f"Empty SOAP section(s): {', '.join(missing)}"
    return True, "All four SOAP sections are filled"


def check_has_diagnoses(suggestions: ClinicalSuggestions) -> tuple[bool, str]:
    if not suggestions.diagnoses:
        return False, "No diagnoses were suggested"
    return True, f"{len(suggestions.diagnoses)} diagnosis suggestion(s)"


def check_diagnoses_have_valid_likelihood(suggestions: ClinicalSuggestions) -> tuple[bool, str]:
    bad = [d.name for d in suggestions.diagnoses if d.likelihood.lower() not in VALID_LIKELIHOODS]
    if bad:
        return False, f"Invalid likelihood on: {', '.join(bad)}"
    return True, "Every diagnosis has a valid likelihood (high/moderate/low)"


def check_medications_have_dose(suggestions: ClinicalSuggestions) -> tuple[bool, str]:
    bad = [m.name for m in suggestions.medications if not m.dose or not m.dose.strip()]
    if bad:
        return False, f"Medication(s) missing a dose: {', '.join(bad)}"
    return True, "Every medication includes a dose"


def check_schedule_items_have_timeframe(suggestions: ClinicalSuggestions) -> tuple[bool, str]:
    missing = sum(
        1 for item in suggestions.care_schedule if not item.timeframe or not item.timeframe.strip()
    )
    if missing:
        return False, f"{missing} care schedule item(s) missing a timeframe"
    return True, "Every care schedule item has a timeframe"


def check_mentions_expected_terms(
    note: SOAPNote,
    suggestions: ClinicalSuggestions,
    expected_terms: list[str],
) -> tuple[bool, str]:
    """At least one clinically-expected term should appear somewhere in the output."""
    if not expected_terms:
        return True, "No expected terms specified (skipped)"

    blob = (note.model_dump_json() + suggestions.model_dump_json()).lower()
    found = [term for term in expected_terms if term.lower() in blob]
    if not found:
        return False, f"None of the expected terms appeared: {', '.join(expected_terms)}"
    return True, f"Mentioned expected term(s): {', '.join(found)}"
