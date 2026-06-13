FROM python:3.12-slim

WORKDIR /app

# establish a install cache for the packages only
# any change to src does not affect cache
# either change to requirements.txt (two sources of truth)
# or use uv pip install...
COPY pyproject.toml ./
RUN pip install --no-cache-dir .

# Copy the source code into the container.
COPY . .

# Expose the port that the application listens on.
EXPOSE 8000

# Run the application.
CMD ["python3", "-m", "uvicorn", "src.main:app", "--host=0.0.0.0", "--port=8000"]


