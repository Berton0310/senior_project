<template>
  <div class="new-doc" id="new-document">
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
          <!-- 標題區域 -->
          <div class="title-section">
            <div class="title-main">全能報告生成助手</div>
            <div class="title-subtitle">AI 驅動的智能文檔創作平台</div>
          </div>
          
          <!-- <label for="report書題目">請輸入報告書題目</label> -->
          <div class="input-pill">
            <t-textarea
              id="report-title"
              v-model="title"
              :readonly="generating"
              placeholder="例如：2025 年 Q4 成果報告"
              autocomplete="off"
              rows="1"
              @keydown="onTextareaKeydown"
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
        
        <!-- 附件列表：顯示已上傳的附件 -->
        <div v-if="conversionItems.length > 0" class="attachment-list" style="margin-top: 16px; width: 720px; margin-left: auto; margin-right: auto;">
          <div class="attachment-header">
            <h4>已上傳附件 ({{ conversionItems.length }})</h4>
          </div>
          <div class="attachment-items">
            <div v-for="item in conversionItems" :key="item.id" class="attachment-item" :class="`status-${item.status}`">
              <div class="attachment-icon">
                <!-- 上傳中：旋轉圖示 -->
                <svg v-if="item.status === 'uploading'" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width: 1.5em; height: 1.5em;" class="rotating">
                  <path d="M21 12a9 9 0 11-6.219-8.56"/>
                </svg>
                <!-- 轉換中：旋轉圖示 -->
                <svg v-else-if="item.status === 'converting'" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width: 1.5em; height: 1.5em;" class="rotating">
                  <path d="M21 12a9 9 0 11-6.219-8.56"/>
                </svg>
                <!-- 已完成：綠色勾勾 -->
                <svg v-else-if="item.status === 'completed'" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width: 1.5em; height: 1.5em;" class="status-completed">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                  <polyline points="22,4 12,14.01 9,11.01"/>
                </svg>
                <!-- 上傳失敗：紅色 X -->
                <svg v-else-if="item.status === 'failed'" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width: 1.5em; height: 1.5em;" class="status-failed">
                  <circle cx="12" cy="12" r="10"/>
                  <line x1="15" y1="9" x2="9" y2="15"/>
                  <line x1="9" y1="9" x2="15" y2="15"/>
                </svg>
              </div>
              <div class="attachment-content">
                <div class="attachment-title">{{ item.fileName }}</div>
                <div class="attachment-meta">
                  <span v-if="item.status === 'uploading'">正在上傳...</span>
                  <span v-else-if="item.status === 'converting'">正在轉換...</span>
                  <span v-else-if="item.status === 'completed'">轉換完成</span>
                  <span v-else-if="item.status === 'failed'" class="error-text">{{ item.errorMessage }}</span>
                  <span class="file-size">({{ formatFileSize(item.fileSize) }})</span>
                </div>
                <!-- 上傳進度條 -->
                <div v-if="item.status === 'uploading' || item.status === 'converting'" class="progress-bar">
                  <div class="progress-bar-fill"></div>
                </div>
              </div>
              <div class="attachment-actions">
                <t-button 
                  v-if="item.status === 'completed' && item.convertedUrl"
                  theme="primary" 
                  variant="text" 
                  size="small"
                  @click="viewMarkdownContent(item)"
                >
                  檢視 Markdown
                </t-button>
                <t-button 
                  v-if="item.status === 'completed' && item.convertedUrl"
                  theme="default" 
                  variant="text" 
                  size="small"
                  @click="openConvertedFile(item)"
                >
                  查看原始
                </t-button>
                <t-button 
                  v-if="item.status === 'failed'"
                  theme="default" 
                  variant="text" 
                  size="small"
                  @click="retryConversion(item)"
                >
                  重試
                </t-button>
                <t-button 
                  theme="default" 
                  variant="text" 
                  size="small"
                  @click="removeConversionItem(item)"
                >
                  移除
                </t-button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 進度日誌：任何時候都顯示 -->
        <div v-if="progress.length" class="progress" style="margin-top: 16px; width: 720px; margin-left: auto; margin-right: auto;">
          <div class="progress-list">
            <div v-for="(p, i) in progress" :key="i" class="log-line">
              <span class="type">[{{ p.type ?? 'info' }}]</span>
              <span v-if="p.stage" class="stage">({{ p.stage }})</span>
              <span>{{ p.message }}</span>
            </div>
          </div>
        </div>
        
      </div>
    </t-card>

    <!-- 隱藏檔案選擇器 -->
    <input ref="filePickerRef" type="file" style="display:none" @change="onFileChosen" />

    <!-- Markdown 檢視 Modal -->
    <t-dialog
      v-model:visible="showMarkdownModal"
      :header="markdownModalTitle"
      width="80%"
      height="80%"
      :close-on-overlay-click="true"
      :close-on-esc-keydown="true"
    >
      <div class="markdown-viewer">
        <!-- 工具欄 -->
        <div class="markdown-toolbar">
          <div class="toolbar-left">
            <div class="view-mode-buttons">
              <t-button 
                :variant="markdownViewMode === 'raw' ? 'base' : 'outline'"
                @click="markdownViewMode = 'raw'"
                size="small"
              >
                原始
              </t-button>
              <t-button 
                :variant="markdownViewMode === 'preview' ? 'base' : 'outline'"
                @click="markdownViewMode = 'preview'"
                size="small"
              >
                預覽
              </t-button>
              <t-button 
                :variant="markdownViewMode === 'split' ? 'base' : 'outline'"
                @click="markdownViewMode = 'split'"
                size="small"
              >
                並排
              </t-button>
            </div>
          </div>
          <div class="toolbar-right">
            <t-button @click="copyMarkdownContent" size="small">複製內容</t-button>
            <t-button @click="insertToEditor" size="small">插入到編輯器</t-button>
            <t-button @click="downloadMarkdown" size="small">下載檔案</t-button>
          </div>
        </div>
        
        <!-- 內容區域 -->
        <div class="markdown-content">
          <!-- 原始 Markdown -->
          <div v-if="markdownViewMode === 'raw'" class="markdown-raw">
            <pre>{{ markdownContent }}</pre>
          </div>
          
          <!-- 渲染後的 HTML -->
          <div v-else-if="markdownViewMode === 'preview'" class="markdown-preview" v-html="renderedMarkdown"></div>
          
          <!-- 並排顯示 -->
          <div v-else-if="markdownViewMode === 'split'" class="markdown-split">
            <div class="markdown-raw">
              <h4>原始 Markdown</h4>
              <pre>{{ markdownContent }}</pre>
            </div>
            <div class="markdown-preview">
              <h4>預覽</h4>
              <div v-html="renderedMarkdown"></div>
            </div>
          </div>
        </div>
      </div>
    </t-dialog>

  </div>
  
