<template>
  <div class="log-viewer">
    <div class="log-header">
      <div class="search-filter">
        <el-input
          v-model="searchText"
          placeholder="搜索日志内容"
          prefix-icon="el-icon-search"
          clearable
          size="small"
          @input="filterLogs"
        />
        <el-select v-model="filterLevel" placeholder="日志级别" size="small" @change="filterLogs">
          <el-option label="全部" value="" />
          <el-option label="DEBUG" value="DEBUG" />
          <el-option label="INFO" value="INFO" />
          <el-option label="WARNING" value="WARNING" />
          <el-option label="ERROR" value="ERROR" />
          <el-option label="CRITICAL" value="CRITICAL" />
        </el-select>
      </div>
      <div class="log-controls">
        <el-button type="primary" size="small" @click="refreshLogs">刷新</el-button>
        <el-button type="success" size="small" @click="saveLogs">保存</el-button>
        <el-button type="danger" size="small" @click="clearLogs">清空</el-button>
      </div>
    </div>
    
    <div class="log-container" ref="logContainer">
      <div v-for="(log, index) in filteredLogs" :key="index" :class="['log-item', `log-${log.level.toLowerCase()}`]">
        <span class="log-time">{{ log.formatted_time }}</span>
        <span class="log-level">{{ log.level }}</span>
        <span class="log-message">{{ log.message }}</span>
      </div>
      <div v-if="filteredLogs.length === 0" class="log-empty">
        {{ searchText || filterLevel ? '没有匹配的日志记录' : '暂无日志记录' }}
      </div>
    </div>
    
    <div class="log-status">
      <span>共 {{ logs.length }} 条日志</span>
      <span v-if="filteredLogs.length !== logs.length">，显示 {{ filteredLogs.length }} 条</span>
      <el-switch
        v-model="autoScroll"
        active-text="自动滚动"
        inactive-text=""
        size="small"
        style="margin-left: 15px;"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'

// 日志数据
const logs = ref([])
const filteredLogs = ref([])
const filterLevel = ref('')
const searchText = ref('')
const logContainer = ref(null)
const autoScroll = ref(true)

// 处理新日志
const handleNewLog = (logData) => {
  logs.value.push(logData)
  
  // 如果日志数量超过500条，移除最早的日志
  if (logs.value.length > 500) {
    logs.value.shift()
  }
  
  // 应用过滤
  filterLogs()
  
  // 自动滚动到底部
  if (autoScroll.value) {
    nextTick(() => {
      scrollToBottom()
    })
  }
}

// 滚动到底部
const scrollToBottom = () => {
  if (logContainer.value) {
    logContainer.value.scrollTop = logContainer.value.scrollHeight
  }
}

// 过滤日志
const filterLogs = () => {
  let filtered = [...logs.value]
  
  // 按级别过滤
  if (filterLevel.value) {
    filtered = filtered.filter(log => log.level === filterLevel.value)
  }
  
  // 按搜索文本过滤
  if (searchText.value) {
    const searchLower = searchText.value.toLowerCase()
    filtered = filtered.filter(log => 
      log.message.toLowerCase().includes(searchLower) || 
      log.level.toLowerCase().includes(searchLower)
    )
  }
  
  filteredLogs.value = filtered
}

// 刷新日志
const refreshLogs = async () => {
  try {
    // 调用后端API获取日志
    const result = await window.pywebview.api.get_logs(500, null)
    if (result && result.success) {
      logs.value = result.data
      filterLogs()
      
      nextTick(() => {
        scrollToBottom()
      })
    }
  } catch (error) {
    console.error('获取日志失败:', error)
    ElMessage.error('获取日志失败')
  }
}

// 清空日志
const clearLogs = async () => {
  try {
    // 调用后端API清空日志
    const result = await window.pywebview.api.clear_logs()
    if (result && result.success) {
      logs.value = []
      filteredLogs.value = []
      ElMessage.success('日志已清空')
    }
  } catch (error) {
    console.error('清空日志失败:', error)
    ElMessage.error('清空日志失败')
  }
}

// 保存日志
const saveLogs = () => {
  try {
    // 创建日志文本
    const logText = filteredLogs.value.map(log => 
      `[${log.formatted_time}] [${log.level}] ${log.message}`
    ).join('\n')
    
    // 创建Blob对象
    const blob = new Blob([logText], { type: 'text/plain' })
    
    // 创建下载链接
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `logs_${new Date().toISOString().replace(/[:.]/g, '-')}.txt`
    
    // 触发下载
    document.body.appendChild(link)
    link.click()
    
    // 清理
    URL.revokeObjectURL(url)
    document.body.removeChild(link)
    
    ElMessage.success('日志已保存')
  } catch (error) {
    console.error('保存日志失败:', error)
    ElMessage.error('保存日志失败')
  }
}

// 监听滚动事件
const handleScroll = () => {
  if (logContainer.value) {
    const { scrollTop, scrollHeight, clientHeight } = logContainer.value
    // 如果用户滚动到接近底部，启用自动滚动
    autoScroll.value = scrollTop + clientHeight >= scrollHeight - 50
  }
}

// 监听过滤条件变化
watch([filterLevel, searchText], () => {
  filterLogs()
})

onMounted(() => {
  // 添加日志事件监听
  window.addEventListener('log-message', handleLogMessage)
  
  // 添加滚动事件监听
  if (logContainer.value) {
    logContainer.value.addEventListener('scroll', handleScroll)
  }
  
  // 初始加载日志
  refreshLogs()
})

onBeforeUnmount(() => {
  // 移除日志事件监听
  window.removeEventListener('log-message', handleLogMessage)
  
  // 移除滚动事件监听
  if (logContainer.value) {
    logContainer.value.removeEventListener('scroll', handleScroll)
  }
})

// 处理日志消息事件
const handleLogMessage = (event) => {
  const logData = event.detail
  console.log(`[${logData.level}] ${logData.message}`)
  handleNewLog(logData)
}
</script>

<style lang="scss" scoped>
.log-viewer {
  display: flex;
  flex-direction: column;
  height: 100%;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
}

.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background-color: #f5f7fa;
  border-bottom: 1px solid #dcdfe6;
  
  .search-filter {
    display: flex;
    gap: 10px;
    flex: 1;
    
    .el-input {
      max-width: 250px;
    }
  }
  
  .log-controls {
    display: flex;
    gap: 8px;
  }
}

.log-container {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
  background-color: #fafafa;
  font-family: monospace;
  font-size: 13px;
}

.log-item {
  padding: 3px 0;
  line-height: 1.4;
  border-bottom: 1px solid #f0f0f0;
  white-space: pre-wrap;
  word-break: break-all;
  
  &:last-child {
    border-bottom: none;
  }
}

.log-time {
  color: #8c8c8c;
  margin-right: 8px;
}

.log-level {
  display: inline-block;
  width: 70px;
  margin-right: 8px;
  font-weight: bold;
}

.log-debug .log-level {
  color: #8c8c8c;
}

.log-info .log-level {
  color: #1890ff;
}

.log-warning .log-level {
  color: #faad14;
}

.log-error .log-level,
.log-critical .log-level {
  color: #f5222d;
}

.log-empty {
  text-align: center;
  color: #8c8c8c;
  padding: 20px 0;
}

.log-status {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  background-color: #f5f7fa;
  border-top: 1px solid #dcdfe6;
  color: #606266;
  font-size: 12px;
}
</style> 