.PHONY: lint validate-config build unit-tests coverage integration-tests simulation-tests ci-pr ci-post-merge security-sast security-policy

lint:
	bash scripts/lint.sh

validate-config:
	bash scripts/validate_config.sh

build:
	bash scripts/build.sh

unit-tests:
	bash scripts/unit_tests.sh

coverage:
	bash scripts/python_coverage.sh

integration-tests:
	bash scripts/integration_tests.sh

simulation-tests:
	bash scripts/simulation_tests.sh

ci-pr: lint validate-config build unit-tests coverage

ci-post-merge: ci-pr integration-tests simulation-tests

security-sast:
	bash scripts/security_sast.sh

security-policy:
	bash scripts/validate_security_exceptions.sh