</template>

<script setup lang="ts">
import { marked } from 'marked'

type PendingAttachment = { id: string; url: string; name: string; type: string; size: number }
const emit = defineEmits<{
  (e: 'confirm', title: string, attachments?: PendingAttachment[], documentId?: string): void
  (e: 'cancel'): void
}>()

const title = ref('')
const error = ref('')
const generating = ref(false)
const progress = ref<Array<{ type?: string; stage?: string; message: string }>>([])
let es: EventSource | null = null
const canceling = ref(false)
let composing = false

// 為需要使用 Tooltip/Popup 的子元件提供容器
provide('container', '#new-document')

// 立即上傳後暫存的附件結果（待進入編輯器時插入）
const pendingAttachments = ref<PendingAttachment[]>([])

// PDF 轉換狀態管理
interface ConversionItem {
  id: string
  fileName: string
  fileSize: number
  uploadTime: Date
  status: 'uploading' | 'converting' | 'completed' | 'failed'
  progress?: number
  errorMessage?: string
  convertedUrl?: string
}
const conversionItems = ref<ConversionItem[]>([])

// Markdown 檢視相關變數
const showMarkdownModal = ref(false)
const markdownModalTitle = ref('')
const markdownContent = ref('')
const markdownViewMode = ref<'raw' | 'preview' | 'split'>('preview')

