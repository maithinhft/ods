# ODS realtime with Flink CDC and StarRocks

Project này xây dựng một nền tảng ODS gần thời gian thực phục vụ analytics và dashboard. Dữ liệu được sinh từ PostgreSQL/MySQL, đồng bộ bằng Flink CDC, lưu vào StarRocks và quan sát bằng Prometheus/Grafana.

## Kiến trúc tổng quan

- `data-generator`: sinh dữ liệu giả lập vào PostgreSQL và MySQL.
- `flink`: chạy Flink cluster và submit các job CDC.
- `starrocks`: chạy StarRocks FE/BE và tạo bảng đích ODS.
- `prometheus`: thu thập metrics.
- `grafana`: trực quan hóa metrics và dashboard.

Luồng dữ liệu chính:

1. PostgreSQL/MySQL là nguồn dữ liệu CDC.
2. Flink CDC đọc thay đổi từ nguồn.
3. Dữ liệu được đẩy vào StarRocks qua sink.
4. Prometheus/Grafana theo dõi trạng thái và hiệu năng hệ thống.

## Yêu cầu trước khi chạy

- Docker và Docker Compose.
- Python 3.12 cho `data-generator`.
- Đã tạo network dùng chung `cdc-network`.
- `/etc/hosts` trỏ được đến `starrocks-fe` và `starrocks-be1`.

Thêm network:

```bash
docker network create cdc-network
```

Thêm hosts entry:

```text
127.0.0.1 starrocks-fe starrocks-be1
```

## Cấu trúc thư mục

```text
data-generator/   # sinh dữ liệu cho PostgreSQL/MySQL
flink/            # Flink cluster, CDC jobs, script khởi động
grafana/          # dashboard và provisioning
prometheus/       # cấu hình scrape metrics
starrocks/        # StarRocks compose và schema ODS
```

## Setup nguồn dữ liệu

### PostgreSQL

Chạy container PostgreSQL với logical replication bật sẵn:

```bash
docker run --name my_postgres \
  -e POSTGRES_PASSWORD=admin \
  -v postgresql_volume:/var/lib/postgresql/data \
  -p 5432:5432 \
  -d --restart unless-stopped \
  pgvector/pgvector:pg16 \
  -c wal_level=logical
```

### MySQL

Chạy container MySQL với binlog và GTID:

```bash
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

## Chạy hệ thống

### 1. StarRocks

```bash
cd starrocks
docker compose up -d
```

Sau khi FE/BE lên ổn định, tạo database ODS và nạp schema:

```bash
mysql -h 127.0.0.1 -P 9030 -uroot -e "CREATE DATABASE IF NOT EXISTS ods;"
mysql -h 127.0.0.1 -P 9030 -uroot ods < init.sql
```

### 2. Flink

```bash
cd flink
docker compose up -d
```

Job CDC dùng các file cấu hình trong `flink/jobs/`:

- `cdc-mysq-to-starrocks.yml`
- `cdc-postgres-to-starrocks.yml`

Script `run-job.sh` là ví dụ submit job qua `flink-cdc.sh`.

### 3. Monitoring

```bash
cd prometheus
docker compose up -d

cd ../grafana
docker compose up -d
```

### 4. Data generator

Thư mục `data-generator/` dùng `uv` và Python 3.12.

```bash
cd data-generator
uv sync
uv run python src/main.py
```

Biến môi trường mà generator cần:

- `POSTGRES_HOST`, `POSTGRES_DBNAME`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`
- `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`

## Dữ liệu và schema

- Dữ liệu đầu vào mẫu nằm trong `data-generator/sample_data/`.
- Dữ liệu đã chuẩn bị nằm trong `data-generator/prepared_data/`.
- Schema ODS và materialized view nằm trong `starrocks/init.sql`.
- Các job CDC map dữ liệu vào schema đích `ods`.

## Cổng dịch vụ

- Flink JobManager: `8081`
- Flink metrics: `9249`
- StarRocks FE: `8030`, `9030`, `9020`
- StarRocks BE: `8040`
- Prometheus: `9090`
- Grafana: `3000`

## Ghi chú vận hành

- Các compose file đều dùng network external `cdc-network`, nên phải tạo network trước khi chạy.
- `starrocks-fe` và `starrocks-be1` cần resolve được trong `hosts` để Flink và các container khác kết nối ổn định.
- Nếu muốn đổi nguồn dữ liệu hoặc thông số CDC, sửa trực tiếp các file trong `flink/jobs/`.
