# Foreword
- Medallion architectures are threated as rigid, step-by-step framework, when they are acttualy a flexible approach to making sense of an envolving landscape.
- Lakehouse combine the best of lakes and warehouses.
- Medallion architectures emerged as the bridge to guide organizations through the lakehouse era.
- data lakes have become the de factor technology for data platforms
- Meddalion architecture are a simple Bronze-Silver-Gold conceptualization of the operating model for running a data lakehouse. An attempt to make a set of complex, flexible technical decisions, an easy-to-understand process to prevent organizations from falling into data swamps
- When implementing a Medallion architecture focus on providing your data consumers with context - organize your data so they understand when it has been cleaned, when it is ready for consumption. Help them find the data to empower their work as fast and easily as possible

# The evolution of Data Architecture
- creating a robust data architecture is one of the most challenging aspectos of data management
- A data archtecture** features three layers:
 1. ***data providers**: reprents the diverse sources from wich data is extracted. This extracted data is characterized by a mixture of data types, formats, and locations spread across different organizations 
 2. **distribution layer**: represents the distribution platform and is complex due to the vast array of tools and technologies available. This layer is where medallion archtecture is implmented
 3. **data consumers**: characterized by consuming data services, like business intelligence, machine learning and artificial intelligence
 4. **metadata and governance layer**: crucial for managing and overseeing the entire data architecture
 - Modern data stack: shift from propietary to more adaptable, open source and distributed data architectures. Its not a complete data plataform, it requires the integration of many independent services and tools, a significant barrier to entry.

 ## What is a Medallion Architecture?
 - A Medallion architecture is a data design pattern used to logically organize data, most often in a lakehouse, using three layers for the data platform, with the goal of incrementally and progressively improving the structure and quality of data as it flows through each layer of data architecture (from Bronze -> Silver -> Gold Layer)

 ### Bronze Layer
 - store raw data from various sources in its native structure, serving as a historical record and a reliable initial storage

 ### Silver Layer
 - refines and standardizes raw data form complex analytics through quality checks, standardization, deduplication and other transformations

 ### Gold Layer
 - optimizes refined data for specific business insights and decisions. It aggregates, summarizes, and enriches data for high-level reporting and analytics, emphasizing performance and scalability to provide fast access to key metrics and insights

- Engineers in the context of data virtualization argue for keeping all historical data within the OLTP system instead of moving it to a lakehouse. However, storing vast amounts of historical data can bog down OLTP system, resulting in slower transaction processing and update times. The standard practice is to move this data to a middle layer.
- Slowly Changing Dimensions (SCDs) is a type of dimension thar has attributes to show change overtime
- SCD1: overwrite, involves simply updating the existing record with the new information. You only needs the most current data.
- SCD2: add new row, involves creating a new record for each change that occurs, while still retaining the original record. Useful when historical data is important and needs to be preserved
- SCD3: add new attribute, involves adding a new attribute to the existing record to track changes. This method is useful when only a few attributes need to be tracked over time
- The concept of layring data isnt new and proven to be eddective strategy for separating different concerns which helps in organizing ana managing data more efficiently
- data modelings is crucial, boost performance, reduce redudancy and serve as interface for business
- **schema-on-read** approach allows to ingest and store data without fixed structure and only define the schema when you read the data. The schema is applied dynamically when the data is accessed for reading. Some engineers mistakenly believe that schema on read eliminates the need for data modeling. Without proper data modeling, data will be incoplete or low of quality, and integrating data from multiple sources becomes challeging. Inadequate data modeling can also lead to poor performance
- HDFS divides data into large blocks of 128MB, wich are then distributed and replicated across nodes (default 3 replicas) within a network of computers. Blocks are immutable, you can only insert and append records, not directly update data
- Small files: numerous small files can lead to excessive processing tasks, causing significant overhead. Data is spread across multiple machines and is replicated to enhance parallel processing. Each file, regardless of its size, occupies a minimun default blockl size in memory because data and metadata are stored seperately. Small files can place excessive pressure, many files means bigger metadata what can drastically reduce the read performance.
- Horizontal scaling involves adding more machines or nodes to a system to handle increased load, distributing the workload across multiple servers
- Map: the input data is divides into smaller chuncks, wich are processed in parallel across the nodes in the cluster. However,m if the data is not evenly distributed across the nodes, some nodes may complete their tasks faster than others, potentially reducing overall performance
- Shuffle: the output data from the map phase is sorted and partitioned before being transfered to the reduce phase. if output data is voluminous and needs to be transferred across the network, this phase can be time-consuming
- Reduce: the shuffled data is aggregated and further processed in parallel across the nodes in the cluster
- Since data needs to be transfered across the network, it is crucial that tasks run efficiently
- External table: mount a file to query it, metastore do not manage it. When you drop it it only removes the metadata, leaviung the underlying data intact
- Managed table: Fully controlled by metastore. When you drop it delete both the tables metadata  and its underlying data
- Hive metastore is a central repository that store metadata abount the tables, columns and partitions, this metadata includes the data schema and data location
- disk seeking is time-consuming and significantly slows down the overall operation

