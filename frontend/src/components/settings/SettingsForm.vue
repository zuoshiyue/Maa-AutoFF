<template>
  <div class="settings-container">
    <h3 class="section-title">MuMu模拟器路径</h3>
    <div class="path-input-group">
      <el-input 
        v-model="mumuPath" 
        readonly 
        placeholder="请选择MuMu模拟器安装路径"
      />
      <el-button type="primary" plain @click="selectMumuPath">选择路径</el-button>
    </div>
    
    <h3 class="section-title">日志保留条数</h3>
    <div class="log-retention-group">
      <el-slider 
        v-model="logRetentionCount" 
        :min="100" 
        :max="3000" 
        :step="10" 
        show-input
        :show-input-controls="false"
        @change="saveLogRetention"
      />
    </div>

    <h3 class="section-title">截图频率 (FPS)</h3>
    <div class="fps-group">
      <el-slider 
        v-model="screenshotFps" 
        :min="1" 
        :max="60" 
        :step="1" 
        show-input
        :show-input-controls="false"
        @change="saveScreenshotFps"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElLoading } from 'element-plus'

const mumuPath = ref('')
const logRetentionCount = ref(300)
const screenshotFps = ref(15)

// 加载设置
const loadSettings = async () => {
  try {
    // 静默加载设置，不显示加载中提示
  const loading = ElLoading.service({
      lock: false,
      text: '',
      background: 'rgba(0, 0, 0, 0)'
    })
    
    const response = await window.pywebview.api.get_all_settings()
    loading.close()
    
    if (response.success) {
      const settings = response.data
      mumuPath.value = settings.mumuPath || ''
      logRetentionCount.value = settings.logRetentionCount || 300
      screenshotFps.value = settings.screenshotFps || 15
      // 静默加载设置，不显示成功提示
    } else {
      ElMessage.error(`加载设置失败: ${response.error}`)
    }
  } catch (error) {
    ElMessage.error(`加载设置出错: ${error}`)
  }
}

// 选择MuMu模拟器路径
const selectMumuPath = async () => {
  try {
    // 调用API选择目录，并验证是否包含shell文件夹
    const response = await window.pywebview.api.select_directory(true)
    
    if (response.success) {
      if (response.has_shell === false) {
        // 如果没有shell文件夹，显示提示并且不保存路径
        ElMessage({
          message: '所选目录不是有效的MuMu模拟器目录',
          type: 'warning',
          duration: 3000
        })
        // 不更新路径值，也不保存到设置中
      } else {
        // 只有在目录有效时才更新路径并保存设置
        mumuPath.value = response.data
        // 保存路径设置
        await updateSetting('mumuPath', response.data)
      }
    } else if (response.error !== '未选择目录') {
      ElMessage.error(`选择路径失败: ${response.error}`)
    }
  } catch (error) {
    ElMessage.error(`选择路径出错: ${error}`)
  }
}

// 更新单个设置
const updateSetting = async (key, value) => {
  try {
    const response = await window.pywebview.api.update_setting(key, value)
    
    if (response.success) {
      // 静默保存设置，不显示成功提示
      return true
    } else {
      ElMessage.error(`保存设置失败: ${response.error}`)
      return false
    }
  } catch (error) {
    ElMessage.error(`保存设置出错: ${error}`)
    return false
  }
}

// 保存日志保留条数
const saveLogRetention = async () => {
  await updateSetting('logRetentionCount', logRetentionCount.value)
}

// 保存截图频率
const saveScreenshotFps = async () => {
  await updateSetting('screenshotFps', screenshotFps.value)
}

// 组件挂载时加载设置
onMounted(() => {
  loadSettings()
})
</script>

<style lang="scss" scoped>
.settings-container {
  .section-title {
    font-size: 16px;
    color: #303133;
    margin-bottom: 12px;
    margin-top: 20px;
  }
  
  .path-input-group {
    display: flex;
    gap: 12px;
    
    .el-input {
      flex: 1;
    }
  }
  
  .log-retention-group {
    margin-top: 8px;
    padding: 0 8px;
  }

  .fps-group {
    margin-top: 8px;
    padding: 0 8px;
  }
}
</style> 