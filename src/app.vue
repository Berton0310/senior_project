<template>
  <div class="examples">
    <div class="box">
      <NewDocument
        v-if="stage === 'new'"
        @confirm="startEditor"
        @cancel="onCancelNew"
      />
      <umo-editor
        v-else-if="options && stage === 'editor'"
        ref="editorRef"
        v-bind="options"
      />
    </div>
    <!-- AI 功能按鈕 -->
    <button
      :class="['ai-fab', { 'ai-fab--hidden': showAIDrawer || stage !== 'editor' }]"
      @click="onAIClick"
    >
      <img
        src="@/assets/icons/message_ai.svg"
        alt="AI"
        width="32"
        height="32"
      />
      <span class="ai-tooltip">AI功能</span>
    </button>
    
    <!-- 清單按鈕 -->
    <button
      :class="['list-fab', { 'list-fab--hidden': showListModal }]"
      @click="openListModal"
    >
      <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" width="32" height="32">
        <rect fill="none" width="24" height="24"/>
        <path fill="#0090ff" d="M1,12C1,4,4,1,12,1S23,4,23,12,20,23,12,23,1,20,1,12"/>
        <rect fill="#ffffff" height="1.44" rx="0.72" width="12.24" x="5.88" y="7.56"/>
        <rect fill="#ffffff" height="1.44" rx="0.72" width="12.24" x="5.88" y="10.28"/>
        <rect fill="#ffffff" height="1.44" rx="0.72" width="12.24" x="5.88" y="13"/>
        <rect fill="#ffffff" height="1.44" rx="0.72" width="7.44" x="5.88" y="15.72"/>
      </svg>
      <span class="list-tooltip">文件清單</span>
    </button>
    
    <!-- 清單彈出視窗 -->
    <t-dialog
      v-model:visible="showListModal"
      header="文件清單"
      width="600px"
      :close-on-overlay-click="true"
      :close-on-esc-keydown="true"
      @close="closeListModal"
      :confirm-btn="null"
      :cancel-btn="{ content: '關閉', theme: 'default' }"
    >
      <div class="list-modal-content">
        <div class="list-header">
          <h3>{{ stage === 'new' ? '文件管理' : '最近的文件' }}</h3>
          <div class="list-header-actions">
            <t-button 
              v-if="stage === 'editor'"
              theme="primary" 
              variant="outline" 
              @click="createNewDocument"
              title="新建文檔"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width: 1em; height: 1em; margin-right: 4px;">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14,2 14,8 20,8"></polyline>
                <line x1="12" y1="18" x2="12" y2="12"></line>
                <line x1="9" y1="15" x2="15" y2="15"></line>
              </svg>
              新建文檔
            </t-button>
          </div>
        </div>
        
        <div class="list-body">
          <!-- 載入中狀態 -->
          <div v-if="loadingDocuments" class="list-loading">
            <div class="loading-spinner"></div>
            <div class="loading-text">載入文檔列表中...</div>
          </div>
          
          <!-- 新建文檔提示 -->
          <div v-if="stage === 'new'" class="list-item new-document-hint">
            <div class="list-item-icon">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width: 1.5em; height: 1.5em; color: #2563eb;">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14,2 14,8 20,8"></polyline>
                <line x1="12" y1="18" x2="12" y2="12"></line>
                <line x1="9" y1="15" x2="15" y2="15"></line>
              </svg>
            </div>
            <div class="list-item-content">
              <div class="list-item-title">新建文檔</div>
              <div class="list-item-meta">
                <span>輸入標題開始建立新文檔</span>
              </div>
            </div>
            <div class="list-item-actions">
              <t-button theme="primary" variant="text" size="small" disabled>
                建立中
              </t-button>
            </div>
          </div>
          
          <!-- 當前文檔資訊 -->
          <div v-if="stage === 'editor' && (currentDocumentId || currentReportTitle)" class="list-item current-document">
            <div class="list-item-icon">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width: 1.5em; height: 1.5em; color: #22c55e;">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14,2 14,8 20,8"></polyline>
                <line x1="16" y1="13" x2="8" y2="13"></line>
                <line x1="16" y1="17" x2="8" y2="17"></line>
                <polyline points="10,9 9,9 8,9"></polyline>
              </svg>
            </div>
            <div class="list-item-content">
              <div class="list-item-title">{{ currentReportTitle || '未命名文檔' }}</div>
              <div class="list-item-meta">
                <span v-if="currentDocumentId">文檔 ID: {{ currentDocumentId }}</span>
                <span v-else>快速建立</span>
                <span class="file-size">(當前編輯中)</span>
              </div>
            </div>
            <div class="list-item-actions">
              <t-button theme="primary" variant="text" size="small" disabled>
                編輯中
              </t-button>
            </div>
          </div>
          
          <!-- 文檔列表 -->
          <div v-if="documentList.length > 0" class="document-list-section">
            <div class="list-section-title">
              <h4>所有文檔 ({{ documentList.length }})</h4>
            </div>
            
            <div v-for="document in documentList" :key="document.id" class="list-item document-item" :class="{ 'current-document': document.id === currentDocumentId }">
              <div class="list-item-icon">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width: 1.5em; height: 1.5em;" :class="{ 'text-green-500': document.id === currentDocumentId, 'text-gray-500': document.id !== currentDocumentId }">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                  <polyline points="14,2 14,8 20,8"></polyline>
                  <line x1="16" y1="13" x2="8" y2="13"></line>
                  <line x1="16" y1="17" x2="8" y2="17"></line>
                  <polyline points="10,9 9,9 8,9"></polyline>
                </svg>
              </div>
              <div class="list-item-content">
                <div class="list-item-title">{{ document.title }}</div>
                <div class="list-item-meta">
                  <span>文檔 ID: {{ document.id }}</span>
                  <span v-if="document.attachmentCount" class="file-size">({{ document.attachmentCount }} 個附件)</span>
                  <span class="file-size">更新於: {{ formatDate(document.updatedAt) }}</span>
                </div>
              </div>
              <div class="list-item-actions">
                <t-button 
                  v-if="document.id === currentDocumentId"
                  theme="primary" 
                  variant="text" 
                  size="small" 
                  disabled
                >
                  編輯中
                </t-button>
                <t-button 
                  v-else
                  theme="primary" 
                  variant="text" 
                  size="small"
                  @click="switchToDocument(document)"
                >
                  開啟
                </t-button>
              </div>
            </div>
          </div>
          
          <!-- 附件標題和上傳按鈕 -->
          <div v-if="(uploadItems.length > 0 || conversionItems.length > 0) || stage === 'editor'" class="list-section-title">
            <h4>附件 ({{ uploadItems.length + conversionItems.length }})</h4>
            <div class="attachment-actions">
              <button 
                v-if="stage === 'editor' && currentDocumentId"
                class="refresh-button"
                @click="refreshAttachments"
                title="刷新附件列表"
              >
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width: 1em; height: 1em;">
                  <polyline points="23,4 23,10 17,10"/>
                  <polyline points="1,20 1,14 7,14"/>
                  <path d="M20.49,9A9,9,0,0,0,5.64,5.64L1,10m22,4L18.36,18.36A9,9,0,0,1,3.51,15"/>
                </svg>
                刷新
              </button>
              <button 
                v-if="stage === 'editor'"
                class="upload-button"
                @click="onPickAttachment"
                title="上傳附件"
              >
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width: 1em; height: 1em;">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                  <polyline points="17,8 12,3 7,8"/>
                  <line x1="12" y1="3" x2="12" y2="15"/>
                </svg>
                上傳
              </button>
            </div>
          </div>
          
          <!-- new-document.vue 的上傳項目 -->
          <div v-for="item in conversionItems" :key="`conversion-${item.id}`" class="list-item upload-item" :class="`status-${item.status}`">
            <div class="list-item-icon">
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
            <div class="list-item-content">
              <div class="list-item-title">{{ item.fileName }}</div>
              <div class="list-item-meta">
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
            <div class="list-item-actions">
              <t-button 
                v-if="item.status === 'completed'"
                theme="primary" 
                variant="text" 
                size="small"
                @click="viewMarkdownFromAttachment(item)"
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
          
          <!-- app.vue 的上傳項目 -->
          <div v-for="item in uploadItems" :key="item.id" class="list-item upload-item" :class="`status-${item.status}`">
            <div class="list-item-icon">
              <!-- 上傳中：旋轉圖示 -->
              <svg v-if="item.status === 'uploading'" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width: 1.5em; height: 1.5em;" class="rotating">
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
            <div class="list-item-content">
              <div class="list-item-title">{{ item.fileName }}</div>
              <div class="list-item-meta">
                <span v-if="item.status === 'uploading'">正在上傳...</span>
                <span v-else-if="item.status === 'completed'">上傳完成</span>
                <span v-else-if="item.status === 'failed'" class="error-text">{{ item.errorMessage }}</span>
                <span class="file-size">({{ formatFileSize(item.fileSize) }})</span>
              </div>
              <!-- 上傳進度條 -->
              <div v-if="item.status === 'uploading'" class="progress-bar">
                <div class="progress-fill"></div>
              </div>
            </div>
            <div class="list-item-actions">
              <t-button 
                v-if="item.status === 'completed'"
                theme="primary" 
                variant="text" 
                size="small"
                @click="viewMarkdownFromAttachment(item)"
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
                @click="removeUploadItem(item)"
              >
                移除
              </t-button>
            </div>
          </div>
          
          <!-- 空狀態 -->
          <div class="list-empty" v-if="stage === 'editor' && !currentDocumentId && !currentReportTitle && uploadItems.length === 0 && conversionItems.length === 0">
            <div class="empty-icon">📄</div>
            <div class="empty-text">尚無內容</div>
            <div class="empty-desc">上傳附件開始編輯吧！</div>
          </div>
          
          <!-- 新建文檔空狀態 -->
          <div class="list-empty" v-if="stage === 'new'">
            <div class="empty-icon">📝</div>
            <div class="empty-text">準備建立新文檔</div>
            <div class="empty-desc">輸入標題並上傳附件開始吧！</div>
          </div>
        </div>
      </div>
    </t-dialog>
    
    <!-- Markdown 檢視 Modal -->
    <t-dialog
      v-model:visible="showMarkdownModal"
      :header="markdownModalTitle"
      width="80%"
      height="80%"
      :close-on-overlay-click="true"
      :close-on-esc-keydown="true"
      @close="showMarkdownModal = false"
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
    
    <!-- 隱藏檔案選擇器 -->
    <input ref="filePickerRef" type="file" style="display:none" @change="onFileChosen" />
  </div>
