# ods
tạo docker network cdc-network
config `127.0.0.1 starrocks-fe starrocks-be1` trong /etc/hosts để khi gửi job thì flink có thể biết đến starrocks-fe và starrocks-be1

# setup source database
* postgresql: 
```docker run --name my_postgres -e POSTGRES_PASSWORD=admin -v postgresql_volume:/var/lib/postgresql/data -p 5432:5432 -d --restart unless-stopped pgvector/pgvector:pg16 -c wal_level=logical```

* mysql:
chạy container

```
docker run -d \
  --name mysql \
  -p 3306:3306 \
  -e MYSQL_ROOT_PASSWORD=admin \
  -e MYSQL_DATABASE=cdc_db \
  mysql:8.0 \
  --server-id=1 \
  --log-bin=mysql-bin \
  --binlog-format=ROW \
  --binlog-row-image=FULL \
  --binlog-expire-logs-seconds=864000 \
  --gtid-mode=ON \
  --enforce-gtid-consistency=ON
```
