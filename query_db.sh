docker exec -i exchange_rates-mongodb-1 mongoexport \
--username currency_adm \
--password currency_adm \
--authenticationDatabase admin \
--db exchange_rates \
--collection rates \
--pretty \
--jsonArray \
--out /tmp/dump.json &&
docker cp exchange_rates-mongodb-1:/tmp/dump.json ./dump.json &&
echo 'saved data into ./dump.json'