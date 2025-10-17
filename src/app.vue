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
  </div>
</template>

<script setup lang="ts">
import { shortId } from '@/utils/short-id'
import NewDocument from '@/pages/new-document.vue'

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
// ref 變數宣告
const editorRef = ref(null)
const options = ref(null)
const stage = ref<'new' | 'editor'>('new')
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

type PendingAttachment = { id: string; url: string; name: string; type: string; size: number }
async function startEditor(titleFromUser: string, attachments?: PendingAttachment[]) {
  const doc = await initDocument()
  const title = titleFromUser?.trim() || doc.title || '新文檔'
  const content = doc.content?.trim() ? doc.content : `<h1>${title}</h1><p></p>`

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

  stage.value = 'editor'

  // 如果有從新建頁面帶入的附件，這裡可選擇插入提示或記錄
  if (attachments && attachments.length > 0) {
    console.log('帶入的附件:', attachments)
    // 如需立即插入到文件，可在此調用 editor API 或透過 onFileUpload 整合
  }
}

function onCancelNew() {
  // 取消時直接進入編輯器，使用預設內容
  void startEditor('')
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
</style>