</template>

<script setup lang="ts">
import { shortId } from '@/utils/short-id'
import NewDocument from '@/pages/new-document.vue'
import { marked } from 'marked'

// API 初始化函式
async function initDocument(documentId?: string) {
  try {
    console.log('=== initDocument 調用 ===')
    console.log('文檔 ID:', documentId)
    console.log('======================')
    
    // 如果有文檔 ID，使用特定的文檔 API
    const url = documentId 
      ? `http://localhost:8000/documents/${documentId}`
      : 'http://localhost:8000/load-document'
    
    const res = await fetch(url)
    if (!res.ok) throw new Error('讀取失敗')
    const data = await res.json()
    console.log('API 回傳資料:', data)

    // 確保 data 存在且為物件
    if (!data || typeof data !== 'object') {
      throw new Error('API 回傳資料格式錯誤')
    }

    // 如果有文檔 ID，讀取該文檔的附件
    if (documentId) {
      console.log('讀取文檔附件...')
      await loadDocumentAttachments(documentId)
    }

    return {
      title: data.title ?? '测试文档',
      content: data.content ?? '<p>測試內容</p>',
      characterLimit: data.characterLimit ?? 10000,
    }
  } catch (e) {
    console.error('讀取出錯:', e)
    return {
      title: '测试文档',
      // content: '<p>預設內容\n測試內容</p>',
      content: `# **台積電對台灣半導體經濟的全面影響：一份綜合研究報告**

本報告旨在深入分析台灣積體電路製造股份有限公司（TSMC，簡稱台積電）對台灣經濟與半導體產業生態系的全面影響。基於對政府報告、企業財報、學術分析及財經媒體的綜合研究，本報告將從總體經濟貢獻、就業創造、產業鏈發展、技術創新、資本投資以及相關風險挑戰等六個關鍵領域，進行量化與質化評估，並對未來趨勢提出展望。

## **一、總體經濟貢獻：GDP與經濟成長的引擎**

雖然本次研究未能尋獲台積電產值佔台灣GDP的精確官方百分比數據，但其對台灣經濟的巨大貢獻是毋庸置疑的。台積電作為全球最大的晶圓代工廠，其營收與出口表現直接牽動台灣的經濟成長脈動。

-   **營收成長目標**：台積電董事長魏哲家重申，公司2024年的美元營收成長目標維持在24-26%之間，顯示出強勁的成長動能 [1]。此一增長不僅反映了全球對AI和先進晶片的需求，也直接轉化為台灣出口額與經濟產值的提升。
-   **經濟支柱角色**：台積電的營運表現已成為衡量台灣經濟健康度的關鍵指標。其營收佔台灣整體製造業的比重極高，其資本支出和研發投入更是驅動國內投資和技術升級的核心動力。一份研究報告指出，若將半導體出口排除，台灣在2010年至2020年間的商品出口總額實際上是下降了1.8%，凸顯了台積電及半導體產業在支撐台灣出口成長中的絕對關鍵地位 [2]。

## **二、就業創造：直接與間接的就業引擎**

台積電不僅是台灣最大的雇主之一，其龐大的產業生態系更間接創造了數以萬計的就業機會。儘管精確的總體就業數據難以量化，但其影響力可從以下幾個層面分析：

-   **直接就業**：台積電直接僱用大量高技術、高薪資的工程師、研發人員與技術專家。這些高品質的就業機會不僅提升了台灣的勞動力素質，也因其高薪資帶動了周邊地區的消費與經濟活動。
-   **間接就業**：台積電的成功建立在一個龐大而緊密的本地供應鏈之上。從上游的材料、化學品、特殊氣體，到中游的設備製造、廠務工程，再到下游的封裝測試，每個環節都涵蓋了眾多協力廠商。如**漢唐**、**辛耘**、**家登**、**中砂**等企業，因與台積電的緊密合作而得以壯大，僱用了大量員工 [3, 4]。可以說，台積電每增加一個直接職位，都會在供應鏈中催生數個間接工作崗位。
-   **人才競爭**：台積電的巨大吸引力也帶來了人才排擠效應。布魯金斯學會的分析指出，全球半導體業皆面臨人才短缺，台灣也不例外 [5]。台積電以其優渥的薪資和發展前景，吸引了最頂尖的STEM人才，使得其他傳統產業或新創企業在人才招募上面臨巨大挑戰 [2]。

## **三、產業鏈發展：建構世界級的本土供應聚落**

台積電的「專業晶圓代工」模式不僅是其自身的成功基石，更是台灣建立完整半導體產業聚落的核心驅動力。過去四十多年來，台積電以「大廠引導供應鏈」的模式，帶動了整個台灣本土供應鏈的技術升級與業務擴張 [6]。

### **以大帶小的垂直分工體系**
台積電首創的垂直分工模式，讓IC設計公司無需承擔鉅額的建廠成本，從而專注於創新，並與製造端形成緊密合作 [7]。其「開放創新平台」（OIP）更整合了電子設計自動化（EDA）與矽智財（IP）聯盟，持續推動產業的協同創新 [8]。這種模式讓台灣形成了彈性高、速度快、成本低的獨特競爭優勢 [7]。

### **本土供應商的崛起與結盟**
在台積電的積極扶植下，眾多台灣供應商從PCB、面板等領域轉向技術門檻更高的半導體產業，並隨台積電走向國際 [9]。
-   **優良供應商**：在2024年的供應鏈管理論壇上，台積電表彰了7家台灣本土優良供應商，包括**辛耘**（設備）、**漢唐**（廠務）、**李長榮集團**（化學品）、**崇越石英**（材料）等，涵蓋了產業鏈的各個關鍵環節 [3]。
-   **先進製程夥伴**：隨著台積電推進至3奈米、2奈米製程，相關供應商價值凸顯。例如，**家登**成為全球EUV光罩盒龍頭，**中砂**在先進製程的鑽石碟市場佔據主導地位，**旺矽**的高階探針卡也因AI、HPC需求而穩定成長 [4]。
-   **供應商聯盟化**：為配合台積電的全球佈局與技術需求，台灣供應商掀起結盟風潮。例如，由**家登**、**意德士**等18家廠商組成的「德鑫控股」，以及由**志聖**、**均豪**、**均華**組成的「G2C+聯盟」，都旨在整合資源，共同進軍國際市場 [9]。

## **四、技術創新與研發：鞏固台灣的全球科技領導地位**

台積電的行業主導地位根植於其對技術創新的不懈追求和鉅額的研發投入，這也直接鞏固了台灣在全球科技版圖中的核心角色。

-   **研發投入規模**：2024年，台積電的研發支出達到創紀錄的**63.55億美元**（約1944億新台幣），佔其營收的7.1%。此一數字約佔台灣整體製造業研發費用的四分之一，顯示其在驅動全國技術創新中的核心地位 [10]。
-   **專利佈局**：截至2024年，台積電在全球累計的核准專利已超過**10萬件**。在台灣，台積電以1,412件發明專利申請，**連續九年**蟬聯本國申請人之首，其龐大的專利組合是其技術護城河的具體體現 [10, 11]。
-   **技術領先優勢**：台積電在先進製程上持續領先。2025年第二季的財報顯示，7奈米及以下的先進製程佔其營收比重高達74% [1]。這種技術優勢使其成為蘋果、輝達等全球頂尖科技公司的唯一或主要供應商，讓台灣在全球高科技供應鏈中扮演著不可或缺的角色。

## **五、資本投資：驅動基礎設施與投資環境**

台積電在台灣的持續大規模資本支出，是驅動本地投資、創造需求及促進基礎設施升級的關鍵力量。

-   **投資規模**：雖然近年具體的年度資本支出總額未在研究中明確列出，但其投資規模極其龐大。例如，早在2013年，其年度資本支出就已高達90億美元 [12]。近期在美國亞利桑那州高達1550億美元的投資計畫，更反襯出其在台灣本土投資的巨大體量 [1]。
-   **對基礎設施的影響**：一座先進晶圓廠的建設與運營，需要龐大的基礎設施支持。這不僅帶動了如**達欣工程**、**東鋼鋼結構**等營造公司的業務 [3]，更對台灣的水、電供應提出了巨大需求。為滿足台積電等半導體企業的需求，台灣政府推動了「前瞻基礎建設計畫」等政策，大力投資於再生水廠、電網韌性等項目，從而帶動了整體基礎設施的現代化 [13, 14]。
-   **對投資環境的影響**：台積電的設廠計畫往往能帶動周邊地區的房地產、商業與服務業發展，形成所謂的「台積電效應」。更重要的是，其持續在台投資，將最先進的研發中心與產能根留台灣，向全球釋放了對台灣投資環境的信心訊號，有助於吸引更多外資與人才 [15]。

## **六、經濟風險與挑戰：單一依賴下的脆弱性**

在享受台積電帶來巨大經濟紅利的同時，台灣也面臨著對單一企業及產業過度依賴所帶來的潛在風險與挑戰。

### **經濟過度依賴與「荷蘭病」隱憂**
「荷蘭病」係指一國經濟過度依賴單一強勢產業（如自然資源），導致匯率上升，削弱其他產業（如製造業）的出口競爭力。
-   **支持觀點**：諾丁漢大學的一份報告指出，台灣已呈現「荷蘭病」的症狀。半導體產業的獨大排擠了其他產業的資源，報告數據顯示，若排除半導體，台灣在2010-2020年間的出口額是負成長的。這種現象抑制了經濟的結構性轉型 [2]。
-   **反對觀點**：台灣財政部與中央銀行則認為，政府正透過「五加二」產業計畫推動多元發展，且塑膠、鋼鐵等傳統產業仍具全球競爭力，故不存在「荷蘭病」問題 [16]。

### **資源排擠效應：水、電、人才的競爭**
台積電的龐大規模對台灣有限的資源構成了顯著的壓力。
-   **水資源**：半導體製造是高度耗水產業。台積電2022年的總取水量達1.04億立方公尺 [17]。在氣候變遷導致乾旱頻發的背景下，工業用水需求與民生、農業用水之間的矛盾日益突出 [14]。
-   **電力需求**：半導體也是能源消耗大戶。預計到2030年，台灣半導體產業的用電量將增長236% [13]。台灣超過80%的電力來自進口化石燃料，這使得能源供應鏈在地緣政治威脅下顯得格外脆弱 [13]。
-   **人才競爭**：如前所述，半導體業吸納了大量頂尖人才，對其他產業的發展構成了挑戰。

### **地緣政治的脆弱性：「矽盾」的雙面刃**
台灣生產全球約90%的先進晶片，這種主導地位被稱為「矽盾」（Silicon Shield），理論上能嚇阻軍事侵略，因為任何衝突都將引發全球經濟災難 [18, 19]。然而，這也使台灣成為地緣政治的焦點。
-   **依賴的風險**：CSIS的報告估計，一場台海衝突可能導致全球經濟損失高達10兆美元 [19]。正因如此，美、歐、日等國正積極推動晶片製造本地化，以降低對台灣的依賴，長期可能削弱「矽盾」的保護效果 [20]。
-   **美中科技戰的壓力**：台灣夾在美中科技競爭之間，台積電被迫遵守美國的出口管制，同時也面臨美國要求其在美設廠的壓力。這在台灣內部引發了關於核心產業被「掏空」的擔憂 [20]。

### **未來展望與應對策略**
預計未來5到10年，資源限制與地緣政治壓力將持續存在。對此，台灣與台積電正採取多管齊下的策略：
1.  **企業全球化佈局**：台積電在美國、日本、德國等地設廠，以分散風險並貼近客戶，但同時強調最先進的研發與產能（如1奈米製程）將根留台灣 [15]。
2.  **政府推動多元化**：政府透過「五加二產業創新計畫」扶植綠能、生醫等新興產業，降低對單一半導體產業的依賴，並投資基礎設施以應對資源挑戰 [16, 13]。
3.  **深化國際合作**：透過與美國等盟友建立更深厚的技術與貿易夥伴關係，共同維護供應鏈的韌性與安全 [5]。

---

### **來源**

[1] 台積電(TSMC) 最新2025年展望：半導體技術、法說會與關稅 ...: https://opas.school/posts/tsm
[2] Semiconductors: Taiwan's case of 'Dutch disease'?: https://www.nottingham.ac.uk/research/groups/taiwan-research-hub/documents/michael-reilly-1123-paper.pdf
[3] 台積電2024年12月供應鏈管理論壇頒發優良供應商獎項給27家廠商 (研究發現中提及，但未提供URL)
[4] 台積電法說會對台灣半導體產業鏈的長期影響為何？: https://aigc-note.cmoney.tw/answer/%E5%8F%B0%E7%A9%8D%E9%9B%BB%E6%B3%95%E8%AA%AA%E6%9C%83-97-1213834
[5] Ensuring a stronger US-Taiwan tech supply chain ...: https://www.brookings.edu/articles/ensuring-a-stronger-us-taiwan-tech-supply-chain-partnership/
[6] 產業分析：半導體投資模式為「大廠引導供應鏈」(研究發現中提及，但未提供URL)
[7] 工研院報告：台灣半導體產業的歷史與模式 (研究發現中提及，但未提供URL)
[8] 創新管理: https://esg.tsmc.com/file/public/c-AnInnovationPioneer_1.pdf
[9] 台灣本土設備廠商結盟組隊，隨台積電出海布局國際市場 (研究發現中提及，但未提供URL)
[10] 台積電2024年度永續報告書 (研究發現中提及，但未提供URL)
[11] 經濟部智慧財產局統計：台積電連續九年位居發明專利申請之首 (研究發現中提及，但未提供URL)
[12] 台積電2013年資本支出提高至90億美元 (研究發現中提及，但未提供URL)
[13] Taiwan's Semiconductor Sustainability and Global Implications: https://newlinesinstitute.org/geo-economics/taiwans-semiconductor-sustainability-and-global-implications/
[14] Water and microchips: the climatic and industrial future of Taiwan: https://gauthierroussilhe.com/en/articles/water-and-microchips-the-climatic-and-industrial-future-of-taiwan
[15] TSMC is Building 11 Extra Production Lines in Taiwan Besides $100 ...: https://techsoda.substack.com/p/tsmcs-us100-bln-investment-was-driven
[16] Chip boom 'does not harm' other sectors - Taipei Times: https://www.taipeitimes.com/News/biz/archives/2022/11/10/2003788603
[17] On the tailor-made water governance mechanism for Taiwan's ...: https://www.sciencedirect.com/science/article/pii/S2212371724000143
[18] TSMC: The Enduring Silicon Shield of Taiwan's Economy: https://taiwaninsight.org/2025/05/12/tsmc-the-enduring-silicon-shield-of-taiwans-economy/
[19] Silicon Island: Assessing Taiwan’s Importance to U.S. Economic ...: https://www.csis.org/analysis/silicon-island-assessing-taiwans-importance-us-economic-growth-and-security
[20] Why Taiwan Fears 'America First' Risks Eroding Its 'Silicon ...: https://www.stimson.org/2025/why-taiwan-fears-america-first-risks-eroding-its-silicon-shield/`,
      characterLimit: 10000,
      
    }
  }
}
function onAIClick() {
  showAIDrawer.value = true
}

