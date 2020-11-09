SELF_DIR := $(dir $(lastword $(MAKEFILE_LIST)))

include $(SELF_DIR)/.env

# HELP
# This will output the help for each task
# thanks to https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
.PHONY: help test

help:
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help

# cli args
ARGS = $(filter-out $@,$(MAKECMDGOALS))

MAKE_CMD = $(MAKE) -s  --no-print-directory -C makefiles

# PYTHON VERSION
ifneq ($(strip $(python)),)
	PYTHON_ENV = _python$(python)
endif
ifeq ($(env),)
	env = build
endif


clean:
	@$(MAKE_CMD) -f conda.mk clean

# FAST TESTING
check: ## Test code with 'pytest', this is the fastest way to test the code
	   @$(MAKE_CMD) -f test.mk check

test: ## Test code with 'pytest', this is the fastest way to test the code
	   @$(MAKE_CMD) -f test.mk test args=$(args)

check-inconda: ## Test conda package
ifneq ($(strip $(env)),)
	$(eval env=check)
endif
	@$(MAKE_CMD) -f conda.mk check-environment-check env=$(env)
	@$(MAKE_CMD) -f conda.mk conda-run-env env=check cmd="make -C .. check"

test-inconda: ## Test code with 'pytest' within a conda environment, this is the fastest way to test the code
ifneq ($(strip $(env)),)
	$(eval env=test)
endif
		 @$(MAKE_CMD) -f conda.mk check-environment-test env=$(env)
	   @$(MAKE_CMD) -f conda.mk conda-run-env env=$(env) \
																					  cmd="make -C .. test" \
																						args=$(ARGS)

conda-all: conda-build conda-test conda-convert conda-publish ## (default) Perform all conda process (build, test, convert, publish)

# CONDA WORKFLOW
conda-build: ## Build (without tests) conda package, if 'python=<version>' (default is latest available) is set then the package will be built for this version of Python
	@$(MAKE_CMD) -f conda.mk conda-build-only$(PYTHON_ENV)

conda-test: ## Test conda package, if 'python=<version>' (default is all variants of package built) is set then the package built for this version of Python will be tested
	@$(MAKE_CMD) -f conda.mk conda-test-only$(PYTHON_ENV)

conda-convert: ## Convert conda package towards all platforms, if 'python=<version>' (default is all variants of package built) is set then the package built for this version of Python will be converted
	@$(MAKE_CMD) -f conda.mk conda-convert$(PYTHON_ENV)

conda-publish: ## Publish conda package, if 'python=<version>' (default is all variants of package built) is set then the package built for this version of Python will be published
	@$(MAKE_CMD) -f conda.mk conda-publish$(PYTHON_ENV)

conda-check-recipe: ## Check conda recipe
	@$(MAKE_CMD) -f conda.mk conda-recipe-check
