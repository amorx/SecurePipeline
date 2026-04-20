# STAGE 1: Builder
FROM python:3.11-slim-bookworm AS builder

WORKDIR /build
COPY requirements.txt .
# Install dependencies to a local folder
RUN pip install --no-cache-dir --user -r requirements.txt

# STAGE 2: Runtime (The actual "Fortress")
FROM python:3.11-slim-bookworm AS runtime

# Create a dedicated security user (No-Root!)
RUN groupadd -g 1000 vaultgroup && \
    useradd -r -u 1000 -g vaultgroup vaultuser

WORKDIR /home/vaultuser/app

# Copy only the installed packages from the builder stage
COPY --from=builder --chown=vaultuser:vaultgroup /root/.local /home/vaultuser/.local
COPY --from=builder --chown=vaultuser:vaultgroup /build/requirements.txt .

# Copy your source code
COPY --chown=vaultuser:vaultgroup src/ ./src/

# Update PATH to find the installed packages
ENV PATH=/home/vaultuser/.local/bin:$PATH
USER vaultuser

# Execute as a module
CMD ["python", "-m", "src.app"]
