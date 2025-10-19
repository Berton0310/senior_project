#!/usr/bin/env python3
"""
研究服務器啟動腳本（獨立版）
- 將原本 src/app/api/main.py 的程式整合進本檔
- 不再以模組匯入方式載入 app
"""

# 基本與路徑設定
import json
import asyncio
import time
from datetime import datetime
from pprint import pformat
import uvicorn
from bson.objectid import ObjectId  # 保留原結構，用於未來擴充（目前未啟用）
from pymongo import MongoClient  # 保留原結構，用於未來擴充（目前未啟用）
from pydantic import BaseModel
from fastapi.responses import FileResponse, StreamingResponse
from fastapi import UploadFile, File, HTTPException
from starlette.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Query, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import sys
import os
import logging
import re
import json
import shutil
from pathlib import Path
import traceback
# 確保可匯入 src.*（供研究代理與設定使用）
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# 第三方套件

# ===== 應用與 CORS 設定 =====
app = FastAPI()

# 設定編碼
if sys.platform == "win32":
    # Windows 系統設定
    import locale
    try:
        locale.setlocale(locale.LC_ALL, 'zh_TW.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_ALL, 'Chinese_Taiwan.950')
        except:
            pass

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 開發環境允許所有來源，生產環境請限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全域驗證錯誤處理器


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"請求驗證失敗: {exc.errors()}")
    logger.error(f"請求體: {await request.body()}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": "請求資料格式錯誤",
            "errors": exc.errors(),
            "body": (await request.body()).decode('utf-8') if request.method == "POST" else None
        }
    )

# ===== 上傳與靜態檔案設定 =====
# 直接指定既有的 tmp 目錄（不自動建立）
TMP_DIR = r"C:\Users\berto\Desktop\capstone project\tmp"
TMP_IMAGE_DIR = r"C:\Users\berto\Desktop\capstone project\tmp\images_table"
TMP_OUTPUT_DIR = r"C:\Users\berto\Desktop\capstone project\tmp\tmp_doc"
MAX_UPLOAD_BYTES = 25 * 1024 * 1024  # 25MB 上限
DOC_ID_DIR = r'C:\Users\berto\Desktop\capstone project\tmp\document_file'
# 將 tmp 目錄掛載為可直接存取的靜態路由
try:
    app.mount("/uploads", StaticFiles(directory=TMP_DIR), name="uploads")
except Exception:
    # 若目錄不存在或其它原因導致掛載失敗，不阻斷服務啟動
    logger.exception("掛載 /uploads 靜態路由失敗，請確認目錄是否存在：%s", TMP_DIR)

# ===== MongoDB 連線設定 =====
client = MongoClient(
    "mongodb+srv://root:root123@cluster0.pbz1j.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
    serverSelectionTimeoutMS=5000,  # 5秒內選擇伺服器
    connectTimeoutMS=10000,         # 10秒連線超時
    socketTimeoutMS=20000,          # 20秒 socket 超時
    maxPoolSize=10,                 # 最大連線池大小
    minPoolSize=1,                  # 最小連線池大小
    maxIdleTimeMS=30000,           # 30秒閒置超時
    retryWrites=True,              # 重試寫入
    retryReads=True                # 重試讀取
)
db = client.test  # database
collection = db.umodoc_main

# 測試 MongoDB 連線
try:
    # 測試連線
    client.admin.command('ping')
    logger.info("✅ MongoDB 連線成功")
except Exception as e:
    logger.error(f"❌ MongoDB 連線失敗: {e}")
    # 不中斷服務，但記錄錯誤

# ===== SSE 工具 =====


def sse_event(payload: dict) -> str:
    try:
        data = json.dumps(payload, ensure_ascii=False)
    except Exception:
        data = json.dumps(
            {"type": "error", "message": "serialization failed"}, ensure_ascii=False)
    return f"data: {data}\n\n"

# ===== 檔案寫入工具 =====


def _write_result_to_file(result: dict, started_at: str, ended_at: str, elapsed_seconds: float, filename: str = "output.txt"):
    """將研究結果寫入檔案（與 run_research.py 一致風格）。"""
    try:
        # 去重 timings：保留每個標籤的最後一次記錄
        if isinstance(result, dict) and "timings" in result:
            timings = result["timings"]
            if isinstance(timings, list):
                # 建立標籤到最後時間的映射
                last_timings = {}
                for timing in timings:
                    if isinstance(timing, str) and ": " in timing:
                        label, time_str = timing.split(": ", 1)
                        last_timings[label] = time_str

                # 重建去重後的 timings
                result = result.copy()
                result["timings"] = [
                    f"{label}: {time_str}" for label, time_str in last_timings.items()]

        with open(filename, "w", encoding="utf-8") as f:
            f.write(
                f"started_at: {started_at}\nended_at: {ended_at}\nelapsed_seconds: {elapsed_seconds:.2f}\n")
            f.write("\n===== result (pretty) =====\n")
            f.write(pformat(result, depth=5, width=120))
            if isinstance(result, dict) and "final_report" in result:
                f.write("\n\n===== final_report =====\n")
                f.write(str(result["final_report"]))
    except Exception as write_err:
        logger.warning(f"寫入 {filename} 失敗: {write_err}")

# ===== 簡易文件暫存（供前端 load-document 使用） =====


