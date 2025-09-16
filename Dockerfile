# Stage 1: Build the backend
FROM python:3.13-slim AS backend-builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Create a non-root user
RUN adduser --disabled-password --gecos "" appuser

# Explicitly create the work directory
RUN mkdir -p /app/backend
WORKDIR /app/backend

# Copy only dependency files first to leverage Docker cache
COPY --chown=appuser:appuser backend/requirements.txt ./

# Copy the rest of the backend application
COPY --chown=appuser:appuser backend/ ./

# Stage 2: Build the frontend (using Nginx for static files)
FROM nginx:alpine AS frontend-builder

WORKDIR /app/frontend

# Copy all frontend files
COPY frontend/ .

# Stage 3: Combine backend and frontend into a single image
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app/backend

# Install Nginx for serving frontend and proxying backend (as root)
RUN DEBIAN_FRONTEND=noninteractive apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends nginx && \
    rm -rf /var/lib/apt/lists/*

# Create a non-root user in the final stage
RUN adduser --disabled-password --gecos "" appuser

# Set ownership of /app to appuser before copying files
RUN mkdir -p /app/frontend && chown -R appuser:appuser /app

# Copy the entire backend application, including the .venv, from the builder stage
COPY --from=backend-builder --chown=appuser:appuser /app/backend /app/backend

# Install dependencies into the virtual environment
RUN pip install --no-cache-dir -r requirements.txt

# Copy frontend from frontend-builder stage
COPY --from=frontend-builder --chown=appuser:appuser /app/frontend /app/frontend

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Ensure Nginx can run as a non-root user by creating its pid directory and giving ownership
RUN mkdir -p /var/run/nginx /var/cache/nginx /var/log/nginx /var/lib/nginx && \
    chown -R appuser:appuser /var/run/nginx /var/cache/nginx /var/log/nginx /var/lib/nginx /etc/nginx/conf.d
# Add user directive and set the pid file location for Nginx
RUN sed -i '1iuser appuser;\n' /etc/nginx/nginx.conf && \
    sed -i 's|pid /run/nginx.pid;|pid /var/run/nginx/nginx.pid;|' /etc/nginx/nginx.conf

# Expose port 8100 (for Nginx)
EXPOSE 8100

# Create a startup script
COPY --chown=appuser:appuser docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

USER appuser

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
