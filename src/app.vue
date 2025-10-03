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
      // content: '<p>預設內容\n測試內容</p>',
      content: `<h3 id="_1"><strong>第一部分：正面影響——台灣經濟的成長引 擎與「護國神山」</strong><a class="headerlink" href="#_1" title="永久連結到此標題">&para;</a></h3>
<ol>
<li>
<p><strong>經濟成長的核心驅動力</strong>：</p>
<ul>
<li><strong>對GDP的巨大貢axian</strong>：半導體產業產值約佔台灣GDP的18-20%，是支撐台灣經濟成長的最重要支柱。以台積電為首的企業，其資本支出和市值對經濟有著舉足輕重的影響。</li>
<li><strong>出口創匯的絕對主力</strong>：電子零組件（以半導體為主）佔台灣總出口額超過四成，為台灣賺取大量外匯，穩 定金融市場，並增強了抵禦全球經濟風險的能力。</li>        
</ul>
</li>
<li>
<p><strong>建立完整的產業生態系</strong>：</p>
<ul>
<li>台灣已形成從上游（IC設計，如聯發科）、中游（晶圓代工 ，如台積電），到下游（封裝測試，如日月光）的完整且高效的 垂直分工產業鏈。</li>
<li>這種高度群聚的效應（主要集中在新竹、台中、台南科學園 區）大幅提升了生產效率、促進了技術交流，鞏固了台灣在全球 的領導地位。</li>
</ul>
</li>
<li>
<p><strong>創造高薪就業與培養人才</strong>：</p>
<ul>
<li>該產業創造了數十萬個高薪的就業機會，顯著高於國內平均 薪資水平，有效提升了國民所得，並帶動了周邊服務業的發展。</li>
<li>頂尖的產業環境吸引了全球人才，並成為台灣理工科系學生 的職涯首選，形成了穩固的人才正向循環。</li>
</ul>
</li>
<li>
<p><strong>提升全球戰略地位（「矽盾」）</strong>：</p>   
<ul>
<li>台灣在全球半導體供應鏈中的關鍵地位，使其成為全球經濟 不可或缺的一環。任何對台灣的威脅都可能導致全球電子產業斷 鏈，從而引發經濟危機。</li>
<li>「矽盾」（Silicon Shield）的角色讓美國、日本、歐洲等 主要經濟體有強烈動機維護台海穩定，也成為台灣在美中科技角 力下的重要地緣政治籌碼。</li>
</ul>
</li>
</ol>
<h3 id="_2"><strong>第二部分：潛在風險與挑戰——榮景背後的 隱憂</strong><a class="headerlink" href="#_2" title="永久連結到此標題">&para;</a></h3>
<ol>
<li>
<p><strong>產業過度集中的風險</strong>：</p>
<ul>
<li><strong>經濟失衡</strong>：過多資源（人才、資金、水電）集中於半導體，可能排擠其他傳統產業與服務業的發展，導致 產業結構失衡與貧富差距擴大。</li>
<li><strong>景氣循環衝擊</strong>：半導體產業具有高度的景氣循環性。一旦全球市場需求放緩，將直接且劇烈地衝擊台灣的 整體經濟。</li>
</ul>
</li>
<li>
<p><strong>地緣政治的雙面刃</strong>：</p>
<ul>
<li><strong>戰略目標風險</strong>：「矽盾」雖是保護，但也使台灣成為地緣政治衝突的焦點，面臨來自中國的威脅以及美國 供應鏈「去台化」的壓力。</li>
<li><strong>自主性受限</strong>：在全球科技戰的背景下，台灣的產業政策與發展不得不過度參考美國的臉色，自主性受到挑 戰。</li>
</ul>
</li>
<li>
<p><strong>國內資源的排擠與環境壓力</strong>：</p>       
<ul>
<li><strong>資源消耗巨大</strong>：先進製程是典型的高耗能、高耗水產業，在台灣水電資源本已緊張的情況下，加劇了與民 生及其他產業的資源競爭。</li>
<li><strong>環境負擔</strong>：製程中使用的化學品及產生的廢棄物，對環境的長期影響是社會必須正視的課題。</li>      
</ul>
</li>
<li>
<p><strong>人才斷層與外流</strong>：</p>
<ul>
<li>隨著各國大力發展本土半導體產業，對台灣人才的挖角日益 激烈，造成人才缺口。</li>
<li>台灣的少子化問題，將在未來嚴重影響理工人才的供給，對 產業的長期發展構成根本性威脅。</li>
</ul>
</li>
</ol>
<h3 id="_3"><strong>結論與未來展望</strong><a class="headerlink" href="#_3" title="永久連結到此標題">&para;</a></h3>
<p>總體而言，半導體產業是驅動台灣經濟成長、鞏固國際地位的「渦輪引擎」。然而，這個引擎也消耗了大量資源，並使經濟結 構過度集中，帶來潛在風險。</p>
<p>為了實現永續發展，台灣未來必須：<br />
1.  <strong>維持技術領先</strong>：持續投入研發，確保在先進製程領域的領導地位。<br />
2.  <strong>推動產業多元化</strong>：利用半導體優勢，帶動AI、智慧醫療、綠能等新興產業發展，打造「第二座護國神山」 。<br />
3.  <strong>解決資源與人才問題</strong>：制定長期的能源與人才政策，應對內部挑戰。<br />
4.  <strong>靈活應對地緣政治</strong>：在全球供應鏈重組中，採取靈活的國際佈局，同時將核心技術根留台灣。</p>       
<p>駕馭好這座「護國神山」，使其在保護台灣的同時，不對社會與環境造成過度負擔，將是台灣未來最重要的課題。</p>     `,
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
