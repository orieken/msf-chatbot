from invoke import task

@task
def test_unit(c):
    """Run unit tests"""
    c.run("pytest tests/unit")

@task
def test_unit_coverage(c):
    """Run unit tests with coverage report"""
    c.run("pytest tests/unit --cov=. --cov-report=term-missing")

@task
def test_bdd(c):
    """Run BDD tests"""
    c.run("pytest tests/bdd")

@task
def test(c):
    """Run all tests"""
    c.run("pytest tests")

@task
def test_coverage(c):
    """Run all tests with coverage report"""
    c.run("pytest tests --cov=. --cov-report=term-missing")

@task
def run_bot(c):
    """Run the Discord bot"""
    c.run("python bot.py")

@task
def lint(c):
    """Run linting checks"""
    c.run("ruff check .")
    c.run("black --check .")

@task
def format(c):
    """Format code with black"""
    c.run("black .")
