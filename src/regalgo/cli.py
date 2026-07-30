from __future__ import annotations

from pathlib import Path
import click


@click.group()
def main() -> None:
    """Regalgo — outillage pour les algorithmes réglementaires publics."""


# ---------------------------------------------------------------------------
# init
# ---------------------------------------------------------------------------

_REGLES_PY = '''\
from __future__ import annotations

from regalgo import AlgoInput, AlgoResult, PublicRule


class {class_name}(PublicRule):
    """Implémentation de l\'algorithme {project_name}."""

    def compute(self, algo_input: AlgoInput) -> AlgoResult:
        data = algo_input.data

        # TODO : implémenter la logique réglementaire ici
        result_value = None

        return AlgoResult(
            value=result_value,
            algo_id=self.algo_id,
            regulation=self.regulation,
            inputs_snapshot=data,
        )
'''

_TEST_PY = '''\
from datetime import date

import pytest

from regalgo import PersonInput

from {module_name}.regles import {class_name}


@pytest.fixture
def algo():
    return {class_name}()


def test_cas_nominal(algo):
    person = PersonInput(
        cv_nationality="FR",
        schema_birth_date=date(1990, 1, 1),
        cccev_civil_rights_intact=True,
        cccev_electoral_list_registered=True,
    )
    result = algo.compute(person.to_algo_input())
    assert result.algo_id == "{project_name}"
'''

_METADATA_JSON = '''\
{{
    "dct:identifier": "{project_name}",
    "dct:title": "{title}",
    "dct:description": "{description}",
    "cprmv:isBasedOn": {{
        "dct:source": "{reg_source}",
        "dct:description": "{reg_description}"
    }}
}}
'''

_PYPROJECT_TOML = '''\
[tool.poetry]
name = "{project_name}"
version = "0.1.0"
description = ""
packages = [{{include = "{module_name}", from = "src"}}]

[tool.poetry.dependencies]
python = "^3.10"
regalgo = "*"

[tool.poetry.group.dev.dependencies]
pytest = "*"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
'''

_README_MD = '''\
# {project_name}

Algorithme réglementaire basé sur [regalgo](https://github.com/qloridant/regalgo).

## Installation

```bash
pip install {project_name}
```

## Utilisation

```python
from datetime import date
from regalgo import PersonInput
from {module_name}.regles import {class_name}

person = PersonInput(
    cv_nationality="FR",
    schema_birth_date=date(1990, 1, 1),
    cccev_civil_rights_intact=True,
    cccev_electoral_list_registered=True,
)

algo = {class_name}()
result = algo.compute(person.to_algo_input())
print(result.value)
```
'''

_INIT_PY = '''\
from .regles import {class_name}

__all__ = ["{class_name}"]
'''


def _to_class_name(name: str) -> str:
    return "".join(part.capitalize() for part in name.replace("-", "_").split("_"))


def _to_module_name(name: str) -> str:
    return name.replace("-", "_")


@main.command("init")
@click.argument("project_name")
@click.option("--output-dir", "-o", default=".", type=click.Path(),
              help="Répertoire parent où créer le projet (défaut : répertoire courant)")
@click.option("--no-input", is_flag=True, default=False,
              help="Mode non interactif : utilise les valeurs par défaut pour le metadata.json")
def init(project_name: str, output_dir: str, no_input: bool) -> None:
    """Initialise un nouveau projet regalgo avec la structure standard.

    PROJECT_NAME est le nom du projet (ex. mon-algo, eligibilite-rsa).
    """
    module_name = _to_module_name(project_name)
    class_name = _to_class_name(project_name)
    base = Path(output_dir) / project_name

    if base.exists():
        raise click.ClickException(f"Le répertoire '{base}' existe déjà.")

    if no_input:
        title = project_name
        description = "Description de l'algorithme"
        reg_source = ""
        reg_description = "Référence réglementaire"
    else:
        click.echo("\nConfiguration du fichier metadata.json :")
        title = click.prompt("  Titre de l'algorithme", default=project_name)
        description = click.prompt("  Description de l'algorithme", default="Description de l'algorithme")
        reg_source = click.prompt("  Source réglementaire (URL ou référence légale)", default="")
        reg_description = click.prompt("  Description de la référence réglementaire", default="Référence réglementaire")

    files: dict[Path, str] = {
        base / "pyproject.toml": _PYPROJECT_TOML.format(
            project_name=project_name, module_name=module_name
        ),
        base / "README.md": _README_MD.format(
            project_name=project_name, module_name=module_name, class_name=class_name
        ),
        base / "src" / module_name / "__init__.py": _INIT_PY.format(class_name=class_name),
        base / "src" / module_name / "regles.py": _REGLES_PY.format(
            project_name=project_name, class_name=class_name
        ),
        base / "src" / module_name / "metadata.json": _METADATA_JSON.format(
            project_name=project_name,
            title=title,
            description=description,
            reg_source=reg_source,
            reg_description=reg_description,
        ),
        base / "tests" / "test_regles.py": _TEST_PY.format(
            project_name=project_name, module_name=module_name, class_name=class_name
        ),
    }

    for path, content in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        click.echo(f"  créé  {path.relative_to(Path(output_dir))}")

    click.secho(f"\nProjet '{project_name}' initialisé.", fg="green")
    click.echo(f"\n  cd {project_name}")
    click.echo("  poetry install")
    click.echo("  pytest")
