## Sample project with microservice architecture.
---

This is a sample application built with microservice architecture with 4 standalone services:
- API
- Simple Parser 
- Message Queue
- Worker


_Note: The microservices are intentionally made as simple as possible to showcase how the entirety of an application works as a system._ 

---
### Application workflow:

--> Parser microservice each 20 minute interval parses the image from given url, saves it to the filesystem and sends its ID to RabbitMQ Exchange \ Queue. 

--> From there, Worker microservice consumer listens to specified Exchange / Queue and redirects messages further to celery tasks, thereby consuming a message from queue.

--> Lastly, workers having received a message, retrieves model's absolute path and makes an HTTP request to the API microservice, after which the records are being updated with the data from API, thus completing the flow.


Overall workflow  | `Parser` --> `RabbitMQ` --> `Celery` --> `API`

---
Start the project with:
```sh
make up
```

It is easy to send custom message to queue with:
```
# Update env variables if needed
export $(cat .env.compose)
make msg
```