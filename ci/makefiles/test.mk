include ../../extras/.env
include ../.env

# HELP
# This will output the help for each task
# thanks to https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
.PHONY: help test

help: ## Basic help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.DEFAULT_GOAL := all

# cli args
ARGS = $(filter-out $@,$(MAKECMDGOALS))


all: check test ## Run check and test code

# CHECK
check: flake bandit ## Run flake and bandit over code and tests
	@echo "Checking code..."
bandit: ## Run bandit over code
	@bandit -r ../../${PACKAGE}
flake: ## Run flake over code and tests
	# stop the build if there are Python syntax errors or undefined names
	@flake8 ../../${PACKAGE} --count --select=E9,F63,F7,F82 --show-source --statistics
	# exit-zero treats all errors as warnings. The GitHub editor is 127 chars wide
	@flake8 ../../${PACKAGE} --count --ignore=E272,E501,E266,E241,E226,E251,E303,E221 --exit-zero --max-complexity=10 --max-line-length=127 --statistics
	# exit-zero treats all errors as warnings. The GitHub editor is 127 chars wide
	@flake8 ../../tests --count --ignore=E272,E501,E266,E241,E226,E251,E303,E221,E122,E211,E302 --exit-zero --max-complexity=10 --max-line-length=127 --statistics

# TEST
test: ## Test code with 'pytest'
	@export PYTHONPATH=$$PWD/../.. ; \
	cd ../../tests ; \
	python -m pytest -v $(args)