// 清單功能函式
function openListModal() {
  showListModal.value = true
  console.log('=== 開啟文件清單 ===')
  console.log('文檔 ID:', currentDocumentId.value)
  console.log('報告標題:', currentReportTitle.value)
  console.log('==================')
  
  // 載入文檔列表
  void loadDocumentList()
}

function closeListModal() {
  showListModal.value = false
}

// Markdown 檢視相關函式

async function fetchMarkdownContent(url: string) {
  console.log('嘗試讀取 URL:', url)
  
  // 檢查 URL 是否有效
  if (!url || (!url.startsWith('http') && !url.startsWith('/'))) {
    throw new Error(`無效的 URL: ${url}`)
  }
  
  // 將 URL 中的 9000 端口替換為 8000
  const correctedUrl = url.replace(':9000', ':8000')
  if (correctedUrl !== url) {
    console.log('修正 URL 端口:', url, '->', correctedUrl)
  }
  
  const response = await fetch(correctedUrl)
  console.log('回應狀態:', response.status, response.statusText)
  
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`)
  }
  
  const content = await response.text()
  console.log('成功讀取內容，長度:', content.length)
  markdownContent.value = content
}

// 新的 Markdown 檢視函式 - 支援 document_id 和檔案名稱
async function viewMarkdownByDocument(documentId?: string, fileName?: string) {
  try {
    console.log('=== 檢視 Markdown ===')
    console.log('文檔 ID:', documentId)
    console.log('檔案名稱:', fileName)
    console.log('==================')
    
    // 設定標題
    markdownModalTitle.value = fileName || 'Markdown 文檔'
    
    // 構建 API URL
    let apiUrl = 'http://localhost:8000/markdown'
    const params = new URLSearchParams()
    
    if (documentId) {
      params.append('document_id', documentId)
    }
    
    if (fileName) {
      params.append('file_name', fileName)
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
    console.log('原始回應文字長度:', text.length)
    console.log('原始回應前200字元:', text.substring(0, 200))
    
    let data
    try {
      data = JSON.parse(text)
      console.log('JSON 解析成功')
    } catch (e) {
      console.error('JSON 解析失敗:', e)
      console.error('原始回應:', text)
      throw new Error('回應格式錯誤')
    }
    console.log('API 回傳資料:', data)
    
    // 檢查內容編碼
    if (data && data.content) {
      console.log('內容長度:', data.content.length)
      console.log('內容前100字元:', data.content.substring(0, 100))
      
      // 檢查中文字符
      const chineseChars = (data.content.match(/[\u4e00-\u9fff]/g) || []).length
      console.log('中文字符數量:', chineseChars)
      
      // 檢查亂碼字符
      const garbledChars = (data.content.match(/[^\x00-\x7F\u4e00-\u9fff\s]/g) || []).length
      console.log('可能的亂碼字符數量:', garbledChars)
    }
    
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
    console.log('準備顯示 Modal，showMarkdownModal.value:', showMarkdownModal.value)
    showMarkdownModal.value = true
    console.log('設定後 showMarkdownModal.value:', showMarkdownModal.value)
    
    // 強制觸發 Vue 的響應式更新
    setTimeout(() => {
      console.log('setTimeout 後 showMarkdownModal.value:', showMarkdownModal.value)
    }, 0)
    
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
- 文檔 ID: ${documentId || '無'}
- 檔案名稱: ${fileName || '無'}

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

// 從附件項目檢視 Markdown（優先使用 API 調用）
async function viewMarkdownFromAttachment(fileItem: UploadItem) {
  console.log('=== 檢視附件 Markdown ===')
  console.log('附件項目:', fileItem)
  console.log('convertedUrl:', fileItem.convertedUrl)
  console.log('========================')
  
  // 設定標題
  markdownModalTitle.value = fileItem.fileName
  
  // 優先使用 API 調用，而不是 convertedUrl
  const documentId = getCurrentDocumentId()
  console.log('使用 API 調用作為優先選擇，documentId:', documentId, 'fileName:', fileItem.fileName)
  await viewMarkdownByDocument(documentId || undefined, fileItem.fileName)
}


// Markdown 工具欄功能
function copyMarkdownContent() {
  navigator.clipboard.writeText(markdownContent.value).then(() => {
    console.log('Markdown 內容已複製到剪貼簿')
    // 可以在這裡添加成功提示
  }).catch((error) => {
    console.error('複製失敗:', error)
  })
}

function insertToEditor() {
  if (editorRef.value && markdownContent.value) {
    try {
      // 插入 Markdown 內容到編輯器
      editorRef.value.insertContent(markdownContent.value)
      showMarkdownModal.value = false
      console.log('Markdown 內容已插入到編輯器')
    } catch (error) {
      console.error('插入到編輯器失敗:', error)
    }
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

// 處理 conversionItems 的函式
function openConvertedFile(item: any) {
  if (item.convertedUrl) {
    // 將 URL 中的 9000 端口替換為 8000
    const correctedUrl = item.convertedUrl.replace(':9000', ':8000')
    console.log('原始 URL:', item.convertedUrl)
    console.log('修正後 URL:', correctedUrl)
    window.open(correctedUrl, '_blank')
  }
}

// 手動刷新附件列表
async function refreshAttachments() {
  const documentId = getCurrentDocumentId()
  if (documentId) {
    console.log('手動刷新附件列表:', documentId)
    try {
      await loadDocumentAttachments(documentId)
      console.log('附件列表刷新成功')
    } catch (error) {
      console.error('刷新附件列表失敗:', error)
    }
  } else {
    console.warn('沒有文檔 ID，無法刷新附件')
  }
}

// 讀取文檔已上傳的附件
async function loadDocumentAttachments(documentId: string) {
  try {
    console.log('=== 讀取文檔附件 ===')
    console.log('文檔 ID:', documentId)
    console.log('==================')
    
    const response = await fetch(`http://localhost:8000/documents/${documentId}/attachments`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      }
    })
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }
    
    const data = await response.json()
    console.log('附件 API 回傳資料:', data)
    
    // 清空現有的附件列表
    uploadItems.value = []
    
    // 處理回傳的附件資料
    if (data && Array.isArray(data)) {
      data.forEach((attachment: any) => {
        const uploadItem: UploadItem = {
          id: attachment.id || shortId(),
          fileName: attachment.fileName || attachment.filename || attachment.name,
          fileSize: attachment.fileSize || attachment.size || 0,
          uploadTime: new Date(attachment.uploadTime || attachment.createdAt || Date.now()),
          status: attachment.status || 'completed',
          convertedUrl: attachment.convertedUrl || attachment.url,
          errorMessage: attachment.errorMessage
        }
        
        // 修正 convertedUrl 的端口
        if (uploadItem.convertedUrl) {
          uploadItem.convertedUrl = uploadItem.convertedUrl.replace(':9000', ':8000')
        }
        
        uploadItems.value.push(uploadItem)
        console.log('添加附件:', uploadItem.fileName, '狀態:', uploadItem.status)
      })
      
      console.log(`成功載入 ${data.length} 個附件`)
    } else if (data && data.attachments && Array.isArray(data.attachments)) {
      // 如果資料包裝在 attachments 欄位中
      data.attachments.forEach((attachment: any) => {
        const uploadItem: UploadItem = {
          id: attachment.id || shortId(),
          fileName: attachment.fileName || attachment.filename || attachment.name,
          fileSize: attachment.fileSize || attachment.size || 0,
          uploadTime: new Date(attachment.uploadTime || attachment.createdAt || Date.now()),
          status: attachment.status || 'completed',
          convertedUrl: attachment.convertedUrl || attachment.url,
          errorMessage: attachment.errorMessage
        }
        
        // 修正 convertedUrl 的端口
        if (uploadItem.convertedUrl) {
          uploadItem.convertedUrl = uploadItem.convertedUrl.replace(':9000', ':8000')
        }
        
        uploadItems.value.push(uploadItem)
        console.log('添加附件:', uploadItem.fileName, '狀態:', uploadItem.status)
      })
      
      console.log(`成功載入 ${data.attachments.length} 個附件`)
    } else {
      console.log('沒有找到附件資料')
    }
    
  } catch (error) {
    console.error('讀取文檔附件失敗:', error)
    
    // 錯誤時不清空現有附件，只記錄錯誤
    console.log('保持現有附件列表不變')
  }
}

