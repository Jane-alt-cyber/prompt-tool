import os
from dataclasses import dataclass

@dataclass
class LLMProvider:
    name: str
    base_url: str
    default_model: str
    env_key: str

PROVIDERS = {
    "deepseek": LLMProvider("deepseek", "https://api.deepseek.com", "deepseek-chat", "DEEPSEEK_API_KEY"),
    "openai": LLMProvider("openai", "https://api.openai.com/v1", "gpt-4o", "OPENAI_API_KEY"),
    "kimi": LLMProvider("kimi", "https://api.moonshot.cn/v1", "moonshot-v1-8k", "MOONSHOT_API_KEY"),
    "claude": LLMProvider("claude", "", "claude-sonnet-4-20250514", "ANTHROPIC_API_KEY"),
}

# 默认供应商（可通过环境变量覆盖）
DEFAULT_PROVIDER = os.environ.get("DEFAULT_PROVIDER", "deepseek")

# 服务端口
PORT = int(os.environ.get("PORT", 8000))

# 上传文件大小限制（10MB）
MAX_UPLOAD_SIZE = 10 * 1024 * 1024
