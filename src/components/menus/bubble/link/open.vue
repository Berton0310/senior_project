<template>
  <menus-button ico="link" :text="t('insert.link.open')" @menu-click="openLink" />
</template>

<script setup lang="ts">
const editor = inject('editor')
const emits = defineEmits(['hide-bubble'])

const openLink = () => {
  const href = editor?.value?.storage?.link?.meta?.href
  if (!href) return
  const a = document.createElement('a')
  a.href = href
  a.target = '_blank'
  a.rel = 'noopener noreferrer'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  emits('hide-bubble')
}
</script>

<style lang="less" scoped>
/* no-op: visual handled by menus-button */
</style>
