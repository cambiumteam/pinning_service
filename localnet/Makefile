# CLI commands
DOCKER := $(shell which docker)

# Regen configuration.
REGEN := regen-ledger/build/regen
REGEN_VERSION ?= 18e247166d506d6c9b9c444b0b197ae5e3f80efa

# Key configuration.
LOCALNET_KEYRING_DIR ?= $(shell pwd)/keys
KEYRING_ARGS = --keyring-backend test --keyring-dir $(LOCALNET_KEYRING_DIR)
LOCALNET_KEY_NAME ?= localnet_node0
MANAGER_KEY_NAME ?= localnet_manager
SERVICE_KEY_NAME ?= localnet_pinning_service

# Resolver configuration.
RESOLVER_URL ?= http://localhost:8000/resource

###############
### General ###
###############

# Start an existing localnet or init a new one.
start: localnet-start

# Configure a localnet with keys and resolver.
configure: localnet-start keys-init fund-manager define-resolver grant-service-account

# Stop an existing localnet to start later.
stop: localnet-stop

# Clear localnet.
clean: localnet-clean

.PHONY: start configure stop clean

####################
### Regen ledger ###
####################
regen-ledger:
		git clone https://github.com/regen-network/regen-ledger.git
		cd regen-ledger && git checkout $(REGEN_VERSION) && make build

regen-ledger-clean:
		- rm -r regen-ledger

.PHONY: regen-ledger-clean

################
### Localnet ###
################
.testnets: regen-ledger
		$(MAKE) -C regen-ledger localnet-build-env
		$(DOCKER) run --rm -v $(CURDIR)/.testnets:/data regenledger/regen-env testnet init-files --v 4 -o /data --starting-ip-address 192.168.10.2 --keyring-backend=test
localnet-init: .testnets

# Do not use regen-ledger localnet-start target. Volumes cannot be used if the localnet is stopped.
localnet-start: localnet-init
		docker compose up -d
		@echo "Wait for nodes to start."
		sleep 10

localnet-stop:
		docker compose down

localnet-clean: localnet-stop keys-clean
		- sudo rm -r .testnets

define localnet_chain_id
$(shell jq -r .chain_id .testnets/node0/regen/config/genesis.json)
endef
localnet-chain-id:
		@echo $(call localnet_chain_id)

.PHONY: localnet-init localnet-start localnet-stop localnet-clean localnet-chain-id

############
### Keys ###
############

define get_key_address
$(shell $(REGEN) keys show -a $1 $(KEYRING_ARGS))
endef

keys:
		@echo "Creating keys"
		@jq -r .secret .testnets/node0/regen/key_seed.json | $(REGEN) keys add $(LOCALNET_KEY_NAME) --recover $(KEYRING_ARGS)
		@$(REGEN) keys add $(MANAGER_KEY_NAME) --no-backup $(KEYRING_ARGS)
		@$(REGEN) keys add $(SERVICE_KEY_NAME) --no-backup $(KEYRING_ARGS)
keys-init: localnet-start keys

keys-clean:
		- rm -r keys

keys-manager-address:
		@echo $(call get_key_address, $(MANAGER_KEY_NAME))

keys-service-address:
		@echo $(call get_key_address, $(SERVICE_KEY_NAME))


.PHONY: keys-init keys-clean keys-manager-address keys-service-address

#####################
### Account setup ###
#####################

fund-manager: keys-init
		@echo "Funding manager account 500stake"
		$(REGEN) tx bank send $(call get_key_address, $(LOCALNET_KEY_NAME)) $(call get_key_address, $(MANAGER_KEY_NAME)) 500stake --chain-id $(call localnet_chain_id) --fees 2stake -y -b block $(KEYRING_ARGS)
		@echo "Funding manager account 1000testtoken"
		$(REGEN) tx bank send $(call get_key_address, $(LOCALNET_KEY_NAME)) $(call get_key_address, $(MANAGER_KEY_NAME)) 1000testtoken --chain-id $(call localnet_chain_id) --fees 2stake -y -b block $(KEYRING_ARGS)

define-resolver:
		@echo "Defining resolver: $(RESOLVER_URL)"
		$(REGEN) tx data define-resolver $(RESOLVER_URL) --from $(call get_key_address, $(MANAGER_KEY_NAME)) --chain-id $(call localnet_chain_id) --fees 2stake -y -b block $(KEYRING_ARGS)

grant-service-account:
		@echo "Granting service account: authz /regen.data.v1.MsgRegisterResolver"
		$(REGEN) tx authz grant $(call get_key_address, $(SERVICE_KEY_NAME)) generic --msg-type /regen.data.v1.MsgRegisterResolver --from $(call get_key_address, $(MANAGER_KEY_NAME)) --chain-id $(call localnet_chain_id) --fees 2stake -y -b block $(KEYRING_ARGS)
		@echo "Granting service account: feegrant /cosmos.authz.v1beta1.MsgExec,/regen.data.v1.MsgRegisterResolver"
		$(REGEN) tx feegrant grant $(call get_key_address, $(MANAGER_KEY_NAME)) $(call get_key_address, $(SERVICE_KEY_NAME)) --spend-limit 100stake --allowed-messages /cosmos.authz.v1beta1.MsgExec,/regen.data.v1.MsgRegisterResolver --chain-id $(call localnet_chain_id) --fees 2stake -y -b block $(KEYRING_ARGS)

# For testing: register data with a resolver from the service account using authz and feegrant.
register-resolver:
		@echo "Build register-resolver tx.json"
		$(REGEN) tx data register-resolver 1 content.json --from $(call get_key_address, $(MANAGER_KEY_NAME)) --chain-id $(call localnet_chain_id) --fees 2stake --generate-only $(KEYRING_ARGS) > tx.json
		@echo "Execute register-resolver tx.json"
		$(REGEN) tx authz exec tx.json --from $(call get_key_address, $(SERVICE_KEY_NAME)) --chain-id $(call localnet_chain_id) --fee-account $(call get_key_address, $(MANAGER_KEY_NAME))  --fees 2stake -y -b block $(KEYRING_ARGS)

.PHONY: fund-manager define-resolver grant-service-account register-resolver