// Markdown 渲染計算屬性
const renderedMarkdown = computed(() => {
  try {
    return marked(markdownContent.value)
  } catch (error) {
    console.error('Markdown 渲染錯誤:', error)
    return '<p>Markdown 渲染失敗</p>'
  }
})

// 提供附件數據給 app.vue 使用
provide('conversionItems', conversionItems)
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
    
    // 如果是 PDF 檔案，加入轉換清單
    if (file.type === 'application/pdf') {
      const conversionItem: ConversionItem = {
        id: `pdf-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        fileName: file.name,
        fileSize: file.size,
        uploadTime: new Date(),
        status: 'uploading'
      }
      conversionItems.value.push(conversionItem)
    }
    
    const form = new FormData()
    form.append('file', file)
    const res = await fetch('http://localhost:8000/upload', {
      method: 'POST',
      body: form,
    })
    if (!res.ok) throw new Error('上傳失敗')
    const data = await res.json() as { 
      id: string; 
      url: string; 
      name?: string; 
      processed?: boolean; 
      status?: string; 
      error?: string 
    }
    
    // 如果是 PDF，根據後端回應更新轉換狀態
    if (file.type === 'application/pdf') {
      const item = conversionItems.value.find((c: ConversionItem) => c.fileName === file.name)
      if (item) {
        if (data.processed && data.status === 'completed') {
          item.status = 'completed'
          // 將相對路徑轉換為絕對路徑，使用 8000 端口
          console.log('後端回傳的 data.url:', data.url)
          if (data.url.startsWith('/')) {
            // 相對路徑，轉換為絕對路徑
            item.convertedUrl = `http://localhost:8000${data.url}`
          } else {
            // 已經是絕對路徑，替換端口
            item.convertedUrl = data.url.replace(':9000', ':8000')
          }
          console.log('設定後的 item.convertedUrl:', item.convertedUrl)
          pushLog({ type: 'info', message: `PDF 轉換完成：${file.name}` })
        } else if (data.status === 'failed') {
          item.status = 'failed'
          item.errorMessage = data.error || '轉換失敗'
          pushLog({ type: 'error', message: `PDF 轉換失敗：${file.name} - ${item.errorMessage}` })
        } else {
          item.status = 'converting'
          pushLog({ type: 'info', message: `正在轉換 PDF：${file.name}` })
        }
      }
    } else {
      // 非 PDF 檔案直接加入待處理附件
      const item = {
        id: data.id,
        url: data.url,
        name: data.name ?? file.name,
        type: file.type,
        size: file.size,
      }
      pendingAttachments.value.push(item)
    }
    
    pushLog({ type: 'info', message: `附件已上傳：${file.name}` })
  } catch (err: any) {
    pushLog({ type: 'error', message: `附件上傳失敗：${err?.message ?? '未知錯誤'}` })
    
    // 如果是 PDF 上傳失敗，更新狀態
    if (file.type === 'application/pdf') {
      const item = conversionItems.value.find((c: ConversionItem) => c.fileName === file.name)
      if (item) {
        item.status = 'failed'
        item.errorMessage = err?.message ?? '上傳失敗'
      }
    }
  }
}

// 附件操作函式
function openConvertedFile(item: ConversionItem) {
  if (item.convertedUrl) {
    console.log('=== openConvertedFile 調用 ===')
    console.log('item.convertedUrl:', item.convertedUrl)
    console.log('============================')
    
    // 直接使用 convertedUrl，因為它已經是正確的絕對路徑
    window.open(item.convertedUrl, '_blank')
  } else {
    console.error('convertedUrl 不存在:', item)
  }
}

