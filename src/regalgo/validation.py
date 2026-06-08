from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .standard_rules import PersonInput

_SHAPES_URL = "https://semiceu.github.io/Core-Person-Vocabulary/releases/2.1.0/shacl/core-person-ap-SHACL.ttl"


@dataclass
class ValidationResult:
    """Résultat d'une validation SHACL d'un PersonInput contre le Core Person Vocabulary."""
    valid: bool
    violations: list[str] = field(default_factory=list)

    def __bool__(self) -> bool:
        return self.valid


def validate_person_input(person: PersonInput) -> ValidationResult:
    """
    Valide un PersonInput contre les shapes SHACL dérivées du Core Person Vocabulary 2.1.0.

    Raises:
        ImportError: Si rdflib ou pyshacl ne sont pas installés
                     (pip install 'regalgo-civique-droit-vote[shacl]').
    """
    try:
        from rdflib import Graph, Literal, Namespace, URIRef
        from rdflib.namespace import RDF, XSD
        import pyshacl
    except ImportError as exc:
        raise ImportError(
            "rdflib et pyshacl sont requis : "
            "pip install 'regalgo-civique-droit-vote[shacl]'"
        ) from exc

    _CV = Namespace("http://data.europa.eu/m8g/")
    _SCHEMA = Namespace("http://schema.org/")
    _SH = Namespace("http://www.w3.org/ns/shacl#")

    # --- Sérialisation de PersonInput en graphe RDF ---
    data_graph = Graph()
    data_graph.bind("cv", _CV)
    data_graph.bind("schema", _SCHEMA)
    node = URIRef("urn:person:input")
    data_graph.add((node, RDF.type, _CV.Person))
    # Valeurs brutes — pas de normalisation, c'est précisément ce qu'on valide
    data_graph.add((node, _CV.nationality,
                    Literal(person.cv_nationality, datatype=XSD.string)))
    data_graph.add((node, _SCHEMA.birthDate,
                    Literal(person.schema_birth_date.isoformat(), datatype=XSD.date)))
    data_graph.add((node, _CV.domicile,
                    Literal(person.cv_domicile_country, datatype=XSD.string)))

    # --- Validation SHACL ---
    shapes_graph = Graph().parse(_SHAPES_URL, format="turtle")
    conforms, results_graph, _ = pyshacl.validate(
        data_graph,
        shacl_graph=shapes_graph,
        inference="rdfs",
        abort_on_first=False,
    )

    violations: list[str] = []
    for result_node in results_graph.subjects(RDF.type, _SH.ValidationResult):
        msg = results_graph.value(result_node, _SH.resultMessage)
        path = results_graph.value(result_node, _SH.resultPath)
        value = results_graph.value(result_node, _SH.value)
        violations.append(
            str(msg) if msg else f"Violation sur {path} : valeur '{value}'"
        )

    # Contrainte dynamique : schema:birthDate ne peut pas être dans le futur
    if person.schema_birth_date > date.today():
        conforms = False
        violations.append(
            f"schema:birthDate '{person.schema_birth_date}' ne peut pas être dans le futur"
        )

    return ValidationResult(valid=conforms, violations=violations)