DOCUMENT_STORE = {
    "title": "研究文件",
    "content": "<p>尚未有內容</p>",
    "characterLimit": 100000,
}


def _update_document_content(html: str):
    """將 final_report 寫入暫存區，供 /load-document 回傳。"""
    try:
        if html and isinstance(html, str):
            # 若內容包含 Markdown 標題，從第一個 '#' 開始截取
            try:
                first_hash_idx = html.find("#")
                normalized = html[first_hash_idx:] if first_hash_idx != -1 else html
            except Exception:
                normalized = html
            DOCUMENT_STORE["content"] = normalized
    except Exception as e:
        logger.warning(f"更新文件暫存失敗: {e}")

# ===== 資料模型（保留原結構） =====


class DocumentContent(BaseModel):
    html: str
    json_data: dict  # 避免與 BaseModel.json() 衝突
    text: str


class PageSize(BaseModel):
    label: str
    width: float
    height: float
    default: bool


class Page(BaseModel):
    size: PageSize
    # 可擴充其他欄位（zoomLevel, margin 等）


class DocumentData(BaseModel):
    content: DocumentContent
    page: Page
    document: dict


# ===== AI 助手（保留原結構） =====
class AssistantPayload(BaseModel):
    lang: str
    input: str
    command: str
    output: str


class AssistantContent(BaseModel):
    html: str
    text: str
    json_data: dict


class AssistantRequest(BaseModel):
    payload: AssistantPayload
    content: AssistantContent


class AssistantResponse(BaseModel):
    success: bool
    message: str
    content: str = ""
    error: str = ""


# ===== 文檔儲存資料模型 =====
class DocumentContent(BaseModel):
    html: str
    json: dict
    text: str


class PageSize(BaseModel):
    label: str
    width: float
    height: float
    default: bool


class Page(BaseModel):
    size: PageSize
    # 加上其他欄位也可以，如 zoomLevel, margin 等（依需求）


class DocumentData(BaseModel):
    content: DocumentContent
    page: Page
    document: dict


class DocumentSaveRequest(BaseModel):
    documentId: str
    reportTitle: str = ""  # 設為可選，提供預設值
    data: DocumentData  # 使用新的結構化資料格式


class DocumentSaveResponse(BaseModel):
    success: bool
    message: str
    document_id: str = ""
    error: str = ""


class AssistantHandler:
    def __init__(self):
        self.commands = {
            "續寫": self._continue_writing,
            "重寫": self._rewrite,
            "縮寫": self._abbreviate,
            "擴寫": self._expand,
            "潤色": self._polish,
            "校閱": self._proofread,
            "翻譯": self._translate,
            "Continuation": self._continue_writing,
            "Rewrite": self._rewrite,
            "Abbreviation": self._abbreviate,
            "Expansion": self._expand,
            "Polish": self._polish,
            "Proofread": self._proofread,
            "Translate": self._translate,
        }

    def process_command(self, payload: AssistantPayload, content: AssistantContent) -> str:
        command = payload.command.strip()
        selected_text = payload.input.strip()

        print("收到AI助手請求:")
        print(f"  指令: {command}")
        print(f"  選中文字: {selected_text}")
        print(f"  語言: {payload.lang}")
        print(f"  文件內容長度: {len(content.text)} 字元")

        if command in self.commands:
            return self.commands[command](selected_text, content)
        else:
            return self._custom_command(command, selected_text, content)

    def _continue_writing(self, selected_text: str, content: AssistantContent) -> str:
        if not selected_text:
            return "<p>請先選擇要續寫的文字內容。</p>"
        continuation = (
            f"<p>{selected_text}... 這是續寫的內容。根據您提供的文字，我將繼續發展這個主題，"
            f"提供更多相關的資訊和見解。</p>"
        )
        return continuation

    def _rewrite(self, selected_text: str, content: AssistantContent) -> str:
        if not selected_text:
            return "<p>請先選擇要重寫的文字內容。</p>"
        return (
            f"<p>重寫版本：{selected_text}</p><p>這是一個重新表達的版本，保持了原意但使用了不同的表達方式。</p>"
        )

    def _abbreviate(self, selected_text: str, content: AssistantContent) -> str:
        if not selected_text:
            return "<p>請先選擇要縮寫的文字內容。</p>"
        return f"<p>縮寫版本：{selected_text[:50]}...</p>"

    def _expand(self, selected_text: str, content: AssistantContent) -> str:
        if not selected_text:
            return "<p>請先選擇要擴寫的文字內容。</p>"
        return (
            f"<p>擴寫版本：{selected_text}</p><p>這是一個更詳細的版本，包含了更多背景資訊、例子和解釋，讓內容更加豐富和完整。</p>"
        )

    def _polish(self, selected_text: str, content: AssistantContent) -> str:
        if not selected_text:
            return "<p>請先選擇要潤色的文字內容。</p>"
        return (
            f"<p>潤色版本：{selected_text}</p><p>這個版本經過了語言優化，表達更加流暢自然，用詞更加精準。</p>"
        )

    def _proofread(self, selected_text: str, content: AssistantContent) -> str:
        if not selected_text:
            return "<p>請先選擇要校閱的文字內容。</p>"
        return (
            f"<p>校閱結果：</p><p>原文：{selected_text}</p><p>修正建議：已檢查拼字、語法和表達，內容基本正確。</p>"
        )

    def _translate(self, selected_text: str, content: AssistantContent) -> str:
        if not selected_text:
            return "<p>請先選擇要翻譯的文字內容。</p>"
        return (
            f"<p>翻譯結果：</p><p>原文：{selected_text}</p><p>譯文：This is a translated version of the selected text.</p>"
        )

    def _custom_command(self, command: str, selected_text: str, content: AssistantContent) -> str:
        return f"<p>收到自定義指令：{command}</p><p>選中文字：{selected_text}</p><p>這是一個自定義的AI處理結果。</p>"