function retryConversion(item: ConversionItem) {
  // 重新上傳檔案
  const file = new File([''], item.fileName, { type: 'application/pdf' })
  void uploadAttachment(file)
}

function removeConversionItem(item: ConversionItem) {
  const index = conversionItems.value.findIndex((c: ConversionItem) => c.id === item.id)
  if (index !== -1) {
    conversionItems.value.splice(index, 1)
  }
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// Markdown 檢視相關函式 - 參考 app.vue 的實作方式
async function viewMarkdownContent(item: ConversionItem) {
  try {
    console.log('=== 檢視 Markdown ===')
    console.log('檔案名稱:', item.fileName)
    console.log('convertedUrl:', item.convertedUrl)
    console.log('==================')
    
    // 設定標題
    markdownModalTitle.value = item.fileName
    
    // 構建 API URL - 不傳入 documentId，只傳入檔案名稱
    let apiUrl = 'http://localhost:8000/markdown'
    const params = new URLSearchParams()
    
    // 只傳入檔案名稱，不傳入 documentId
    if (item.fileName) {
      params.append('file_name', item.fileName)
    }
    
    if (params.toString()) {
      apiUrl += `?${params.toString()}`
    }
    
    console.log('API URL:', apiUrl)
    
    // 發送請求
    const response = await fetch(apiUrl, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json; charset=utf-8',
        'Accept': 'application/json; charset=utf-8',
      }
    })
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }
    
    // 確保正確處理編碼
    const text = await response.text()
    let data
    try {
      data = JSON.parse(text)
    } catch (e) {
      console.error('JSON 解析失敗:', e)
      console.error('原始回應:', text)
      throw new Error('回應格式錯誤')
    }
    console.log('API 回傳資料:', data)
    
    // 檢查回傳資料格式
    if (data && typeof data === 'object') {
      if (data.content) {
        markdownContent.value = data.content
      } else if (data.markdown) {
        markdownContent.value = data.markdown
      } else if (data.text) {
        markdownContent.value = data.text
      } else {
        throw new Error('API 回傳資料中沒有找到 Markdown 內容')
      }
      
      // 更新標題（如果 API 回傳了檔案名稱）
      if (data.fileName) {
        markdownModalTitle.value = data.fileName
      } else if (data.filename) {
        markdownModalTitle.value = data.filename
      }
    } else if (typeof data === 'string') {
      // 如果直接回傳字串
      markdownContent.value = data
    } else {
      throw new Error('API 回傳資料格式不正確')
    }
    
    // 顯示 Modal
    showMarkdownModal.value = true
    
  } catch (error) {
    console.error('讀取 Markdown 內容失敗:', error)
    
    // 錯誤處理：顯示預設內容
    markdownContent.value = `# ${markdownModalTitle.value}

## 讀取失敗

無法從伺服器讀取 Markdown 內容。

### 錯誤詳情
\`\`\`
${error instanceof Error ? error.message : String(error)}
\`\`\`

### 請求參數
- 檔案名稱: ${item.fileName || '無'}

### 可能的解決方案
1. 檢查伺服器是否正在運行
2. 確認 API 端點是否正確
3. 檢查網路連接
4. 確認檔案是否存在

---

**注意**: 請檢查控制台以獲取更多錯誤詳情。`
    
    showMarkdownModal.value = true
  }
}

// Markdown 工具欄功能
function copyMarkdownContent() {
  navigator.clipboard.writeText(markdownContent.value).then(() => {
    console.log('Markdown 內容已複製到剪貼簿')
  }).catch((error) => {
    console.error('複製失敗:', error)
  })
}

