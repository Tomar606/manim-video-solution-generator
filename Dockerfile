FROM python:3.11-slim

# Manim needs a C toolchain, cairo/pango, ffmpeg and a LaTeX distribution.
# texlive-* is the bulk of the image; it's what typesets the equations.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    pkg-config \
    ffmpeg \
    libcairo2-dev \
    libpango1.0-dev \
    python3-dev \
    texlive \
    texlive-latex-base \
    texlive-latex-recommended \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    texlive-science \
    dvisvgm \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Requirements first so dependency layers cache across code changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Project folders are created on demand, but seed them so a bind-mounted
# host directory starts with the right shape.
RUN mkdir -p projects assets/sfx

ENV MANIMGL_CACHE_DIR=/tmp/manim_cache \
    PYTHONUNBUFFERED=1

# Synthesize the sound-effect library at build time so the first render has it.
RUN python video.py sfx || true

EXPOSE 8000

# Everything runs through one entrypoint:
#   docker compose run --rm app python video.py build <project>
CMD ["python", "video.py", "--help"]