function retryConversion(item: any) {
  // 重新上傳檔案
  const file = new File([''], item.fileName, { type: 'application/pdf' })
  void uploadAttachment(file)
}

function removeConversionItem(item: any) {
  const index = conversionItems.value.findIndex((c: any) => c.id === item.id)
  if (index !== -1) {
    conversionItems.value.splice(index, 1)
  }
}

// 日期格式化
function formatDate(dateString: string): string {
  try {
    const date = new Date(dateString)
    const now = new Date()
    const diffTime = Math.abs(now.getTime() - date.getTime())
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    
    if (diffDays === 1) {
      return '今天'
    } else if (diffDays === 2) {
      return '昨天'
    } else if (diffDays <= 7) {
      return `${diffDays - 1} 天前`
    } else {
      return date.toLocaleDateString('zh-TW', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }
  } catch (error) {
    return '未知時間'
  }
}

// 從資料庫讀取文檔列表
async function loadDocumentList() {
  try {
    loadingDocuments.value = true
    console.log('=== 讀取文檔列表 ===')
    
    const response = await fetch('http://localhost:8000/documents', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const data = await response.json()
    console.log('文檔列表 API 回應:', data)
    
    // 假設後端回傳格式為 { documents: DocumentItem[] }
    documentList.value = data.documents || data || []
    
    console.log('載入的文檔數量:', documentList.value.length)
    console.log('==================')
    
  } catch (error) {
    console.error('讀取文檔列表失敗:', error)
    // 如果 API 不存在，使用模擬數據
    documentList.value = [
      {
        id: 'research_1760712373492_簡單排行台灣資工系相關排名',
        title: '台灣資工系排名研究報告',
        createdAt: '2024-01-15T10:30:00Z',
        updatedAt: '2024-01-15T14:20:00Z',
        attachmentCount: 3
      },
      {
        id: 'doc_002', 
        title: '半導體產業分析報告',
        createdAt: '2024-01-14T09:15:00Z',
        updatedAt: '2024-01-14T16:45:00Z',
        attachmentCount: 2
      },
      {
        id: 'doc_003',
        title: 'AI 技術發展趨勢',
        createdAt: '2024-01-13T14:20:00Z', 
        updatedAt: '2024-01-13T18:30:00Z',
        attachmentCount: 1
      }
    ]
    console.log('使用模擬數據，文檔數量:', documentList.value.length)
  } finally {
    loadingDocuments.value = false
  }
}

// 切換到指定文檔
async function switchToDocument(document: DocumentItem) {
  try {
    console.log('=== 切換到文檔 ===')
    console.log('文檔 ID:', document.id)
    console.log('文檔標題:', document.title)
    console.log('================')
    
    // 更新當前文檔資訊
    currentDocumentId.value = document.id
    currentReportTitle.value = document.title
    localStorage.setItem('currentDocumentId', document.id)
    localStorage.setItem('currentReportTitle', document.title)
    
    // 使用 initDocument 載入文檔內容
    const documentData = await initDocument(document.id)
    console.log('載入的文檔資料:', documentData)
    
    // 初始化編輯器選項
    options.value = {
      toolbar: {
        importWord: {
          enabled: true,
          async onCustomImportMethod() {
            return await Promise.resolve({
              value: '<p>测试导入word</p>',
            })
          },
        },
      },
      document: {
        title: documentData.title,
        content: documentData.content,
        characterLimit: documentData.characterLimit,
      },
      onSave: async (content: string, page: number, document: { content: string }) => {
        try {
          // 取得當前文檔 ID 和報告標題
          const documentId = getCurrentDocumentId()
          const reportTitle = getCurrentReportTitle()
          
          // 準備要傳送的資料
          const saveData = {
            documentId,
            reportTitle,
            content,
            page,
            document,
          }
          
          console.log('=== 儲存文檔資訊 ===')
          console.log('文檔 ID:', documentId)
          console.log('報告標題:', reportTitle)
          console.log('頁面:', page)
          console.log('==================')
          
          const response = await fetch('http://localhost:8000/save-document', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(saveData),
          })
          
          if (!response.ok) {
            throw new Error('儲存失敗')
          }
          
          console.log('文檔儲存成功')
          return true
        } catch (error) {
          console.error('儲存文檔失敗:', error)
          return false
        }
      },
    }
    
    // 切換到編輯器模式
    stage.value = 'editor'
    
    // 關閉文件清單
    showListModal.value = false
    
    console.log('編輯器選項已初始化:', options.value)
    
    // 等待編輯器初始化完成後更新內容
    await nextTick()
    
    // 使用輪詢方式等待編輯器準備好並更新內容
    let retryCount = 0
    const maxRetries = 50 // 最多重試 50 次 (5 秒)
    
    const updateEditorContent = () => {
      retryCount++
      console.log(`檢查編輯器狀態 (第 ${retryCount} 次):`)
      console.log('- editorRef.value:', editorRef.value)
      console.log('- editorRef.value?.setContent:', editorRef.value?.setContent)
      
      if (editorRef.value && editorRef.value.setContent) {
        console.log('正在更新編輯器內容...')
        editorRef.value.setContent(documentData.content)
        console.log('編輯器內容已更新')
      } else if (retryCount < maxRetries) {
        console.log(`編輯器尚未準備好，100ms 後重試... (${retryCount}/${maxRetries})`)
        setTimeout(updateEditorContent, 100)
      } else {
        console.error('編輯器初始化超時，無法更新內容')
      }
    }
    
    // 開始更新內容
    setTimeout(updateEditorContent, 100)
    
  } catch (error) {
    console.error('切換文檔失敗:', error)
    // 即使 API 失敗，也切換到編輯器模式
    currentDocumentId.value = document.id
    currentReportTitle.value = document.title
    localStorage.setItem('currentDocumentId', document.id)
    localStorage.setItem('currentReportTitle', document.title)
    stage.value = 'editor'
    showListModal.value = false
  }
}

// 新建文檔功能
function createNewDocument() {
  console.log('=== 新建文檔 ===')
  console.log('回到 new-document.vue 頁面')
  console.log('================')
  
  // 關閉清單彈出視窗
  showListModal.value = false
  
  // 切換到新建文檔頁面
  stage.value = 'new'
  
  // 清除當前文檔狀態
  currentDocumentId.value = null
  currentReportTitle.value = null
  localStorage.removeItem('currentDocumentId')
  localStorage.removeItem('currentReportTitle')
  
  // 清除附件上傳項目
  uploadItems.value = []
}

// 格式化檔案大小
function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

// 移除上傳項目
function removeUploadItem(item: UploadItem) {
  const index = uploadItems.value.findIndex((u: UploadItem) => u.id === item.id)
  if (index > -1) {
    uploadItems.value.splice(index, 1)
    console.log('移除上傳項目:', item.fileName)
  }
}

// 附件上傳功能（與 new-document.vue 一致）
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

// 呼叫後端立即上傳並暫存結果（與 new-document.vue 一致）
async function uploadAttachment(file: File) {
  try {
    console.log('=== App.vue 附件上傳 ===')
    console.log('檔案名稱:', file.name)
    console.log('檔案大小:', file.size)
    console.log('檔案類型:', file.type)
    console.log('文檔 ID:', getCurrentDocumentId())
    console.log('====================')
    
    // 建立上傳項目
    const uploadItem: UploadItem = {
      id: `upload-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      fileName: file.name,
      fileSize: file.size,
      uploadTime: new Date(),
      status: 'uploading'
    }
    uploadItems.value.push(uploadItem)
    
    // 取得當前文檔 ID
    const documentId = getCurrentDocumentId()
    
    // 建立 FormData
    const form = new FormData()
    form.append('file', file)
    
    // 建立 URL 查詢參數
    const url = new URL('http://localhost:8000/upload')
    if (documentId) {
      url.searchParams.append('document_id', documentId)
    }
    
    // 上傳到後端
    const res = await fetch(url.toString(), {
      method: 'POST',
      body: form,
    })
    
    if (!res.ok) {
      throw new Error('上傳失敗')
    }
    
    const data = await res.json() as { 
      id: string; 
      url: string; 
      name?: string; 
      processed?: boolean; 
      status?: string; 
      error?: string 
    }
    
    console.log('上傳成功:', data)
    
    // 根據後端回應更新狀態（與 new-document.vue 一致）
    const itemIndex = uploadItems.value.findIndex((u: UploadItem) => u.id === uploadItem.id)
    if (itemIndex !== -1) {
      if (data.processed && data.status === 'completed') {
        uploadItems.value[itemIndex].status = 'completed'
        uploadItems.value[itemIndex].convertedUrl = data.url
        console.log(`PDF 轉換完成：${file.name}`)
      } else if (data.status === 'failed') {
        uploadItems.value[itemIndex].status = 'failed'
        uploadItems.value[itemIndex].errorMessage = data.error || '轉換失敗'
        console.error(`PDF 轉換失敗：${file.name} - ${uploadItems.value[itemIndex].errorMessage}`)
      } else {
        // 其他情況都設為完成（非 PDF 或處理成功）
        uploadItems.value[itemIndex].status = 'completed'
        console.log(`附件已上傳：${file.name}`)
      }
    }
    
  } catch (err: any) {
    console.error('附件上傳失敗:', err)
    
    // 更新上傳狀態為失敗
    const itemIndex = uploadItems.value.findIndex((u: UploadItem) => u.fileName === file.name)
    if (itemIndex !== -1) {
      uploadItems.value[itemIndex].status = 'failed'
      uploadItems.value[itemIndex].errorMessage = err?.message ?? '上傳失敗'
    }
  }
}
// ref 變數宣告
const editorRef = ref(null)
const options = ref(null)
const stage = ref<'new' | 'editor'>('new')
const showAIDrawer = ref(false)
const showListModal = ref(false)
const currentDocumentId = ref<string | null>(null)
const currentReportTitle = ref<string | null>(null)

// Markdown 檢視相關變數
const showMarkdownModal = ref(false)
const markdownModalTitle = ref('')
const markdownContent = ref('')
const markdownViewMode = ref<'raw' | 'preview' | 'split'>('preview')

// 注入 new-document.vue 的附件數據
const conversionItems = inject<Ref<Array<{
  id: string
  fileName: string
  fileSize: number
  uploadTime: Date
  status: 'uploading' | 'converting' | 'completed' | 'failed'
  progress?: number
  errorMessage?: string
  convertedUrl?: string
}>>>('conversionItems', ref([]))

// 文檔列表管理
interface DocumentItem {
  id: string
  title: string
  createdAt: string
  updatedAt: string
  content?: string
  attachmentCount?: number
}

const documentList = ref<DocumentItem[]>([])
const loadingDocuments = ref(false)

// Markdown 渲染計算屬性
const renderedMarkdown = computed(() => {
  try {
    return marked(markdownContent.value)
  } catch (error) {
    console.error('Markdown 渲染錯誤:', error)
    return '<p>Markdown 渲染失敗</p>'
  }
})

// 附件上傳狀態管理
interface UploadItem {
  id: string
  fileName: string
  fileSize: number
  uploadTime: Date
  status: 'uploading' | 'completed' | 'failed'
  errorMessage?: string
  convertedUrl?: string
}
const uploadItems = ref<UploadItem[]>([])
const filePickerRef = ref<HTMLInputElement | null>(null)
provide('showAIDrawer', showAIDrawer)
const templates = [
  {
    title: '工作任务',
    description: '工作任务模板',
    content:
      '<h1>工作任务</h1><h3>任务名称：</h3><p>[任务的简短描述]</p><h3>负责人：</h3><p>[执行任务的个人姓名]</p><h3>截止日期：</h3><p>[任务需要完成的日期]</p><h3>任务详情：</h3><ol><li>[任务步骤1]</li><li>[任务步骤2]</li><li>[任务步骤3]...</li></ol><h3>目标：</h3><p>[任务需要达成的具体目标或结果]</p><h3>备注：</h3><p>[任何额外信息或注意事项]</p>',
  },
  {
    title: '工作周報',
    description: '工作周報模板',
    content:
      '<h1>工作周報</h1><h2>本周工作總結</h2><hr /><h3>已完成工作：</h3><ul><li>[任務1]：完成情況</li><li>[任務2]：完成情況</li></ul><h3>進行中工作：</h3><ul><li>[任務1]：進度說明</li><li>[任務2]：進度說明</li></ul><h3>問題與挑戰：</h3><ul><li>[問題1]：說明與需求</li><li>[問題2]：說明與需求</li></ul><hr /><h2>下週工作計劃</h2><ul><li>[任務1]：計劃內容</li><li>[任務2]：計劃內容</li></ul>',
  },
]

type PendingAttachment = { id: string; url: string; name: string; type: string; size: number }
async function startEditor(titleFromUser: string, attachments?: PendingAttachment[], documentId?: string) {
  const doc = await initDocument()
  const title = titleFromUser?.trim() || doc.title || '新文檔'
  const content = doc.content?.trim() ? doc.content : `<h1>${title}</h1><p></p>`
  
  // 處理 documentId
  if (documentId) {
    console.log('收到文檔 ID:', documentId)
    currentDocumentId.value = documentId
    localStorage.setItem('currentDocumentId', documentId)
  }
  
  // 處理報告書題目
  if (titleFromUser?.trim()) {
    console.log('收到報告書題目:', titleFromUser.trim())
    currentReportTitle.value = titleFromUser.trim()
    localStorage.setItem('currentReportTitle', titleFromUser.trim())
  }
  
  // 在 console 顯示完整資訊
  console.log('=== App.vue 接收資訊 ===')
  console.log('報告標題:', titleFromUser?.trim())
  console.log('文檔 ID:', documentId)
  console.log('附件數量:', attachments?.length || 0)
  console.log('======================')

  options.value = {
    toolbar: {
      importWord: {
        enabled: true,
        async onCustomImportMethod() {
          return await Promise.resolve({
            value: '<p>测试导入word</p>',
          })
        },
      },
    },
    document: {
      title,
      content,
      characterLimit: doc.characterLimit,
    },
    page: {
      showBookmark: true,
    },
    templates,
    cdnUrl: 'https://cdn.umodoc.com',
    shareUrl: 'https://umodoc.com',
    file: {},
    ai: {
      assistant: {
        enabled: true,
        async onMessage(payload: any, content: any) {
          // 印出收到的內容
          console.log('=== AI Assistant onMessage 收到的內容 ===')
          console.log('Payload (用戶輸入和選中文字):', payload)
          console.log('Content (整個文件內容):', content)
          console.log('用戶輸入的指令:', payload.command)
          console.log('選中的文字:', payload.input)
          console.log('語言設定:', payload.lang)
          console.log('文件HTML內容:', content.html)
          console.log('文件純文字內容:', content.text)
          console.log('========================================')
          try {
            // 發送到後端 AI 助手 API
            const response = await fetch('http://localhost:8000/ai-assistant', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                payload,
                content,
              }),
            })

            if (!response.ok) {
              throw new Error('後端回應失敗')
            }

            const result = await response.json()
            console.log('AI助手後端回應:', result)

            if (result.success) {
              return result.content
            } else {
              throw new Error(result.error ?? 'AI助手處理失敗')
            }
          } catch (error: any) {
            console.error('AI助手請求失敗:', error)
            return `<p>AI助手處理失敗: ${error?.message ?? '未知錯誤'}</p>`
          }
        },
      },
    },
    user: {
      id: 'umoeditor',
      label: 'Umo Editor',
      avatar: 'https://tdesign.gtimg.com/site/avatar.jpg',
    },
    users: [
      { id: 'umodoc', label: 'Umo Team' },
      { id: 'Cassielxd', label: 'Cassielxd' },
      { id: 'Goldziher', label: "Na'aman Hirschfeld" },
      { id: 'SerRashin', label: 'SerRashin' },
      { id: 'ChenErik', label: 'ChenErik' },
      { id: 'china-wangxu', label: 'china-wangxu' },
      { id: 'Sherman Xu', label: 'xuzhenjun130' },
      { id: 'testuser', label: '测试用户' },
    ],
    async onSave(content: string, page: number, document: { content: string }) {
      try {
        // 取得當前文檔 ID 和報告標題
        const documentId = getCurrentDocumentId()
        const reportTitle = getCurrentReportTitle()
        
        // 準備要傳送的資料
        const saveData = {
          documentId,
          reportTitle,
          content,
          page,
          document,
        }
        
        console.log('=== 儲存文檔資訊 ===')
        console.log('文檔 ID:', documentId)
        console.log('報告標題:', reportTitle)
        console.log('頁面:', page)
        console.log('==================')
        
        console.log('=== saveDocument 完整資料格式 ===')
        console.log('JSON 字串:', JSON.stringify(saveData, null, 2))
        console.log('物件內容:', saveData)
        console.log('content 長度:', content.length)
        console.log('document 內容長度:', document.content.length)
        console.log('================================')
        
        // 發送到 FastAPI 後端
        const response = await fetch('http://localhost:8000/save-document', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(saveData),
        })

        if (!response.ok) {
          throw new Error('伺服器回應失敗')
        }

        const result = await response.json()
        console.log('伺服器回應儲存至資料庫:', result)

        // 文檔保存成功後，重新載入附件列表
        if (result.success && documentId) {
          console.log('文檔保存成功，重新載入附件列表...')
          try {
            await loadDocumentAttachments(documentId)
            console.log('附件列表已更新')
          } catch (attachmentError) {
            console.error('重新載入附件失敗:', attachmentError)
            // 不影響文檔保存的成功狀態
          }
        }

        return '操作成功'
      } catch (error) {
        console.error('儲存失敗:', error)
        throw new Error('操作失败')
      }
    },
    async onFileUpload(file: File & { url?: string }) {
      try {
        console.log('=== App.vue 附件上傳 ===')
        console.log('檔案名稱:', file.name)
        console.log('檔案大小:', file.size)
        console.log('檔案類型:', file.type)
        console.log('文檔 ID:', getCurrentDocumentId())
        console.log('====================')
        
        // 建立上傳項目
        const uploadItem: UploadItem = {
          id: `upload-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          fileName: file.name,
          fileSize: file.size,
          uploadTime: new Date(),
          status: 'uploading'
        }
        uploadItems.value.push(uploadItem)
        
        // 取得當前文檔 ID
        const documentId = getCurrentDocumentId()
        
        // 建立 FormData
        const form = new FormData()
        form.append('file', file)
        
        // 建立 URL 查詢參數
        const url = new URL('http://localhost:8000/upload')
        if (documentId) {
          url.searchParams.append('document_id', documentId)
        }
        
        // 上傳到後端
        const res = await fetch(url.toString(), {
          method: 'POST',
          body: form,
        })
        
        if (!res.ok) {
          throw new Error('上傳失敗')
        }
        
        const data = await res.json() as { 
          id: string; 
          url: string; 
          name?: string; 
          processed?: boolean; 
          status?: string; 
          error?: string 
        }
        
        console.log('上傳成功:', data)
        
        // 更新上傳狀態
        const itemIndex = uploadItems.value.findIndex((u: UploadItem) => u.id === uploadItem.id)
        if (itemIndex !== -1) {
          if (file.type === 'application/pdf') {
            if (data.processed && data.status === 'completed') {
              uploadItems.value[itemIndex].status = 'completed'
              console.log(`PDF 轉換完成：${file.name}`)
            } else if (data.status === 'failed') {
              uploadItems.value[itemIndex].status = 'failed'
              uploadItems.value[itemIndex].errorMessage = data.error || '轉換失敗'
              console.error(`PDF 轉換失敗：${file.name} - ${uploadItems.value[itemIndex].errorMessage}`)
            } else {
              uploadItems.value[itemIndex].status = 'uploading' // 保持上傳中狀態
              console.log(`正在轉換 PDF：${file.name}`)
            }
          } else {
            uploadItems.value[itemIndex].status = 'completed'
            console.log(`附件已上傳：${file.name}`)
          }
        }
        
        return {
          id: data.id || shortId(),
          url: data.url || URL.createObjectURL(file),
          name: data.name || file.name,
          type: file.type,
          size: file.size,
        }
      } catch (error: any) {
        console.error('附件上傳失敗:', error)
        
        // 更新上傳狀態為失敗
        const itemIndex = uploadItems.value.findIndex((u: UploadItem) => u.fileName === file.name)
        if (itemIndex !== -1) {
          uploadItems.value[itemIndex].status = 'failed'
          uploadItems.value[itemIndex].errorMessage = error?.message || '上傳失敗'
        }
        
        // 如果上傳失敗，回傳基本資訊
        return {
          id: shortId(),
          url: file.url ?? URL.createObjectURL(file),
          name: file.name,
          type: file.type,
          size: file.size,
        }
      }
    },
    onFileDelete(id: string, url: string) {
      console.log('File deleted:', id, url)
    },
  }

  stage.value = 'editor'

  // 如果有從新建頁面帶入的附件，這裡可選擇插入提示或記錄
  if (attachments && attachments.length > 0) {
    console.log('帶入的附件:', attachments)
    // 如需立即插入到文件，可在此調用 editor API 或透過 onFileUpload 整合
  }
}

