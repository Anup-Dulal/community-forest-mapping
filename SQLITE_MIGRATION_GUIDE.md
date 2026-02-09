# SQLite Migration Guide

## Overview

This document describes the migration from PostgreSQL with PostGIS to SQLite for GitHub-compatible hosting. SQLite provides a lightweight, file-based database solution that requires no external database server.

## What Changed

### 1. Database Driver
- **Before**: PostgreSQL JDBC driver
- **After**: SQLite JDBC driver (org.xerial:sqlite-jdbc)

### 2. Hibernate Dialect
- **Before**: PostgisPG95Dialect (PostGIS-specific)
- **After**: SQLiteDialect (SQLite-specific)

### 3. Geometry Storage
- **Before**: PostGIS geometry types (GEOMETRY(POLYGON, 4326), GEOMETRY(POINT, 4326))
- **After**: WKT (Well-Known Text) strings stored as TEXT columns

### 4. Database Configuration
- **Before**: External PostgreSQL server (localhost:5432)
- **After**: Local SQLite file (./cfm.db)

### 5. Model Classes
- **Before**: JTS Polygon and Point objects
- **After**: String objects containing WKT geometry

## Migration Steps

### Step 1: Update Dependencies

The pom.xml has been updated to:
- Remove PostGIS dependencies
- Add SQLite JDBC driver
- Add SQLite Hibernate dialect
- Keep JTS library for geometry operations

```xml
<!-- SQLite JDBC Driver -->
<dependency>
    <groupId>org.xerial</groupId>
    <artifactId>sqlite-jdbc</artifactId>
    <version>3.44.0.0</version>
</dependency>

<!-- SQLite Dialect for Hibernate -->
<dependency>
    <groupId>org.hibernate.orm</groupId>
    <artifactId>hibernate-community-dialects</artifactId>
    <version>6.3.1.Final</version>
</dependency>
```

### Step 2: Update Configuration

The application.yml has been updated:

```yaml
spring:
  datasource:
    url: jdbc:sqlite:./cfm.db
    driver-class-name: org.sqlite.JDBC
  jpa:
    properties:
      hibernate:
        dialect: org.hibernate.community.dialect.SQLiteDialect
```

### Step 3: Update Database Schema

The schema.sql has been updated to:
- Use TEXT columns for geometry (WKT format)
- Remove PostGIS-specific syntax
- Use SQLite-compatible data types
- Remove GIST indexes (not supported in SQLite)

```sql
-- Before
CREATE TABLE shapefiles (
    geometry GEOMETRY(POLYGON, 4326),
    ...
);

-- After
CREATE TABLE shapefiles (
    geometry TEXT,  -- WKT format
    ...
);
```

### Step 4: Update Model Classes

Model classes have been updated to use String for geometry:

```java
// Before
@Column(columnDefinition = "geometry(POLYGON, 4326)")
private Polygon geometry;

// After
@Column(columnDefinition = "TEXT")
private String geometry;  // WKT format
```

Affected classes:
- Shapefile.java
- Compartment.java
- SamplePlot.java

### Step 5: Update Docker Configuration

docker-compose.yml has been updated to:
- Remove PostgreSQL service
- Remove database initialization
- Use SQLite file volume

```yaml
# Before
services:
  postgres:
    image: postgis/postgis:15-3.3
    ...

# After
# PostgreSQL service removed
# SQLite database file mounted as volume
volumes:
  - ./cfm.db:/app/cfm.db
```

### Step 6: Update Environment Configuration

The .env.example has been updated:

```bash
# Before
SPRING_DATASOURCE_URL=jdbc:postgresql://localhost:5432/cfm
SPRING_DATASOURCE_USERNAME=postgres
SPRING_DATASOURCE_PASSWORD=postgres

# After
SPRING_DATASOURCE_URL=jdbc:sqlite:./cfm.db
SPRING_DATASOURCE_USERNAME=
SPRING_DATASOURCE_PASSWORD=
```

## Geometry Handling

### WKT Format