assistant_handler = AssistantHandler()


# ===== AI 助手 API =====
@app.post("/ai-assistant")
async def ai_assistant(request: AssistantRequest):
    try:
        result_content = assistant_handler.process_command(
            request.payload,
            request.content,
        )
        return AssistantResponse(
            success=True,
            message="AI助手處理成功",
            content=result_content,
        )
    except Exception as e:
        # 僅在伺服器端記錄完整錯誤，避免向使用者洩漏內部細節
        logger.exception("AI 助手處理失敗")
        return AssistantResponse(
            success=False,
            message="AI助手處理失敗",
            error="系統繁忙，請稍後再試",
        )


# ===== 研究頁面與研究 API（非串流） =====
@app.get("/research")
async def research_page():
    """提供研究頁面"""
    html_path = Path(__file__).parent / "src" / "app" / "api" / "research.html"
    return FileResponse(html_path)


@app.post("/research/run")
async def run_research(request: dict):
    """執行研究並返回結果（非串流）"""
    try:
        question = request.get("question", "")
        if not question:
            return {"error": "請提供研究問題"}

        # 動態匯入研究代理（仍需 src.* 可匯入）
        from src.app.agents.research_agent import deep_researcher
        from src.app.config import Configuration

        config = Configuration()
        configurable = {**config.model_dump(mode="json")}
        configurable["allow_clarification"] = False
        run_config = {"configurable": configurable}

        # 生成 task_id（與串流端點一致）
        task_id = f"research_{int(time.time() * 1000)}_{question[:20]}"

        start_dt = datetime.now().isoformat(timespec="seconds")
        start_time = time.perf_counter()
        result = await deep_researcher.ainvoke(
            {"messages": [{"role": "user", "content": question}]},
            run_config,
        )
        end_time = time.perf_counter()
        end_dt = datetime.now().isoformat(timespec="seconds")
        elapsed = end_time - start_time

        # 寫入檔案
        _write_result_to_file(result, start_dt, end_dt, elapsed)
        # 更新暫存文件內容供 /load-document 使用
        _update_document_content(result.get("final_report", ""))

        return {
            "success": True,
            "final_report": result.get("final_report", "研究完成但未生成報告"),
            "timings": result.get("timings", []),
            "document_id": task_id,  # 新增文檔 ID
        }

    except Exception:
        # 僅在伺服器端記錄完整錯誤堆疊
        logger.exception("研究執行失敗")
        return {"error": "研究執行失敗，請稍後重試"}


# ===== 全域任務管理 =====
active_tasks: dict[str, asyncio.Task] = {}
# SSE 連接管理（用於檔案處理進度推送）
sse_connections: set[asyncio.Queue] = set()


def cancel_task(task_id: str):
    """取消指定的任務"""
    if task_id in active_tasks:
        task = active_tasks[task_id]
        if not task.done():
            task.cancel()
        del active_tasks[task_id]


def register_task(task_id: str, task: asyncio.Task):
    """註冊任務到全域管理"""
    active_tasks[task_id] = task


def broadcast_sse_event(event: dict):
    """廣播 SSE 事件到所有連接"""
    for queue in list(sse_connections):
        try:
            # 將字典轉為 JSON 字串，與 print_progress 格式一致
            import json
            event_str = json.dumps(event, ensure_ascii=False)
            queue.put_nowait(event_str)
        except Exception:
            # 移除無效連接
            sse_connections.discard(queue)

# ===== 研究進度 SSE 串流（即時 print_progress） =====


