<template>
  <drag-handle
    :editor="editor"
    :tippy-options="tippyOpitons"
    class="umo-block-menu-drag-handle"
    :class="{ 'is-empty': editor.isEmpty }"
    @node-change="nodeChange"
  >
    <div
      class="umo-block-menu-hander"
      :class="`umo-selected-node-${selectedNode?.type?.name || 'unknown'} `"
    >
      <menus-context-block-node @dropdown-visible="dropdownVisible" />
      <menus-context-block-common
        v-if="
          !editor.isEmpty ||
          editor.isActive('table') ||
          editor.isActive('callout')
        "
        :node="selectedNode"
        :pos="selectedNodePos"
        @dropdown-visible="dropdownVisible"
      />
    </div>
  </drag-handle>
</template>

<script setup lang="ts">
import DragHandle from '@tiptap-pro/extension-drag-handle-vue-3'
import type { Instance } from 'tippy.js'
import tippy from 'tippy.js'

const editor = inject('editor')
let selectedNode = $ref(null)
let selectedNodePos = $ref(null)

let tippyInstance = $ref<Instance | null>(null)

// 自動重建 tippy 實例
function recreateTippyInstance() {
  if (tippyInstance?.state && !tippyInstance.state.isDestroyed) {
    tippyInstance.destroy()
  }
  // 這裡假設 drag-handle 組件會自動掛載 tippy，否則可手動創建
  tippyInstance = null
  // 若有需要可在此手動創建 tippy 實例
}

const tippyOpitons = $ref<Partial<Instance>>({
  zIndex: 20,
  // 增加協作編輯相關的配置
  appendTo: () => document.body,
  interactive: true,
  trigger: 'manual',
  placement: 'left-start',
  // 改進 popper 配置以更好地處理協作更新
  popperOptions: {
    modifiers: [
      {
        name: 'eventListeners',
        options: { scroll: false, resize: false },
      },
      {
        name: 'preventOverflow',
        options: {
          boundary: 'viewport',
          padding: 8,
        },
      },
      {
        name: 'flip',
        options: {
          fallbackPlacements: ['left-end', 'right-start', 'right-end'],
        },
      },
    ],
  },
  onMount(instance: Instance) {
    // console.log('[BlockMenu] tippy onMount', instance)
    tippyInstance = instance
  },
  onDestroy() {
    tippyInstance = null
  },
})

// 菜单位置更新
const updateMenuPostion = useThrottleFn(() => {
  // 強化 tippy 狀態檢查
  // console.log('[BlockMenu] updateMenuPostion called')
  // console.log('tippyInstance', tippyInstance, tippyInstance?.state)
  if (!tippyInstance || tippyInstance.state?.isDestroyed || !editor.value) {
    recreateTippyInstance()
    return
  }
  try {
    const { state, view } = editor.value
    if (view.isDestroyed) return
    const topPos = state.selection.$from.before(1)
    const topDOM = view.nodeDOM(topPos)
    // console.log('topPos', topPos, 'topDOM', topDOM)
    // 如果找不到 DOM 元素，嘗試其他方法
    if (!topDOM) {
      const selection = window.getSelection()
      if (selection && selection.rangeCount > 0) {
        const range = selection.getRangeAt(0)
        const rect = range.getBoundingClientRect()
        // console.log('fallback rect', rect)
        if (rect && rect.width > 0 && rect.height > 0) {
          tippyInstance.setProps({
            getReferenceClientRect: () => rect,
          })
          tippyInstance.popperInstance?.update()
        }
      }
      return
    }
    const rect = topDOM.getBoundingClientRect()
    // console.log('rect', rect)
    if (rect && rect.width > 0 && rect.height > 0) {
      tippyInstance.setProps({
        getReferenceClientRect: () => rect,
      })
      tippyInstance.popperInstance?.update()
      // 自動顯示 block menu
      if (!tippyInstance.state.isDestroyed && !tippyInstance.state.isVisible) {
        tippyInstance.show()
      }
    }
  } catch (e) {
    console.error('Failed to update block menu position:', e)
  }
}, 200)

// 多次重試位置更新
function robustUpdateMenuPosition() {
  void updateMenuPostion()
  setTimeout(updateMenuPostion, 100)
  setTimeout(updateMenuPostion, 200)
}

// 檢查是否為協作更新
const isCollaborationUpdate = (transaction: any) => {
  return (
    transaction.getMeta('y-transaction') ??
    transaction.getMeta('collaboration') ??
    transaction.getMeta('remote')
  )
}

// 檢查是否為本地用戶操作
const isLocalUserAction = (transaction: any) => {
  return (
    transaction.getMeta('local') ??
    transaction.getMeta('user') ??
    !isCollaborationUpdate(transaction)
  )
}

// 協作更新後的延遲更新函數
const delayedUpdateForCollaboration = useDebounceFn(() => {
  void updateMenuPostion()
}, 100)

