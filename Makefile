.PHONY: lint validate-config build unit-tests coverage integration-tests simulation-tests ci-pr ci-post-merge security-sast security-policy check-aws infra-init infra-format infra-validate infra-plan infra-apply platform-bootstrap runner-register platform-verify evidence-export infra-destroy

TERRAFORM_DIR ?= infra/terraform
TFVARS ?= terraform.tfvars

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

check-aws:
	bash infra/scripts/check-aws-session.sh

infra-init:
	terraform -chdir=$(TERRAFORM_DIR) init

infra-format:
	terraform -chdir=$(TERRAFORM_DIR) fmt -recursive

infra-validate: infra-init
	terraform -chdir=$(TERRAFORM_DIR) validate

infra-plan: check-aws infra-init
	terraform -chdir=$(TERRAFORM_DIR) plan -var-file=$(TFVARS) -out=robotek.tfplan

infra-apply: check-aws
	terraform -chdir=$(TERRAFORM_DIR) apply robotek.tfplan

platform-bootstrap:
	bash infra/scripts/remote-bootstrap.sh

runner-register:
	bash infra/scripts/remote-register-runner.sh

platform-verify:
	bash infra/scripts/remote-verify-platform.sh

evidence-export:
	bash infra/scripts/export-evidence.sh

infra-destroy: check-aws
	bash infra/scripts/reset-environment.sh