@app.get("/research/stream")
async def research_stream(
    request: Request,
    question: str = Query(..., description="研究問題"),
):
    async def event_generator():

        # 以 asyncio.Queue 收集 print_progress 的即時訊息
        progress_queue: asyncio.Queue[str] = asyncio.Queue()

        # 註冊此連接到全域 SSE 管理
        sse_connections.add(progress_queue)

        # 綁定回調（不暴露內部資訊）
        try:
            from src.app.agents import research_agent as ra
        except Exception:
            logger.exception("載入研究代理失敗")
            yield sse_event({"type": "error", "message": "系統初始化失敗"})
            return

        def progress_callback(msg: str):
            try:
                progress_queue.put_nowait(msg)
            except Exception:
                pass

        # 設定回調
        ra.print_progress.progress_callback = progress_callback

        # 啟動研究背景任務
        async def run_research_task():
            try:
                from src.app.config import Configuration
                config = Configuration()
                configurable = {**config.model_dump(mode="json")}
                configurable["allow_clarification"] = False
                run_config = {"configurable": configurable}
                result = await ra.deep_researcher.ainvoke(
                    {"messages": [{"role": "user", "content": question}]},
                    run_config,
                )
                return result
            except Exception:
                logger.exception("研究過程錯誤")
                return {"error": True}

        # 記錄開始時間，完成後與結果一同寫入 output.txt
        started_at = datetime.now().isoformat(timespec="seconds")
        wall_start = time.perf_counter()
        task = asyncio.create_task(run_research_task())

        # 生成任務ID並註冊到全域管理
        task_id = f"research_{int(time.time() * 1000)}_{question[:20]}"
        register_task(task_id, task)

        # 首次事件：帶 task_id 的階段起始事件
        try:
            yield sse_event({
                "type": "stage_start",
                "stage": "deep_researcher",
                "message": "開始研究",
                "task_id": task_id,
            })
        except Exception:
            pass

        try:
            # 迴圈推送進度，直到任務完成或客戶端中斷
            while not task.done():
                # 檢查前端是否已中斷連線（使用者取消）
                if await request.is_disconnected():
                    if not task.done():
                        task.cancel()
                    break
                try:
                    msg = await asyncio.wait_for(progress_queue.get(), timeout=0.25)

                    # 解析並轉發標準化階段事件
                    if "STAGE::" in msg:
                        try:
                            stage_segment = msg[msg.index("STAGE::"):]
                            # e.g., STAGE::research_supervisor::enter::iteration=3
                            parts = stage_segment.split("::")
                            stage_key = parts[1] if len(parts) > 1 else ""
                            iteration = None
                            if len(parts) >= 4 and parts[3].startswith("iteration="):
                                try:
                                    iteration = int(parts[3].split("=", 1)[1])
                                except Exception:
                                    iteration = None

                            stage_map = {
                                "clarify_with_user": "clarify",
                                "write_research_brief": "plan",
                                "research_supervisor": "execute",
                                "final_report_generation": "report",
                            }
                            stage_name = stage_map.get(stage_key)
                            if stage_name:
                                yield sse_event({
                                    "type": "stage",
                                    "stage": stage_name,
                                    "iteration": iteration,
                                })
                                continue
                        except Exception:
                            # 若解析失敗則退回一般進度訊息
                            pass

                    # 一般進度訊息
                    yield sse_event({"type": "progress", "message": msg})
                except asyncio.TimeoutError:
                    # 空轉，檢查任務是否完成
                    continue
                except Exception:
                    # 靜默忽略單筆推送問題
                    continue

            # 如果是正常完成，推送最終報告（若有）
            if not task.cancelled():
                result = task.result()
                ended_at = datetime.now().isoformat(timespec="seconds")
                elapsed = time.perf_counter() - wall_start
                if isinstance(result, dict) and not result.get("error"):
                    # 寫入檔案（與非串流端點一致）
                    _write_result_to_file(
                        result, started_at, ended_at, elapsed)
                    final_report = result.get("final_report")
                    if final_report:
                        # 更新暫存文件內容供 /load-document 使用
                        _update_document_content(final_report)
                        # 推送最終報告，包含 task_id 作為文檔 ID
                        yield sse_event({
                            "type": "final_report",
                            "report": final_report,
                            "document_id": task_id  # 使用 task_id 作為文檔 ID
                        })
                else:
                    yield sse_event({"type": "error", "message": "研究執行失敗，請稍後重試"})

        except asyncio.CancelledError:
            # 生成器被終止（連線中斷），確保任務被取消
            if not task.done():
                task.cancel()
            raise
        finally:
            # 清理任務註冊
            if task_id in active_tasks:
                del active_tasks[task_id]
            # 清理 SSE 連接註冊
            sse_connections.discard(progress_queue)
            # 統一收尾訊號（若是客戶端取消，這段可能不會被收到）
            try:
                yield sse_event({"type": "stage_complete", "stage": "deep_researcher"})
            except Exception:
                pass

    headers = {"Cache-Control": "no-cache", "Connection": "keep-alive"}
    return StreamingResponse(event_generator(), media_type="text/event-stream", headers=headers)


# ===== 取消研究任務 API =====
@app.post("/research/cancel")
async def cancel_research(request: dict):
    """取消當前正在執行的研究任務"""
    try:
        task_id_param = request.get("task_id")
        question = request.get("question", "")

        canceled_tasks = []

        # 優先使用 task_id 精準取消
        if task_id_param:
            task = active_tasks.get(task_id_param)
            if task and not task.done():
                task.cancel()
                canceled_tasks.append(task_id_param)
                del active_tasks[task_id_param]
        else:
            # 回退：使用 question 前 20 字元作為鍵匹配既有 task_id 模式 research_{ts}_{question[:20]}
            if not question:
                return {"error": "請提供 task_id 或 question"}
            short = question[:20]
            for tid, task in list(active_tasks.items()):
                if short and tid.endswith(short) and not task.done():
                    task.cancel()
                    canceled_tasks.append(tid)
                    del active_tasks[tid]

        if canceled_tasks:
            logger.info(f"已取消 {len(canceled_tasks)} 個研究任務: {canceled_tasks}")
            return {
                "success": True,
                "message": f"已成功取消 {len(canceled_tasks)} 個研究任務",
                "canceled_tasks": canceled_tasks
            }
        else:
            return {
                "success": False,
                "message": "未找到匹配的研究任務或任務已完成"
            }

    except Exception as e:
        logger.exception("取消研究任務失敗")
        return {"error": "取消研究任務失敗，請稍後重試"}


