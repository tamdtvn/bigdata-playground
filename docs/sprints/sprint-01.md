# Sprint 1 – Docker Fundamentals

## Goal
Understand why Docker exists.

## Sessions

### Session 1 – Why Docker Exists

Learned:
- Environment Drift
- Reproducible Environment
- Docker standardizes application environments.

Lessons Learned:
- Technology should be understood through the problem it solves.

### Session 2 – Image vs Container

Learned:
- Docker Image is a packaged environment/artifact.
- Container is a running instance of an image.
- Multiple containers can be created from the same image.
- Changes inside one container do not automatically change other containers.
- Images should be treated as immutable artifacts.

Key Insight:
- Dockerfile: describes how to build an Image. 
- Image: is the built artifact/template. 
- Container: is a runtime instance of Image.
- Workflow:
                    ┌──────────────┐
                    │ Dockerfile   │
                    └──────┬───────┘
                           │
                        build
                           │
                           ▼
                    ┌──────────────┐
                    │ Docker Image │
                    └──────┬───────┘
                           │
                         push
                           │
                           ▼
                    ┌──────────────┐
                    │   Registry   │
                    └──────┬───────┘
                           │
                         pull
                           │
                           ▼
                    ┌──────────────┐
                    │  Container   │
                    └──────────────┘

### Docker Desktop
| Thành phần        | Vai trò                                    |
| ----------------- | ------------------------------------------ |
| **Docker CLI**    | Nhận command từ chúng ta                   |
| **Docker Engine** | Thực hiện việc build/run/manage containers |
| **Docker Image**  | Artifact dùng để tạo container             |
| **Container**     | Runtime instance                           |

### Session 3 – Dockerfile & Image Layers

#### Goal
Build the first custom Docker image and understand build cache.

#### Key Lessons
- Dockerfile defines image build instructions.
- `FROM` selects a base image.
- `COPY` adds application files during build.
- `CMD` defines the default runtime command.
- Docker images are built from layers.
- Docker uses build cache.
- Changing an instruction/input can invalidate subsequent cached steps.
- Put stable dependencies before frequently changing application code.

#### Key Insight
Dockerfile order affects build efficiency.

### Session 4 – Build Context & .dockerignore

#### Goal
Understand Docker build context and control which files are available during build.

#### Learned
- `.` specifies the build context.
- Docker build can only access files available in the build context.
- `.dockerignore` excludes files from the build context.
- `COPY` cannot copy files excluded by `.dockerignore`.
- Files outside the build context cannot be copied.
- `COPY . .` should be used carefully.
- Build context affects performance, security, and maintainability.

#### Experiment
Verified that:
- Files in the build context can be copied into an image.
- Files excluded by `.dockerignore` cannot be copied.
- Container filesystem reflects what was included in the image.

### Session 5 – Docker Network & Compose

#### Goal

Understand how multiple Docker containers communicate and introduce
Docker Compose as a way to define a multi-container application.

#### Learned

- Containers communicate through Docker networks.
- `localhost` inside a container refers to that container itself.
- Containers on different networks cannot automatically communicate.
- Docker provides DNS-based service discovery within a shared network.
- Containers should communicate using service names rather than IP addresses.
- Container IP addresses are ephemeral infrastructure details.
- Docker Compose automatically creates a default network for an application.
- Compose service names can be used for service-to-service communication.
- Docker Compose provides a declarative way to define multi-container systems.

#### Experiments

1. Created a custom Docker network manually.
2. Started PostgreSQL on the network.
3. Started a Python container on the same network.
4. Verified that `postgres` resolves to the PostgreSQL container.
5. Deleted and recreated the PostgreSQL container.
6. Observed that the container IP may be reused, confirming that applications should not depend on container IP addresses.
7. Created a `compose.yaml` with PostgreSQL and Python services.
8. Verified that Docker Compose automatically created a default network.
9. Verified communication between services using the service name `postgres`.

#### Key Insight

Applications should depend on stable service names rather than ephemeral container IP addresses.

Docker Compose allows us to describe the desired multi-container environment declaratively instead of manually running and connecting
individual containers.

#### Definition of Done

- [x] Understand Docker network basics.
- [x] Understand container-to-container communication.
- [x] Understand Docker DNS/service discovery.
- [x] Understand why container IPs should not be hard-coded.
- [x] Create and inspect a Docker network.
- [x] Verify service discovery with `getent hosts`.
- [x] Create a basic `compose.yaml`.
- [x] Run multiple services with `docker compose up`.
- [x] Verify the automatically created Compose network.