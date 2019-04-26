#!/bin/bash
# docker exec -t db-container pg_dumpall -c -U postgres > dump_`date +%d-%m-%Y"_"%H_%M_%S`.sql
docker exec -t modana_wallet_postgres_1 -c -U modana > dump_`date +%d-%m-%Y"_"%H_%M_%S`.sql