@app.get("/load-document")
async def load_document():
    # 直接回傳暫存文件（保持與前端期望結構的相容性）
    return {
        "title": DOCUMENT_STORE.get("title", "研究文件"),
        "content": DOCUMENT_STORE.get("content", "<p>尚未有內容</p>"),
        "characterLimit": DOCUMENT_STORE.get("characterLimit", 100000)
    }


# ===== 檔案上傳 API =====
@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    document_id: str = Query(default="", description="文檔 ID，用於關聯檔案")
):
    try:
        logger.info(f"收到上傳請求: {file.filename}, document_id: {document_id}")
        # 檔名淨化：保留英數、部分符號，避免路徑穿越
        original_name = file.filename or "unnamed"
        safe_name = original_name
        # "".join(
        #     ch for ch in original_name if ch.isalnum() or ch in (" ", "-", "_", ".")
        # ).strip()
        # logger.info(f"原始檔名: {original_name}, 淨化後: {safe_name}")
        # if not safe_name:
        #     raise HTTPException(status_code=400, detail="檔名無效")

        # 檔案大小限制：25MB（以累計 bytes 檢查）
        total_read = 0

        # 所有 PDF 檔案都先存入 TMP_DIR
        target_path = os.path.join(TMP_DIR, safe_name)

        # 確保目錄存在（依你的要求：tmp 目錄本身不由程式建立，若不存在則報錯）
        if not os.path.isdir(TMP_DIR):
            raise HTTPException(status_code=500, detail="暫存目錄不存在，請先建立 tmp 目錄")

        with open(target_path, "wb") as out:
            while True:
                chunk = await file.read(1024 * 1024)  # 1MB
                if not chunk:
                    break
                total_read += len(chunk)
                if total_read > MAX_UPLOAD_BYTES:
                    # 超出大小限制
                    raise HTTPException(status_code=413, detail="檔案超過 25MB 上限")
                out.write(chunk)

        # 建立可供前端直接存取的 URL
        file_url = f"/uploads/{safe_name}"

        # 檢查是否為 PDF 檔案，若是則立即處理
        logger.info(
            f"檔案檢查: {safe_name}, 副檔名檢查: {safe_name.lower().endswith('.pdf')}, document_id: {document_id}")
        if safe_name.lower().endswith('.pdf'):
            try:
                # 直接處理 PDF（所有 PDF 都先存入 TMP_DIR）
                logger.info(f"開始處理 PDF: {safe_name}")
                logger.info(f"PDF 檔案路徑: {target_path}")
                logger.info(f"圖片存放路徑: {TMP_IMAGE_DIR}")

                new_path = re.sub(r"\.pdf$", ".md", safe_name)
                logger.info(f"預期生成的 MD 檔案: {new_path}")

                # 根據是否有 document_id 決定處理方式
                if document_id:
                    # 有 document_id：直接輸出到 document_file/{document_id} 目錄
                    target_dir = os.path.join(DOC_ID_DIR, document_id)
                    os.makedirs(target_dir, exist_ok=True)
                    file_info_path = os.path.join(target_dir, "file_info.json")

                    # 直接調用 file_md.main 輸出到目標目錄
                    import file_md
                    file_md.main(target_path, TMP_IMAGE_DIR, target_dir)

                    # 檔案已經在目標目錄，不需要移動
                    source_md_path = os.path.join(target_dir, new_path)
                    target_md_path = source_md_path
                else:
                    # 沒有 document_id：使用 TMP_OUTPUT_DIR 目錄
                    target_dir = TMP_OUTPUT_DIR
                    file_info_path = os.path.join(target_dir, "file_info.json")

                    # 直接調用 file_md.main 輸出到 TMP_OUTPUT_DIR
                    import file_md
                    file_md.main(target_path, TMP_IMAGE_DIR, TMP_OUTPUT_DIR)

                    # 檔案已經在 TMP_OUTPUT_DIR 目錄，不需要移動
                    source_md_path = os.path.join(TMP_OUTPUT_DIR, new_path)
                    target_md_path = source_md_path

                # 檢查生成的檔案是否存在
                if os.path.exists(source_md_path):
                    logger.info(f"MD 檔案已生成: {source_md_path}")
                else:
                    logger.error(f"找不到生成的 Markdown 檔案: {source_md_path}")
                    logger.error(
                        f"目標目錄內容: {os.listdir(target_dir) if os.path.exists(target_dir) else '目錄不存在'}")
                    # 即使找不到檔案，也繼續處理，但標記為失敗
                    target_md_path = source_md_path  # 使用原始路徑作為備用

                # 圖片檔案保留在 TMP_IMAGE_DIR，不需要移動
                if document_id:
                    logger.info(f"有 document_id，圖片檔案保留在: {TMP_IMAGE_DIR}")
                else:
                    logger.info(f"沒有 document_id，圖片檔案保留在: {TMP_IMAGE_DIR}")

                new_data = {
                    "file_path": target_md_path,
                    "file_name": safe_name.replace('.pdf', ''),
                    "describe": f"附件檔案：{safe_name}",
                    "document_id": document_id
                }

                # 如果檔案存在 → 讀取舊資料
                if os.path.exists(file_info_path):
                    with open(file_info_path, "r", encoding="utf-8") as f:
                        try:
                            data = json.load(f)
                        except json.JSONDecodeError:
                            data = []
                else:
                    data = []

                # 新增資料
                data.append(new_data)

                # 寫回檔案
                with open(file_info_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)

                print("✅ 新資料已寫入！")

                logger.info(f"PDF 處理完成: {safe_name}")

                return {
                    "id": safe_name,
                    "url": file_url,
                    "name": safe_name,
                    "processed": True,
                    "status": "completed",
                    "document_id": document_id,
                    "md_file_path": target_md_path
                }
            except Exception as e:
                logger.exception(f"PDF 處理失敗: {safe_name}")

                return {
                    "id": safe_name,
                    "url": file_url,
                    "name": safe_name,
                    "processed": False,
                    "status": "failed",
                    "error": str(e),
                    "document_id": document_id
                }
        else:
            # 非 PDF 檔案
            return {
                "id": safe_name,
                "url": file_url,
                "name": safe_name,
                "processed": False,
                "status": "skipped",
                "document_id": document_id
            }
    except HTTPException:
        raise
    except Exception:
        logger.exception("檔案上傳失敗")
        raise HTTPException(status_code=500, detail="檔案上傳失敗")


