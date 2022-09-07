SHELL=/bin/bash

TEST_ENV=( [[ "$$CONDA_PREFIX" == */pantanal ]] || \
		 (echo -e "\nERROR: environment not active: run '. ./activate'" && false) )

REQ=requirements/requirements
REQS=$(REQ).txt \
	$(REQ).dev.txt

PY=python
PIPC=pip-compile

NEW_SHELL=$(shell getent passwd $$USER | awk -F: '{print $$NF}')

# tools profile
PROFILE=client

# include if exists
-include ./helm/Makefile

.PHONY: create-env
create-env:
	conda create -n pantanal -y python=3.9
	@echo "Run: '. ./activate' to finish setup"

# install dependencies
.PHONY: install-deps
install-deps: compile-deps
	@$(TEST_ENV)
	$(PY) -m pip install -U \
		-r $(REQ).txt \
		-r $(REQ).dev.txt

# compile (lock) dependencies
.PHONY: compile-deps
compile-deps: $(REQS)

# compile (lock) dependencies
.PHONY: compile-deps-clean
compile-deps-clean:
	rm -f $(REQS)

# setup third-party tools for isa
.PHONY: setup-tools
setup-tools:
	@$(TEST_ENV)
	@$(PY) run tools setup -p $(PROFILE)
	@echo -e "\nRun 'hash -r' to complete setup."

# compile requirements
$(REQS): %.txt : %.in
	@$(TEST_ENV)
	@rm -rf $@
	$(PIPC) -U -q $<

