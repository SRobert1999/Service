# 🐳 Docker Deployment Guide

## Quick Start

### **1. Prerequisites**
- Docker Desktop installed
- Git (optional)

### **2. Start the application**
```bash
# Clone or navigate to the project directory
cd Service

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

### **3. Access the application**
- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:5000
- **API Documentation**: http://localhost:5000/docs

### **4. Stop the application**
```bash
docker-compose down
```

---

## 🚀 What Happens During Startup

### **Backend Container:**
1. **Builds** the Python environment with all dependencies
2. **Runs database initialization** (`init_db.py`)
   - Creates database schema
   - Adds test data if database is empty
   - Creates default users
3. **Starts FastAPI server** on port 5000

### **Frontend Container:**
1. **Builds** the Vue.js application
2. **Starts development server** on port 8080
3. **Connects** to backend API

---

## 📊 Default Test Data

### **Users:**
- **Admin**: username `admin`, password `parola123`
- **User 1**: username `user1`, password `parola123`
- **User 2**: username `user2`, password `parola123`

### **Jobs & Services:**
- **Stomatolog**: Consultations, extractions, canal treatments
- **Mecanic Auto**: Technical checks, oil changes
- **Electrician**: Electrical diagnosis, installations
- **Altele**: General consulting

### **Sample Appointments:**
- 3 future appointments for testing
- Various statuses (pending, confirmed)

---

## 🔧 Development

### **View Logs:**
```bash
# Backend logs
docker-compose logs -f backend

# Frontend logs
docker-compose logs -f frontend

# All logs
docker-compose logs -f
```

### **Rebuild Services:**
```bash
# Rebuild after code changes
docker-compose up -d --build backend

# Rebuild frontend after changes
docker-compose up -d --build frontend

# Rebuild all services
docker-compose up -d --build
```

### **Access Container Shells:**
```bash
# Access backend container
docker-compose exec backend bash

# Access frontend container
docker-compose exec frontend sh
```

---

## 🛠️ Troubleshooting

### **Common Issues:**

#### **Port Already in Use**
```bash
# Check what's using the ports
netstat -an | grep :5000
netstat -an | grep :8080

# Stop conflicting services or change ports in docker-compose.yml
```

#### **Database Issues**
```bash
# Remove containers and volumes
docker-compose down -v

# Restart fresh
docker-compose up -d
```

#### **Build Errors**
```bash
# Clear Docker cache
docker system prune -a

# Rebuild from scratch
docker-compose build --no-cache
```

#### **Permission Issues**
```bash
# On Linux/Mac, ensure proper permissions
sudo chown -R $USER:$USER .

# On Windows, check Docker Desktop settings
```

---

## 📁 File Structure in Containers

### **Backend Container (/app):**
```
/app
├── src/           # FastAPI application code
├── db/            # Database files (SQLite)
├── migrations/    # Database migration files
├── init_db.py     # Database initialization script
├── requirements.txt
└── Dockerfile
```

### **Frontend Container (/app):**
```
/app
├── src/           # Vue.js source code
├── public/        # Static assets
├── package.json
├── vue.config.js
└── Dockerfile
```

---

## 🔄 Database Persistence

- **Database files** are stored in `./services/backend/db/` on host
- **Data persists** across container restarts
- **To reset data**: Delete `db/programari.db` and restart

---

## 🌐 Network Configuration

### **Internal Communication:**
- Frontend → Backend: `http://backend:5000`
- Backend → Database: SQLite file (internal)

### **External Access:**
- Frontend: `http://localhost:8080`
- Backend API: `http://localhost:5000`

---

## 📝 Environment Variables

### **Backend:**
- `DATABASE_URL`: SQLite database path
- `SECRET_KEY`: JWT signing key (change in production!)

### **Frontend:**
- `API_URL`: Backend API URL

---

## 🔒 Security Notes

### **For Production:**
1. **Change `SECRET_KEY`** in docker-compose.yml
2. **Use HTTPS** with reverse proxy (nginx/traefik)
3. **Remove development tools** and debug modes
4. **Use proper user permissions** on database files
5. **Regular backups** of database

---

## 🐛 Development Tips

### **Hot Reloading:**
- Backend: Code changes auto-reload (thanks to --reload flag)
- Frontend: Vue.js dev server auto-reloads

### **Database Access:**
```bash
# Access database directly
docker-compose exec backend sqlite3 /app/db/programari.db

# Or access local copy
sqlite3 ./services/backend/db/programari.db
```

### **API Testing:**
```bash
# Test health endpoint
curl http://localhost:5000/

# Test jobs endpoint
curl http://localhost:5000/jobs

# Test with authentication
curl -H "Authorization: Bearer <token>" http://localhost:5000/protected
```

---

## 📚 Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Vue.js Documentation](https://vuejs.org/)
- [Project Documentation](./modificari.md)