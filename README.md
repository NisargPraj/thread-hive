# Thread Hive

Thread Hive is a modern social media platform built with a microservices architecture, featuring real-time updates and scalable infrastructure.

## 🏗️ Architecture

The application is divided into frontend and backend services:

### Frontend

- Built with React + TypeScript + Vite
- Features modern UI components with Tailwind CSS
- Responsive design with layout components
- Protected routes for authentication
- Admin dashboard for system monitoring

### Backend Microservices

1. **User Service**

   - Handles user authentication and management
   - Manages user relationships (followers, blocked users)
   - Integrates with Neo4j for social graph

2. **Post Service**

   - Manages post creation and retrieval
   - Handles media uploads
   - Custom permissions and authentication

3. **Admin Service**

   - System health monitoring
   - Service metrics collection
   - Administrative functions

4. **Kafka Consumer**
   - Processes event streams
   - Handles asynchronous operations

## 🚀 Getting Started

### Prerequisites

- Docker and Docker Compose
- Node.js (for frontend development)
- Python 3.x (for backend development)

### Setup Instructions

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/thread-hive.git
   cd thread-hive
   ```

2. **Backend Setup**

   ```bash
   cd backend
   docker-compose up
   ```

   This will start all microservices and required databases.

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## 🛠️ Tech Stack

### Frontend

- React
- TypeScript
- Vite
- Tailwind CSS
- React Router
- Shadcn UI Components

### Backend

- Django/Django REST Framework
- MySQL
- MongoDB
- Neo4j
- Apache Kafka
- Docker

## 📁 Project Structure

```
thread-hive/
├── frontend/                # React frontend application
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/         # Page components
│   │   ├── layouts/       # Layout components
│   │   └── constants/     # Constants and configurations
│
└── backend/
    ├── user-service/      # User management microservice
    ├── post-service/      # Post handling microservice
    ├── admin-service/     # Admin dashboard service
    └── kafka-consumer/    # Event processing service
```

## 🔐 Environment Variables

Each service requires specific environment variables. Example `.env` files are provided for reference:

- `backend/user-service/.env`
- `backend/post-service/.env`
- `backend/admin-service/.env`

## 🌟 Features

- User authentication and authorization
- Post creation and sharing
- User following/blocking system
- Real-time updates via Kafka
- Admin dashboard with system metrics
- Media upload support
- Responsive design
- Protected routes