# ===== Markdown 檔案 API =====
@app.get("/markdown")
async def get_markdown(
    document_id: str = Query(default="", description="文檔 ID"),
    file_name: str = Query(..., description="檔案名稱")
):
    """獲取 Markdown 檔案內容"""
    try:
        logger.info(
            f"收到 Markdown 請求: document_id={document_id}, file_name={file_name}")

        # 將 .pdf 改為 .md
        md_filename = re.sub(r"\.pdf$", ".md", file_name)

        # 根據是否有 document_id 決定檔案路徑
        if document_id:
            # 有 document_id：從 document_file/{document_id} 目錄讀取
            file_path = os.path.join(DOC_ID_DIR, document_id, md_filename)
            logger.info(f"有 document_id，檔案路徑: {file_path}")
        else:
            # 沒有 document_id：從 tmp_doc 目錄讀取
            file_path = os.path.join(TMP_OUTPUT_DIR, md_filename)
            logger.info(f"沒有 document_id，檔案路徑: {file_path}")

        # 檢查檔案是否存在
        if not os.path.exists(file_path):
            logger.warning(f"Markdown 檔案不存在: {file_path}")
            raise HTTPException(status_code=404, detail="Markdown 檔案不存在")

        # 讀取檔案內容
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 詳細的編碼檢查和調試
            logger.info(f"檔案讀取成功: {file_path}")
            logger.info(f"內容長度: {len(content)}")
            logger.info(f"內容前100字元: {repr(content[:100])}")

            # 檢查內容是否包含亂碼
            if content and len(content) > 0:
                # 檢查是否包含中文字符
                chinese_chars = sum(
                    1 for char in content if '\u4e00' <= char <= '\u9fff')
                logger.info(f"中文字符數量: {chinese_chars}")

                # 檢查是否有亂碼字符
                garbled_chars = sum(1 for char in content if ord(
                    char) > 127 and char not in '\n\r\t')
                logger.info(f"高ASCII字符數量: {garbled_chars}")

                # 嘗試檢測編碼問題
                try:
                    # 確保內容可以正確編碼為 UTF-8
                    encoded_content = content.encode('utf-8')
                    logger.info(f"UTF-8 編碼成功，編碼後長度: {len(encoded_content)}")
                except UnicodeEncodeError as e:
                    logger.error(f"UTF-8 編碼錯誤: {e}")
                    # 嘗試使用其他編碼讀取
                    with open(file_path, "r", encoding="big5") as f:
                        content = f.read()
                    logger.info(f"使用 Big5 編碼重新讀取成功: {file_path}")
            else:
                logger.warning(f"檔案內容為空: {file_path}")
                content = f"# {file_name}\n\n檔案內容為空或無法讀取。"

        except UnicodeDecodeError as e:
            logger.error(f"UTF-8 解碼失敗: {e}")
            # 嘗試使用其他編碼
            try:
                with open(file_path, "r", encoding="big5") as f:
                    content = f.read()
                logger.info(f"使用 Big5 編碼讀取成功: {file_path}")
            except Exception as e2:
                logger.error(f"Big5 編碼也失敗: {e2}")
                content = f"# {file_name}\n\n檔案編碼無法識別，請檢查檔案格式。"
        except Exception as e:
            logger.error(f"讀取檔案失敗: {e}")
            content = f"# {file_name}\n\n檔案讀取失敗: {str(e)}"

        # 建立回應並設定正確的編碼標頭
        from fastapi.responses import JSONResponse
        response = JSONResponse({
            "content": content,
            "fileName": file_name
        })
        response.headers["Content-Type"] = "application/json; charset=utf-8"
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"讀取 Markdown 檔案失敗: {file_path}")
        raise HTTPException(status_code=500, detail="讀取 Markdown 檔案失敗")


