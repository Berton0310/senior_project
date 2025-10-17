<template>
  <div class="umo-ai-container" :style="{ width: aiWidth + 'px' }">
    <div class="umo-ai-title">
      <icon class="icon-ai" name="assistant" /> AI 助手
      <div class="umo-dialog__close" @click="$emit('close')">
        <icon name="close" />
      </div>
    </div>
    <div class="umo-ai-content umo-scrollbar">
      <!-- 這裡放 AI 功能內容 -->
      <div
        v-for="(msg, idx) in messages"
        :key="idx"
        :class="[
          'umo-ai-msg',
          msg.role === 'user' ? 'umo-ai-msg--user' : 'umo-ai-msg--ai',
        ]"
      >
        <span>{{ msg.content }}</span>
      </div>
      <div v-if="disableSend" class="umo-ai-msg umo-ai-msg--generating">
        <!-- 脈搏文字動畫 -->
        <div class="umo-ai-typing-text">AI 正在回覆...</div>
      </div>
    </div>
    <form class="umo-ai-input-bar" @submit.prevent="onSend">
      <div class="umo-ai-input-panel">
        <textarea
          ref="inputRef"
          v-model="inputMsg"
          class="umo-ai-input"
          placeholder="輸入訊息..."
          autocomplete="off"
          rows="1"
          @keydown.enter.exact.prevent="onSend"
          @keydown.enter.shift.exact.prevent="inputMsg += '\n'"
        ></textarea>
        <div class="umo-ai-actions">
          <button
            class="umo-ai-send"
            type="submit"
            :disabled="disableSend || !inputMsg.trim()"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 -5 24 32"
              stroke-width="1.5"
              stroke="currentColor"
              class="umo-ai-send-icon"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M4.5 10.5 12 3m0 0 7.5 7.5M12 3v18"
              />
            </svg>
          </button>
        </div>
      </div>
    </form>
    <div class="umo-ai-resize-handle" @mousedown="startResize"></div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  width?: number
  messages: { role: 'user' | 'ai'; content: string }[]
  disableSend?: boolean
}>()
const emits = defineEmits(['close', 'update:width', 'send'])
const baseAiWidth = 360
const aiWidth = ref(props.width ?? baseAiWidth)
const inputMsg = ref('')
const inputRef = ref<HTMLInputElement>()
// 自動調整輸入框高度
const autoResize = () => {
  if (inputRef.value) {
    inputRef.value.style.height = 'auto'
    const newHeight = Math.min(inputRef.value.scrollHeight, 120)
    inputRef.value.style.height = `${newHeight}px`
  }
}
watch(inputMsg, () => {
  nextTick(() => {
    autoResize()
  })
})
onMounted(() => {
  autoResize()
})

const onSend = () => {
  const msg = inputMsg.value.trim()
  if (!msg) return
  emits('send', msg)
  inputMsg.value = ''
  nextTick(() => {
    autoResize()
  })
}
watch(
  () => props.width,
  (w: number | undefined) => {
    if (typeof w === 'number') aiWidth.value = w
  },
)

const isResizing = ref(false)
const startX = ref(0)
const initialWidth = ref(baseAiWidth)
const startResize = (e: MouseEvent) => {
  isResizing.value = true
  startX.value = e.clientX
  initialWidth.value = aiWidth.value
  // 禁止選取內容
  document.body.style.userSelect = 'none'
  document.addEventListener('mousemove', resize)
  document.addEventListener('mouseup', stopResize)
}
const resize = (e: MouseEvent) => {
  if (isResizing.value) {
    const offsetX = startX.value - e.clientX
    const newWidth = initialWidth.value + offsetX
    const minWidth = baseAiWidth / 1.5
    const maxWidth = baseAiWidth * 2
    if (newWidth >= minWidth && newWidth <= maxWidth) {
      aiWidth.value = newWidth
      emits('update:width', newWidth)
    }
  }
}
const stopResize = () => {
  isResizing.value = false
  // 恢復選取內容
  document.body.style.userSelect = ''
  document.removeEventListener('mousemove', resize)
  document.removeEventListener('mouseup', stopResize)
}
</script>

<style lang="less" scoped>
.umo-ai-container {
  background-color: var(--umo-color-white);
  border-left: solid 1px var(--umo-border-color);
  width: 360px;
  min-width: 200px;
  max-width: 400px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  position: relative;
  flex-shrink: 0;
  z-index: 10;
  transition: width 0.001s;
  .umo-ai-resize-handle {
    position: absolute;
    top: 0;
    left: -2px;
    width: 3px;
    height: 100%;
    opacity: 0.5;
    background-color: transparent;
    &:hover {
      background-color: var(--umo-primary-color);
      cursor: col-resize;
    }
  }
  .umo-ai-title {
    border-bottom: solid 1px var(--umo-border-color-light);
    display: flex;
    align-items: center;
    position: relative;
    padding: 10px 15px;
    font-family: var(--umo-font-family);
    .icon-ai {
      margin-right: 5px;
      font-size: 20px;
    }
    .umo-dialog__close {
      position: absolute;
      right: 15px;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
    }
  }
  .umo-ai-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    padding: 10px;
    overflow-y: auto;
    .umo-ai-msg {
      max-width: 80%;
      margin: 10px 0;
      padding: 8px 14px;
      border-radius: 16px;
      font-size: 1rem;
      word-break: break-all;
      font-family: var(--umo-font-family);
    }
    .umo-ai-msg--user {
      align-self: flex-end;
      background: var(--umo-primary-color);
      color: #fff;
    }
    .umo-ai-msg--ai {
      align-self: flex-start;
      background: #f5f5f5;
      color: #333;
    }
  }
  .umo-ai-input-bar {
    padding: 0 0 10px 0;
    background: transparent;
    border: none;
    box-shadow: none;
    display: flex;
    justify-content: center;
  }
  .umo-ai-input-panel {
    width: 100%;
    max-width: 600px;
    background: #fff;
    border: 1.5px solid #e0e0e0;
    border-radius: 20px;
    box-shadow: 0 2px 8px 0 rgba(0, 0, 0, 0.06);
    display: flex;
    flex-direction: column;
    padding: 12px 16px 8px 16px;
    gap: 8px;
  }
  .umo-ai-input {
    background: transparent;
    border: none;
    color: #222;
    font-size: 1rem;
    font-family: var(--umo-font-family);
    resize: none;
    min-height: 32px;
    outline: none;
    width: 100%;
    margin-bottom: 4px;
  }
  .umo-ai-actions {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 8px;
  }
  .umo-ai-send {
    background: var(--umo-primary-color); /* 藍色填滿 */
    border: none;
    border-radius: 50%; /* 圓形 */
    width: 25px;
    height: 25px;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0;
    margin: 0;
    cursor: pointer;
    transition:
      opacity 0.2s,
      background 0.2s;
  }
  .umo-ai-send:disabled {
    opacity: 0.25;
    cursor: not-allowed;
  }

  .umo-ai-send-icon {
    width: 2em;
    height: 2em;
    color: #fff; /* 箭頭線條為白色 */
    display: block;
  }
  .umo-ai-msg--generating {
    align-self: flex-start;
    background: #f5f5f5;
    color: #333;
    animation: fadeIn 0.3s ease-in;
  }

  .umo-ai-typing-text {
    color: #666;
    font-style: italic;
    animation: pulse 1.5s infinite ease-in-out;
  }

  @keyframes pulse {
    0%,
    100% {
      opacity: 0.5;
    }
    50% {
      opacity: 1;
    }
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
}
</style>
