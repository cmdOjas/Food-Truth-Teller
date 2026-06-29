FROM python:3.12-slim

WORKDIR /ml

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY ml/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    python -m nltk.downloader stopwords wordnet punkt && \
    python -m spacy download en_core_web_sm

COPY ml/ .

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Generate dataset and train on build
RUN python dataset/generate_dataset.py && python train.py

CMD ["python", "predict.py"]
