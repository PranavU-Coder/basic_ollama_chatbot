FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://ollama.ai/install.sh | sh \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=user . .

RUN chmod +x start.sh

EXPOSE 8501

CMD ["./start.sh"]