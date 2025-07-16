<template>
  <div class="control-section">
    <div class="fresh-card">
      <h2 class="card-title">模拟器连接</h2>
      <div class="card-content">
        <div class="connect-controls">
          <el-select 
            v-model="selectedEmulator" 
            placeholder="请选择模拟器"
            size="small"
            class="emulator-select"
            :loading="loadingEmulators"
            :disabled="!isPathSet || emulatorConnected || emulatorList.length === 0"
          >
            <el-option
              v-for="item in emulatorList"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
            <template #empty>
              <div class="empty-text">
                <span v-if="!isPathSet">请在设置中选择MuMu模拟器路径</span>
                <span v-else-if="loadingEmulators">正在加载模拟器列表...</span>
                <span v-else>未检测到模拟器，请启动MuMu模拟器后点击刷新按钮</span>
              </div>
            </template>
          </el-select>
          <div class="connect-buttons">
            <el-button 
              :type="emulatorList.length === 0 ? 'danger' : (emulatorConnected ? 'success' : 'primary')" 
              size="small"
              @click="handleConnectionToggle"
              :loading="connectingEmulator"
              :disabled="!canConnect || emulatorConnected"
              class="small-button no-outline"
            >
              <el-icon v-if="!connectingEmulator">
                <Connection />
              </el-icon>
            </el-button>
            <el-button 
              size="small"
              @click="refreshEmulators"
              :loading="loadingEmulators"
              :disabled="!isPathSet || !apiAvailable || emulatorConnected"
              class="small-button no-outline"
            >
              <el-icon><Refresh /></el-icon>
            </el-button>
          </div>
        </div>
        
        <!-- 连接状态信息 -->
        <div class="emulator-status" v-if="emulatorConnected">
          <el-tag type="success" size="small">已连接</el-tag>
          <span class="emulator-info">
            端口: {{ emulatorInfo.adb_port }}
          </span>
        </div>
        

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Connection, Refresh } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// 状态
const emulatorList = ref([])
const selectedEmulator = ref('')
const emulatorConnected = ref(false)
const mumuPath = ref('')
const loadingEmulators = ref(false)
const connectingEmulator = ref(false)
const apiAvailable = ref(false)
const emulatorInfo = ref({
  index: 1,
  adb_port: '127.0.0.1:0000',
  state: false
})

// 计算属性
const isPathSet = computed(() => !!mumuPath.value)
const canConnect = computed(() => {
  return isPathSet.value && selectedEmulator.value && apiAvailable.value && !emulatorConnected.value && emulatorList.value.length > 0
})

// 检查API是否可用
const checkApiAvailable = () => {
  if (window.pywebview && window.pywebview.api) {
    apiAvailable.value = true
    return true
  } else {
    console.error('pywebview API 不可用')
    apiAvailable.value = false
    return false
  }
}

// 获取模拟器状态
const getEmulatorStatus = async () => {
  if (!checkApiAvailable()) {
    return { status: false, message: 'API不可用' }
  }
  
  try {
    const response = await window.pywebview.api.get_emulator_status()
    mumuPath.value = response.mumuPath
    emulatorInfo.value = response.emulatorInfo
    emulatorConnected.value = response.emulatorInfo.state
    return response
  } catch (error) {
    console.error('获取模拟器状态失败:', error)
    return { status: false, message: `获取模拟器状态失败: ${error.message || error}` }
  }
}

// 获取模拟器列表
const getEmulatorList = async () => {
  if (!checkApiAvailable()) {
    return { status: false, message: 'API不可用' }
  }
  
  if (!isPathSet.value) {
    emulatorList.value = []
    return { status: false, message: '请在设置中选择MuMu模拟器路径' }
  }

  try {
    loadingEmulators.value = true
    const response = await window.pywebview.api.get_emulator_list()
    
    if (response.status) {
      // 过滤出已开启的模拟器
      const runningEmulators = response.data.filter(item => item.状态 === 'M-开启')
      
      // 转换为下拉菜单格式，显示编号和名称
      emulatorList.value = runningEmulators.map(item => ({
        value: item.编号.toString(),
        label: `#${item.编号} - ${item.名称}`,
        status: item.状态,
        adbPort: item.ADB || ''
      }))
      
      // 如果只有一个开启的模拟器，默认选中它
      if (emulatorList.value.length === 1 && !emulatorConnected.value) {
        selectedEmulator.value = emulatorList.value[0].value
        console.log(`自动选择唯一的开启模拟器: ${selectedEmulator.value}`)
      } else if (emulatorList.value.length === 0) {
        // 如果没有开启的模拟器，清空选择
        selectedEmulator.value = ''
        console.log('未检测到已开启的模拟器')
      }
    } else {
      emulatorList.value = []
      if (response.message !== '未检测到MuMu模拟器实例') {
        ElMessage.warning(response.message)
      }
    }
    
    return response
  } catch (error) {
    console.error('获取模拟器列表失败:', error)
    emulatorList.value = []
    return { status: false, message: `获取模拟器列表失败: ${error.message || error}` }
  } finally {
    loadingEmulators.value = false
  }
}

// 连接模拟器
const connectEmulator = async (index) => {
  if (!checkApiAvailable()) {
    return { status: false, message: 'API不可用' }
  }
  
  if (!index) {
    index = selectedEmulator.value
  }
  
  if (!index) {
    return { status: false, message: '请选择要连接的模拟器' }
  }

  try {
    connectingEmulator.value = true
    const response = await window.pywebview.api.connect_emulator(parseInt(index))
    
    if (response.status) {
      emulatorConnected.value = true
      emulatorInfo.value = response.emulatorInfo
    }
    
    return response
  } catch (error) {
    console.error('连接模拟器失败:', error)
    return { status: false, message: `连接模拟器失败: ${error.message || error}` }
  } finally {
    connectingEmulator.value = false
  }
}

