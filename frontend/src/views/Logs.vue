<template>
  <div class="logs-view">
    <el-card class="logs-card">
      <template #header>
        <div class="card-header">
          <h2>系统日志</h2>
        </div>
      </template>
      
      <LogViewer class="log-viewer-container" />
    </el-card>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import LogViewer from '../components/logs/LogViewer.vue'

onMounted(() => {
  console.log('日志页面已加载')
})
</script>

<style lang="scss" scoped>
.logs-view {
  padding: 20px;
  height: 100%;
}

.logs-card {
  height: calc(100% - 40px);
  
  :deep(.el-card__body) {
    height: calc(100% - 60px);
    padding: 0;
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  
  h2 {
    margin: 0;
  }
}

.log-viewer-container {
  height: 100%;
}
</style> 