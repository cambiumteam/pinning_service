docker run --rm -v $(pwd)/\.testnets:/data ghcr.io/cambiumteam/pinning_service:regen-env \
    testnet init-files --v 4 -o /data --starting-ip-address 192.168.10.2 --keyring-backend=test