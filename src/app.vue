<template>
  <div class="examples">
    <div class="box">
      <umo-editor v-if="options" ref="editorRef" v-bind="options" />
    </div>
    <button
      :class="['ai-fab', { 'ai-fab--hidden': showAIDrawer }]"
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
  </div>
</template>

<script setup lang="ts">
import { shortId } from '@/utils/short-id'

// API 初始化函式
async function initDocument() {
  try {
    const res = await fetch('http://localhost:8000/load-document')
    if (!res.ok) throw new Error('讀取失敗')
    const data = await res.json()
    console.log('API 回傳資料:', data)

    return {
      title: data.title ?? '测试文档',
      content: data.content ?? '<p>測試內容</p>',
      characterLimit: data.characterLimit ?? 10000,
    }
  } catch (e) {
    console.error('讀取出錯:', e)
    return {
      title: '测试文档',
      content: '<p>預設內容\n測試內容</p>',
      characterLimit: 10000,
    }
  }
}
function onAIClick() {
  showAIDrawer.value = true
}
// ref 變數宣告
const editorRef = ref(null)
const options = ref(null)
const showAIDrawer = ref(false)
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

// 組件掛載後載入資料與建立 options
onMounted(async () => {
  const doc = await initDocument()

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
    //   document: {
    //   title: '测试文档',
    //   content: localStorage.getItem('document.content1') ?? '<p>测试文档測試</p>',
    //   characterLimit: 10000,
    // },
    document: {
      title: doc.title,
      content: doc.content,
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
      // localStorage.setItem('document.content1', document.content)
      // return new Promise((resolve, reject) => {
      //   setTimeout(() => {
      //     const success = true
      //     if (success) {
      //       console.log('onSave', { content, page, document })
      //       resolve('操作成功')
      //     } else {
      //       reject(new Error('操作失败'))
      //     }
      //   }, 2000)
      // })
      try {
        // 發送到 FastAPI 後端
        const response = await fetch('http://localhost:8000/save-document', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            content,
            page,
            document,
          }),
        })

        if (!response.ok) {
          throw new Error('伺服器回應失敗')
        }

        const result = await response.json()
        console.log('伺服器回應儲存至資料庫:', result)

        return '操作成功'
      } catch (error) {
        console.error('儲存失敗:', error)
        throw new Error('操作失败')
      }
    },
    async onFileUpload(file: File & { url?: string }) {
      console.log('onUpload', file)
      await new Promise((resolve) => setTimeout(resolve, 1000))
      return {
        id: shortId(),
        url: file.url ?? URL.createObjectURL(file),
        name: file.name,
        type: file.type,
        size: file.size,
      }
    },
    onFileDelete(id: string, url: string) {
      console.log('File deleted:', id, url)
    },
  }
})
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
</style>
