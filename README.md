# glints_data_engineering
# Problem Set
A key part of a Data Engineer’s responsibilities is maintaining the serviceability of Data Warehouse. To achieve this, you will need to understand the set up and operation of a basic Data Warehouse.

In this technical assessment, you are required to submit the setup for the data pipeline of a basic data warehouse using Docker and Apache Airflow.

Your final setup should include the following:

* A source postgres database (Database X)
* A target postgres database (Database Y, which is not the same Docker container as Database X)
* Apache Airflow with webserver accessible from localhost:5884
* A Directed Acyclic Graph (DAG) for transferring the content of Source Database X to Target Database Y
* README.md detailing the usage of your submission

As the focus of this technical assessment is on the set up of a basic data pipeline using Airflow, the content of the table in Source Postgres Database X to be transferred can be determined by the candidate. It can be as basic as:

id	| creation_date | sale_value
----|---------------|-----------
0	| 12-12-21	| 1000
1	| 13-12-21	| 2000

# Introduction
To solve problem set above, we can use docker compose that can cover creating multi container. By using docker compose, we will create 4 containers which are :
* Postgres, as source database
* Another Postgres, as destination database
* Airflow, contains airflow webserver & scheduler
* pgadmin, as Postgres GUI tools

Now let's take a look at docker-compose.yml file
```yml
version: '3.1'

services:
  pg_x:
    image: postgres:latest
    container_name: pg_x
    restart: always
    environment:
      - DATABASE_HOST=127.0.0.1
      - POSTGRES_USER=airflow
      - POSTGRES_PASSWORD=airflow
      - POSTGRES_DB=airflow
    ports: 
      - "5432:5432"
    logging:
      options:
        max-size: 10m
        max-file: "3"
    volumes:
      - ./init-data.sql:/docker-entrypoint-initdb.d/init-data.sql

  pg_y:
    image: postgres:latest
    container_name: pg_y
    restart: always
    environment:
      - DATABASE_HOST=127.0.0.1
      - POSTGRES_USER=airflow
      - POSTGRES_PASSWORD=airflow
      - POSTGRES_DB=airflow
    ports:
      - "5433:5432"
    volumes:
      - ./init-data-pg2.sql:/docker-entrypoint-initdb.d/init-data-pg2.sql

  webserver:
    image: puckel/docker-airflow 
    container_name: airflow
    restart: always
    depends_on:
      - pg_x
      - pg_y
    environment:
      - FERNET_KEY=${FERNET_KEY}
    volumes:
      - ./dags:/usr/local/airflow/dags
    ports:
      - "5884:8080"
    healthcheck:
      test: ["CMD-SHELL", "[ -f /usr/local/airflow/airflow-webserver.pid ]"]
      interval: 30s
      timeout: 30s
      retries: 3

  pgadmin-compose:
    image: dpage/pgadmin4
    container_name: pgadmin
    environment: 
      PGADMIN_DEFAULT_EMAIL: "airflow@gmail.com"
      PGADMIN_DEFAULT_PASSWORD: "airflow"
    ports: 
      - "16543:80"
    depends_on: 
      - pg_x
      - pg_y
    restart: 
      unless-stopped    
```

