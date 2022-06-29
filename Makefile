.PHONY: task-queue-init-db task-queue-health task-queue-init

task-queue-init-db:
	PYTHONPATH=. procrastinate --app=pinning_service.task_queue.task_queue schema --apply

task-queue-health:
	PYTHONPATH=. procrastinate --app=pinning_service.task_queue.task_queue healthchecks

task-queue-init: task-queue-init-db task-queue-health

task-queue-worker:
	PYTHONPATH=. procrastinate --app=pinning_service.task_queue.task_queue worker


.PHONY: start test test-watch

start:
	uvicorn pinning_service.main:app --reload

test:
	pytest

test-watch:
	ptw

################
### LOCALNET ###
################

# Start an existing localnet or init a new one.
localnet-start:
		$(MAKE) -C localnet start

# Configure the localnet keys and service account. Update .env to match.
localnet-configure:
		$(MAKE) -C localnet configure
		@echo "Configuring .env for localnet"
		cp .env.default .env
		echo "REGEN_CHAIN_ID = \"$$(make -sC localnet localnet-chain-id)\"" >> .env
		echo "REGEN_KEY_ADDRESS = \"$$(make -sC localnet keys-manager-address)\"" >> .env

# Stop an existing localnet to start later.
localnet-stop:
		$(MAKE) -C localnet stop

localnet-clean:
		$(MAKE) -C localnet clean

.PHONY: localnet-start localnet-configure localnet-stop localnet-clean
