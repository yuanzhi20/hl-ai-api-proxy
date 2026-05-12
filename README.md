# HL AI API Proxy

国内直连 DeepSeek V4 API，无需翻墙。OpenAI 兼容接口。

## 快速开始

```bash
curl -X POST http://8.209.254.65/v1/chat/completions \
  -H "Authorization: Bearer hl-proxy-token-demo" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-chat",
    "messages": [{"role": "user", "content": "你好"}]
  }'
```

## 价格

| 方案 | 价格 |
|------|------|
| 按量付费 | ¥0.01 / 1K tokens |
| 包月 | ¥99 / 月 |

## API 参考

- **Base URL**: `http://8.209.254.65/v1`
- **模型**: `deepseek-chat`, `deepseek-reasoner`
- **认证**: Bearer Token

### Python

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://8.209.254.65/v1",
    api_key="hl-proxy-token-demo"
)

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": "你好"}]
)
print(response.choices[0].message.content)
```

## 充值

USDT TRC-20: `TWdth6bNRRZqX7NvYnnvWjqM7zPNkYTndg`

## 技术

一个轻量级 Python 代理，转发到 DeepSeek API。源码 80 行。