Geometry is now stored as Well-Known Text (WKT) strings:

```
POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))
POINT (0 0)
```

### Conversion

When reading/writing geometry:

```java
// Convert JTS Polygon to WKT
Polygon polygon = geometryFactory.createPolygon(...);
String wkt = polygon.toText();

// Convert WKT to JTS Polygon
WKTReader reader = new WKTReader();
Polygon polygon = (Polygon) reader.read(wkt);
```

### Querying

SQLite doesn't support spatial queries like PostGIS. For spatial operations:

1. Load geometry as WKT strings
2. Convert to JTS objects in Java
3. Perform spatial operations in Java
4. Store results back as WKT

## Performance Considerations

### Advantages
- No external database server needed
- Single file backup
- Easier deployment
- Lower resource usage
- Suitable for small to medium datasets

### Limitations
- Limited concurrent write support
- No spatial indexing (GIST)
- Slower for very large datasets
- Single-server only

### Optimization Tips

1. **Use Indexes**: Create indexes on frequently queried columns
2. **Batch Operations**: Use batch processing for bulk inserts
3. **Caching**: Implement caching for frequently accessed data
4. **Lazy Loading**: Use lazy loading for relationships
5. **Connection Pooling**: Configure connection pool appropriately

## Testing

### Unit Tests

Tests should work without modification since they use in-memory SQLite:

```java
@DataJpaTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.ANY)
public class RepositoryTest {
    // Tests will use in-memory SQLite
}
```

### Integration Tests

Integration tests have been updated to use SQLite:

```java
@SpringBootTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.ANY)
public class IntegrationTest {
    // Tests will use in-memory SQLite
}
```

### Running Tests

```bash
# All tests
mvn test

# Specific test
mvn test -Dtest=ShapefileUploadServiceTest

# With coverage
mvn test jacoco:report
```

## Backup and Recovery

### Backup

```bash
# Simple file copy
cp cfm.db cfm.db.backup

# Automated backup
0 2 * * * cp /app/cfm.db /backups/cfm.db.$(date +\%Y\%m\%d)
```

### Recovery

```bash
# Restore from backup
cp cfm.db.backup cfm.db

# Verify integrity
sqlite3 cfm.db "PRAGMA integrity_check;"
```

## Troubleshooting

### Database Locked Error

```
Error: database is locked
```

**Solution**: 
- Ensure only one process is writing to database
- Increase timeout: `PRAGMA busy_timeout = 5000;`
- Check for long-running transactions

### Geometry Parsing Error

```
Error: Invalid WKT format
```

**Solution**:
- Verify WKT format is valid
- Check coordinate order (X Y or Y X)
- Use WKTReader for parsing

### Performance Issues

```
Slow queries
```

**Solution**:
- Add indexes on frequently queried columns
- Use EXPLAIN QUERY PLAN to analyze queries
- Consider caching for repeated queries

## Migration Checklist

- [x] Update pom.xml dependencies
- [x] Update application.yml configuration
- [x] Update database schema
- [x] Update model classes
- [x] Update docker-compose.yml
- [x] Update .env.example
- [x] Update documentation
- [x] Run all tests
- [x] Verify functionality
- [x] Test backup/recovery

## Future Considerations

### Scaling to PostgreSQL

If the system needs to scale beyond SQLite capabilities:

1. Create PostgreSQL database
2. Update application.yml to use PostgreSQL
3. Update model classes to use JTS geometry types
4. Migrate data from SQLite to PostgreSQL
5. Update docker-compose.yml

### Hybrid Approach

For very large datasets:

1. Use SQLite for session/metadata
2. Use PostGIS for spatial data
3. Implement data synchronization
4. Use caching layer (Redis)

## Support

For issues or questions:
- Check LOCAL_VALIDATION_GUIDE.md for setup help
- Review QUICK_START.md for quick reference
- Check application logs for error messages
- Review IMPLEMENTATION_GUIDE.md for architecture details

---

**Last Updated**: 2026-02-08
**Status**: Migration Complete
**Database**: SQLite (cfm.db)
