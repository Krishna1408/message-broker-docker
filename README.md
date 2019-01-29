# message-broker-docker

## Overview

This repo contains two rest services created using python Flask. One of them sends a message and other receives it using rabbitmq as a message broker. All the services are running over docker. There are two more capabilities provided:
1. Fluentd for shipping logs and it also acts as a structured logger.
2. Prometheus is used for monitoring using rabbitmq exporter. 
3. Alertmanager is being used for alerting.
4. Both the producer and consumer services run in parallel.
5. Basic auth is provided using environment variables.

### Python Services

There are two python flask services running. Both are using *pika* client to connect to rabbitmq. Basic auth is provided using environment variables which can be found in docker-compose. You get a welcome message at path `/` for both the python services.

#### Publisher
First is *publisher* which produces data and runs at `localhost:5000`. Publisher can post data using path `/data`. The correct format to send message is using : `message=your_message`

Basic error handling is provided if the payload is not in `message=your_message` format. User will get a message which tell user to use correct format.

#### Subscriber
Second one is *subscriber* which receives messages and it runs at `localhost:5001`. Subscriber can receive data using path `/receive`

##### Note:

docker version: `18.09.0` & docker-compose version: `1.23.2` are used. 


## Deploying 

### To run the deployment:

```
git clone https://github.com/Krishna1408/message-broker-docker.git
cd message-broker-docker
docker-compose up
```

You will see the application stack coming up. Wait for sometime till all the services are up and running.

### To test the deployment:

1. Open a new terminal.
2. Test the publisher application first by running:
```yaml
# curl -d "message={'Hello-1':'hi'}" -X POST http://localhost:5000/data
{
  "Message sent": "{'Hello-1':'hi'}"
}
```
3. Test the subscriber application by running:
```yaml
# curl http://localhost:5001/receive
{'Hello-1':'hi'}
```
4. You can send any number of messages and receive them in correct order.
5. Test the error handling by providing incorrect format:
```yaml
# curl -d "mes={"Hello-2":"hii"}" -X POST http://localhost:5000/data
{
  "message": "Payload is missing parameter 'message'."
}
```


### Fluentd as structured logger:

Fluentd is collecting logs of rabbitmq, prometheus, alertmanager and rabbitmq exporter and then storing them in `/tmp/file` directory. The *file* output plugin of fluentd is used so at first files having name as **buffer.xx.log** will be created. Example:
```
# ls /tmp/file
/tmp/file
buffer.b5809dbc5d4c143bccae1c4266ba48ab2.log.meta
buffer.b5809dbc5d4c143bccae1c4266ba48ab2.log
```

The file with extension `.meta` is a binary file created by fluentd and should be ignored. File with extension .log can be opened to view the logs. More info at : https://docs.fluentd.org/v1.0/articles/out_file#path

### Prometheus integration:

1. Rabbitmq exporter is running at the port 9149 and it is sending metrics to prometheus. User can get the rabbitmq metrics by running:
```
#   curl http://localhost:9149/metrics

# TYPE rabbitmq_channelsTotal gauge
rabbitmq_channelsTotal 0
# HELP rabbitmq_connectionsTotal Total number of open connections.
# TYPE rabbitmq_connectionsTotal gauge
rabbitmq_connectionsTotal 0
# HELP rabbitmq_consumersTotal Total number of message consumers.
# TYPE rabbitmq_consumersTotal gauge
rabbitmq_consumersTotal 0
# HELP rabbitmq_exchange_messages_published_in_total Count of messages published in to an exchange, i.e. not taking account of routing.
# TYPE rabbitmq_exchange_messages_published_in_total counter
rabbitmq_exchange_messages_published_in_total{exchange="",vhost="/"} 2
# HELP rabbitmq_exchange_messages_published_out_total Count of messages published out of an exchange, i.e. taking account of routing.
# TYPE rabbitmq_exchange_messages_published_out_total counter
rabbitmq_exchange_messages_published_out_total{exchange="",vhost="/"} 2
```

2. User can also get prometheus and alertmanager metrics using:
```
# For prometheus
curl http://localhost:9090/metrics
# For alertmanager
curl http://localhost:9093/metrics
```

#### Testing Prometheus

Login to prometheus console using `http://localhost:9090/` 

Rabbitmq metrics can be easily accessed from prometheus dashboard :
![Alt text](images/pro-con-1.jpg?raw=true "Title")


Check the alertmanager from `Alerts` tab:

![Alt text](images/pro-con-2.jpg?raw=true "Title")

Bring down **rabbitmq** to check if se see any alerts using: `docker-compose stop rabbitmq-server`

Check the alertmanager and you should see the alert being created:

![Alt text](images/pro-con-3.jpg?raw=true "Title")


### Cleaning up

```
docker-compose stop
docker rm -f $(docker ps -a -q)
docker image rm -f $(docker image ls)
```


