#setup flink cdc
mkdir -p flink-cdc && wget -O- https://dlcdn.apache.org/flink/flink-cdc-3.6.0/flink-cdc-3.6.0-1.20-bin.tar.gz | tar -zxvf - -C flink-cdc --strip-components=1

#setup flink env
mkdir -p flink-env && wget -O- https://dlcdn.apache.org/flink/flink-1.20.5/flink-1.20.5-bin-scala_2.12.tgz | tar -zxvf - -C flink-env --strip-components=1
export FLINK_HOME=$(pwd)/flink-env

# setup connector
wget -P ./flink-cdc/lib https://repo1.maven.org/maven2/org/apache/flink/flink-cdc-pipeline-connector-mysql/3.6.0-1.20/flink-cdc-pipeline-connector-mysql-3.6.0-1.20.jar
wget -P ./flink-cdc/lib https://repo1.maven.org/maven2/org/apache/flink/flink-cdc-pipeline-connector-postgres/3.6.0-1.20/flink-cdc-pipeline-connector-postgres-3.6.0-1.20.jar
wget -P ./flink-cdc/lib https://repo1.maven.org/maven2/org/apache/flink/flink-cdc-pipeline-connector-starrocks/3.6.0-1.20/flink-cdc-pipeline-connector-starrocks-3.6.0-1.20.jar

# run flink cluster with docker
docker compose up -d

sleep 5s

# submit job
./flink-cdc/bin/flink-cdc.sh ./jobs/cdc-to-ods.yml \ 
  -Dexecution.target=remote \
  -Drest.address=localhost \
  -Drest.port=8081