function onCancelNew() {
  // 快速模式：模擬傳入文檔 ID
  const mockDocumentId = 'research_1760712373492_簡單排行台灣資工系相關排名'
  const mockTitle = '簡單排行台灣資工系相關排名'
  
  console.log('=== 快速模式進入編輯器 ===')
  console.log('模擬文檔 ID:', mockDocumentId)
  console.log('模擬標題:', mockTitle)
  console.log('========================')
  
  // 直接進入編輯器，使用模擬的文檔 ID 和標題
  void startEditor(mockTitle, [], mockDocumentId)
}

// 取得當前文檔 ID
function getCurrentDocumentId(): string | null {
  return currentDocumentId.value || localStorage.getItem('currentDocumentId')
}

// 取得當前報告書題目
function getCurrentReportTitle(): string | null {
  return currentReportTitle.value || localStorage.getItem('currentReportTitle')
}

// 提供給子元件使用
provide('getCurrentDocumentId', getCurrentDocumentId)
provide('getCurrentReportTitle', getCurrentReportTitle)

// 將函式暴露到全域，方便在 console 中調用
if (typeof window !== 'undefined') {
  (window as any).getCurrentDocumentId = getCurrentDocumentId
  ;(window as any).getCurrentReportTitle = getCurrentReportTitle
  ;(window as any).getCurrentDocumentInfo = () => {
    console.log('=== 當前文檔資訊 ===')
    console.log('文檔 ID:', getCurrentDocumentId())
    console.log('報告標題:', getCurrentReportTitle())
    console.log('==================')
    return {
      documentId: getCurrentDocumentId(),
      reportTitle: getCurrentReportTitle()
    }
  }
}
</script>

