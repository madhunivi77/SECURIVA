FROM python:3.12-slim

WORKDIR /app

# Install uv

RUN pip install uv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

COPY . .

EXPOSE 8000

CMD ["uv", "run", "run.py"]
