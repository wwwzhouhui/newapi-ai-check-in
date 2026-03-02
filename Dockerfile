# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    TZ=Asia/Shanghai

WORKDIR /app

# camoufox/playwright 运行所需系统依赖 + xvfb（无头环境跑浏览器）
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl xvfb \
    libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 \
    libgbm1 libasound2 libpango-1.0-0 libcairo2 libgtk-3-0 libx11-xcb1 libxshmfence1 \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# 先拷贝依赖清单，利用 Docker layer cache
COPY pyproject.toml uv.lock ./

# 安装 uv 并安装项目依赖
RUN pip install --no-cache-dir uv \
    && uv sync --frozen --no-dev

# 拷贝项目代码
COPY . .

# 准备运行目录
RUN mkdir -p /app/storage-states /app/logs /app/screenshots

# 预下载 camoufox 浏览器，避免容器启动时再下载
RUN uv run camoufox fetch

# 与 GitHub Actions 一致：执行主签到脚本
# 由于代码中使用 headless=False，这里通过 xvfb 提供虚拟显示
ENTRYPOINT ["xvfb-run", "-a", "uv", "run", "python", "-u", "main.py"]