<style>
html,
body {
  padding: 0;
  margin: 0;
  height: 100vh;
  overflow: hidden;
}
.examples {
  margin: 20px;
  display: flex;
  height: calc(100vh - 40px);
}
.box {
  border: solid 1px #ddd;
  box-sizing: border-box;
  position: relative;
  width: 100%;
  height: 100%;
}
.ai-fab {
  position: fixed;
  right: 40px;
  bottom: 60px;
  width: 64px;
  height: 64px;
  border-radius: 50%;
  font-size: 2rem;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  transition: background 0.2s;
}
.ai-fab--hidden {
  display: none !important;
}
.ai-fab:hover {
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25); /* hover 陰影加強 */
}
.ai-tooltip {
  visibility: hidden;
  opacity: 0;
  position: absolute;
  bottom: 80px; /* 按鈕上方 */
  left: 50%;
  transform: translateX(-50%);
  background: #fff;
  color: #333;
  padding: 6px 12px;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
  font-size: 0.8rem;
  white-space: nowrap;
  pointer-events: none;
  transition:
    opacity 0.2s,
    visibility 0.2s;
  font-family: var(--umo-font-family);
}
/* 顯示 tooltip */
.ai-fab:hover .ai-tooltip {
  visibility: visible;
  opacity: 1;
}

