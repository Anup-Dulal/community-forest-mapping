# GitHub Deployment Guide

## Overview

This guide explains how to deploy the Community Forest Mapping system using GitHub Pages for the frontend and a backend service for the API.

## Architecture

```
GitHub Pages (Frontend)
    ↓ HTTP/REST
Backend Service (Spring Boot + SQLite)
    ↓ SQL
SQLite Database (cfm.db)
```

## Prerequisites

- GitHub account
- GitHub repository
- Backend hosting service (Railway, Render, Fly.io, etc.)
- Domain name (optional)

## Step 1: Prepare Frontend for GitHub Pages

### 1.1 Update Frontend Configuration

```bash
cd community-forest-mapping/frontend
```

Update `vite.config.ts` or `package.json` for GitHub Pages:

```javascript
// vite.config.ts
export default {
  base: '/community-forest-mapping/',  // If deploying to subdirectory
  // or
  base: '/',  // If deploying to root domain
}
```

### 1.2 Update API URL

Update `src/services/api.ts` to use environment variable:

```typescript
const API_URL = process.env.REACT_APP_API_URL || 'https://api.example.com';
```

### 1.3 Build Frontend

```bash
npm run build

# Output will be in dist/ directory
```

## Step 2: Deploy Frontend to GitHub Pages

### 2.1 Create GitHub Pages Branch

```bash
# Create gh-pages branch
git checkout --orphan gh-pages
git rm -rf .

# Or use existing branch
git checkout -b gh-pages
```

### 2.2 Deploy Using GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: |
          cd community-forest-mapping/frontend
          npm install
      
      - name: Build
        run: |
          cd community-forest-mapping/frontend
          npm run build
      
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./community-forest-mapping/frontend/dist
          cname: example.com  # Optional: if using custom domain
```

### 2.3 Configure GitHub Pages Settings

1. Go to repository Settings
2. Navigate to Pages
3. Select "Deploy from a branch"
4. Choose "gh-pages" branch
5. Save

Frontend will be available at: `https://username.github.io/community-forest-mapping/`

## Step 3: Deploy Backend Service

### 3.1 Choose Hosting Platform

#### Option A: Railway.app

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Deploy
railway up
```

#### Option B: Render.com

1. Connect GitHub repository
2. Create new Web Service
3. Configure:
   - Build Command: `mvn clean package`
   - Start Command: `java -jar target/community-forest-mapping-1.0.0.jar`
   - Environment: Java 17

#### Option C: Fly.io

```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Login
flyctl auth login

# Launch
flyctl launch

# Deploy
flyctl deploy
```

### 3.2 Configure Environment Variables

Set these on your hosting platform:

```bash
SPRING_DATASOURCE_URL=jdbc:sqlite:/app/cfm.db
GIS_SERVICE_URL=https://gis-service.example.com
UPLOAD_DIR=/app/uploads
DEM_CACHE_DIR=/app/dem_cache
EXPORT_DIR=/app/exports
```

### 3.3 Create Dockerfile (if needed)

```dockerfile
FROM openjdk:17-jdk-slim

WORKDIR /app

COPY backend/target/community-forest-mapping-1.0.0.jar app.jar

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "app.jar"]
```

## Step 4: Deploy GIS Service (Optional)

The GIS Service can be deployed separately or as part of the backend.

### 4.1 As Separate Service

```bash
# Create Dockerfile for GIS Service
cd community-forest-mapping/gis-service

