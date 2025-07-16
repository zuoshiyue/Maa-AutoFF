<template>
  <div class="fishing-page">
    <el-button
      :type="buttonType"
      size="large"
      @click="toggleFishing"
      :loading="isLoading"
      class="start-button"
      :class="{'running': isFishing, 'pulse': !isFishing && !isLoading}"
    >
      {{ fishingButtonText }}
    </el-button>

    <!-- 钓鱼设置选项 -->
    <div class="fishing-settings">
      <el-checkbox
        v-model="needRepair"
        @change="updateSetting('need_repair', needRepair)"
        :disabled="isFishing"
      >
        自动维修装备
      </el-checkbox>
      <el-checkbox
        v-model="needSubmit"
        @change="updateSetting('need_submit', needSubmit)"
        :disabled="isFishing"
      >
        自动提交收藏品
      </el-checkbox>
      <el-checkbox
        v-model="smallToBig"
        @change="updateSetting('small_to_big', smallToBig)"
        :disabled="isFishing"
      >
        以小钓大
      </el-checkbox>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'

const isFishing = ref(false)
const isLoading = ref(false)

// 钓鱼设置
const needRepair = ref(false)
const needSubmit = ref(false)
const smallToBig = ref(false)

const fishingButtonText = computed(() => {
  if (isLoading.value) {
    return isFishing.value ? '停止中...' : '启动中...'
  }
  return isFishing.value ? '停止钓鱼' : '开始钓鱼'
})

const buttonType = computed(() => {
  return isFishing.value ? 'warning' : 'primary'
})

const toggleFishing = async () => {
  isLoading.value = true
  try {
    const result = await window.pywebview.api.toggle_fishing()
    if (result) {
      if (result.success) {
        isFishing.value = result.is_fishing
        ElMessage.success(result.message)
      } else {
        ElMessage.error(result.message)
      }
    }
  } catch (error) {
    console.error('调用钓鱼API失败:', error)
    ElMessage.error('与后端通信失败')
  } finally {
    isLoading.value = false
  }
}

const getStatus = async () => {
  try {
    const result = await window.pywebview.api.get_fishing_status()
    if (result && typeof result.is_fishing !== 'undefined') {
      isFishing.value = result.is_fishing
    }
  } catch (error) {
    console.error('获取钓鱼状态失败:', error)
  }
}

// 获取钓鱼设置
const getFishingSettings = async () => {
  try {
    const result = await window.pywebview.api.get_fishing_settings()
    if (result && result.success) {
      needRepair.value = result.settings.need_repair || false
      needSubmit.value = result.settings.need_submit || false
      smallToBig.value = result.settings.small_to_big || false
    }
  } catch (error) {
    console.error('获取钓鱼设置失败:', error)
  }
}

// 更新单个设置
const updateSetting = async (key, value) => {
  try {
    const result = await window.pywebview.api.update_fishing_setting(key, value)
    if (result && result.success) {
      // 静默更新，不显示成功提示
    } else {
      ElMessage.error(result?.message || '更新设置失败')
      // 如果更新失败，恢复原值
      await getFishingSettings()
    }
  } catch (error) {
    console.error('更新钓鱼设置失败:', error)
    ElMessage.error('更新设置失败')
    // 如果更新失败，恢复原值
    await getFishingSettings()
  }
}

onMounted(() => {
  getStatus()
  getFishingSettings()
})
</script>

<style scoped>
.fishing-page {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100%;
}



.fishing-settings {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 24px;
  padding: 16px;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
  max-width: 300px;
}

.fishing-settings :deep(.el-checkbox) {
  margin-right: 0;
}

.fishing-settings :deep(.el-checkbox__label) {
  font-size: 14px;
  color: #606266;
}

.start-button {
  font-weight: 500;
  min-width: 120px;
  transition: all 0.5s ease;
}

.start-button.running {
  background-color: #e6a23c;
  border-color: #e6a23c;
  transition: background-color 0.5s ease, border-color 0.5s ease;
}

.start-button.pulse {
  animation: pulse 2s infinite;
  box-shadow: 0 0 0 rgba(64, 158, 255, 0.4);
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(64, 158, 255, 0.7);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(64, 158, 255, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(64, 158, 255, 0);
  }
}
</style> 