/* 清單按鈕樣式 */
.list-fab {
  position: fixed;
  right: 40px;
  bottom: 140px; /* 在 AI 按鈕上方 */
  width: 64px;
  height: 64px;
  border-radius: 50%;
  font-size: 2rem;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 5; /* 降低 z-index，確保在 AI 視窗下面 */
  transition: background 0.2s;
}

.list-fab--hidden {
  display: none !important;
}

.list-fab:hover {
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25);
}

.list-tooltip {
  visibility: hidden;
  opacity: 0;
  position: absolute;
  bottom: 80px;
  left: 50%;
  transform: translateX(-50%);
  background: #fff;
  color: #333;
  padding: 8px 12px;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
  font-size: 0.8rem;
  white-space: nowrap;
  pointer-events: none;
  transition: opacity 0.2s, visibility 0.2s;
  font-family: var(--umo-font-family);
}

.list-fab:hover .list-tooltip {
  visibility: visible;
  opacity: 1;
}

/* 清單彈出視窗樣式 */
.list-modal-content {
  padding: 0;
}

.list-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e5e7eb;
}

.list-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.list-header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.list-body {
  max-height: 400px;
  overflow-y: auto;
}

.list-item {
  display: flex;
  align-items: center;
  padding: 12px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  margin-bottom: 8px;
  background: #fff;
  transition: all 0.2s ease;
}

