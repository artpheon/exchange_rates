mkdir -p ./logs ./plugins
echo -e "AIRFLOW_UID=$(id -u)" > .env
docker-compose -f docker-compose.yaml up --build