# Updates models located in other microservices with disributed version
# Call from project root to update
cat ./migrations/models_dist.py > ./worker/models.py
cat ./migrations/models_dist.py > ./parser/models.py
cat ./migrations/models_dist.py > ./api/db.py