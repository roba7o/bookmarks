FROM python:3.12-slim

WORKDIR /src

RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Copy the source code into the container.
COPY . .

# Then install packages -> requirements.txt can cache
# because it ONLY has third-party dep's. toml will
# attempt to build full project. use uv (pip) in future
RUN pip install .

# Expose the port that the application listens on.
EXPOSE 8000

# Run the application.
CMD ["/venv/bin/python3", "-m", "uvicorn", "src.main:app", "--host=0.0.0.0", "--port=8000"]