### Spark
- This framework was designed to facilitate large-scale data processing more efficiently by storing data in memory rather than reading it from disk for every operation
- Spark needs to read data from the disks to bring it into memory, when restarting the cluster, all in-memory data is lost, and the data must be reloaded
- By 2013, the Spark project to ensure its long term sustainability and vendor independence, the ream decided to contribute Spark as open source to the Apache Softare Foundation
- Spark 1.0 in 2014, Spark 2.0 in 2016, Spark 3.0 in 2020 and Spark 4.0 in 2025
- it can operate independently in a cluster of virtual machines or within containers managed by Kubernets

### Data lakes
- Data lakes are robust solutions for storing massive volumes of raw data in various formats, bothe structured and unstructured.
- Data lakes rely on open source formats like Parquet, wich are widely recognized by numerous tools, ensuring seamless interoperability

### Lakehouse Architecture
- Vendors replaced the HDFS with cloud-based object storage. With object storage,the data blocks of a file are kept together as an object, together with its relevant meta data and a unique identifier.
- Object storage are generally less expensive for storing large volumes of data, but it also scales more efficiently. Every major cloud provider offer such service, complete withe robust service-level agreements (SLAs) and options for geographical replication

### Databricks
- In 2013, the creatos of Spark founded a company named Databricks to support and monetize Spark's rapid growth
- Databrticks opted for a cloud-only distribution called Databricks Cloud. Databricks started first with Amazon Web Services. In 2017, Databricks announced as a first-party service on Microsoft Azure via its integration, Azure Databricks.
- Databricks is the leading force behind Apache Spark's roadmap and development. it offers a managed platform, whereby users get the full benefits of Spark, without the need to manage the underlying infrastructure.

### Open Table format
- Parquet: columnar storage open source file format used in Delta and Iceberg. Beneficial for analytical queries involving aggregations, filtering and sorting of large datasets. They enhance performance and efficiency by drastically reducing I/O operatioins and the amount of data loaded into memory. Columnar formats offer better data compression, wich saves storage space and reduces the costs associated with managing large volumes of data
- Recognizing the critical need for improved transactional guarantees, enhanced metadata handling, and stronger data integrity with columnar storage formats, several projects were developed and later became open source, such as Delta Lake, Apche Hudi, and Apache Iceberg.
- In 2019, Dabricks launched Delta Lake, wich brought ACID transactions, scalable metadata handling, and unified streaming and batch data processing, all while ensuring data integrity through scham enforcement and evolution.
- Delta Lake exclusively utilizes the Parquet format for data storage and employs Snappy as the default compression algorithm
- In 2024, Databricks acquire Tabular, a company that supports the apache Iceberg initiative. The mais objective of this acquisition is to enable compability between various lakehouse platforms.
- Uniform: allow write data primarly to Delta Lake the asynchronously generate the metadata for Apache Iceberg and Hudi.