onMounted(() => {
  // Fallback: 手動建立 tippy 實例
  setTimeout(() => {
    if (!tippyInstance) {
      const ref = document.querySelector('.umo-block-menu-hander')
      if (ref) {
        tippyInstance = tippy(ref, { ...tippyOpitons, content: ref })
        // console.log('[BlockMenu] 手動建立 tippy', tippyInstance)
      } else {
        // console.log('[BlockMenu] 找不到 .umo-block-menu-hander')
      }
    }
  }, 500)

  // 監聽選擇更新事件
  editor.value.on(
    'selectionUpdate',
    ({ transaction }: { transaction: any }) => {
      if (isCollaborationUpdate(transaction)) {
        return
      }
      robustUpdateMenuPosition()
    },
  )

  // 監聽文檔更新事件
  editor.value.on(
    'update',
    ({ editor, transaction }: { editor: any; transaction: any }) => {
      if (isCollaborationUpdate(transaction)) {
        nextTick(() => {
          robustUpdateMenuPosition()
        })
      }
    },
  )

  // 監聽事務事件
  editor.value.on(
    'transaction',
    ({ editor, transaction }: { editor: any; transaction: any }) => {
      if (isCollaborationUpdate(transaction)) {
        const hasRelevantChanges = transaction.steps.some((step: any) => {
          return step.from !== step.to || step.slice.size > 0
        })
        if (hasRelevantChanges) {
          setTimeout(() => {
            // 強制 focus
            editor.view.focus()
            robustUpdateMenuPosition()
          }, 100)
        }
      }
    },
  )

  // 監聽協作狀態變化
  editor.value.on('focus', () => {
    nextTick(() => {
      robustUpdateMenuPosition()
    })
  })

  // 監聽滾動事件，確保菜單位置跟隨滾動
  const pageContainer = document.querySelector(
    `${inject('container')} .umo-zoomable-container`,
  ) as HTMLElement

  if (pageContainer) {
    const handleScroll = useThrottleFn(() => {
      if (tippyInstance?.state.isVisible) {
        void updateMenuPostion()
      }
    }, 100)

    pageContainer.addEventListener('scroll', handleScroll)

    // 清理事件監聽器
    onUnmounted(() => {
      pageContainer.removeEventListener('scroll', handleScroll)
    })
  }
})

const nodeChange = ({ node, pos }: { node: Node | null; pos: number }) => {
  selectedNode = node ?? null
  if (pos !== null) {
    selectedNodePos = pos
  }
}

const dropdownVisible = (visible: boolean) => {
  editor.value.commands.setMeta('lockDragHandle', visible)
}
</script>

<style lang="less">
.umo-block-menu {
  .umo-menu-button {
    color: var(--umo-text-color-light) !important;
  }
  &-drag-handle.is-empty {
    .umo-block-menu-hander {
      margin-top: 2px;
    }
  }
  &-hander {
    position: absolute;
    display: flex;
    right: -10px;
    top: -5px;
    padding-right: 15px;
    @media print {
      display: none;
    }
    &.umo-selected-node {
      &-table,
      &-horizontalRule,
      &-ProseMirror-gapcursor {
        margin-top: 5px;
      }
      &-pageBreak {
        margin-top: -6px;
      }
    }
    .umo-menu-button {
      background-color: var(--umo-page-background);
      .umo-button-content {
        color: rgba(0, 0, 0, 0.5);
      }
      &:not(.active):hover {
        background-color: var(--umo-content-node-selected-background);
      }
      &.active {
        &:hover {
          opacity: 0.8;
        }
        .umo-button-content {
          color: var(--umo-text-color-light);
        }
      }
    }
  }
  &-dropdown {
    .umo-block-menu-group-name {
      padding-left: 15px !important;
    }
    .umo-dropdown__menu,
    .umo-dropdown__submenu {
      --td-radius-default: 0;
      padding: 8px 0 !important;
      .umo-divider {
        margin: 4px 0 2px;
        opacity: 0.5;
      }
      .umo-dropdown__item {
        padding: 2px 0;
        min-width: 140px !important;
        .umo-menu-button {
          background-color: transparent;
          padding: 0 15px;
          box-sizing: border-box;
          justify-content: flex-start;
          width: 100%;
          &-wrap {
            display: block !important;
          }
          .umo-button__text {
            width: 100%;
          }
        }
        .umo-button-content {
          width: 100%;
          justify-content: flex-start;
          .umo-button-text {
            color: var(--umo-text-color);
          }
          .umo-button-icon {
            margin-right: 3px;
            font-size: 16px;
            color: #666;
          }
          .umo-button-kbd {
            flex: 1;
            text-align: right;
            color: var(--umo-text-color-light);
            font-family: Arial, Helvetica, sans-serif;
            font-size: 9px;
          }
          .umo-heading {
            display: flex;
            color: var(--umo-text-color);
            .icon-heading {
              font-size: 12px;
              display: inline-block;
              width: 2em;
            }
          }
        }
        &--disabled {
          .umo-button-content {
            opacity: 0.6;
          }
        }
        &-direction {
          opacity: 0.4;
          font-size: 12px !important;
          margin-right: 8px;
        }
        .umo-dropdown-item-label {
          padding: 1px 15px;
          overflow: hidden;
          text-overflow: ellipsis;
          display: -webkit-box;
          -webkit-line-clamp: 2;
          line-clamp: 2;
          -webkit-box-orient: vertical;
        }
      }
    }

    .umo-delete-node {
      .umo-button {
        * {
          color: var(--umo-error-color) !important;
        }
      }
    }
  }
}

.ProseMirror-noderangeselection {
  *::selection {
    background: transparent;
  }
  * {
    caret-color: transparent;
  }
}
</style>
