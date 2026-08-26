from __future__ import annotations

import json
from pathlib import Path
from datetime import date
from dataclasses import dataclass, field
from typing import Any
from abc import ABC, abstractmethod

# États membres de l'UE — ISO 3166-1 alpha-2 (27 membres, 2024)
EU_MEMBER_STATES: frozenset[str] = frozenset({
    "AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "ES", "FI",
    "FR", "GR", "HR", "HU", "IE", "IT", "LT", "LU", "LV", "MT",
    "NL", "PL", "PT", "RO", "SE", "SI", "SK",
})


# --- Structures de données standard  ---

@dataclass
class AlgoInput:
    """Entrée normalisée d'un algorithme réglementaire."""
    data: dict[str, Any]
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class PersonInput:
    """
    Représentation d'une personne alignée sur l'identité pivot de France Connect.

    Préfixes :
      fc:     France Connect
      cv:     http://data.europa.eu/m8g/       (Core Person Vocabulary)
      schema: http://schema.org/
      cccev:  http://data.europa.eu/m8g/cccev/ (Core Criterion & Evidence Vocabulary)
    """
    # cv:nationality — code ISO 3166-1 alpha-2 (ex. "FR", "DE")
    cv_nationality: str
    # schema:birthDate — date de naissance, l'âge est calculé à la volée
    schema_birth_date: date
    # CCCEV criterion : non privé de ses droits civiques (Art. L.5, L.6)
    cccev_civil_rights_intact: bool
    # CCCEV criterion : inscrit sur les listes électorales (Art. L.7 / L.O. 227-1)
    cccev_electoral_list_registered: bool
    # cv:domicile → adminUnitL1 — pays de résidence, ISO 3166-1 alpha-2 (défaut "FR")
    cv_domicile_country: str = "FR"

    def to_algo_input(self, context: dict[str, Any] | None = None) -> AlgoInput:
        """Convertit vers AlgoInput en calculant l'âge depuis schema:birthDate."""
        today = date.today()
        age = today.year - self.schema_birth_date.year - (
            (today.month, today.day)
            < (self.schema_birth_date.month, self.schema_birth_date.day)
        )
        return AlgoInput(
            data={
                "nationalite_francaise": self.cv_nationality.upper() == "FR",
                "citoyennete_ue": self.cv_nationality.upper() in EU_MEMBER_STATES,
                "domicile_france": self.cv_domicile_country.upper() == "FR",
                "age": age,
                "capacite_civique": self.cccev_civil_rights_intact,
                "inscrit_listes_electorales": self.cccev_electoral_list_registered,
            },
            context=context or {},
        )


@dataclass
class AlgoResult:
    """Sortie normalisée d'un algorithme réglementaire."""
    value: Any
    algo_id: str
    regulation: dict[str, str]
    inputs_snapshot: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)


# --- Abtract Implémentation de l'algorithme ---
class PublicRule(ABC):

    def __init__(self) -> None:
        _meta_path = Path(__file__).parent / "metadata.json"
        self._metadata = json.loads(_meta_path.read_text())

    @property
    def algo_id(self) -> str:
        return self._metadata["dct:identifier"]

    @property
    def regulation(self) -> dict[str, str]:
        return self._metadata["cprmv:isBasedOn"]

    @abstractmethod
    def compute(self, algo_input: AlgoInput) -> AlgoResult:
        pass