FROM python:3.9-slim

# System dependencies for face processing - FIXED VERSION
RUN apt-get update && apt-get install -y \
    libgl1-mesa-dev \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    ffmpeg \
    wget \
    libgthread-2.0-0 \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot files
COPY . .

# Create models directory
RUN mkdir -p /app/models

EXPOSE 8000

CMD ["python", "bot.py"]
