<template>
  <div class="new-doc">
    <!-- 左側可縮放側欄 -->
    <aside class="nd-sidebar" :style="{ width: sidebarWidth + 'px' }">
      <div class="nd-sidebar__content">
        <!-- 在此放側欄內容（清單/模板/說明等） -->
        <div class="nd-sidebar__placeholder">側欄內容</div>
      </div>
      <div class="nd-sidebar__resize" @mousedown="startSidebarResize"></div>
    </aside>

    <t-card header="" style="width:100%; height:100%;" class="flat-card nd-main">
      <div style="display:flex; flex-direction:column; gap:12px; height:100%; justify-content:center; align-items:center; width:100%;">
        <!-- 進度視覺化：生成期間顯示 -->
        <div v-if="generating" class="viz-wrapper">
          <div class="viz-header">
            <div class="viz-title">研究報告生成進度</div>
            <div class="viz-actions">
              <tooltip :content="'中止生成'">
                <t-button theme="default" variant="text" shape="square" :loading="canceling" @click="stopGeneration" aria-label="中止生成" title="中止生成">
                  <!-- stop icon -->
                  <svg viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg" style="width: 2em; height: 2em; display:block;">
                    <path fill="#007bff" d="M256 0C114.6 0 0 114.6 0 256c0 141.4 114.6 256 256 256s256-114.6 256-256C512 114.6 397.4 0 256 0zM352 328c0 13.2-10.8 24-24 24h-144C170.8 352 160 341.2 160 328v-144C160 170.8 170.8 160 184 160h144C341.2 160 352 170.8 352 184V328z"/>
                  </svg>
                </t-button>
              </tooltip>
              <div class="viz-conn">
                <span :class="['dot', isConnected ? 'on' : 'off']"></span>
                <span>{{ isConnected ? '即時連線中' : '已完成' }}</span>
              </div>
            </div>
          </div>

          <div class="viz-progressbar">
            <div class="bar">
              <div
                class="bar-fill"
                :style="{ width: ((currentStageIndex >= 0 ? currentStageIndex : 0) / (stages.length - 1)) * 100 + '%' }"
              >
              </div>
            </div>

            <div class="viz-stages">
              <div v-for="s in stages" :key="s.id" class="stage">
                <div
                  :class="[
                    'stage-icon',
                    getStageStatus(s.id) === 'completed' && 'completed',
                    getStageStatus(s.id) === 'active' && 'active',
                    getStageStatus(s.id) === 'pending' && 'pending',
                  ]"
                >
                  <span v-if="getStageStatus(s.id) === 'completed'">✓</span>
                  <span v-else-if="getStageStatus(s.id) === 'active'">⟳</span>
                  <span v-else>○</span>
                </div>
                <div class="stage-text">
                  <div
                    :class="[
                      'stage-name',
                      getStageStatus(s.id) === 'active' && 'name-active',
                      getStageStatus(s.id) === 'completed' && 'name-done',
                      getStageStatus(s.id) === 'pending' && 'name-pending',
                    ]"
                  >
                    {{ s.name }}
                  </div>
                  <div class="stage-desc">{{ s.description }}</div>
                </div>
              </div>
            </div>
          </div>

          <div class="viz-card">
            <div class="card-icon">⟳</div>
            <div class="card-body">
              <div class="card-title">{{ stages[currentStageIndex]?.name }}</div>
              <div class="card-desc">{{ stages[currentStageIndex]?.description }}</div>

              <div v-if="currentStage === 'execute' && iteration > 0" class="iter">
                <div class="iter-label">研究迭代：</div>
                <div class="iter-steps">
                  <div
                    v-for="i in 5"
                    :key="i"
                    :class="[
                      'iter-step',
                      i < iteration && 'iter-done',
                      i === iteration && 'iter-active',
                      i > iteration && 'iter-pending',
                    ]"
                  >
                    {{ i }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 輸入與操作：非生成期間顯示 -->
        <div v-show="!generating">
          <!-- <label for="report書題目">請輸入報告書題目</label> -->
          <div class="input-pill">
            <t-textarea
              id="report-title"
              v-model="title"
              :readonly="generating"
              placeholder="例如：2025 年 Q4 成果報告"
              autosize
              autocomplete="off"
              rows="1"
              @keydown.enter.exact.prevent="onEnter()"
              @keydown.enter.shift.exact.stop
              @compositionstart="onCompositionStart"
              @compositionend="onCompositionEnd"
              class="modern-textarea"
            />
            <!-- 附件：隱藏檔案選擇器 -->
            <input ref="filePickerRef" type="file" style="display:none" @change="onFileChosen" />
            <t-button
              theme="default"
              variant="outline"
              aria-label="附件"
              class="pill-attach"
              @click="onPickAttachment"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="width: 1.7em; height: 1.7em; display:block;">
                <path d="M21.44 11.05 12.5 20a5.5 5.5 0 1 1-7.78-7.78L13 4.94a3.5 3.5 0 1 1 4.95 4.95L9.88 18.96a1.5 1.5 0 0 1-2.12-2.12L15.5 9.1"/>
              </svg>
            </t-button>
            <t-button
              theme="primary"
              shape="square"
              aria-label="建立"
              class="pill-send"
              @click="onConfirm"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 -5 24 32"
                stroke-width="1.5"
                stroke="currentColor"
                style="width: 1.5em; height: 1.5em; display:block; transform: rotate(90deg);"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M4.5 10.5 12 3m0 0 7.5 7.5M12 3v18"
                />
              </svg>
            </t-button>
          </div>
          
          <t-alert v-if="error" class="t-alert-transparent" theme="error" :message="error" :close="false" />
        </div>
        
        
      </div>
    </t-card>
    <!-- 右下浮動按鈕 -->
    <button class="doc-fab" aria-label="清單">
      <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <rect fill="none" width="24" height="24"/>
        <path fill="#0090ff" d="M1,12C1,4,4,1,12,1S23,4,23,12,20,23,12,23,1,20,1,12"/>
        <rect fill="#ffffff" height="1.44" rx="0.72" width="12.24" x="5.88" y="7.56"/>
        <rect fill="#ffffff" height="1.44" rx="0.72" width="12.24" x="5.88" y="10.28"/>
        <rect fill="#ffffff" height="1.44" rx="0.72" width="12.24" x="5.88" y="13"/>
        <rect fill="#ffffff" height="1.44" rx="0.72" width="7.44" x="5.88" y="15.72"/>
      </svg>
    </button>
  </div>
  
</template>

<script setup lang="ts">
type PendingAttachment = { id: string; url: string; name: string; type: string; size: number }
const emit = defineEmits<{
  (e: 'confirm', title: string, attachments?: PendingAttachment[]): void
  (e: 'cancel'): void
}>()

const title = ref('')
const error = ref('')
const generating = ref(false)
const progress = ref<Array<{ type?: string; stage?: string; message: string }>>([])
let es: EventSource | null = null
const canceling = ref(false)
let composing = false
const sidebarOpen = ref(true)
const sidebarWidth = ref(260)
const minSidebarWidth = 260
const maxSidebarWidth = 500
let resizingSidebar = false
let resizeStartX = 0
let startWidth = 260

function startSidebarResize(e: MouseEvent) {
  resizingSidebar = true
  resizeStartX = e.clientX
  startWidth = sidebarWidth.value
  document.body.style.userSelect = 'none'
  document.addEventListener('mousemove', onSidebarResize)
  document.addEventListener('mouseup', stopSidebarResize)
}
function onSidebarResize(e: MouseEvent) {
  if (!resizingSidebar) return
  const delta = e.clientX - resizeStartX
  const next = Math.max(minSidebarWidth, Math.min(maxSidebarWidth, startWidth + delta))
  sidebarWidth.value = next
}
function stopSidebarResize() {
  resizingSidebar = false
  document.body.style.userSelect = ''
  document.removeEventListener('mousemove', onSidebarResize)
  document.removeEventListener('mouseup', stopSidebarResize)
}
// 立即上傳後暫存的附件結果（待進入編輯器時插入）
const pendingAttachments = ref<PendingAttachment[]>([])
const filePickerRef = ref<HTMLInputElement | null>(null)

function onPickAttachment() {
  filePickerRef.value?.click()
}
function onFileChosen(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files && input.files[0]
  if (!file) return
  void uploadAttachment(file)
  input.value = '' // 重置以便再次選取同名檔也能觸發 change
}

// 呼叫後端立即上傳並暫存結果
async function uploadAttachment(file: File) {
  try {
    pushLog({ type: 'info', message: `正在上傳附件：${file.name}` })
    const form = new FormData()
    form.append('file', file)
    const res = await fetch('http://localhost:8000/upload', {
      method: 'POST',
      body: form,
    })
    if (!res.ok) throw new Error('上傳失敗')
    const data = await res.json() as { id: string; url: string; name?: string }
    const item = {
      id: data.id,
      url: data.url,
      name: data.name ?? file.name,
      type: file.type,
      size: file.size,
    }
    pendingAttachments.value.push(item)
    pushLog({ type: 'info', message: `附件已上傳：${item.name}` })
  } catch (err: any) {
    pushLog({ type: 'error', message: `附件上傳失敗：${err?.message ?? '未知錯誤'}` })
  }
}

// 後端 SSE 端點（依實際部署調整）
const SSE_ENDPOINT = 'http://localhost:8000/research/stream'
const CANCEL_ENDPOINT = 'http://localhost:8000/research/cancel'
// 研究進度視覺化狀態
const stages = [
  { id: 'clarify', name: '需求澄清', description: '確認研究範圍與目標' },
  { id: 'plan', name: '規劃研究', description: '制定研究計畫與策略' },
  { id: 'execute', name: '執行研究', description: '進行資料蒐集與分析' },
  { id: 'report', name: '生成報告', description: '撰寫最終研究報告' },
] as const
type StageId = typeof stages[number]['id']
const currentStage = ref<StageId>('clarify')
const iteration = ref(0)
const isConnected = ref(false)
const currentStageIndex = computed(() => stages.findIndex(s => s.id === currentStage.value))
function getStageStatus(stageId: StageId) {
  const order = stages.map(s => s.id)
  const cur = order.indexOf(currentStage.value)
  const idx = order.indexOf(stageId)
  if (idx < cur) return 'completed'
  if (idx === cur) return 'active'
  return 'pending'
}

function validate(v: string) {
  if (!v || !v.trim()) return '題目不能為空'
  if (v.length > 120) return '題目長度不可超過 120 字元'
  return ''
}

function pushLog(entry: { type?: string; stage?: string; message: string }) {
  progress.value.push(entry)
}

function abortStream() {
  if (!generating.value) return
  canceling.value = true
  pushLog({ type: 'info', message: '正在取消…' })
  if (es) {
    es.close()
    es = null
  }
  generating.value = false
  pushLog({ type: 'info', message: '已中止生成流程' })
  canceling.value = false
}

// 中止並通知後端取消當前任務
async function stopGeneration() {
  if (canceling.value) return
  canceling.value = true
  try {
    // 優先通知後端取消
    await fetch(CANCEL_ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: title.value?.trim?.() ?? '' }),
    }).catch(() => {})
  } finally {
    abortStream()
  }
}

