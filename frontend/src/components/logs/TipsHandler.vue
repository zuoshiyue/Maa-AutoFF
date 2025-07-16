<template>
  <!-- 这是一个无渲染组件，只用于处理提示信息事件 -->
</template>

<script setup>
import { onMounted, onBeforeUnmount } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 处理提示信息事件
const handleTipMessage = (event) => {
  const tipData = event.detail
  
  // 使用Element Plus的消息组件显示提示
  ElMessage({
    message: tipData.message,
    type: tipData.type,
    duration: tipData.duration,
    showClose: true
  })
}

// 处理确认对话框事件
const handleConfirmMessage = (event) => {
  const confirmData = event.detail
  
  // 使用Element Plus的确认对话框组件
  ElMessageBox.confirm(
    confirmData.message,
    confirmData.title,
    {
      confirmButtonText: confirmData.confirmText,
      cancelButtonText: confirmData.cancelText,
      type: 'warning'
    }
  ).then(() => {
    // 用户点击确认
    if (confirmData.callback) {
      confirmData.callback(true)
    }
  }).catch(() => {
    // 用户点击取消
    if (confirmData.callback) {
      confirmData.callback(false)
    }
  })
}

onMounted(() => {
  // 添加提示信息事件监听
  window.addEventListener('show-tip', handleTipMessage)
  
  // 添加确认对话框事件监听
  window.addEventListener('show-confirm', handleConfirmMessage)
})

onBeforeUnmount(() => {
  // 移除提示信息事件监听
  window.removeEventListener('show-tip', handleTipMessage)
  
  // 移除确认对话框事件监听
  window.removeEventListener('show-confirm', handleConfirmMessage)
})
</script> 