from datetime import date, timedelta

import pytest

rdflib = pytest.importorskip("rdflib")
pyshacl = pytest.importorskip("pyshacl")

from regalgo_civique_droit_vote import PersonInput
from regalgo_civique_droit_vote.validation import validate_person_input, ValidationResult


PERSON_VALIDE = PersonInput(
    cv_nationality="FR",
    schema_birth_date=date(1990, 6, 15),
    cccev_civil_rights_intact=True,
    cccev_electoral_list_registered=True,
    cv_domicile_country="FR",
)


def test_person_valide_passe():
    result = validate_person_input(PERSON_VALIDE)
    assert result.valid is True
    assert result.violations == []


def test_bool_result():
    assert bool(validate_person_input(PERSON_VALIDE)) is True


def test_nationalite_minuscules_invalide():
    person = PersonInput(
        cv_nationality="fr",  # doit être en majuscules
        schema_birth_date=date(1990, 6, 15),
        cccev_civil_rights_intact=True,
        cccev_electoral_list_registered=True,
    )
    result = validate_person_input(person)
    assert result.valid is False
    assert any("nationality" in v.lower() or "cv:nationality" in v.lower() for v in result.violations)


def test_nationalite_code_invalide():
    person = PersonInput(
        cv_nationality="FRA",  # alpha-3, pas alpha-2
        schema_birth_date=date(1990, 6, 15),
        cccev_civil_rights_intact=True,
        cccev_electoral_list_registered=True,
    )
    result = validate_person_input(person)
    assert result.valid is False


def test_domicile_invalide():
    person = PersonInput(
        cv_nationality="DE",
        schema_birth_date=date(1990, 6, 15),
        cccev_civil_rights_intact=True,
        cccev_electoral_list_registered=True,
        cv_domicile_country="france",  # invalide — doit être 2 majuscules
    )
    result = validate_person_input(person)
    assert result.valid is False
    assert any("domicile" in v.lower() for v in result.violations)


def test_birth_date_dans_le_futur():
    person = PersonInput(
        cv_nationality="FR",
        schema_birth_date=date.today() + timedelta(days=1),
        cccev_civil_rights_intact=True,
        cccev_electoral_list_registered=True,
    )
    result = validate_person_input(person)
    assert result.valid is False
    assert any("futur" in v for v in result.violations)


def test_citoyen_ue_valide():
    person = PersonInput(
        cv_nationality="DE",
        schema_birth_date=date(1985, 3, 20),
        cccev_civil_rights_intact=True,
        cccev_electoral_list_registered=True,
        cv_domicile_country="FR",
    )
    result = validate_person_input(person)
    assert result.valid is True
