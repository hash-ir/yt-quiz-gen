# Use a Python base image
FROM python:3.11-slim
# COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Install curl and other necessary dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
# RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Copy requirements file
COPY requirements.txt .

# RUN /root/.local/bin/uv python install 3.12 && 
# RUN /root/.local/bin/uv venv
# ENV PATH="/app/.venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose port for Gradio
EXPOSE 7860

# Run the application
CMD ["python", "main.py"]