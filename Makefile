# Configuration
# =============

# Have zero effect by default to prevent accidental changes.
.DEFAULT_GOAL := none

# Delete targets that fail to prevent subsequent attempts incorrectly assuming
# the target is up to date.
.DELETE_ON_ERROR: ;

# Prevent pesky default rules from creating unexpected dependency graphs.
.SUFFIXES: ;


# Verbs
# =====

.PHONY: none

none:
	@echo No target specified


# Nouns
# =====

# TODO: Incremental build probably fails if a preq is removed
requirements.txt: $(wildcard requirements-*.in)
	pip-compile --allow-unsafe --generate-hashes --no-header --output-file $@ $^ \
	> /dev/null 2>&1
