#!/bin/bash

wt.exe \
        new-tab --title "Server" wsl bash -c "docker compose run --rm server" \
        ';'  new-tab --title "Client 1" wsl bash -c "docker compose run --rm client1" \
        ';' new-tab --title "Client 2" wsl bash -c "docker compose run --rm client2"
