# Compiler / Tools
UV = uv

# Main files
MAIN = src/testingApp.py
WHEEL = mazegenerator-00001-py3-none-any.whl

# MyPy Flags
MYPY_FLAGS = --warn-return-any --warn-unused-ignores --ignore-missing-imports \
             --disallow-untyped-defs --check-untyped-defs --exclude .venv

# Terminal colors
GREEN = \033[0;32m
CYAN  = \033[0;36m
NC    = \033[0m

.PHONY: all install run debug clean lint lint-strict test

all: run

install:
	$(UV) sync
	UV_SKIP_WHEEL_FILENAME_CHECK=1 $(UV) pip install $(WHEEL)

run: install
	$(UV) run python3 $(MAIN)

debug: install
	$(UV) run python3 -m pdb $(MAIN)

clean:
	@echo "$(CYAN)Cleaning temporary files...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .venv
	@echo "$(GREEN)Clean completed.$(NC)"

lint: install
	@echo "$(CYAN)Executing flake8...$(NC)"
	-$(UV) run flake8 .
	@echo "$(CYAN)Executing mypy...$(NC)"
	-$(UV) run mypy . $(MYPY_FLAGS)

lint-strict: install
	@echo "$(CYAN)Executing flake8...$(NC)"
	-$(UV) run flake8 .
	@echo "$(CYAN)Executing mypy strict...$(NC)"
	-$(UV) run mypy . --exclude .venv --strict --ignore-missing-imports

test: install
	$(UV) run python -m pytest -v -s -o pythonpath=. tests/