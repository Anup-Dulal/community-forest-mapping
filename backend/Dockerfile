# Production stage - use pre-built JAR
FROM eclipse-temurin:17-jre

WORKDIR /app

# Copy pre-built JAR from local build
COPY backend/target/*.jar app.jar

EXPOSE 8080

CMD ["java", "-jar", "app.jar"]
