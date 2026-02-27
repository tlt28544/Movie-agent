import os


TZ = "Asia/Singapore"
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465

# 火山引擎 Ark 官方 OpenAI 兼容入口（可通过环境变量覆盖）
ARK_BASE_URL = os.getenv("ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3").rstrip("/")

# Ark 的 model 字段通常建议使用已创建推理接入点的 Endpoint ID（ep-xxxx）。
# 兼容历史变量名：ARK_MODEL_WEBSEARCH。
ARK_MODEL_WEBSEARCH = (
    os.getenv("ARK_ENDPOINT_ID", "").strip()
    or os.getenv("ARK_MODEL_WEBSEARCH", "").strip()
    or "doubao-seed-1-6-250615"
)
