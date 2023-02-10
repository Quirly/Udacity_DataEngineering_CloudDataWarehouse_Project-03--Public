# **Udacity Data Engineering Nanodegree**

# **Project 1: Data Modeling with Postgres**

# (1) Scope

Sparkify, a tech startup company, is hosting a new music streaming app. Management collects data on songs and user activity. The data is stored in JSON files which is not easy to query.

There is JSON metadata (song data) and JSON logs on user activity (log data) stored in an Amazon S3 data lake named "udacity-dend". All song and log data in this data lake data shall be transferred to a data warehouse in Amazon Redshift. Best practices in data warehousing shall be considered. Thus, the first goal is to transfer the data from S3 to staging tables within our Amazon Redshift data warehouse. In a further step, we will then query the staging tables with respect to our created star schema and insert data systematically to our fact and dimension tables.

As technology we will use Amazon Web Services in combination with boto3 library using Python for coding. An EC2 instance
will be set up, Anaconda will be installed on this virtual machine with a Linux AMI (e.g. Ubuntu). We will use Jupyter notebooks for development and debugging. After finalization, we can use the command line to run our data pipelines.

# (2) How to Run Notebooks, Description of Workflow

Please create an Amazon EC2 instance with a Linux AMI. Select a key pair and store this key pair on your disk. Then donwload Anaconda3. Please install Anaconda3 on this machine. Then create an environment named 'Udacity' using the yaml file "Udacity_Project3.yml". Activate this environment within Conda and import "Udacity_Project3.yml".

- **2.2.1** Please create an environment using the \*.yml file. You can do this by

  *conda env create -f Udacity_Project3.yml*

- **2.2.2** Please activate this environment

  *conda activate Udacity*

- To run *.ipynb files type in *"jupyter notebook --no-browser"\* in your shell when the environment is activated

- In your Jupyter Notebook please ensure that "Python3" is selected as kernel

- **2.2.3** Connect to your EC2 instance using port forwarding

If all this works please open another shell, move to the folder where your key-pair is stored and connect to your EC2 instance from Terminal from there. Please replace *key-pair.pem* with the name of your key pair and *yourpublicipofEC2 by the public *"Public IPv4 DNS"* of your instance which you can find within AWS Management Console as a property of your EC2 instance.

- *ssh -i key-pair.pem 8000:localhost:8888 ubuntu@yourpublicipofEC2*

- **2.2.4** Start Jupyter

- *jupyter notebook --no-browser*

You can now open your Jupyter Notebook and all your files on your EC2 instance typing in "localhost:8000" in your Google Chrome browser.

You will now see the tree structure of your EC2 instance. 

- **2.2.5** Create a new folder "UdacityDWH"

Navigate to this folder in your browser and upload all files of this package.

## (2.3) How to Configure Your Project

To configure your project we first need to create our data warehouse. Before we will do that, we will create a role for
our Redshift service within our AWS account. Please call this role "myRedshiftRole" and attach an "fAmazon S3 Read Only" policy.

- **3.1** Create an IAM role "myRedshiftRole" that has permission to read data from S3

- **3.2** Copy ARN of this role to file *dwh.cfg* in block [IAM_ROLE]

## (2.4) Start Jupyter Notebook and Create Data Warehouse

- **4.1** Run Chapter (0),(1),(2), (3) and (4) of notebook **"Udacity_DataEngNanodegree_Prototype_DWH.ipynb"

## (2.5) Check Status of Data Warehouse Creation

- **5.1** Run Chapter (5) of notebook **"Udacity_DataEngNanodegree_Prototype_DWH.ipynb". As soon as the data warehouse has  
   been created, an endpoint and the arn of your database user will be printed. If you get an error, please just wait, it 
   takes some time to create the warehouse.  Run chapter (4.2) and check status. As long as "ClusterStatus" shows "Creating", wait. As soon as "ClusterStatus" is "available" you can continue with steps in chapter (6).

## (2.6) How to Configure your Data Warehouse - Additional Steps

- **6.1** Copy the DWH endpoint and insert it in your dwh.cfg file in block *[CLUSTER]*. Assign the endpoint string to 
  parameter HOST.

