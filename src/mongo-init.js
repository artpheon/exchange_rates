dbAdmin = db.getSiblingDB("admin");
dbAdmin.createUser(
    {
        user: "currency_adm",
        pwd: "currency_adm",
        roles: [
            {
                role: "readWrite",
                db: "exchange_rates"
            }
        ]
    }
);

dbAdmin.auth(
    {
        user: "currency_adm",
        pwd: "currency_adm",
        digestPassword: true,
    }
);

db = new Mongo().getDB("exchange_rates");
db.createCollection("rates", { capped: false });