// 初始化函数
const initialize = async () => {
  // 等待pywebview API可用
  let retries = 0
  const maxRetries = 20
  const retryInterval = 300 // 毫秒
  
  while (!checkApiAvailable() && retries < maxRetries) {
    console.log(`等待pywebview API可用，尝试次数: ${retries + 1}/${maxRetries}`)
    await new Promise(resolve => setTimeout(resolve, retryInterval))
    retries++
  }
  
  if (apiAvailable.value) {
    console.log('pywebview API已可用，获取模拟器状态')
    await getEmulatorStatus()
  } else {
    console.error(`pywebview API 在${maxRetries}次尝试后仍不可用`)
    ElMessage.error('无法连接到后端服务，请重启应用')
  }
}

// 处理连接
const handleConnectionToggle = async () => {
  if (!apiAvailable.value) {
    ElMessage.error('后端API不可用，请重启应用')
    return
  }
  
  // 连接后不能断开，只能连接
  if (emulatorConnected.value) {
    return
  }
  
  try {
    // 连接模拟器
    const response = await connectEmulator()
    
    // 显示操作结果
    if (response.status) {
      ElMessage.success(response.message)
    } else {
      ElMessage.error(response.message)
    }
  } catch (error) {
    console.error('操作失败:', error)
    ElMessage.error('操作失败，请查看控制台日志')
  }
}

// 刷新模拟器列表
const refreshEmulators = async () => {
  if (!apiAvailable.value) {
    ElMessage.error('后端API不可用，请重启应用')
    return
  }
  
  try {
    const response = await getEmulatorList()
    
    if (!response.status && response.message !== '未检测到MuMu模拟器实例') {
      ElMessage.warning(response.message)
    }
  } catch (error) {
    console.error('刷新模拟器列表失败:', error)
    ElMessage.error('刷新模拟器列表失败')
  }
}

// 初始化模拟器状态
const initializeEmulator = async () => {
  // 初始化模拟器状态
  await initialize()
  
  // 如果有设置模拟器路径，则获取模拟器列表
  if (isPathSet.value && apiAvailable.value) {
    refreshEmulators()
  }
}

// 组件挂载时初始化
onMounted(async () => {
  try {
    // 检查pywebview是否已就绪
    if (window.pywebview && window.pywebview.api) {
      // 如果已就绪，直接初始化
      console.log('pywebview已就绪，直接初始化')
      await initializeEmulator()
    } else {
      console.log('pywebview未就绪，等待ready事件')
      
      // 监听自定义事件
      window.addEventListener('pywebview-ready', async () => {
        console.log('收到pywebview-ready事件，初始化模拟器状态')
        await initializeEmulator()
      })
      
      // 监听原始pywebview事件
      window.addEventListener('pywebviewready', async () => {
        console.log('收到pywebviewready事件，初始化模拟器状态')
        await initializeEmulator()
      })
      
      // 添加超时处理，防止事件不触发
      setTimeout(async () => {
        if (!apiAvailable.value) {
          console.warn('pywebview ready事件超时，尝试直接初始化')
          await initializeEmulator()
        }
      }, 5000)
    }
  } catch (error) {
    console.error('初始化模拟器状态失败:', error)
  }
})
</script>

<style lang="scss" scoped>
.control-section {
  width: 100%;
  display: flex;
}

.fresh-card {
  padding: 16px;
  display: flex;
  flex-direction: column;
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  width: 100%;
  transition: all 0.3s ease-in-out;
  overflow: hidden;
  -webkit-mask-image: -webkit-radial-gradient(white, black);
  mask-image: radial-gradient(white, black);
  box-sizing: border-box;

  &:hover {
    box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.08);
  }
  
  .card-title {
    font-size: 1rem;
    font-weight: 600;
    color: #303133;
    margin-bottom: 16px;
    padding-bottom: 10px;
    border-bottom: 1px solid #ebeef5;
    flex-shrink: 0;
    opacity: 0;
    animation: slide-up 0.3s ease-out forwards;
    animation-delay: 0.1s;
  }
  
  .card-content {
    font-size: 0.875rem;
    line-height: 1.6;
    color: #606266;
    overflow-y: auto;
    scrollbar-width: none;
    -ms-overflow-style: none;
    flex-grow: 1;
    opacity: 0;
    animation: fade-in 0.3s ease-out forwards;
    animation-delay: 0.2s;
    
    &::-webkit-scrollbar {
      display: none;
      width: 0;
      height: 0;
    }
  }
}

.connect-controls {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.emulator-select {
  flex-grow: 1;
  opacity: 0;
  animation: fade-in 0.3s ease-out forwards;
  animation-delay: 0.3s;
}

.connect-buttons {
  display: flex;
  gap: 5px;
  flex-shrink: 0;
  opacity: 0;
  animation: fade-in 0.3s ease-out forwards;
  animation-delay: 0.3s;
}

.small-button {
  padding: 8px;
}

.no-outline {
  &:focus,
  &:focus-visible {
    outline: none !important;
    box-shadow: none !important;
  }
}

.empty-text {
  padding: 8px 0;
  text-align: center;
  color: #909399;
  font-size: 14px;
}

.emulator-status {
  margin-top: 10px;
  display: flex;
  align-items: center;
  gap: 8px;
  opacity: 0;
  animation: fade-in 0.3s ease-out forwards;
  animation-delay: 0.4s;
  
  &.warning {
    color: #e6a23c;
  }
  
  .emulator-info {
    font-size: 12px;
    color: #606266;
  }
}

@keyframes fade-in {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slide-up {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style> 