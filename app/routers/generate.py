import asyncio
import json
import time
import uuid
import os
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse, Response

from ..config import PROVIDERS, DEFAULT_PROVIDER
from ..services.excel_parser import parse_excel
from ..services.excel_writer import write_output
from ..services.llm_client import (
    get_client, call_llm, format_batch_message,
    parse_premium_response, parse_opensource_response
)
from ..prompts.premium import PREMIUM_SYSTEM_PROMPT
from ..prompts.opensource import OPENSOURCE_SYSTEM_PROMPT

router = APIRouter(prefix="/api", tags=["generate"])

# 内存存储生成结果（生产环境应换 Redis）
results_store = {}


@router.post("/generate")
async def generate_prompts(
    file: UploadFile = File(...),
    provider: str = Form(DEFAULT_PROVIDER),
    model: str = Form(""),
    style: str = Form("暗黑奇幻风"),
    ratio: str = Form("16:9"),
    tone: str = Form("冷暗色调"),
    lighting: str = Form("室内点光源"),
    characters: str = Form(""),
):
    """上传 Excel + 参数，返回 SSE 进度流，最后返回下载 ID"""

    # 验证供应商
    if provider not in PROVIDERS:
        raise HTTPException(400, f"不支持的供应商：{provider}")

    prov = PROVIDERS[provider]
    actual_model = model if model else prov.default_model

    # 检查 API Key
    api_key = os.environ.get(prov.env_key)
    if not api_key:
        raise HTTPException(400, f"服务端未配置 {prov.env_key}，请联系管理员")

    # 读取文件
    file_bytes = await file.read()
    if len(file_bytes) == 0:
        raise HTTPException(400, "上传文件为空")

    # 解析 Excel
    try:
        wb, rows, col_map = parse_excel(file_bytes)
    except Exception as e:
        raise HTTPException(400, f"Excel 解析失败：{str(e)}")

    shots = [r for r in rows if r["type"] == "shot"]
    if not shots:
        raise HTTPException(400, "未检测到有效镜头行")

    global_settings = f"{style}，{ratio}，{tone}，{lighting}"
    task_id = str(uuid.uuid4())[:8]

    async def event_stream():
        client = get_client(provider, api_key)
        premium_results = {}
        opensource_results = {}
        batch_size = 3
        total_batches = (len(shots) + batch_size - 1) // batch_size

        for i in range(0, len(shots), batch_size):
            batch = shots[i:i + batch_size]
            batch_num = i // batch_size + 1
            seq_range = f"S{batch[0]['data'].get('序号','?')}-S{batch[-1]['data'].get('序号','?')}"

            # 进度事件
            yield f"data: {json.dumps({'type': 'progress', 'batch': batch_num, 'total': total_batches, 'range': seq_range, 'step': 'premium'}, ensure_ascii=False)}\n\n"

            user_msg = format_batch_message(batch, global_settings, characters)

            # 优质模型
            try:
                text = call_llm(client, PREMIUM_SYSTEM_PROMPT, user_msg, actual_model, provider)
                parsed = parse_premium_response(text)
                premium_results.update(parsed)
                yield f"data: {json.dumps({'type': 'batch_done', 'batch': batch_num, 'mode': 'premium', 'count': len(parsed)}, ensure_ascii=False)}\n\n"
            except Exception as e:
                for shot in batch:
                    seq = shot["data"].get("序号", "")
                    premium_results[seq] = f"[生成失败: {str(e)[:50]}]"
                yield f"data: {json.dumps({'type': 'batch_error', 'batch': batch_num, 'mode': 'premium', 'error': str(e)[:100]}, ensure_ascii=False)}\n\n"

            yield f"data: {json.dumps({'type': 'progress', 'batch': batch_num, 'total': total_batches, 'range': seq_range, 'step': 'opensource'}, ensure_ascii=False)}\n\n"

            # 开源模型
            try:
                text = call_llm(client, OPENSOURCE_SYSTEM_PROMPT, user_msg, actual_model, provider)
                parsed = parse_opensource_response(text)
                opensource_results.update(parsed)
                yield f"data: {json.dumps({'type': 'batch_done', 'batch': batch_num, 'mode': 'opensource', 'count': len(parsed)}, ensure_ascii=False)}\n\n"
            except Exception as e:
                for shot in batch:
                    seq = shot["data"].get("序号", "")
                    opensource_results[seq] = {"first_frame": f"[失败]", "last_frame": f"[失败]", "video_motion": f"[失败]"}
                yield f"data: {json.dumps({'type': 'batch_error', 'batch': batch_num, 'mode': 'opensource', 'error': str(e)[:100]}, ensure_ascii=False)}\n\n"

            # 避免限流
            if i + batch_size < len(shots):
                await asyncio.sleep(0.5)

        # 生成 Excel
        try:
            output_bytes = write_output(wb, rows, premium_results, opensource_results)
            results_store[task_id] = {
                "data": output_bytes,
                "filename": f"prompt_output_{task_id}.xlsx",
                "created": time.time()
            }
            yield f"data: {json.dumps({'type': 'complete', 'task_id': task_id, 'premium_count': len(premium_results), 'opensource_count': len(opensource_results), 'total_shots': len(shots)}, ensure_ascii=False)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': f'Excel 写入失败: {str(e)}'}, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.get("/download/{task_id}")
async def download_result(task_id: str):
    """下载生成的 Excel"""
    result = results_store.get(task_id)
    if not result:
        raise HTTPException(404, "文件不存在或已过期")

    return Response(
        content=result["data"],
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={result['filename']}"}
    )


@router.get("/providers")
async def list_providers():
    """返回可用的供应商列表（只返回已配置 Key 的）"""
    available = []
    for name, prov in PROVIDERS.items():
        has_key = bool(os.environ.get(prov.env_key))
        available.append({
            "name": name,
            "model": prov.default_model,
            "available": has_key
        })
    return {"providers": available, "default": DEFAULT_PROVIDER}
