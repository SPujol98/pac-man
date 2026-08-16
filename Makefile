# Compiler / Tools
UV = uv

# Main files
MAIN = pac-man.py config.json
WHEEL = mazegenerator-00001-py3-none-any.whl

# Marker file: touched by install, checked by everything else
INSTALL_MARKER = .venv/.installed

# MyPy Flags
MYPY_FLAGS = --warn-return-any --warn-unused-ignores --ignore-missing-imports \
             --disallow-untyped-defs --check-untyped-defs --exclude .venv

# Terminal colors
GREEN = \033[0;32m
CYAN  = \033[0;36m
RED   = \033[0;31m
NC    = \033[0m

.PHONY: all install run debug clean lint lint-strict test check-install

all: run

install:
	$(UV) sync
	UV_SKIP_WHEEL_FILENAME_CHECK=1 $(UV) pip install $(WHEEL)
	@touch $(INSTALL_MARKER)
	@echo "$(GREEN)Install completed.$(NC)"

check-install:
	@test -f $(INSTALL_MARKER) || \
		(echo "$(RED)Dependencies not installed. Run 'make install' first.$(NC)" && exit 1)

run: check-install
	$(UV) run python3 $(MAIN)

debug: check-install
	$(UV) run python3 -m pdb $(MAIN)

test: check-install
	$(UV) run python -m pytest -v -s -o pythonpath=. tests/

lint: check-install
	@echo "$(CYAN)Executing flake8...$(NC)"
	-$(UV) run flake8 .
	@echo "$(CYAN)Executing mypy...$(NC)"
	-$(UV) run mypy . $(MYPY_FLAGS)

lint-strict: check-install
	@echo "$(CYAN)Executing flake8...$(NC)"
	-$(UV) run flake8 .
	@echo "$(CYAN)Executing mypy strict...$(NC)"
	-$(UV) run mypy . --exclude .venv --strict --ignore-missing-imports

clean:
	@echo "$(CYAN)Cleaning temporary files...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .venv
	@echo "$(GREEN)Clean completed.$(NC)"