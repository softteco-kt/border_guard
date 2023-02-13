### Microservice for database management.

At the moment container is designed to run and exit before other containers to apply pending changes to the database, i.e. migrations, sql scripts, etc. Database migrations are applied at this microservice.