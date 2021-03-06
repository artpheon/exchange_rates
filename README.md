# exchange_rates

This is an Airflow-based ETL process, which uses <b>exchangerate.host</b>(https://exchangerate.host/) API to gather present and historical data about BTC to USD ratio. Historical data is collected only once starting with the specified date in <b>sources.py</b>. Latest rates are collected and updated once in 3 hours.

All rates are then stored in MongoDB, and can be extracted using the <b>query_db.sh</b> script, or manually at http://localhost:27017, using currency_adm/currency_adm as login/password.

The ETL process is meant to be running across several <b>Docker</b> containers, using the <b>docker-compose</b> configuration.

How to run exchange_rates:

1. Make sure you have both Docker engine and docker-compose installed:
  - https://docs.docker.com/get-docker/
  - https://docs.docker.com/compose/install/
2. Clone the repo: https://github.com/artpheon/exchange_rates.git
3. Having Docker up and running, run the script while in the same directory:
  
  <code>bash run.sh</code>

4. After all containers have launched and passed the healthchecks, he Airflow dashboard will be available on http://localhost:8080 - log in using airflow/airflow as creadentials.
5. To extract the entries in json format you may use the query_db.sh script:

  <code>bash ./query_db.sh</code>

This will save the entries in dump.json in the directory you are in.

6. To stop the ETL and clear the docker environment, run the command:

<code>
  docker-compose down -f docker-compose.yaml --rmi local
</code>
