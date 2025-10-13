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
      content: `# 人工智慧在醫療診斷領域的最新應用：2023-2025 年現狀、挑戰與未來展望

## 概覽

自 2023 年以來，人工智慧 (AI) 持續在醫療診斷領域掀起變革，尤其是在放射學與病理學等高度依賴影像分析的專科中。以深度學習 (DL) 為核心的技術，透過自動化特徵提取與模式識別，在提高診斷準確性、速度及效率方面展現了巨大潛力。從偵測微小骨折到辨識癌細胞，AI 正從輔助工具逐步發展為臨床工作流程中不可或缺的一部分。然而，這項技術的廣泛應用仍面臨著數據隱私、法規遵循、工作流程整合以及倫理等多重挑戰。本報告旨在綜合 2023 年至 2025 年的最新研究，全面概述 AI 在醫療診斷領域的現狀、具體應用、挑戰及未來方向。

## 放射學：AI 賦能影像診斷的新紀元

放射學是 AI 應用最成熟的領域之一。從 2023 年到 2025 年，由卷積神經網路 (CNN) 驅動的 AI 工具，在分析 X 光、CT 掃描和 MRI 等醫學影像方面取得了顯著進展，特別是在神經影像和胸腔影像等臨床需求高的領域 [1, 2]。

### AI 技術與具體應用案例

*   **技術類型**：深度學習模型是此領域的核心，例如用於分類的 **ResNet** 和用於影像分割的 **U-Net**。此外，大型語言模型 (LLM) 也開始被用於自動生成放射學報告，以減輕放射科醫生的工作負擔 [1]。

*   **乳癌診斷**：深度學習在分析乳房組織病理學影像方面顯示出卓越的診斷潛力。
    *   **效能比較**：一項 2024 年的研究指出，基於 YOLO 的系統在偵測腫塊位置的準確率高達 99.7%；在區分良惡性病灶方面，準確率為 97% [3]。在淋巴結轉移診斷中，DL 演算法的表現甚至優於病理學家，其曲線下面積 (AUC) 達到 0.99，而病理學家的 AUC 為 0.88 [3]。

*   **肺癌偵測**：AI 在胸部電腦斷層 (CT) 掃描中偵測肺結節的能力已得到驗證。
    *   **效能比較**：一篇 2025 年的系統性回顧發現，AI 模型在偵測肺結節方面的**敏感度**（86.0–98.1%）顯著高於放射科醫生（68–76%），但在**特異度**上略低（77.5–87% vs. 87–91.7%）[4]。這意味著 AI 能更有效地找出潛在病灶，但也可能產生更多的偽陽性結果。在評估結節惡性程度上，AI 在敏感度、特異度和準確度方面普遍優於放射科醫生 [4]。

*   **骨折偵測**：AI 在 X 光影像中偵測骨折是另一個關鍵應用。多家公司，如 AZmed，已將其納入 2025 年的臨床就緒 AI 工具指南中，顯示其技術已趨於成熟 [5, 6]。

### 評估與挑戰

*   **臨床驗證與挑戰**：儘管 AI 表現出色，但高偽陽性率仍是一大挑戰，尤其是在肺癌偵測中。這可能導致不必要的後續檢查、增加醫療成本並為患者帶來焦慮 [4]。此外，準備高品質、標準化的醫學影像數據以供模型訓練，仍然是一項系統性工程 [1]。

*   **法規遵循**：AI 醫療工具面臨複雜的監管環境。一篇 2024 年的分析指出，歐盟採用全面性的跨部門法規（如 MDR、GDPR、《AI 法案》），雖然謹慎但可能跟不上技術發展的腳步；而美國則採用更具針對性的部門性方法（如 HIPAA、FDA），更具靈活性但被批評為零散 [7]。文章呼籲應採取一種結合兩者優點的「明智且務實」的監管策略 [7]。

*   **倫理影響**：責任歸屬是主要的倫理難題——當 AI 診斷出錯時，責任應由開發者、醫療機構還是 AI 本身承擔尚無定論 [8]。此外，訓練數據的偏見可能導致醫療不平等，而對數據安全的擔憂也成為採用的主要障礙 [8, 9]。

### 未來展望：人機協作

研究一致認為，AI 不會取代放射科醫生，而是作為增強其能力的輔助工具 [1, 8]。放射科醫生具備 AI 難以企及的適應性和深度感知能力，而 AI 則提供無與倫比的速度和數據處理能力。未來的趨勢將是人機協作，AI 負責初步篩查和量化分析，放射科醫生則進行最終的診斷決策，實現效率與精準度的最佳結合 [1]。

## 病理學：AI 引領的數位化革命

隨著全切片影像 (WSI) 技術的普及，數位病理學為 AI 的應用開闢了廣闊的空間。面對全球癌症發病率上升和病理學家短缺的雙重壓力，AI 正在成為提高診斷工作流程效率和準確性的關鍵 [10, 11]。

### AI 技術與具體應用案例

*   **技術類型**：機器學習和深度學習模型是分析數位化組織樣本的核心。

*   **Paige Prostate**：這是一款用於輔助診斷前列腺癌的 AI 工具。
    *   **效能比較與臨床驗證**：一項研究證實，病理學家在使用 Paige Prostate 後，癌症檢測錯誤減少了 70%。該工具的獨立表現顯示，其癌症檢測的敏感性高達 97.4%，特異性為 94.8%。特別是對於非泌尿生殖道專科的病理學家，敏感性顯著提升了 8.5% [12]。

*   **Google 的 LYNA (淋巴結助理)**：此工具用於分析組織病理學切片以識別轉移性乳癌，據報導其準確率達到 99%，在識別微小轉移灶方面優於人類病理學家 [11]。

*   **其他前沿模型**：
    *   **CHIEF**：一個通用的病理學框架，在 11 種癌症的診斷和預後方面，其 AUROC 分數比現有模型高出 10-14% [11]。
    *   **Prov-GigaPath**：一個用於分析千兆像素級 WSI 的基礎模型，在癌症亞型分類方面展現了頂尖性能 [11]。

### 評估與挑戰

*   **實施挑戰**：AI 在病理學的廣泛應用面臨四大挑戰 [13]：
    1.  **數據**：需要大規模、帶有精確註釋的數據集，且數據註釋本身存在觀察者間的差異。
    2.  **模型建立**：需克服組織染色、掃描器差異帶來的變異，並處理 WSI 影像的龐大規模。
    3.  **效能評估**：缺乏標準化的基準數據集和對模型穩健性的分析。
    4.  **部署**：將 AI 工具整合至現有的實驗室資訊系統 (LIS) 成本高昂，且面臨法規批准、互通性及報銷模式缺乏等問題 [10, 13]。

*   **倫理影響**：與放射學相似，病理學 AI 的倫理問題集中在數據隱私、因訓練數據偏見導致的公平性問題，以及診斷錯誤時的問責制 [10, 14, 13]。為確保 AI 工具的公正性與可靠性，讓病理學家從開發初期就參與進來至關重要 [10]。

## 基因組學：待探索的領域

根據本次研究的可用發現，關於人工智慧在基因組學（例如，遺傳疾病診斷）領域從 2023 年至今的最新應用，目前尚無詳細資料。雖然 AI 在基因序列分析、突變預測等方面具有巨大潛力，但本報告無法就此專科提供具體的應用案例及評估維度。這也凸顯了該領域可能是一個值得進一步深入研究的方向。

## 結論與未來方向

綜合 2023 年至 2025 年的研究，人工智慧在醫療診斷領域，特別是放射學和病理學，已從理論走向臨床實踐，展現出作為強大輔助工具的潛力。AI 模型在特定任務上的表現已能媲美甚至超越人類專家，顯著提高了診斷的效率和準確性。

然而，通往廣泛應用的道路依然充滿挑戰。數據標準化、高昂的實施成本、複雜的監管環境以及深刻的倫理問題是所有 AI 醫療應用共同面臨的障礙。高偽陽性率、演算法的「黑箱」性質以及數據偏見等技術瓶頸也亟待解決。

未來的發展方向明確指向「人機協作」的模式。AI 不會取代醫生，而是將他們從繁瑣、重複的任務中解放出來，讓他們能更專注於複雜病例的綜合判斷、與患者的溝通以及制定個人化的治療方案。為了實現這一願景，未來的研究需要不僅專注於演算法的優化，更要著重於建立標準化的評估基準、完善監管與倫理框架，並設計能無縫融入臨床工作流程的解決方案。最終，AI 的成功將取決於它能否真正成為醫生信賴的夥伴，共同提升醫療服務的品質與可及性。

### 來源

[1] Artificial Intelligence-Empowered Radiology—Current Status and Future Perspectives: A State-of-the-Art Review: https://pmc.ncbi.nlm.nih.gov/articles/PMC11816879/
[2] Artificial intelligence for diagnostics in radiology practice: a rapid ...: https://www.thelancet.com/journals/eclinm/article/PIIS2589-5370(25)00160-9/fulltext
[3] Deep learning applications in breast cancer histopathological images: a review for diagnosis, treatment, and prognosis: https://breast-cancer-research.biomedcentral.com/articles/10.1186/s13058-024-01895-6
[4] A Systematic Review of AI Performance in Lung Cancer Detection and Classification From Chest Computed Tomography: https://pmc.ncbi.nlm.nih.gov/articles/PMC12250385/
[5] Enhancing diagnostic accuracy in bone fracture detection from X-ray images using ensemble deep learning models: https://www.science-gate.com/IJAAS/2025/V12I5/1021833ijaas202505008.html
[6] The 2025 guide to clinical-ready tools [Using AI for X-ray] - AZmed: https://www.azmed.co/news-post/ai-in-radiology-the-2025-guide-to-clinical-ready-tools-using-ai-for-x-ray
[7] EU and US Regulatory Challenges Facing AI Health Care Innovator ...: https://law.stanford.edu/2024/04/06/eu-and-us-regulatory-challenges-facing-ai-health-care-innovator-firms/
[8] The Ethical Implications of AI in Clinical Practice in 2025 - RevMaxx: https://www.revmaxx.co/blog/the-ethical-implications-of-ai-in-clinical-practice-in-2025/
[9] Artificial Intelligence-Empowered Radiology—Current Status and ...: https://pmc.ncbi.nlm.nih.gov/articles/PMC11816879/
[10] Digital pathology and AI: your guide to basics and beyond - Aiforia: https://www.aiforia.com/digital-pathology-ai
[11] Current AI technologies in cancer diagnostics and treatment: https://molecular-cancer.biomedcentral.com/articles/10.1186/s12943-025-02369-9
[12] Clinical Validation of Artificial Intelligence–Augmented Pathology...: https://www.paige.ai/publications/clinical-validation-of-artificial-intelligenceaugmented-pathology-diagnosis-demonstrates-significant-gains-in-diagnostic-accuracy-in-prostate-cancer-detection
[13] Unleashing the potential of AI for pathology: challenges and ...: https://pathsocjournals.onlinelibrary.wiley.com/doi/full/10.1002/path.6168
[14] The ethical challenges of artificial intelligence‐driven digital pathology: https://onlinelibrary.wiley.com/doi/10.1002/cjp2.263
 `,
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

async function startEditor(titleFromUser: string) {
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
}

function onCancelNew() {
  // 保持在新建頁；若需要可在此導入預設流程
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
