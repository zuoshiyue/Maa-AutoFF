<template>
  <div>
    <el-button 
      :type="isRunning ? 'danger' : 'primary'"
      @click="toggleTask"
      :loading="isLoading"
    >
      {{ buttonText }}
    </el-button>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { ElButton, ElMessage } from 'element-plus'

const isRunning = ref(false)
const isLoading = ref(false) // 用于处理API调用期间的加载状态
let intervalId = null

const buttonText = computed(() => {
  if (isLoading.value) return '请稍候...'
  return isRunning.value ? '停止莫古抓球' : '开始莫古抓球'
})

// 调用后端API来切换任务状态
const toggleTask = async () => {
  isLoading.value = true
  try {
    const result = await window.pywebview.api.toggle_mog_catch()
    if (result.success) {
      ElMessage.success(result.message)
      isRunning.value = result.is_running
    } else {
      ElMessage.error(result.message)
    }
  } catch (error) {
    console.error('调用toggle_mog_catch失败:', error)
    ElMessage.error('操作失败，请查看日志')
  } finally {
    isLoading.value = false
  }
}

// 获取当前任务状态
const getStatus = async () => {
  try {
    const result = await window.pywebview.api.get_goldsaucer_status()
    isRunning.value = result.is_running
  } catch (error) {
    console.error('获取金碟游乐场状态失败:', error)
    // 如果获取失败，停止轮询
    if (intervalId) {
      clearInterval(intervalId)
      intervalId = null
    }
  }
}

// 组件挂载时，开始轮询状态
onMounted(() => {
  getStatus() // 立即获取一次状态
  intervalId = setInterval(getStatus, 2000) // 每2秒轮询一次
})

// 组件卸载时，清除定时器
onUnmounted(() => {
  if (intervalId) {
    clearInterval(intervalId)
  }
})
</script>

<style scoped>
/* 可以根据需要添加样式 */
</style> 