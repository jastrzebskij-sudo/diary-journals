# XTTS-v2 batch TTS for Pascal GPUs (GTX 1080 Ti): torch cu126 build, CUDA 12.6 runtime image.
FROM nvidia/cuda:12.6.3-runtime-ubuntu24.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1

RUN apt-get update \
 && apt-get install -y --no-install-recommends python3 python3-venv ffmpeg libsndfile1 ca-certificates \
 && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.13.6 /uv /usr/local/bin/uv

# Non-root user; UID/GID should match the owner of /srv/tts-out on the host.
ARG UID=1000
ARG GID=1000
RUN (getent group ${GID} || groupadd -g ${GID} tts) \
 && (getent passwd ${UID} && userdel -r $(getent passwd ${UID} | cut -d: -f1) || true) \
 && useradd -m -u ${UID} -g ${GID} -s /bin/bash tts
USER tts
WORKDIR /app

COPY --chown=${UID}:${GID} requirements.lock ./
RUN uv venv --python /usr/bin/python3 /home/tts/venv \
 && uv pip install --python /home/tts/venv/bin/python \
      --index-url https://download.pytorch.org/whl/cu126 \
      --extra-index-url https://pypi.org/simple \
      --index-strategy unsafe-best-match \
      -r requirements.lock

COPY --chown=${UID}:${GID} scripts ./scripts

ENV PATH=/home/tts/venv/bin:$PATH \
    CUDA_DEVICE_ORDER=PCI_BUS_ID \
    TTS_HOME=/app/models \
    HF_HOME=/app/models/hf

ENTRYPOINT ["python"]
CMD ["scripts/list_speakers.py"]
