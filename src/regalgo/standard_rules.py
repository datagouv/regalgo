from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import Any, Generic, Protocol, TypeVar, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field




# --- Entrée / sortie des algorithmes -----------------------------------------

class AlgoInput(BaseModel):
    """
    Base à sous-classer : chaque algorithme déclare ses champs typés.

    Le schéma JSON (simulateur, doc, OpenAPI) est obtenu via `input_schema()`.
    """
    model_config = ConfigDict(extra="forbid", frozen=True)

    @classmethod
    def input_schema(cls) -> dict[str, Any]:
        return cls.model_json_schema()

    def snapshot(self) -> dict[str, Any]:
        """Représentation JSON-compatible, stockée dans AlgoResult."""
        return self.model_dump(mode="json")


class AlgoResult(BaseModel):
    """Sortie normalisée d'un algorithme réglementaire."""
    value: Any
    inputs_snapshot: dict[str, Any]
    metadata: dict[str, Any] = Field(default_factory=dict)


# --- Sources de données (indépendantes de AlgoInput) --------------------------

@runtime_checkable
class InputSource(Protocol):
    """Contrat commun : tout modèle source sait se projeter en AlgoInput."""

    def to_algo_input(self, context: dict[str, Any] | None = None) -> AlgoInput: ...


class FCPersonInput(BaseModel):
    """Personne alignée sur l'identité pivot de FranceConnect."""
    # Identité pivot (standard OpenID Connect)
    given_name: str                 # prénoms séparés par des espaces
    family_name: str                # nom de famille à l'état civil
    birthdate: date                 # YYYY-MM-DD
    gender: str                     # "male" | "female"
    birthplace: str                 # code INSEE sur 5 chiffres ("" si né à l'étranger)
    birthcountry: str               # code INSEE du pays sur 5 chiffres
    # Données complémentaires
    sub: str                        # identifiant technique
    email: str
    preferred_username: str         # nom d'usage

    def age(self, reference_date: date) -> int:
        return compute_age(self.birthdate, reference_date)


# --- Règle publique générique -------------------------------------------------

I = TypeVar("I", bound=AlgoInput)


class PublicRule(ABC, Generic[I]):
    """
    Un algorithme réglementaire, paramétré par son type d'entrée `I`.

        class MonAlgo(PublicRule[MonInput]):
            def compute(self, algo_input: MonInput) -> AlgoResult: ...
    """

    @abstractmethod
    def compute(self, algo_input: I) -> AlgoResult: ...

    def result(self, value: Any, algo_input: I, **metadata: Any) -> AlgoResult:
        """Construit un AlgoResult traçable (évite de répéter le boilerplate)."""
        return AlgoResult(
            value=value,
            inputs_snapshot=algo_input.snapshot(),
            metadata=metadata,
        )