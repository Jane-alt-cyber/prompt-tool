import os
import re
from ..config import PROVIDERS


def get_client(provider_name, api_key=None):
    """创建 LLM 客户端"""
    provider = PROVIDERS.get(provider_name)
    if not provider:
        raise ValueError(f"不支持的供应商：{provider_name}")

    key = api_key or os.environ.get(provider.env_key)
    if not key:
        raise ValueError(f"缺少 API Key，请设置环境变量 {provider.env_key}")

    if provider_name == "claude":
        import anthropic
        return anthropic.Anthropic(api_key=key)
    else:
        from openai import OpenAI
        return OpenAI(api_key=key, base_url=provider.base_url)


def call_llm(client, system_prompt, user_message, model, provider_name):
    """调用 LLM"""
    if provider_name == "claude":
        response = client.messages.create(
            model=model,
            max_tokens=4096,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}]
        )
        return response.content[0].text
    else:
        response = client.chat.completions.create(
            model=model,
            max_tokens=4096,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content


def format_batch_message(batch, global_settings, characters):
    """拼装发给 LLM 的消息"""
    msg = f"全局设定：{global_settings}\n"
    msg += f"场次：{batch[0]['scene']['time']}，{batch[0]['scene']['space']}，{batch[0]['scene']['location']}\n"
    if characters:
        msg += f"\n角色卡（⚠️ 根据「人物」列判断用哪个描述，没写Q版的绝对不能用Q版描述）：\n{characters}\n"
    msg += "\n请转化以下镜头：\n"
    for shot in batch:
        d = shot["data"]
        seq = d.get("序号", "?")
        msg += f"{seq} | {d.get('人物','')} | {d.get('镜头','')} | {d.get('景别','')} | {d.get('构图','')} | {d.get('画面内容','')} | {d.get('时长','')}\n"
    return msg


def parse_premium_response(text):
    results = {}
    for line in text.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
        match = re.match(r'^(\d+)\s*\|(.+)$', line)
        if match:
            results[match.group(1).strip()] = match.group(2).strip()
    return results


def parse_opensource_response(text):
    results = {}
    for line in text.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
        match = re.match(r'^(\d+)\s*\|(.+)$', line)
        if match:
            seq = match.group(1).strip()
            rest = match.group(2)
            parts = rest.split('|||')
            if len(parts) == 3:
                results[seq] = {
                    "first_frame": parts[0].strip(),
                    "last_frame": parts[1].strip(),
                    "video_motion": parts[2].strip()
                }
            else:
                results[seq] = {"first_frame": rest.strip(), "last_frame": "[解析失败]", "video_motion": "[解析失败]"}
    return results