function onConfirm() {
  error.value = validate(title.value)
  if (error.value) return
  generating.value = true
  progress.value = []
  try {
    const url = new URL(SSE_ENDPOINT)
    url.searchParams.set('question', title.value.trim())
    es = new EventSource(url.toString())
    es.onopen = () => {
      pushLog({ type: 'info', message: '已連線至生成服務，開始處理…' })
      isConnected.value = true
      currentStage.value = 'clarify'
      iteration.value = 0
    }
    es.onerror = () => {
      pushLog({ type: 'error', message: '串流連線發生錯誤或已關閉' })
      isConnected.value = false
      abortStream()
    }
    es.onmessage = (ev: MessageEvent<string>) => {
      try {
        const data = JSON.parse(ev.data) as {
          type?: string
          stage?: StageId
          message?: string
          report?: string
          done?: boolean
          iteration?: number
        }
        // 標準化事件：type:'stage' 時直接更新階段與迭代
        if (data.type === 'stage' && data.stage) {
          currentStage.value = data.stage
          if (typeof data.iteration === 'number') iteration.value = data.iteration
          return
        }
        // 相容既有：stage_start → 更新目前階段
        if (data.stage && data.type === 'stage_start') {
          currentStage.value = data.stage
          pushLog({ type: data.type, stage: data.stage, message: data.message ?? '開始階段' })
          return
        }
        if (data.type === 'error') {
          pushLog({ type: 'error', message: data.message ?? '未知錯誤' })
          return
        }
        if (data.type === 'progress') {
          pushLog({ type: 'progress', message: data.message ?? '' })
          // 若訊息內含「第 X 輪」則嘗試解析為 iteration
          if (data.message) {
            const m = data.message.match(/第\s*(\d+)\s*輪/)
            if (m) iteration.value = Number(m[1])
          }
          return
        }
        if (data.type === 'final_report') {
          pushLog({ type: 'info', message: '最終報告已生成' })
          es?.close()
          es = null
          generating.value = false
          isConnected.value = false
          emit('confirm', title.value.trim(), pendingAttachments.value)
          return
        }
        if (data.type === 'stage_complete') {
          pushLog({ type: 'info', message: `階段完成：${data.stage ?? ''}`.trim() })
          return
        }
        if (data.done) {
          pushLog({ type: 'info', message: '生成已完成，正在開啟編輯器…' })
          es?.close()
          es = null
          generating.value = false
          isConnected.value = false
          emit('confirm', title.value.trim(), pendingAttachments.value)
          return
        }
        if (data.message) {
          pushLog({ type: data.type ?? 'info', message: data.message })
        }
      } catch (e) {
        if (ev.data) pushLog({ type: 'info', message: ev.data })
      }
    }
  } catch (e) {
    pushLog({ type: 'error', message: '無法初始化串流連線' })
    generating.value = false
    isConnected.value = false
  }
}