# Deploy to hosting platform
# (Similar to backend deployment)
```

### 4.2 As Part of Backend

Integrate GIS Service into Spring Boot application or deploy as sidecar.

## Step 5: Configure CORS

Update backend CORS configuration for GitHub Pages domain:

```java
// CorsConfig.java
@Configuration
public class CorsConfig implements WebMvcConfigurer {
    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/api/**")
            .allowedOrigins(
                "https://username.github.io",
                "https://example.com"
            )
            .allowedMethods("GET", "POST", "PUT", "DELETE")
            .allowCredentials(true);
    }
}
```

## Step 6: Update Frontend Configuration

Update `src/services/api.ts`:

```typescript
const API_URL = process.env.REACT_APP_API_URL || 
    'https://api.example.com';

export const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json'
    }
});
```

## Step 7: Database Backup Strategy

### 7.1 Automated Backups

```bash
# Create backup script
#!/bin/bash
BACKUP_DIR="/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
cp /app/cfm.db $BACKUP_DIR/cfm.db.$TIMESTAMP

# Schedule with cron
0 2 * * * /path/to/backup.sh
```

### 7.2 Cloud Storage Backup

```bash
# Backup to AWS S3
aws s3 cp /app/cfm.db s3://my-bucket/backups/cfm.db.$(date +%Y%m%d)

# Backup to Google Cloud Storage
gsutil cp /app/cfm.db gs://my-bucket/backups/cfm.db.$(date +%Y%m%d)
```

## Step 8: Custom Domain (Optional)

### 8.1 Configure DNS

Add CNAME record:
```
CNAME example.com -> username.github.io
```

### 8.2 Update GitHub Pages Settings

1. Go to Settings → Pages
2. Enter custom domain: `example.com`
3. Enable HTTPS

## Step 9: Monitoring and Logging

### 9.1 Application Logs

```bash
# View logs on hosting platform
# Railway: railway logs
# Render: View in dashboard
# Fly.io: flyctl logs
```

### 9.2 Error Tracking

Consider adding error tracking:
- Sentry
- Rollbar
- Bugsnag

### 9.3 Performance Monitoring

Consider adding monitoring:
- New Relic
- DataDog
- Prometheus

## Step 10: Verification

### 10.1 Test Frontend

```bash
# Open in browser
https://username.github.io/community-forest-mapping/

# Check console for errors
# Verify API calls working
```

### 10.2 Test Backend

```bash
# Test API endpoint
curl https://api.example.com/api/health

# Test database
curl https://api.example.com/api/compartments
```

### 10.3 Test Complete Workflow

1. Upload shapefile
2. Verify DEM download
3. Check compartment generation
4. Verify sample plots
5. Test export functionality

## Troubleshooting

### Frontend Not Loading

```bash
# Check GitHub Pages settings
# Verify base URL in vite.config.ts
# Check browser console for errors
```

### API Calls Failing

```bash
# Check CORS configuration
# Verify API URL in frontend
# Check backend logs
# Verify database connection
```

### Database Issues

```bash
# Check database file exists
# Verify permissions
# Check disk space
# Restore from backup if needed
```

### Performance Issues

```bash
# Check backend logs
# Monitor database size
# Review slow queries
# Consider caching
```

## Scaling Considerations

### Current Setup
- Single backend instance
- SQLite database
- Suitable for small to medium traffic

### Scaling Options

1. **Vertical Scaling**: Increase server resources
2. **Horizontal Scaling**: Multiple backend instances with load balancer
3. **Database Migration**: Upgrade to PostgreSQL for better concurrency
4. **Caching Layer**: Add Redis for distributed caching
5. **CDN**: Use CDN for static assets

## Security Checklist

- [ ] HTTPS enabled
- [ ] CORS properly configured
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention
- [ ] Authentication/Authorization (if needed)
- [ ] Secrets not in code
- [ ] Database backups encrypted
- [ ] Regular security updates

## Maintenance Schedule

### Daily
- Monitor error logs
- Check system health
- Verify backups

### Weekly
- Review performance metrics
- Check disk space
- Verify data integrity

### Monthly
- Update dependencies
- Review security logs
- Test disaster recovery

### Quarterly
- Full system audit
- Performance review
- Capacity planning

## Rollback Plan

### If Deployment Fails

```bash
# Revert to previous version
git revert <commit-hash>
git push

# Redeploy
# (Platform will auto-redeploy)
```

### If Database Corrupted

```bash
# Restore from backup
cp cfm.db.backup cfm.db

# Verify integrity
sqlite3 cfm.db "PRAGMA integrity_check;"
```

## Support

For deployment issues:
- Check platform documentation
- Review application logs
- Check PRODUCTION_READINESS.md
- Review LOCAL_VALIDATION_GUIDE.md

## Deployment Checklist

- [ ] Frontend built successfully
- [ ] GitHub Pages configured
- [ ] Backend deployed
- [ ] Environment variables set
- [ ] CORS configured
- [ ] Database initialized
- [ ] API endpoints working
- [ ] Frontend can reach API
- [ ] Complete workflow tested
- [ ] Backups configured
- [ ] Monitoring enabled
- [ ] Documentation updated

---

**Last Updated**: 2026-02-08
**Status**: Ready for GitHub Deployment
**Database**: SQLite (cfm.db)