# ===== 文檔附件 API =====
@app.get("/documents/{document_id}/attachments")
async def get_document_attachments(document_id: str):
    """獲取文檔的附件列表"""
    try:
        logger.info(f"收到附件列表請求: {document_id}")

        # 檢查文檔是否存在
        document = collection.find_one({"document_id": document_id})
        if not document:
            logger.warning(f"文檔不存在: {document_id}")
            raise HTTPException(status_code=404, detail="文檔不存在")

        # 訪問文檔目錄
        document_folder = os.path.join(DOC_ID_DIR, document_id)
        attachments = []

        if os.path.exists(document_folder):
            # 獲取所有 .md 檔案
            for filename in os.listdir(document_folder):
                if filename.endswith('.md'):
                    file_path = os.path.join(document_folder, filename)

                    # 獲取檔案資訊
                    file_stat = os.stat(file_path)
                    file_size = file_stat.st_size
                    upload_time = datetime.fromtimestamp(
                        file_stat.st_ctime).isoformat()

                    # 生成對應的 PDF 檔案名稱
                    pdf_filename = re.sub(r"\.md$", ".pdf", filename)

                    # 生成附件 ID（使用檔案名稱的 hash）
                    import hashlib
                    attachment_id = f"att_{hashlib.md5(filename.encode()).hexdigest()[:8]}"

                    attachments.append({
                        "id": attachment_id,
                        "fileName": pdf_filename,
                        "fileSize": file_size,
                        "uploadTime": upload_time,
                        "status": "completed",
                        "convertedUrl": f"http://localhost:8000/uploads/{pdf_filename}"
                    })

        logger.info(f"附件列表載入成功: {document_id}, 共 {len(attachments)} 個附件")

        return {
            "attachments": attachments
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"載入附件列表失敗: {document_id}")
        raise HTTPException(status_code=500, detail="載入附件列表失敗")


# ===== 文檔載入 API =====
@app.get("/documents")
async def get_documents():
    """獲取所有文檔列表"""
    try:
        logger.info("收到文檔列表請求")

        # 從 MongoDB 獲取所有文檔
        documents_cursor = collection.find({}, {
            "document_id": 1,
            "report_title": 1,
            "created_at": 1,
            "updated_at": 1
        }).sort("updated_at", -1)  # 按更新時間降序排列

        documents = []
        for doc in documents_cursor:
            document_id = doc.get("document_id", "")

            # 計算附件數量
            document_folder = os.path.join(
                TMP_DIR, "document_file", document_id)
            attachment_count = 0
            if os.path.exists(document_folder):
                attachment_count = len([f for f in os.listdir(document_folder)
                                        if os.path.isfile(os.path.join(document_folder, f)) and f.endswith('.md')])

            documents.append({
                "id": document_id,
                "title": doc.get("report_title", ""),
                "createdAt": doc.get("created_at", ""),
                "updatedAt": doc.get("updated_at", ""),
                "attachmentCount": attachment_count
            })

        logger.info(f"文檔列表載入成功，共 {len(documents)} 個文檔")

        return {
            "documents": documents
        }

    except Exception as e:
        logger.exception("載入文檔列表失敗")
        raise HTTPException(status_code=500, detail="載入文檔列表失敗")


@app.get("/documents/{document_id}")
async def get_document(document_id: str):
    """根據文檔 ID 載入文檔"""
    try:
        logger.info(f"收到文檔載入請求: {document_id}")

        # 從 MongoDB 載入文檔
        document = collection.find_one({"document_id": document_id})

        if not document:
            logger.warning(f"文檔不存在: {document_id}")
            raise HTTPException(status_code=404, detail="文檔不存在")

        # 計算附件數量
        document_folder = os.path.join(TMP_DIR, "document_file", document_id)
        attachment_count = 0
        if os.path.exists(document_folder):
            attachment_count = len([f for f in os.listdir(document_folder)
                                    if os.path.isfile(os.path.join(document_folder, f)) and f.endswith('.md')])

        logger.info(f"文檔載入成功: {document_id}, 附件數量: {attachment_count}")

        return {
            "id": document_id,
            "title": document.get("report_title", ""),
            "content": document.get("content", {}).get("html", ""),
            "createdAt": document.get("created_at", ""),
            "updatedAt": document.get("updated_at", ""),
            "attachmentCount": attachment_count
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"載入文檔失敗: {document_id}")
        raise HTTPException(status_code=500, detail="載入文檔失敗")


# ===== 文檔儲存 API =====
@app.post("/test-save-document")
async def test_save_document(request: dict):
    """測試文檔儲存請求格式"""
    try:
        logger.info(f"收到測試請求: {request}")
        return {
            "success": True,
            "message": "請求格式正確",
            "received_data": request
        }
    except Exception as e:
        logger.exception("測試請求失敗")
        return {"error": str(e)}


@app.post("/test-new-format")
async def test_new_format(request: DocumentSaveRequest):
    """測試新的結構化資料格式"""
    try:
        logger.info(f"收到新格式測試請求: {request.documentId}")
        logger.debug(
            f"資料結構: content.html長度={len(request.data.content.html)}, page_size={request.data.page.size.label}")
        return {
            "success": True,
            "message": "新格式請求正確",
            "document_id": request.documentId,
            "content_length": len(request.data.content.html),
            "page_size": request.data.page.size.label
        }
    except Exception as e:
        logger.exception("新格式測試失敗")
        return {"error": str(e)}


