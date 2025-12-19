import nox

@nox.session(python=["3.8", "3.9"])
def tests(session):
    session.install("pytest")
    session.run("pytest")

@nox.session
def lint(session):
    session.install("flake8")
    session.run("flake8", "src", "tests")
