# React-Django Decoupled App

A full-stack application with React frontend and Django REST API backend, configured to run with both development server and production Gunicorn server.

## Features

- Django REST API backend with PostgreSQL database
- React frontend
- LocalStack for S3 storage simulation
- Docker containerization
- Development and production configurations
- Gunicorn WSGI server for production

## Quick Start

### Development Mode (Django dev server)
```bash
docker-compose up --build
```

### Production Mode (Gunicorn server)
```bash
docker-compose -f docker-compose.prod.yml up --build
```

## Configuration

### Environment Files

- `.env.db` - Database configuration (shared)
- `.env.prod` - Production environment variables

### Key Differences Between Modes

| Feature | Development | Production |
|---------|-------------|------------|
| Server | Django dev server | Gunicorn |
| Debug | True | False |
| Workers | Single-threaded | Multi-worker |
| Logging | Basic | Structured |
| Security | Relaxed | Hardened |

## Services

- **Backend**: Django REST API (Port 8000)
- **Frontend**: React app (Port 3000)
- **Database**: PostgreSQL
- **LocalStack**: S3 simulation (Port 4566)

## Gunicorn Configuration

The production setup uses a custom Gunicorn configuration (`backend/gunicorn.conf.py`) with:

- Dynamic worker count based on CPU cores
- Request timeout of 120 seconds
- Access and error logging
- Worker recycling to prevent memory leaks
- Preloaded application for better performance

## LocalStack Integration

Both development and production modes support LocalStack for S3 storage:

- Automatic bucket creation
- Fallback to local storage if LocalStack unavailable
- Health checks and retry logic

## Security Features (Production)

- Environment-based secret key
- Configurable allowed hosts
- XSS protection
- Content type sniffing protection
- HSTS headers
- Frame options protection

## Usage Examples

### Start development environment:
```bash
docker-compose up
```

### Start production environment:
```bash
docker-compose -f docker-compose.prod.yml up
```

### View logs:
```bash
docker-compose logs backend
```

### Access services:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- LocalStack: http://localhost:4566

## Troubleshooting

1. **Database connection issues**: Ensure PostgreSQL container is running
2. **LocalStack not available**: App will fallback to local file storage
3. **Permission errors**: Check Docker volume permissions
4. **Port conflicts**: Ensure ports 3000, 8000, and 4566 are available
5. **Images not displaying**:
   - Check browser console for image loading errors
   - Ensure media files are being served (fixed in this configuration)
   - Verify image uploads are successful via API response

## Development

To make changes:
1. Modify code in `backend/` or `frontend/` directories
2. Restart containers: `docker-compose restart`
3. For database changes: `docker-compose exec backend python manage.py migrate`