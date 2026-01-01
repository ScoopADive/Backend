# ScoopADive

AI-Powered Integrated Scuba Diving Platform

<img width="1440" height="900" alt="스크린샷 2026-01-01 오후 11 24 35" src="https://github.com/user-attachments/assets/0f0bd233-3322-459e-8a87-afcd15a17f29" />


[**https://scoopadive.com**](https://scoopadive.com)    




# Key Features
1. AI Diving Spot Recommendations - Personalized spots based on user logs and AI analysis.

2. Diver Growth Dashboard - Visualized metrics and skill milestones at a glance.

3. Digital Logbook & WordPress Sync - Easy logging with seamless external blog integration.

4. Community Feed - Connect with divers, find buddies, and check real-time rankings.

> PDF File    
> [**Scoopadive_Key_Features.pdf**](https://github.com/user-attachments/files/24399549/Scoopadive_.pdf)


# Technical Architecture & Infrastructure

This project is built on a **Cloud-Native Distributed Architecture** rather than a standalone executable (`.exe` or `.app`).

### 1. Technical Stack & Delivery
| Component | Tech Stack | Deployment / Hosting |
| :--- | :--- | :--- |
| **Front-end** | React | **AWS CloudFront** (Static Content) |
| **Back-end** | Django DRF | **AWS Lightsail** (Dockerized) |
| **Database** | PostgreSQL / Redis | **Docker Containers** |
| **Automation** | GitHub Actions | **CI/CD Pipeline** |

### 2. Why No Executable (.exe / .app)?
* **Decoupled Structure**: The Front-end and Back-end are separated for scalability; they cannot be bundled into a single file.
* **Cloud Dependency**: The system requires real-time access to Cloud DBs, AI APIs, and Celery workers, which only function in a continuous server environment.
* **Containerized Ops**: All services run in **Docker containers**, ensuring the exact same environment as the production server.

### 3. Proof of Operation
Instead of an installer, we provide the following as evidence of a fully functional system:
* **[Project ScoopADive URL](https://scoopadive.com)** – Access the production environment directly.
* **[docker-compose.yml](https://github.com/ScoopADive/Backend/blob/deploy/docker-compose.yml)**, **[deploy.yml](https://github.com/ScoopADive/Backend/blob/deploy/.github/workflows/deploy.yml)** – View `docker-compose.yml` and `CI/CD` workflow files.
* **[DockerFile](https://github.com/ScoopADive/Backend/blob/deploy/Dockerfile)** – High-level overview of our cloud infrastructure.

> PDF  
> [**ScoopADive_Infrastructure.pdf**](https://github.com/user-attachments/files/24399562/ScoopADive_.pdf)



# Video & Screenshot

You can find the demonstration video (170.5MB) in our **[Latest Release](https://github.com/ScoopADive/Backend/releases/tag/v1.0.0)**.

# Database Schema Design (ERD)

<img width="5191" height="1552" alt="scoopadive_visualized" src="https://github.com/user-attachments/assets/8b645f8d-30ab-4d32-8343-a4e7ed2d172c" />

# System Architecture

<img width="4865" height="1971" alt="scoopadive_stack_readme" src="https://github.com/user-attachments/assets/1d763476-7b90-4879-b021-7438478ffcad" />


# Roles and Responsibilities


### **[Hyojeong Jun](https://github.com/gomdoricake) (Project Lead): Back-end, AI & Infrastructure**
* **Back-end Development:** Designing and implementing the server-side logic and RESTful APIs using **Django DRF**.
* **AI Engine & Logic:** Developing the personalized recommendation algorithm based on user surveys and log data.
* **Infrastructure & DevOps:**
    * Containerizing the application using **Docker** and managing **AWS Lightsail** environments.
    * Building automated **CI/CD pipelines** via GitHub Actions.
* **Data Management:** Architecting the database schema for **PostgreSQL** and managing **Redis** for caching and Celery task brokerage.
* **External Integration:** Synchronizing digital logs with **WordPress** and integrating external AI service APIs.



### **[Gyeongrim Kim](https://github.com/wldmng): Front-end Developer**
* **UI/UX Implementation:** Developing an interactive web interface using **React**, focusing on a seamless user experience for divers.
* **Core Features:** Implementing the AI Spot Recommendation Card UI and the visual Diver Growth Dashboard (charts/graphs).
* **API Integration:** Connecting the front-end to the Django REST API to fetch and display real-time data.
* **Optimization:** Ensuring responsive design for mobile accessibility and optimizing image rendering for underwater photography.


