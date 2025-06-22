# React-Django Decoupled App

A full-stack application with React frontend and Django REST API backend, configured to run with both development server and production Gunicorn server.

## Features

- Django REST API backend with PostgreSQL database
- React frontend
- LocalStack for S3 storage simulation (exclusive storage)
- Docker containerization
- Development and production configurations
- Gunicorn WSGI server for production
- All file uploads stored exclusively in simulated S3

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

Both development and production modes use LocalStack exclusively for S3 storage:

- Automatic bucket creation
- All file uploads stored in simulated S3
- No local file storage fallback
- Health checks and retry logic
- Migration script available to move existing files to S3

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
2. **LocalStack not available**: App requires LocalStack for S3 storage
3. **Permission errors**: Check Docker volume permissions
4. **Port conflicts**: Ensure ports 3000, 8000, and 4566 are available
5. **Images not displaying**:
   - Check browser console for image loading errors
   - Ensure LocalStack S3 is running and accessible
   - Verify image uploads are successful via API response
   - Run migration script to move existing local images to S3

## Migration to S3

To migrate existing local images to LocalStack S3:

```bash
docker-compose exec backend python migrate_to_s3.py
```

This script will:
- Move all existing local images to LocalStack S3
- Update database records to point to S3 URLs
- Provide a summary of migrated files

## Development

To make changes:
1. Modify code in `backend/` or `frontend/` directories
2. Restart containers: `docker-compose restart`
3. For database changes: `docker-compose exec backend python manage.py migrate`