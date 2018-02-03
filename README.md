# Data Pipeline for Training a CNN

### Note
Project has been tested on python 2.7 environment. All the required dependencies are mentioned in [requirements.txt](https://github.com/harishasan/ml_pipeline/blob/master/requirements.txt) file except zookeeper and kafka which are discussed in part 2. Project also contains a folder named [data](https://github.com/harishasan/ml_pipeline/tree/master/data/final_data) which has all the files required to run the project. To install dependencies, open terminal and run:

    pip install -r requirements.txt

## Part 1
### Goal
Build a pipeline that is given input directories, it should load required data, find relationships between data, and return a list of tuples each containing an individual data point.

### Solution
[data_pipeline.py](https://github.com/harishasan/ml_pipeline/blob/master/core/data_pipeline.py) contains the driver code for this part. It has a method `load_all_data` which performs the required operation. To run this part, go to [main.py](https://github.com/harishasan/ml_pipeline/blob/master/main.py) and un-comment line #48 and run following command on terminal:

    python main.py

Few details about the solution:

#### Ensuring Correctness of Contour Parsing
This has been achieved at three levels.
 1. Manual testing.
 2. A unit test for contour parser to ensure it loads data correctly.
 3. An integration test to ensure data mapping between dicom and contour is correct.

####  Production Ready Changes

 1. Functionality in parsing.py has been divided into [Parser](https://github.com/harishasan/ml_pipeline/blob/master/core/Parser.py) and [Utility](https://github.com/harishasan/ml_pipeline/blob/master/core/utils.py) module to ensure separation between different modules.
 2. [Parsers](https://github.com/harishasan/ml_pipeline/blob/master/core/Parser.py) have been moved under classes with a common abstract class to easily incorporate future parsers and changes which effect all of them.
 3. A [DataPoint](https://github.com/harishasan/ml_pipeline/blob/master/core/DataPoint.py) wrapper has been created to encapsulate an individual data point.
 4. A [logging](https://github.com/harishasan/ml_pipeline/blob/master/logging.ini) configuration has been added to easily control and monitor logs.
 5. A [requirements.txt](https://github.com/harishasan/ml_pipeline/blob/master/requirements.txt) has been added to smoothly manage dependencies.

####  Parallelizing Operations for Scale
There can be multiple ways to scale it. Within a single process, multiple threads can be used to perform operations in parallel. DataPoint wrapper can come handy here. It can encapsulate one data point which then can be loaded by any available worker thread. Another way, which is implemented in part 2, is to use message queues. This enables different processes and even different nodes to process the data in parallel.

####  Error Checking in Parallel Approach
A distributed approach will require challenges which are faced by any distributed or parallel system. For example, if a thread or process crashes what happens to data point it was handling? How to ensure message still gets processed and is not lost. We might need some ack based mechanism to ensure all data points gets processed. Similarly, not applicable in current implementation, but if there are data structures maintaining common state then they have to be thread safe.

## Part 2:
### Goal
Build a pipeline that produces batch of 8 data points, in form of two arrays, in a single iteration. These points should be randomly chosen from the data set and loaded asynchronously in a separate process.

### Solutions
The core logic of this pipeline is written in [TrainPipeline](https://github.com/harishasan/ml_pipeline/blob/master/core/TrainPipeline.py) class.  After initially finding the data points using `load_data` method, this class sends data loading request to a separate process by putting a message in a Kafka message queue.  The drive program is [main.py](https://github.com/harishasan/ml_pipeline/blob/master/main.py) which sends a load request every 3 seconds.

A separate process written in [async_data_loader.py](https://github.com/harishasan/ml_pipeline/blob/master/services/async_data_loader.py) listens to kafka topic, processes the received message by loading data and creating two result arrays, and puts the result back to another Kafka topic. This way, any process who is interested in ready to use training data just needs to pick a message from Kafka topic.

To run this independent process, execute following command on terminal:

    python services/async_data_loader.py

But keep in mind this requires running kafka and zookeeper. I ran these two services like this:

    export KAFKA_BIN_PATH=/path/on/your/system/kafka_2.12-0.11.0.0/bin
    sh $KAFKA_BIN_PATH/zookeeper-server-start.sh $KAFKA_BIN_PATH/../config/zookeeper.properties
    sh $KAFKA_BIN_PATH/kafka-server-start.sh $KAFKA_BIN_PATH/../config/server.properties

*Please note, I have not implemented the receiver who listens to this new Kafka topic because (1) we are not doing the actual training here (2) Concept of listening to a Kafka topic and working on messages is already shown in `async_data_loader.py`.*

Let's now discuss various aspects of this solutions.

### Loading Data Asynchronously
The main idea is to off load data loading to a separate process. This requires inter process communication and there can be multiple ways to do it.
1. This can be done via socket programing but it requires a lot of work as it is quite low level API.
2. It can be done by reading/writing files. But this solution would be very difficult to scale.
3. Third option was message queues and I chose it because its simple, fault tolerant, scalable to various threads, processes and even nodes.

### Error Checking and/or Safeguards
Cool thing about message queues like Kafka is that they provides builtin fault tolerance and replication. The exact configuration of brokers, topics, and partitions would need a bit more thinking, calculations and performance bench-marking. Another important aspect to think about is scaling of the worker or consumer side according to the load in message queue. Kafka's concept of consumer groups can come handy here, as it allows different workers to work on the same queue by acting like a team.

### Changes and Future Considerations
 There were some minor changes but nothing major. I recall I added serialization and deserialization methods in the DataPoint class to pass messages through the message queue.

One future concern is to think more about deployment model, is it going to be AWS EC2 instances or something like Kubernetes and Dockers. Another is to do the performance benchmarking to ensure the system responds well against the desired load. Similarly, setting up integration tests to make sure these different components works well with each other. Last but not least, `TrainPipeline` is loading all the data points information once into memory for doing the random selection. There should be and can be better way to handle it. Otherwise, it can end up eating a lot of RAM for very small use case.

### Pipeline Correctness
I ran and tested the pipeline on my local environment. Here are the [logs](https://github.com/harishasan/ml_pipeline/blob/master/logs/train_pipeline.log) containing the train pipeline outputs and here are some [worker logs](https://github.com/harishasan/ml_pipeline/blob/master/logs/worker.log) who is listening on Kafka for data loading requests.

### Further Improvements
I have already covered this in previous points.

### Tests
To run tests, execute following command on terminal:

    pytest /tests

