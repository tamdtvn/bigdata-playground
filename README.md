# Big Data Playground Sandbox

## Study Methology

- Problem → Hypothesis → Experiment → Observation → Mental Model → Documentation

- Question → Prediction → Experiment → Evidence → Understanding → Code

## Liên quan trực tiếp đến năng lực công nghệ

Một nền kinh tế chỉ học cách sử dụng công nghệ người khác đã giải quyết thường sẽ tích lũy:

    Knowledge of solutions

Nhưng một hệ sinh thái thường xuyên đối mặt với bài toán mới và có khả năng thử nghiệm sẽ tích lũy:

    Knowledge of problems
            +
    Knowledge of trade-offs
            +
    Experimental capability
            +
    Knowledge of failures
            ↓
    Capability to create new solutions

* Hai thứ này khác nhau rất nhiều.

## 1. Project Structure

    bigdata-playground/
    ├── README.md
    ├── .gitignore
    ├── docker-compose.yml
    ├── docs/
    │   ├── architecture.md
    │   ├── progress.md
    │   └── adr/
    ├── datasets/
    ├── playground/
    ├── services/
    └── scripts/

    datasets/     → kho nguyên liệu
    services/     → nhà máy
    playground/   → khu thử nghiệm
    scripts/      → dụng cụ vận hành
    docs/         → bản đồ + hồ sơ thiết kế


## How to run Big Data Playground Sandbox

### Mở repo bigdata-playground trên Windows. Nếu repo đã có sẵn thì pull bản mới nhất:
    > git pull

- Nếu chưa có thì clone repo rồi mở bằng VS Code.

### Mở Docker Desktop và kiểm tra:
    > docker --version
    > docker info
    > docker compose version

* Quan trọng nhất là docker info phải có phần Server: bình thường.

### Đứng ở thư mục root của project và kiểm tra structure hiện tại vẫn đủ các phần chính:
    bigdata-playground/
    ├── datasets/
    ├── docs/
    ├── playground/
    ├── scripts/
    ├── services/
    ├── .gitignore
    ├── docker-compose.yml
    └── README.md

### Kiểm tra environment cũ vẫn dựng được. Vào:
    > cd playground

Validate Compose trước:

    > docker compose config

Nếu không có lỗi thì:

    > docker compose up -d
    > docker compose ps

Ta muốn PostgreSQL có trạng thái kiểu:

    Up ... (healthy)

Kiểm tra dữ liệu và volume từ Sprint trước còn hoạt động:

    > docker compose exec postgres psql -U postgres -d playground

Trong psql:

    > SELECT COUNT(*) FROM orders;

Sau đó:

    > \q

Không quan trọng count bao nhiêu bằng việc PostgreSQL và persistent volume hoạt động bình thường.