function onCompositionStart() {
  composing = true
}

function onCompositionEnd() {
  composing = false
}

function onEnter() {
  if (composing) return
  onConfirm()
}
</script>

<style scoped>
.new-doc {
  height: 100%; /* 與 editor 容器一致 */
  display: flex;
  align-items: stretch;
  justify-content: flex-start;
  padding: 0;
}
.nd-sidebar {
  height: 100%;
  width: 260px;
  border-right: 1px solid #e5e7eb;
  background: #fafafa;
  box-sizing: border-box;
  position: relative;
  display: flex;
  flex-direction: column;
}
.nd-sidebar__resize {
  position: absolute;
  top: 0;
  right: -2px;
  width: 4px;
  height: 100%;
  background: transparent;
  cursor: col-resize;
}
.nd-sidebar__content { padding: 12px; overflow: auto; }
.nd-sidebar__placeholder { color: #94a3b8; font-size: 12px; }
.nd-main { flex: 1; display: flex; align-items: center; justify-content: center; }
.flat-card :deep(.t-card__body) {
  /* 內層容器無邊框背景，保持卡片語意但視覺扁平 */
  border: none;
  box-shadow: none;
  height: 100%;
  display: flex;
  flex-direction: column;
}
.flat-card :deep(.t-card) {
  border: none;
  box-shadow: none;
  height: 100%;
}
.flat-card :deep(.t-card__header) {
  border-bottom: none;
}
.modern-input :deep(.t-input),
.modern-input :deep(.t-input__wrap),
.modern-input :deep(.t-input__inner),
.modern-input :deep(input) {
  border: none !important;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 6px 18px rgba(0,0,0,0.06);
  transition: box-shadow .2s ease;
  width: 100%;
  box-sizing: border-box;
}
.modern-input :deep(.t-input),
.modern-input :deep(.t-input__wrap) {
  min-height: 56px;
}
.modern-input :deep(.t-input__inner),
.modern-input :deep(input) {
  height: 70px;
  line-height: 70px;
  padding: 0 16px;
  font-size: 16px;
}
.modern-input :deep(.t-input__wrap:focus-within),
.modern-input :deep(input:focus) {
  box-shadow: 0 8px 26px rgba(0,0,0,0.08), 0 0 0 3px rgba(24,144,255,0.12);
}
.modern-input :deep(input::placeholder) {
  color: #9aa0a6;
}

/* Input 與送出按鈕橫排（底對齊、間距、輸入占滿） */
/* 膠囊式輸入框容器 */
.input-pill {
  display: flex;
  align-items: center; /* 垂直置中 */
  gap: 10px; /* 元件間距 */
  width: 720px; /* 縮小輸入列寬度 */
  height: 100px; /* 確保不超過容器寬度  */
  background: #f8fafc; /* 淺底 */
  border: 1px solid #e5e7eb; /* 顯示外框 */
  border-radius: 999px; /* 膠囊圓角 */
  padding: 10px 12px; /* 內距 */
  box-shadow: inset 0 0 0 1px rgba(0,0,0,0.02), 0 2px 6px rgba(0,0,0,0.04);
}
.input-pill :deep(.t-input),
.input-pill :deep(.t-input__wrap) {
  flex: 1 1 auto;
  background: transparent;
  box-shadow: none;
}
.input-pill :deep(.umo-textarea),
.input-pill :deep(.umo-textarea__inner),
.input-pill :deep(textarea) {
  flex: 1 1 auto;
  width: 100%;
  background: transparent;
  border: none !important; /* 去除外框 */
  box-shadow: none !important;
  resize: none; /* 由 autosize 控制高度 */
  padding: 12px 12px; /* 與膠囊內距協調 */
  min-height: 44px;
  line-height: 1.6;
}
.modern-textarea :deep(.umo-textarea__tips),
.modern-textarea :deep(.umo-textarea__info_wrapper) {
  display: none;
}
/* 隱藏滾動條 & 防止出現垂直捲動 */
.modern-textarea :deep(.umo-textarea__inner),
.modern-textarea :deep(textarea) {
  overflow: hidden !important;
  resize: none !important;
  scrollbar-width: none !important; /* FireFox */
  -ms-overflow-style: none !important; /* IE / Edge */
}

/* Chrome / Safari */
.modern-textarea :deep(.umo-textarea__inner::-webkit-scrollbar),
.modern-textarea :deep(textarea::-webkit-scrollbar) {
  display: none !important;
}

.input-pill :deep(.t-input__inner),
.input-pill :deep(input) {
  height: 44px;
  line-height: 44px;
  padding: 0 8px;
  background: transparent;
}
.pill-send {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: #eef2f7;
  border: 1px solid #e5e7eb;
}
.pill-attach {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: #fff;
  border: 1px solid #e5e7eb;
}
.pill-send :deep(.umo-button__text) { padding: 0; }
.input-hint { margin-top: 6px; font-size: 12px; color: #94a3b8; }

/* 右下浮動按鈕 */
.doc-fab {
  position: fixed;
  right: 28px;
  bottom: 28px;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  border: none;
  background: transparent;
  box-shadow: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1200;
}
.doc-fab svg { width: 44px; height: 44px; display: block; }

/* 進度視覺化樣式 */
.viz-wrapper { display: flex; flex-direction: column; gap: 16px; }
.viz-header { display: flex; align-items: center; justify-content: space-between; }
.viz-actions { display: flex; align-items: center; gap: 10px; }
.viz-title { font-size: 18px; font-weight: 600; color: #1f2937; }
.viz-conn { display: flex; align-items: center; gap: 6px; color: #475569; }
.viz-conn .dot { width: 8px; height: 8px; border-radius: 999px; display: inline-block; }
.viz-conn .dot.on { background: #22c55e; animation: viz-pulse 1.5s infinite ease-in-out; }
.viz-conn .dot.off { background: #94a3b8; }
@keyframes viz-pulse { 0%,100%{opacity:.5} 50%{opacity:1} }

.viz-progressbar .bar { position: relative; height: 6px; background: #e5e7eb; border-radius: 999px; overflow: hidden; margin: 8px 0 24px; }
.viz-progressbar .bar-fill { height: 100%; background: var(--umo-primary-color, #2563eb); transition: width .4s ease; }
.viz-stages { display: flex; justify-content: space-between; gap: 12px; }
.stage { display: flex; flex-direction: column; align-items: center; width: 120px; text-align: center; }
.stage-icon { width: 48px; height: 48px; border-radius: 999px; display: flex; align-items: center; justify-content: center; margin-bottom: 6px; border: 2px solid #cbd5e1; color: #94a3b8; background: #fff; transition: all .2s ease; }
.stage-icon.completed { background: #22c55e; color: #fff; border-color: #22c55e; transform: scale(1); }
.stage-icon.active { background: #2563eb; color: #fff; border-color: #2563eb; box-shadow: 0 6px 20px rgba(37,99,235,.25); transform: scale(1.05); }
.stage-icon.pending { background: #fff; color: #94a3b8; border-color: #cbd5e1; }
.stage-name { font-weight: 600; margin-bottom: 2px; }
.name-active { color: #2563eb; }
.name-done { color: #16a34a; }
.name-pending { color: #94a3b8; }
.stage-desc { font-size: 12px; color: #64748b; }

.viz-card { display: flex; gap: 12px; padding: 16px; background: #fff; border: 1px solid #e5e7eb; border-radius: 14px; box-shadow: 0 8px 24px rgba(0,0,0,.06); }
.card-icon { width: 56px; height: 56px; border-radius: 12px; background: #dbeafe; color: #2563eb; display: flex; align-items: center; justify-content: center; font-size: 24px; }
.card-title { font-size: 18px; font-weight: 700; color: #1f2937; margin-bottom: 4px; }
.card-desc { color: #475569; margin-bottom: 8px; }
.iter { display: flex; align-items: center; gap: 8px; padding-top: 10px; border-top: 1px solid #e5e7eb; margin-top: 6px; }
.iter-label { font-size: 13px; color: #334155; }
.iter-steps { display: flex; gap: 6px; }
.iter-step { width: 36px; height: 36px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: 600; background: #e5e7eb; color: #94a3b8; transition: all .2s ease; }
.iter-step.iter-done { background: #22c55e; color: #fff; }
.iter-step.iter-active { background: #2563eb; color: #fff; transform: scale(1.06); box-shadow: 0 8px 20px rgba(37,99,235,.25); }
</style>

<style scoped>
.progress {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.progress-list {
  max-height: 200px;
  overflow: auto;
  border: 1px solid #eee;
  border-radius: 6px;
  padding: 8px;
  background: #fafafa;
}
.t-alert-transparent :deep(.t-alert) {
  border-color: transparent !important;
  background: transparent !important;
  box-shadow: none !important;
}
.t-alert-transparent :deep(.t-alert__icon),
.t-alert-transparent :deep(.t-alert__message),
.t-alert-transparent :deep(.t-alert__description) {
  color: rgb(144, 62, 62) !important; /* 顯示文字，僅外框透明 */
}
.log-line {
  font-size: 12px;
  color: #333;
  line-height: 1.6;
  white-space: pre-wrap;
}
.log-line .stage,
.log-line .type {
  color: #888;
  margin-right: 6px;
}



</style>


