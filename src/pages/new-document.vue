<template>
  <div class="new-doc">
    <t-card header="新建報告" style="max-width:560px; width:100%">
      <div style="display:flex; flex-direction:column; gap:12px">
        <label for="report-title">請輸入報告書題目</label>
        <t-input
          id="report-title"
          v-model="title"
          placeholder="例如：2025 年 Q4 成果報告"
          @enter="onConfirm"
        />
        <t-alert v-if="error" theme="error" :message="error" :close="false" />
        <div style="display:flex; gap:8px; justify-content:flex-end; margin-top:8px">
          <t-button variant="outline" theme="default" @click="$emit('cancel')">取消</t-button>
          <t-button theme="primary" @click="onConfirm">建立</t-button>
        </div>
      </div>
    </t-card>
  </div>
  
</template>

<script setup lang="ts">
const emit = defineEmits<{
  (e: 'confirm', title: string): void
  (e: 'cancel'): void
}>()

const title = ref('')
const error = ref('')

function validate(v: string) {
  if (!v || !v.trim()) return '題目不能為空'
  if (v.length > 120) return '題目長度不可超過 120 字元'
  return ''
}

function onConfirm() {
  error.value = validate(title.value)
  if (error.value) return
  emit('confirm', title.value.trim())
}
</script>

<style scoped>
.new-doc {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}
</style>


