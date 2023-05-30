from __future__ import annotations

import nox


@nox.session(reuse_venv=True)
def lint(session: nox.Session) -> None:
    """Run pre-commit hooks for linting."""
    session.install("pre-commit")
    session.run("pre-commit", "run", "--all-files")


@nox.session(reuse_venv=True)
def test(session: nox.Session) -> None:
    """Run tests."""
    session.install("-r", "requirements.txt", "pytest")
    session.run("pytest", "tests", *session.posargs)