function insertToEditor() {
  // 在 new-document.vue 中，我們可以將內容添加到標題或準備插入到編輯器
  if (markdownContent.value) {
    // 可以將 Markdown 內容添加到標題中，或者準備在進入編輯器時插入
    console.log('準備插入 Markdown 內容到編輯器')
    showMarkdownModal.value = false
    // 這裡可以添加邏輯來處理內容插入
  }
}

function downloadMarkdown() {
  try {
    const blob = new Blob([markdownContent.value], { type: 'text/markdown;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${markdownModalTitle.value.replace(/\.[^/.]+$/, '')}.md`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    console.log('Markdown 檔案已下載')
  } catch (error) {
    console.error('下載失敗:', error)
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
          filename?: string
          status?: string
          document_id?: string
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
          
          // 取得 document_id (task_id)
          const documentId = data.document_id
          if (documentId) {
            pushLog({ type: 'info', message: `文檔 ID: ${documentId}` })
          }
          
          // 在 console 顯示標題和 ID
          console.log('=== 報告完成資訊 ===')
          console.log('報告標題:', title.value.trim())
          console.log('文檔 ID:', documentId)
          console.log('==================')
          
          es?.close()
          es = null
          generating.value = false
          isConnected.value = false
          emit('confirm', title.value.trim(), pendingAttachments.value, documentId)
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

function onTextareaKeydown(e: KeyboardEvent) {
  if (e.key !== 'Enter') return
  if (e.shiftKey) {
    e.stopPropagation()
    return
  }
  e.preventDefault()
  onEnter()
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

/* 標題樣式 */
.title-section {
  text-align: center;
  margin-bottom: 32px;
  margin-top: -40px;
  padding: 0 20px;
}

.title-main {
  font-size: 2.5rem;
  font-weight: 700;
  color: #2563eb;
  text-shadow: 0 4px 8px rgba(37, 99, 235, 0.3);
  margin-bottom: 8px;
  letter-spacing: -0.02em;
  line-height: 1.2;
  transform: translateY(-8px);
}

.title-subtitle {
  font-size: 1.1rem;
  color: #64748b;
  font-weight: 400;
  opacity: 0.8;
  letter-spacing: 0.01em;
}

/* 響應式設計 */
@media (max-width: 768px) {
  .title-main {
    font-size: 2rem;
  }
  
  .title-subtitle {
    font-size: 1rem;
  }
  
  .title-section {
    margin-bottom: 24px;
  }
}

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

/* 附件列表樣式 */
.attachment-list {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.attachment-header {
  margin-bottom: 12px;
}

.attachment-header h4 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #374151;
}

.attachment-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.attachment-item {
  display: flex;
  align-items: center;
  padding: 12px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  background: #f9fafb;
  transition: all 0.2s ease;
}

.attachment-item:hover {
  border-color: #d1d5db;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.attachment-item.status-uploading,
.attachment-item.status-converting {
  border-color: #3b82f6;
  background: #eff6ff;
}

.attachment-item.status-completed {
  border-color: #10b981;
  background: #ecfdf5;
}

.attachment-item.status-failed {
  border-color: #ef4444;
  background: #fef2f2;
}

.attachment-icon {
  margin-right: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
}

.attachment-icon .rotating {
  animation: spin 1s linear infinite;
}

.attachment-icon .status-completed {
  color: #10b981;
}

.attachment-icon .status-failed {
  color: #ef4444;
}

.attachment-content {
  flex: 1;
  min-width: 0;
}

.attachment-title {
  font-weight: 500;
  color: #111827;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.attachment-meta {
  font-size: 12px;
  color: #6b7280;
  display: flex;
  align-items: center;
  gap: 8px;
}

.attachment-meta .error-text {
  color: #ef4444;
}

.attachment-meta .file-size {
  color: #9ca3af;
}

.attachment-actions {
  display: flex;
  gap: 4px;
  margin-left: 12px;
}

.progress-bar {
  width: 100%;
  height: 4px;
  background: #e5e7eb;
  border-radius: 2px;
  overflow: hidden;
  margin-top: 8px;
}

.progress-bar-fill {
  height: 100%;
  background: #3b82f6;
  border-radius: 2px;
  animation: progress 2s ease-in-out infinite;
}

@keyframes progress {
  0% { width: 0%; }
  50% { width: 70%; }
  100% { width: 100%; }
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Markdown 檢視樣式 */
.markdown-viewer {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.markdown-toolbar {
  padding: 12px 16px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #f9fafb;
}

.toolbar-left {
  display: flex;
  align-items: center;
}

.toolbar-right {
  display: flex;
  gap: 8px;
}

.view-mode-buttons {
  display: flex;
  gap: 0;
}

.view-mode-buttons .t-button {
  border-radius: 0;
  border-right: none;
}

.view-mode-buttons .t-button:first-child {
  border-radius: 6px 0 0 6px;
}

.view-mode-buttons .t-button:last-child {
  border-radius: 0 6px 6px 0;
  border-right: 1px solid #d1d5db;
}

.view-mode-buttons .t-button:not(:first-child):not(:last-child) {
  border-radius: 0;
}

.markdown-content {
  flex: 1;
  overflow: auto;
  padding: 16px;
  background: white;
}

.markdown-raw {
  height: 100%;
}

.markdown-raw pre {
  background: #f8fafc;
  padding: 16px;
  border-radius: 8px;
  overflow: auto;
  font-family: 'Monaco', 'Consolas', 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.5;
  border: 1px solid #e5e7eb;
  margin: 0;
  height: 100%;
  box-sizing: border-box;
}

.markdown-preview {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 20px;
  background: white;
  height: 100%;
  overflow: auto;
  box-sizing: border-box;
}

.markdown-preview h1,
.markdown-preview h2,
.markdown-preview h3,
.markdown-preview h4,
.markdown-preview h5,
.markdown-preview h6 {
  margin-top: 24px;
  margin-bottom: 16px;
  font-weight: 600;
  line-height: 1.25;
}

.markdown-preview h1 {
  font-size: 2em;
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 8px;
}

.markdown-preview h2 {
  font-size: 1.5em;
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 8px;
}

.markdown-preview h3 {
  font-size: 1.25em;
}

.markdown-preview p {
  margin-bottom: 16px;
  line-height: 1.6;
}

.markdown-preview ul,
.markdown-preview ol {
  margin-bottom: 16px;
  padding-left: 24px;
}

.markdown-preview li {
  margin-bottom: 4px;
}

.markdown-preview blockquote {
  margin: 16px 0;
  padding: 16px;
  background: #f8fafc;
  border-left: 4px solid #3b82f6;
  border-radius: 0 4px 4px 0;
}

.markdown-preview code {
  background: #f1f5f9;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Monaco', 'Consolas', 'Courier New', monospace;
  font-size: 0.9em;
}

.markdown-preview pre {
  background: #1e293b;
  color: #e2e8f0;
  padding: 16px;
  border-radius: 8px;
  overflow: auto;
  margin: 16px 0;
}

.markdown-preview pre code {
  background: transparent;
  padding: 0;
  color: inherit;
}

.markdown-preview table {
  width: 100%;
  border-collapse: collapse;
  margin: 16px 0;
}

.markdown-preview th,
.markdown-preview td {
  border: 1px solid #e5e7eb;
  padding: 8px 12px;
  text-align: left;
}

.markdown-preview th {
  background: #f9fafb;
  font-weight: 600;
}

.markdown-preview hr {
  border: none;
  border-top: 1px solid #e5e7eb;
  margin: 24px 0;
}

.markdown-split {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  height: 100%;
}

.markdown-split .markdown-raw,
.markdown-split .markdown-preview {
  height: 100%;
  overflow: auto;
}

.markdown-split h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
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


