docker exec -i mongodb_container mongoexport \
--username currency_adm \
--password currency_adm \
--authenticationDatabase admin \
--db exchange_rates \
--collection rates \
--pretty \
--jsonArray \
--out /tmp/dump.json &&
docker cp mongodb_container:/tmp/dump.json ./dump.json &&
echo 'saved data into ./dump.json'