Run the following script:
```
docker-compose -f docker-compose.yml up -d
```
And we can check the container that's being started using command:
```
docker ps 
```
![Airflow](https://github.com/muhabibi/glints/blob/master/assets/docker%20ps.png?raw=true)

# Setup & Configuration
## Postgres 
In docker-compose.yml file above, we pull images that we need from Docker hub image repository. In this section, we'll start by creating postgres containers (pg_x & pg_y)
```yml
pg_x:
    image: postgres:latest
    container_name: pg_x
    restart: always
    environment:
      - DATABASE_HOST=127.0.0.1
      - POSTGRES_USER=airflow
      - POSTGRES_PASSWORD=airflow
      - POSTGRES_DB=airflow
    ports: 
      - "5432:5432"
    logging:
      options:
        max-size: 10m
        max-file: "3"
    volumes:
      - ./init-data.sql:/docker-entrypoint-initdb.d/init-data.sql
  pg_y:
    image: postgres:latest
    container_name: pg_y
    restart: always
    environment:
      - DATABASE_HOST=127.0.0.1
      - POSTGRES_USER=airflow
      - POSTGRES_PASSWORD=airflow
      - POSTGRES_DB=airflow
    ports:
      - "5433:5432"
    volumes:
      - ./init-data-pg2.sql:/docker-entrypoint-initdb.d/init-data-pg2.sql
```

Above we have create Postgres container, by pulling from postgres image from docker hub image repository. This database will use default port 5432 which exposed to host port 5432. To access this database, we can use our defined credential (user, password & db = 'airflow'). To make it easier for file sharing, we use 'volume' to mount our container volume to host volume. In this case we will initiate data to this database using init-data.sql :
```sql
CREATE TABLE tb_trx_src
(
    id SERIAL NOT NULL,
    creation_date date,
    sale_value bigint NOT NULL
);
    
INSERT INTO tb_trx_src(creation_date, sale_value) VALUES
 (current_date, random() * 100),
 (current_date, random() * 100),
 (current_date, random() * 100),
 (current_date, random() * 100),
 (current_date, random() * 100),
 (current_date, random() * 100),
 (current_date, random() * 100),
 (current_date, random() * 100),
 (current_date, random() * 100),
 (current_date, random() * 100)
```

By the time we run our docker-compose file, after postgres image has been created, the data will also be inserted to this database.

### Postgres 5432 & 5433
We create 2 different databases using different containers, as intented as source (using port 5432) & target/ destination database (using port 5433).

Besides port, we also run another init-data sql file (init-data-pg2.sql). But this file only executes DDL, there's no data insertion to destination database. This is init-data-pg2.sql:
```sql
CREATE TABLE tb_trx_dest
(
    id SERIAL NOT NULL,
    creation_date date,
    sale_value bigint NOT NULL
)
```

## Airflow
We pull airflow image from [puckel/docker-airflow](https://hub.docker.com/r/puckel/docker-airflow/). This container will be created after 2 other containers (pg_x & pg_y) has been created beforehand (defined in 'depends_on', it's used to order container creation). For airflow we use port 5884.
```yml
webserver:
    image: puckel/docker-airflow 
    container_name: airflow
    restart: always
    depends_on:
      - pg_x
      - pg_y
    environment:
      - FERNET_KEY=${FERNET_KEY}
    volumes:
      - ./dags:/usr/local/airflow/dags
    ports:
      - "5884:8080"
    healthcheck:
      test: ["CMD-SHELL", "[ -f /usr/local/airflow/airflow-webserver.pid ]"]
      interval: 30s
      timeout: 30s
      retries: 3
```

### Creating Fernet Key
For encrypted connection passwords, we must have the same fernet_key. By default docker-airflow generates the fernet_key at startup, you have to set an environment variable in the docker-compose file to set the same key accross containers. To generate a fernet_key:
```sh
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```
Then adding the line with the new generated key (including the final "=" to) to my **~/.bash_profile** file in this way: 
```sh
export FERNET_KEY="new_generated_key"
``` 

Also in docker-compose file we add parameter
```yml
environment:
    - FERNET_KEY=${FERNET_KEY}
```    
Now we can access Airflow in our localhost:
```
http://localhost:5884
```

![Airflow](https://github.com/muhabibi/glints/blob/master/assets/airflow.png?raw=true)


### Create Connection
To create connection, visit Airflow GUI. Go to Admins -> Connections. 
For section Host, we can run this script in order to know our host IP.
```sh
ifconfig | grep inet
```
In this case we will create 2 Postgres connection.
![Postgres X connection](https://github.com/muhabibi/glints/blob/master/assets/pgx.png?raw=true)
![Postgres Y connection](https://github.com/muhabibi/glints/blob/master/assets/pgy.png?raw=true)

## Pgadmin
For accessing data in our Postgres, we used Pgadmin4 configured already in the docker-compose file. 
```yml
  pgadmin-compose:
    image: dpage/pgadmin4
    container_name: pgadmin
    environment: 
      PGADMIN_DEFAULT_EMAIL: "airflow@gmail.com"
      PGADMIN_DEFAULT_PASSWORD: "airflow"
    ports: 
      - "16543:80"
    depends_on: 
      - pg_x
      - pg_y
    restart: 
      unless-stopped    
```
Pgadmin is accessible via URL:
```
http://localhost:16543
```
![Pgadmin](https://github.com/muhabibi/glints/blob/master/assets/pgadmin.png?raw=true)

### Create connection
In Pgadmin GUI, use this credential:
> Email : airflow@gmail.com
> Password : airflow

To add connection, click Add New Server then fill in the connection string.
![Pgx Pgadmin](https://github.com/muhabibi/glints/blob/master/assets/pgx_pgadmin.png?raw=true)
![Pgy Pgadmin](https://github.com/muhabibi/glints/blob/master/assets/pgy_pgadmin.png?raw=true)
# Data Transfer 
To transfer data from Postgres X to Postgres Y, we can build a DAG inside transfer_data.py under folder /dags:
```py
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.postgres_operator import PostgresOperator
from airflow.hooks.postgres_hook import PostgresHook
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator

dag_params = {
    'dag_id': 'pg2pg',
    'start_date':datetime(2021, 10, 2),
    'schedule_interval': '@once'
}
def _transfer_data():
    src = PostgresHook(postgres_conn_id='pg_x')
    dest = PostgresHook(postgres_conn_id='pg_y')
    src_conn = src.get_conn()
    cursor = src_conn.cursor()
    dest_conn = dest.get_conn()
    dest_cursor = dest_conn.cursor()
    cursor.execute("SELECT * FROM tb_trx_src")
    dest.insert_rows(table="tb_trx_dest", rows=cursor)
with DAG(**dag_params) as dag:
    t1 = DummyOperator(task_id='start', dag=dag)
    t2 = PythonOperator(
        task_id='transfer_data',
        python_callable=_transfer_data,
        dag=dag)
    t1 >> t2
```

To test the data transfer, we can manually trigger this DAG job via airflow GUI. The script will only run once (defined in 'scheduled_interval':'@once'). And it will insert all of the data in source table (tb_trx_src) to destination table (tb_trx_dest).
![dag_pg2pg](https://github.com/muhabibi/glints/blob/master/assets/dag_pg2pg.png?raw=true)

Table tb_trx_src:
![tb_trx_src](https://github.com/muhabibi/glints/blob/master/assets/pg_x_datainit.png?raw=true)

Table tb_trx_dest before ingestion:
![pg_y_tableempty](https://github.com/muhabibi/glints/blob/master/assets/pg_y_tableempty.png?raw=true)

Table tb_trx_dest after ingestion:
![pg_y_tablefilled](https://github.com/muhabibi/glints/blob/master/assets/pg_y_tablefilled.png?raw=true)

In the last image, we can conclude that we successfully transfer data from Postgres X to Postgres Y using manually trigger Airflow DAG.
