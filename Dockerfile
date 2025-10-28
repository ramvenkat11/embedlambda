# syntax=docker/dockerfile:1

# ---- Build layer: install Python deps into /opt/python (Lambda looks there) ----
FROM public.ecr.aws/lambda/python:3.12 AS build
WORKDIR /opt/app
COPY requirements.txt .
RUN python -m pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt --target /opt/python --only-binary=:all:

# ---- Final runtime image ----
FROM public.ecr.aws/lambda/python:3.12

# 1) Add site-packages (on sys.path by default for Lambda)
COPY --from=build /opt/python /opt/python

# 2) Add your (large) model as its own layer so code-only changes don't invalidate it
#    Keep the on-disk layout identical to what fastembed expects.
COPY models /opt/models

# 3) Add your function code
WORKDIR /var/task
COPY embed.py /var/task/embed.py

# Optional: ensure offline-only behavior (no HF pulls) and point fastembed to /opt
ENV HF_HUB_OFFLINE=1
ENV FASTEMBED_CACHE_PATH=/tmp/fastembed_cache
ENV MODEL_DIR=/opt/models/model_name

# Your handler is module.function (embed.py has lambda_handler)
CMD ["embed.lambda_handler"]
