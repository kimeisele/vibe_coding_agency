# Makefile for agency-toolkit

.PHONY: all install lint format test check build-binary

# Variables
PYTHON = python3.11

# Default target
all: install check

# Dependencies
install:
	@echo "Installing dependencies..."
	$(PYTHON) -m pip install -e ".[dev]"

# Code Quality
lint:
	@echo "Running linters (ruff, black, mypy)..."
	ruff check .
	black --check .
	mypy .

format:
	@echo "Formatting code (ruff, black)..."
	ruff check . --fix
	black .

reinstall-fpdf:
	@echo "Reinstalling fpdf2..."
	$(PYTHON) -m pip uninstall -y fpdf
	$(PYTHON) -m pip uninstall -y fpdf2
	$(PYTHON) -m pip install --force-reinstall --no-cache-dir fpdf2

# Testing
test:
	@echo "Running tests..."
	$(PYTHON) -m pytest tests/ -v

# Combined check
check:
	@echo "Running all checks..."
	@$(MAKE) lint
	@$(MAKE) test

# Build binary distribution
build-binary:
	@echo "Building standalone binary with PyInstaller..."
	$(PYTHON) -m PyInstaller \
		--onefile \
		--name=agency-toolkit \
		--add-data "templates:templates" \
		--add-data "registry:registry" \
		--hidden-import=agency_toolkit.commands.briefing \
		--hidden-import=agency_toolkit.commands.image \
		--hidden-import=agency_toolkit.commands.info \
		--hidden-import=agency_toolkit.commands.mistral \
		--hidden-import=agency_toolkit.commands.os \
		--hidden-import=agency_toolkit.commands.social \
		--hidden-import=agency_toolkit.commands.structure \
		--hidden-import=agency_toolkit.commands.validate \
		--hidden-import=agency_toolkit.providers.pollinations \
		--hidden-import=agency_toolkit.providers.replicate \
		agency_toolkit/cli_app.py
	@echo "✓ Binary built successfully: dist/agency-toolkit"
