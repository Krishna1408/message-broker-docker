# AWS migration of 3 Tier application.

Below are the first steps involved to take any 3 tier application to AWS & Kubernetes:
1. Making the Frontend and backend applications stateless if they require any state. It can be done by storing state in a cache service e.g. Redis or Memcached or AWS Elasticache
2. Dockerize the application stack and test run as Kubernetes pods.
3. VPN setup between onpremise and AWS. 

After the above steps below is what need to be done for cloud migration:
1. Migrating data from on-premise database to database running over AWS it can be either CloudSQL or AWS Instance or statefulset over Kubernetes.
2. Running the application over kubernetes
3. Performance tests over a development and staging (Identical to Production) clusters.
3. DNS switch to new stack over AWS & Kubernetes.

**NOTE**: Make sure that your cluster at cloud is highly secure and compliant to some AWS standards and best practices. I've some such scripts available in my git repo.

## 1. Data migration to Cloud

Databases can be run over cloud over Physical VMs or statefulsets in Kubernetes. Depending on the option we choose the data migration strategy changes. Let's go with a easy scenario to run database over a physical VM. This can be done as below:
1. Setup a database instance over AWS which is in the zone and region closer to your onpremise datacenter.
2. Add the database instance as a Slave to the existing master node in data-center. And slowly migrate data from on-premise to cloud. 
3. Instance of step 2 a user can do pg_baseback or pg_dump depending on the choice of data migration.

### Running database over Kubernetes

Kubernetes now supports running stateful applications as statefulsets. In case postgres is being used, a HA postgres can be easily run over kubernetes using either postgres operator from Crunchy or Patroni from Zalando or Stolon.

## 2. Running Application over kubernetes

In AWS there are two good ways to deploy kubernetes i.e. `KOPS` or `EKS`. Production Kubernetes cluster should be spread across zones for High Availability. Once the kubernetes cluster is setup application can be deployed as below:
1. Using yaml manifests to deploy application and services. Password and keys can be passed via Kubernetes secrets and configurations can be passed as configmaps.
2. Converting the yaml manifests to `helm charts` is very important step as it makes deployment process fast and robust.
3. For storing the state of the service User can use AWS Elasticache or run solution like Redis as a statefulset. There is a Redis-operator also available which can be very useful to manage and operate Redis.
4. Nginx ingress

## 3. Application Switch

Once the performance tests are done and application is deployed over production, we can start to send a small portion of traffic to the Kube cluster e.g. 10%. Once after a day or two we see that there is no huge impact we can start to send more traffic to new Kuber Cluster. 

Once the 100% traffic starts to run in the new Kubernetes cluster we can Promote one of the slave database in AWS as Master and with that our whole stack is running over cloud + Kubernetes

## Performance during Peak Loads

Using helm to deploy applications is very useful to rapidly scale up and scale down applications. `Horizontal Pod Autoscaler` is also a good solution to meet high peaks. A `kubernetes cronjob` can be setup to run around peak hours so that it automatically scale up and scale down application during peak hours.

## Cost effective enviornments

1. A single kube cluster with two name spaces i.e. one for Staging and one for development can be used for testing purposes. The staging setup should be a exact replica of production setup e.g. Similar namespace, similar db setup etc.
2. Keeping the whole stack of development/staging in one zone is a good way to save cost as now user doesn't have to pay `.20$ per GB` accross zones cost.
3. Using automation to create stacks for some quick tests is also a good way. 

## Multiple Deployments

Robust CI-Cd strategy is must to do multiple deployments per day. What I personally use is integration of CricleCi, gihub, helm and container registry to deploy my application over kubernetes.

## Monitoring and centralized logging:

**Monitoring**: Using prometheus federation setup is best way to monitor the application running over physical VM's and kubernetes. prometheus operator is the fastest way to deploy prometheus over Kubernetes.

**Logging**: AWS elasticsearch as a service can be used or else a ELK stack can be created. Fluentd need to be run as daemonset to send logs from Kubernetes to Elasticsearch.

## Blue Green & Rollback:

Helm should be used to create the deployments to run over kubernetes as we can easily scale up, down or destroy the deployments using helm.

Blue Green deployments & Rollbacks can be done by:
1. Using a service mesh like `Istio` which will provide ability to send traffic to multiple deployment versions. We can toggle weight in Istio Virtualservice to 0 & 100 and this will send whole traffic to one app and no traffic to other app.
2. Using shell scripts which update the version in selector for a service to point to blue or green deployment. Once the update is done other deployment can be deleted from helm.
3. Using tools like `heptio ark` when an entire cluster migration is required.

#### Rolling deployments via helm

Rolling updates via helm is for the use-case where testing on staging cluster is so robust that a success there means it can be rolled to production. In such scenario we can choose the Percentage of replicas to be rolled up during Deployment. In case a deployment lead to issues we can easily roll back using `helm history` & `helm rollback` commands.

