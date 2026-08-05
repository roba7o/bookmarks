FROM ghcr.io/astral-sh/uv:python3.12-trixie-slim

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --locked

# Copy the source code into the container.
COPY . .

# Expose the port that the application listens on.
EXPOSE 8000

# set venv path that uv has made
ENV PATH="/app/.venv/bin:$PATH"

# Run the application.
CMD ["uvicorn", "bookmarks.main:app", "--host=0.0.0.0", "--port=8000"]


