# Docker Compose Development Setup Troubleshooting

## Fixed Issues (Latest Updates)

### ✅ Frontend-Backend Communication
- **Fixed API URLs**: Frontend now uses configurable API_BASE_URL
- **Fixed CORS**: Added proper CORS settings for Docker environment
- **Fixed Image URLs**: Improved image URL resolution in serializers

### ✅ Docker Configuration
- **Fixed service dependencies**: Backend waits for LocalStack health check
- **Fixed node_modules**: Using named volumes to prevent Windows issues
- **Fixed health checks**: Improved LocalStack health check reliability

## Testing Your Setup

### Quick API Test
Run the test script to verify everything works:
```bash
python test-api.py
```

This will test:
- Messages API (GET/POST)
- Images API (GET)
- S3 Debug endpoint

### Manual Testing
1. **Start the application:**
   ```bash
   docker-compose up --build
   ```

2. **Check all services are running:**
   ```bash
   docker-compose ps
   ```

3. **Test the frontend:** Open http://localhost:3000
4. **Test the backend:** Open http://localhost:8000/api/messages/

## Common Issues and Solutions

### 1. "Send" Button Not Working

**Symptoms:**
- Clicking "Send" does nothing
- No error messages in console
- Messages don't appear

**Solutions:**
- Check browser console for CORS errors
- Verify backend is running: `docker-compose logs backend`
- Test API directly: `curl http://localhost:8000/api/messages/`

### 2. Image Upload Not Working

**Symptoms:**
- Upload button does nothing
- Images don't appear in gallery
- "Upload failed" messages

**Solutions:**
- Check LocalStack is running: `docker-compose logs localstack`
- Test S3 debug endpoint: http://localhost:8000/api/debug-s3/
- Verify bucket creation in backend logs

### 3. Images Not Displaying

**Symptoms:**
- Images upload successfully but don't display
- Broken image icons in gallery
- 404 errors for image URLs

**Solutions:**
- Check image proxy endpoint: http://localhost:8000/api/s3-image/[filename]
- Verify S3 storage configuration in backend logs
- Check LocalStack S3 service status

### 4. LocalStack Connection Issues

**Symptoms:**
- Backend fails to connect to LocalStack
- S3 operations timeout
- "Connection refused" errors

**Solutions:**
- Ensure LocalStack is fully started before backend (fixed with health checks)
- Check if port 4566 is available on your system
- On Windows, ensure Docker Desktop is running properly

### 5. Database Connection Issues

**Symptoms:**
- "Connection refused" to PostgreSQL
- Migration failures
- Backend crashes on startup

**Solutions:**
- Wait for PostgreSQL to be fully ready (improved in aws-init.sh)
- Check if port 5432 is available
- Verify environment variables in .env.db

### 6. Frontend Build Issues

**Symptoms:**
- Node modules not found
- Build failures
- Permission errors on Windows

**Solutions:**
- Use named volume for node_modules (implemented)
- Clear Docker volumes: `docker-compose down -v`
- Rebuild containers: `docker-compose build --no-cache`

### 7. Cross-Platform Issues

**Windows-specific fixes:**
- Removed Docker socket mount (not needed for basic functionality)
- Use named volumes instead of bind mounts for node_modules
- Ensure line endings are LF, not CRLF

**macOS/Linux:**
- Should work with current configuration
- Check Docker permissions if needed

## Quick Fixes

### Reset Everything
```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

### Check Service Health
```bash
docker-compose ps
docker-compose logs [service-name]
```

### Test LocalStack Connection
```bash
docker-compose exec backend aws --endpoint-url=http://localstack:4566 s3 ls
```

### Test Database Connection
```bash
docker-compose exec backend python manage.py dbshell
```

### Debug API Endpoints
```bash
# Test messages
curl http://localhost:8000/api/messages/

# Test images
curl http://localhost:8000/api/images/

# Test S3 debug
curl http://localhost:8000/api/debug-s3/
```

## Environment Variables

Ensure these are set in .env.db:
- POSTGRES_DB=django_db
- POSTGRES_USER=django_user
- POSTGRES_PASSWORD=django_password

## Port Conflicts

Default ports used:
- 3000: Frontend (React)
- 8000: Backend (Django)
- 4566: LocalStack
- 5432: PostgreSQL (internal)

Change ports in docker-compose.yml if conflicts occur.

## Development vs Production

The current setup is optimized for development with:
- Debug mode enabled
- CORS allow all origins
- Verbose logging
- LocalStack for S3 simulation

For production, use `docker-compose.prod.yml` instead.