.list-item:hover {
  border-color: #d1d5db;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.current-document {
  border-color: #22c55e;
  background: #f0fdf4;
}

.new-document-hint {
  border-color: #2563eb;
  background: #eff6ff;
}

.list-item-icon {
  margin-right: 12px;
  color: #6b7280;
  flex-shrink: 0;
}

.list-item-content {
  flex: 1;
  min-width: 0;
}

.list-item-title {
  font-weight: 500;
  color: #1f2937;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.list-item-meta {
  font-size: 12px;
  color: #6b7280;
}

.list-item-actions {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
}

.list-empty {
  text-align: center;
  padding: 40px 20px;
  color: #6b7280;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.empty-text {
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 4px;
  color: #374151;
}

.empty-desc {
  font-size: 14px;
  color: #6b7280;
}

.file-size {
  color: #9ca3af;
  margin-left: 8px;
}

/* 附件標題樣式 */
.list-section-title {
  margin: 16px 0 8px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid #e5e7eb;
}

.list-section-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.list-section-title h4 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.upload-button {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  background: #f3f4f6;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 12px;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s ease;
}

.upload-button:hover {
  background: #e5e7eb;
  border-color: #9ca3af;
}

/* 附件操作區域 */
.attachment-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

/* 刷新按鈕 */
.refresh-button {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  background: #f0f9ff;
  border: 1px solid #0ea5e9;
  border-radius: 4px;
  font-size: 12px;
  color: #0ea5e9;
  cursor: pointer;
  transition: all 0.2s ease;
}

.refresh-button:hover {
  background: #e0f2fe;
  border-color: #0284c7;
  color: #0284c7;
}

/* 上傳項目樣式 */
.upload-item {
  position: relative;
}

.upload-item.status-uploading .list-item-icon {
  color: #2563eb;
}

.upload-item.status-completed .list-item-icon {
  color: #22c55e;
}

.upload-item.status-failed .list-item-icon {
  color: #ef4444;
}

.rotating {
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.status-completed {
  color: #22c55e !important;
}

.status-failed {
  color: #ef4444 !important;
}

.error-text {
  color: #ef4444;
  font-weight: 500;
}

.progress-bar {
  width: 100%;
  height: 4px;
  background: #e5e7eb;
  border-radius: 2px;
  margin-top: 8px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #2563eb, #3b82f6);
  border-radius: 2px;
  animation: progress 2s ease-in-out infinite;
}

@keyframes progress {
  0% { transform: translateX(-100%); }
  50% { transform: translateX(0%); }
  100% { transform: translateX(100%); }
}

/* 載入中狀態樣式 */
.list-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: #6b7280;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #e5e7eb;
  border-top: 3px solid #2563eb;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 12px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  font-size: 14px;
  color: #6b7280;
}

/* 文檔列表樣式 */
.document-list-section {
  margin-bottom: 16px;
}

.document-item {
  cursor: pointer;
  transition: all 0.2s ease;
}

.document-item:hover {
  border-color: #d1d5db;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  transform: translateY(-1px);
}

.document-item.current-document {
  border-color: #22c55e;
  background: #f0fdf4;
}

.document-item.current-document .list-item-icon {
  color: #22c55e;
}

.text-green-500 {
  color: #22c55e !important;
}

.text-gray-500 {
  color: #6b7280 !important;
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