@app.post("/save-document", response_model=DocumentSaveResponse)
async def save_document(request: dict):
    """儲存文檔到 MongoDB"""
    try:
        # 從請求中提取資料，支援兩種格式
        document_id = request.get("documentId", "")
        report_title = request.get("reportTitle", "")

        # 檢查是否為新格式（有 data 欄位）
        if "data" in request:
            data = request["data"]
            content_html = data["content"]["html"]
            content_json = data["content"]["json"]
            content_text = data["content"]["text"]
            page_info = data["page"]
            document_data = data["document"]
        else:
            # 舊格式（直接包含 content, page, document）
            content_html = request.get("content", {}).get("html", "")
            content_json = request.get("content", {}).get("json", {})
            content_text = request.get("content", {}).get("text", "")
            page_info = request.get("page", {})
            document_data = request.get("document", {})

        logger.info(f"收到文檔儲存請求: {document_id}")
        logger.debug(
            f"請求資料: documentId={document_id}, reportTitle={report_title}, content_length={len(content_html)}")
        logger.debug(f"完整請求內容: {request}")

        # 驗證必要欄位
        if not document_id:
            return DocumentSaveResponse(
                success=False,
                message="缺少必要欄位: documentId",
                error="documentId is required"
            )

        if not content_html:
            return DocumentSaveResponse(
                success=False,
                message="缺少必要欄位: content.html",
                error="content.html is required"
            )

        # 準備儲存到 MongoDB 的文檔資料
        mongo_document = {
            "document_id": document_id,
            "report_title": report_title,
            "content": {
                "html": content_html,
                "json": content_json,
                "text": content_text
            },
            "page": page_info,
            "document": document_data,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

        # 檢查文檔是否已存在
        existing_doc = collection.find_one({"document_id": document_id})

        if existing_doc:
            # 更新現有文檔
            result = collection.update_one(
                {"document_id": document_id},
                {
                    "$set": {
                        "content": {
                            "html": content_html,
                            "json": content_json,
                            "text": content_text
                        },
                        "page": page_info,
                        "document": document_data,
                        "updated_at": datetime.now().isoformat()
                    }
                }
            )
            logger.info(
                f"文檔已更新: {document_id}, 修改筆數: {result.modified_count}")
            message = "文檔已更新"
        else:
            # 新文檔：移動 tmp_doc 中的檔案到新建資料夾
            try:
                # 建立目標資料夾
                document_folder = os.path.join(
                    TMP_DIR, "document_file", document_id)
                os.makedirs(document_folder, exist_ok=True)

                # 移動 tmp_doc 中的所有檔案到目標資料夾
                tmp_doc_folder = os.path.join(TMP_DIR, "tmp_doc")
                if os.path.exists(tmp_doc_folder):
                    for filename in os.listdir(tmp_doc_folder):
                        src_path = os.path.join(tmp_doc_folder, filename)
                        dst_path = os.path.join(document_folder, filename)

                        if os.path.isfile(src_path):
                            # 移動檔案
                            shutil.move(src_path, dst_path)
                            logger.info(f"檔案已移動: {filename} -> {dst_path}")

                    # 保留 tmp_doc 資料夾，不刪除
                    logger.info(f"tmp_doc 資料夾已保留: {tmp_doc_folder}")

                # 圖片資料夾保留在 TMP_IMAGE_DIR，不需要移動
                logger.info(f"圖片資料夾保留在: {TMP_IMAGE_DIR}")

                # 更新文檔資料，加入檔案路徑資訊
                document_data["file_folder"] = document_folder
                document_data["file_count"] = len([f for f in os.listdir(
                    document_folder) if os.path.isfile(os.path.join(document_folder, f))])

                logger.info(f"新文檔檔案已移動到: {document_folder}")

            except Exception as move_error:
                logger.exception(f"檔案移動失敗: {move_error}")
                # 即使檔案移動失敗，仍繼續儲存文檔
                pass

            # 插入新文檔
            result = collection.insert_one(mongo_document)
            logger.info(
                f"新文檔已建立: {document_id}, 插入ID: {result.inserted_id}")
            message = "文檔已建立並檔案已移動"

        return DocumentSaveResponse(
            success=True,
            message=message,
            document_id=document_id
        )

    except Exception as e:
        logger.exception(f"文檔儲存失敗: {document_id}")

        # 檢查是否為資料驗證問題
        if "ValidationError" in str(type(e)) or "422" in str(e):
            error_msg = f"資料格式錯誤: {str(e)}"
        # 檢查是否為 MongoDB 連線問題
        elif "ServerSelectionTimeoutError" in str(type(e)) or "AutoReconnect" in str(e):
            error_msg = "資料庫連線問題，請稍後重試"
        elif "OperationFailure" in str(type(e)):
            error_msg = "資料庫操作失敗，請檢查資料格式"
        else:
            error_msg = f"文檔儲存失敗: {str(e)}"

        return DocumentSaveResponse(
            success=False,
            message=error_msg,
            error=str(e)
        )


if __name__ == "__main__":
    print("🚀 正在啟動研究服務器...")
    print("📍 服務器地址: http://127.0.0.1:8000")
    print("🔬 研究界面: http://127.0.0.1:8000/research")
    print("⏹️  按 Ctrl+C 停止服務器")
    print("-" * 50)

    uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)