- **6.2** Start your AWS Management Console. Under "Actions" go to "Manage IAM roles" and attach role "myRedshiftRole" to 
  your created cluster (Click on "Associate Role" after having selected "myRedshiftRole" and save changes).

- **6.3** Go to your cluster properties tab. Edit your "Network and Security" settings. Please assign a security group that allows all inbound and outbound traffic to and from your data warehouse.

## (2.7) You are Ready

## (2.8) Project Work and ETL Pipeline

- **8.1** Please move to your terminal shell. Move to your notebook folder/project folder and start IPython typing in "ipython" command into your terminal. 

- **8.2** You can create all tables (your schema) as definied in file "sql_queries.py" typing in "run create_tables.py"

- **8.3** You can run your pipelines and shuffle the data form S3 to your staging tables and then transfer them to your
  star schema typing in the command "run etl.py"

##  (2.9) Working within your Data Warehouse

- **9.1** Open your AWS Management Console, start Redshift.

- **9.2** Connect to your database (Click on "Create a new connection", type in "dwh" for database and "dwhuser" for user,  
  connect)

- **9.3** Open your Query Editor and run individual queries on your data warehouse tables.

- **9.4** Alternatively, run chapter 9 in Jupyter Notebook and execute available analytical queries. A visualization of *Top 10 songplay time in seconds per artist* is shown for demonstration purposes.

## (2.10) Close your connection to database

## (2.11) Delete your Data Warehouse (optional)


# (3) Star Schema and Data Warehouse Design

We will stick to best practices and use a star schema for our data warehouse.

## (3.1) Staging Table

Tables with all raw data attributes, not following a schema. The table design corresponds to the file definitions of the
raw data. As we have log data and song data, we will have two staging tables.

## (3.2) Fact Table

A fact table or a fact entity is a table or entity in a star or snowflake schema that stores measures that measure the business, here how often products (songs) were consumed (listened to). Fact tables and entities aggregate an important part of our numerical data of our Sparkify business. The fact table will be called "Songplays".

## (3.3) Dimension Tables

Dimension tables are master data or meta data that provide further information on certain attributes of our fact table. Here
we will have tables artists (describing what his/her name is and where he/she lives), users (describing a user with name and contract type), time (providing date parameters related to the individual listening events) and songs (describing songs by duration, the artist to whom the song belongs etc.)

## (3.4) Datatypes

We need to find a compromise between storage usage and robustness/flexibility. 

I chose limited varchar types (varchar(x)) for attributes for which I know the maximum length (e.g. weekday). We know for sure that there will be no unknown values here. Thus, we can save storage without affecting robustness/flexibility for e.g. weekday.

I chose limited char/varchar types (char(x),varchar(x)) for attributes containing categorical text data (e.g. level, gender)

I chose limited varchar types (varchar(20)) for identifier data. If one day the numbers won't suffice anymore, new keys containing more characters then can still be separated. Until then, we can save storage.

I chose maximum varchar types (varchar (256)) to have space for 256 characters for attributes that contain lots of text. Alternatively, I chose text as type which is more performant. In a performance optimization process I might substitute all varchar (256) defined fields by text.

For small numerical data (e.g. item in session) I chose smallint. For regular numerical data I chose integer. For time in milliseconds in staging table for log data I chose BIGINT as timestamps in milliseconds are big and need proper storage.

For data containing decimal values I chose numeric. In performance optimizaton I might compare runtimes with FLOAT against NUMERIC. If storage cost is low, I might replace NUMERIC by FLOAT if more performant. If I add data quality checks and constraints, I might keep NUMERIC as I can define the value length in an exact manner.

This is a first rough definition based on the type of data that can be observed. Talking to the domain business we might get further specifications and constraints, thus choosing the best suitable datatype for the individual kind of data.

## (3.5) Diststlye

I have used diststyle ALL for our staging tables as on insert we will have to join data. This solution costs storage as data is duplicated on each node, however saves us time in our JOIN operations.

For all tables where start_time (of songplay) is part of, I chose diststyle KEY, as all data of one event always belongs together. Thus, if we query events, all attributes are always together on one node.

For all other tables I chose the default option diststyle EVEN, therefore I did not declare a distkey in sql_queries.py herefore.

## (3.6) Sortkey

I have used the primary keys as sortkeys and start_time for time-focused tables songplays and time.