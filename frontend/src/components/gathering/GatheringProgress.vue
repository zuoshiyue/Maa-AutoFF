<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue';
import { useGatheringStore } from '../../stores/gathering';
import GatheringDivider from './GatheringDivider.vue';
import { ArrowDown, ArrowRight, Timer } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';

// 使用采集store
const gatheringStore = useGatheringStore();

const format = (percentage) => {
  return percentage === 100 ? '完成' : `${percentage}%`;
};

// 获取任务状态
const getTaskStatus = (percentage) => {
  if (percentage === 100) return 'success';
  if (percentage >= 50) return 'warning';
  return 'exception';
};

// 采集任务数据
const gatheringTasks = ref([]);

// 更新采集任务数据
const updateGatheringTasks = () => {
  if (window.pywebview && window.pywebview.api && window.pywebview.api.get_gathering_progress) {
    window.pywebview.api.get_gathering_progress().then(response => {
      if (response && response.items) {
        // 转换后端数据格式为前端展示格式
        const tasks = [];
        for (const [name, data] of Object.entries(response.items)) {
          const percentage = data.need > 0 ? Math.floor((data.complete / data.need) * 100) : 0;
          tasks.push({
            id: name, // 使用名称作为唯一ID
            name: name,
            total: data.need,
            current: data.complete,
            percentage: percentage,
            startTime: data.start_time ? data.start_time * 1000 : null, // 转换为毫秒
            endTime: data.end_time ? data.end_time * 1000 : null, // 转换为毫秒
            speed: data.num_per_min || 0,
            job: data.job,
            level: data.level
          });
        }
        gatheringTasks.value = tasks;
      }
    }).catch(error => {
      console.error('获取采集进度失败:', error);
    });
  } else {
    // 在开发环境中使用store中的数据生成模拟进度
    const tasks = [];
    gatheringStore.gatheringItems.forEach((item, index) => {
      // 模拟一些随机进度
      const current = Math.floor(Math.random() * item.quantity);
      const percentage = item.quantity > 0 ? Math.floor((current / item.quantity) * 100) : 0;
      tasks.push({
        id: item.id,
        name: item.name,
        total: item.quantity,
        current: current,
        percentage: percentage,
        startTime: current > 0 ? Date.now() - 1000 * 60 * (Math.random() * 30) : null,
        endTime: percentage === 100 ? Date.now() - 1000 * 60 * (Math.random() * 10) : null,
        speed: Math.random() * 2 + 0.5,
        job: item.job,
        level: item.level
      });
    });
    gatheringTasks.value = tasks;
  }
};

// 采集状态控制
const isGathering = ref(false);

// 初始化时获取采集状态
const initGatheringStatus = async () => {
  try {
    if (window.pywebview && window.pywebview.api && window.pywebview.api.get_gathering_status) {
      const status = await window.pywebview.api.get_gathering_status();
      isGathering.value = status.is_gathering;
    }
  } catch (error) {
    console.error('获取采集状态失败:', error);
  }
};

// 定时更新采集进度
let progressInterval = null;

// 在组件挂载后获取状态和设置定时器
onMounted(() => {
  initGatheringStatus();
  updateGatheringTasks();
  
  // 每3秒更新一次采集进度
  progressInterval = setInterval(() => {
    updateGatheringTasks();
  }, 3000);
});

// 在组件卸载前清除定时器
onBeforeUnmount(() => {
  if (progressInterval) {
    clearInterval(progressInterval);
  }
});

// 切换采集状态
const toggleGathering = async () => {
  try {
    if (window.pywebview && window.pywebview.api && window.pywebview.api.toggle_gathering) {
      const result = await window.pywebview.api.toggle_gathering();
      if (result.success) {
        isGathering.value = result.is_gathering;
      } else {
        // 如果失败，显示错误消息
        console.error('切换采集状态失败:', result.message);
        ElMessage.error(result.message);
      }
    }
  } catch (error) {
    console.error('调用采集API失败:', error);
    ElMessage.error('调用采集API失败: ' + error);
  }
};

// 按钮文本
const buttonText = computed(() => {
  return isGathering.value ? '运行中' : '开始采集';
});

// 按钮类型
const buttonType = computed(() => {
  return isGathering.value ? 'warning' : 'primary';
});

// 分类任务
const inProgressTasks = computed(() => {
  return gatheringTasks.value.filter(task => task.current > 0 && task.current < task.total);
});

const notStartedTasks = computed(() => {
  return gatheringTasks.value.filter(task => task.current === 0);
});

const completedTasks = computed(() => {
  return gatheringTasks.value.filter(task => task.current === task.total);
});

// 检查是否有任务
const hasTasks = computed(() => {
  return gatheringTasks.value.length > 0;
});

// 控制各部分的展开/隐藏状态
const inProgressExpanded = ref(true);
const notStartedExpanded = ref(true);
const completedExpanded = ref(true);

// 切换展开/隐藏状态
const toggleSection = (section) => {
  if (section === 'inProgress') {
    inProgressExpanded.value = !inProgressExpanded.value;
  } else if (section === 'notStarted') {
    notStartedExpanded.value = !notStartedExpanded.value;
  } else if (section === 'completed') {
    completedExpanded.value = !completedExpanded.value;
  }
};

// 格式化时间
const formatTime = (minutes) => {
  if (minutes < 60) {
    return `${minutes.toFixed(1)}分钟`;
  } else {
    const hours = Math.floor(minutes / 60);
    const mins = (minutes % 60).toFixed(1);
    return `${hours}小时${mins > 0 ? ` ${mins}分钟` : ''}`;
  }
};

// 计算已用时间
const getElapsedTime = (startTime, endTime = null) => {
  if (!startTime) return '0.0分钟';
  
  const end = endTime || Date.now();
  const elapsedMinutes = (end - startTime) / (1000 * 60);
  return formatTime(elapsedMinutes);
};

// 计算预计剩余时间
const getRemainingTime = (task) => {
  if (!task.startTime || task.current === task.total || task.current === 0) return '0.0分钟';
  
  // 计算平均每个物品需要的时间（分钟）
  const elapsedMinutes = (Date.now() - task.startTime) / (1000 * 60);
  const avgTimePerItem = elapsedMinutes / task.current;
  
  // 剩余物品数量
  const remaining = task.total - task.current;
  
  // 预计剩余时间
  const remainingMinutes = avgTimePerItem * remaining;
  return formatTime(remainingMinutes);
};
</script>

<template>
  <div class="gathering-progress">
    <div class="progress-header">
      <h3><span class="step-number">3</span> 采集进展</h3>
      <el-button 
        :type="buttonType" 
        size="default" 
        @click="toggleGathering"
        class="start-button"
        :class="{'running': isGathering, 'pulse': !isGathering}"
      >
        {{ buttonText }}
      </el-button>
    </div>
    <GatheringDivider />
    
    <div class="progress-list">
      <div v-if="!hasTasks" class="empty-state">
        <el-empty description="暂无采集任务" />
      </div>
      
      <template v-else>
        <!-- 采集中的任务 -->
        <div v-if="inProgressTasks.length > 0" class="task-section">
          <div 
            class="section-header warning-header" 
            @click="toggleSection('inProgress')"
          >
            <div class="section-title">
              <el-tag type="warning" effect="dark" class="status-tag">采集中</el-tag>
              <span class="task-count-badge">{{ inProgressTasks.length }}个物品进行中</span>
            </div>
            <el-icon class="expand-icon">
              <arrow-down v-if="inProgressExpanded" />
              <arrow-right v-else />
            </el-icon>
          </div>
          
          <div v-show="inProgressExpanded" class="task-list">
            <div 
              v-for="task in inProgressTasks" 
              :key="task.id"
              class="task-item in-progress"
            >
              <div class="task-header">
                <span class="task-name">{{ task.name }}</span>
                <span class="task-count">{{ task.current }}/{{ task.total }}</span>
              </div>
              <el-progress 
                :percentage="task.percentage" 
                :format="format"
                status="warning"
                :stroke-width="10"
                class="progress-bar"
              />
              <div class="task-time-info">
                <div class="time-item">
                  <el-icon><Timer /></el-icon>
                  <span>已用时：{{ getElapsedTime(task.startTime) }}</span>
                </div>
                <div class="time-item">
                  <span>预计剩余：{{ getRemainingTime(task) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 未开始的任务 -->
        <div v-if="notStartedTasks.length > 0" class="task-section">
          <div 
            class="section-header danger-header" 
            @click="toggleSection('notStarted')"
          >
            <div class="section-title">
              <el-tag type="danger" effect="dark" class="status-tag">未开始</el-tag>
              <span class="task-count-badge">{{ notStartedTasks.length }}个物品等待中</span>
            </div>
            <el-icon class="expand-icon">
              <arrow-down v-if="notStartedExpanded" />
              <arrow-right v-else />
            </el-icon>
          </div>
          
          <div v-show="notStartedExpanded" class="task-list">
            <div 
              v-for="task in notStartedTasks" 
              :key="task.id"
              class="task-item not-started"
            >
              <div class="task-header">
                <span class="task-name">{{ task.name }}</span>
                <span class="task-count">{{ task.current }}/{{ task.total }}</span>
              </div>
              <el-progress 
                :percentage="task.percentage" 
                :format="format"
                status="exception"
                :stroke-width="10"
                class="progress-bar"
              />
            </div>
          </div>
        </div>
        
        <!-- 已完成的任务 -->
        <div v-if="completedTasks.length > 0" class="task-section">
          <div 
            class="section-header success-header" 
            @click="toggleSection('completed')"
          >
            <div class="section-title">
              <el-tag type="success" effect="dark" class="status-tag">已完成</el-tag>
              <span class="task-count-badge">{{ completedTasks.length }}个物品已完成</span>
            </div>
            <el-icon class="expand-icon">
              <arrow-down v-if="completedExpanded" />
              <arrow-right v-else />
            </el-icon>
          </div>
          
          <div v-show="completedExpanded" class="task-list">
            <div 
              v-for="task in completedTasks" 
              :key="task.id"
              class="task-item completed"
            >
              <div class="task-header">
                <span class="task-name">{{ task.name }}</span>
                <span class="task-count">{{ task.current }}/{{ task.total }}</span>
              </div>
              <el-progress 
                :percentage="task.percentage" 
                :format="format"
                status="success"
                :stroke-width="10"
                class="progress-bar"
              />
              <div class="task-time-info">
                <div class="time-item">
                  <el-icon><Timer /></el-icon>
                  <span>用时：{{ getElapsedTime(task.startTime, task.endTime) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.gathering-progress {
  padding: 12px;
  border-radius: 8px;
  background-color: #f9fafc;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  height: 100%;
  display: flex;
  flex-direction: column;
  
  .progress-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2px;
    
    h3 {
      margin: 0;
      font-size: 18px;
      font-weight: 600;
      color: #303133;
      display: flex;
      align-items: center;
      
      .step-number {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 18px;
        height: 18px;
        background-color: #409EFF;
        color: white;
        border-radius: 50%;
        margin-right: 6px;
        font-size: 12px;
        font-weight: bold;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
      }
    }
    
    .start-button {
      font-weight: 500;
      min-width: 90px;
      transition: all 0.5s ease;
      
      &.running {
        background-color: #e6a23c;
        border-color: #e6a23c;
        transition: background-color 0.5s ease, border-color 0.5s ease;
      }
      
      &.pulse {
        animation: pulse 2s infinite;
        box-shadow: 0 0 0 rgba(64, 158, 255, 0.4);
      }
    }
  }
  
  .progress-list {
    margin-top: 6px;
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow-y: auto;
    
    &::-webkit-scrollbar {
      width: 4px;
    }
    
    &::-webkit-scrollbar-thumb {
      background-color: #dcdfe6;
      border-radius: 4px;
    }
    
    &::-webkit-scrollbar-track {
      background-color: #f5f7fa;
    }
    
    .empty-state {
      padding: 16px 0;
      animation: fadeIn 0.5s ease;
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    
    .task-section {
      margin-bottom: 12px;
      
      &:last-child {
        margin-bottom: 0;
      }
      
      .section-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 12px;
        border-radius: 6px;
        cursor: pointer;
        transition: all 0.3s ease;
        margin-bottom: 8px;
        
        &:hover {
          filter: brightness(1.05);
        }
        
        &.warning-header {
          background-color: rgba(230, 162, 60, 0.15);
          border-left: 4px solid #E6A23C;
        }
        
        &.danger-header {
          background-color: rgba(245, 108, 108, 0.15);
          border-left: 4px solid #F56C6C;
        }
        
        &.success-header {
          background-color: rgba(103, 194, 58, 0.15);
          border-left: 4px solid #67C23A;
        }
        
        .section-title {
          display: flex;
          align-items: center;
          
          .status-tag {
            font-size: 13px;
            padding: 0 10px;
            height: 26px;
            line-height: 26px;
            border-radius: 4px;
            margin-right: 8px;
          }
          
          .task-count-badge {
            font-size: 12px;
            color: #606266;
            background-color: rgba(255, 255, 255, 0.8);
            padding: 2px 8px;
            border-radius: 10px;
          }
        }
        
        .expand-icon {
          font-size: 16px;
          color: #606266;
          transition: transform 0.3s ease;
        }
      }
      
      .task-list {
        transition: all 0.3s ease;
        overflow: hidden;
        padding-left: 16px;
        padding-right: 8px;
        margin-bottom: 3px;
        position: relative;
        
        &::before {
          content: '';
          position: absolute;
          left: 6px;
          top: 0;
          bottom: 0;
          width: 2px;
          background-color: #EBEEF5;
          border-radius: 1px;
        }
      }
      
      .task-item {
        margin-bottom: 8px;
        padding: 10px;
        border-radius: 6px;
        background-color: #fff;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        animation: slideIn 0.5s ease;
        
        &.in-progress {
          border-left: 4px solid #E6A23C;
        }
        
        &.not-started {
          border-left: 4px solid #F56C6C;
        }
        
        &.completed {
          border-left: 4px solid #67C23A;
          animation: completeTask 0.6s ease;
        }
        
        &:last-child {
          margin-bottom: 0;
        }
        
        .task-header {
          display: flex;
          justify-content: space-between;
          margin-bottom: 6px;
          
          .task-name {
            font-weight: 500;
            font-size: 16px;
          }
          
          .task-count {
            color: #606266;
            font-size: 14px;
            font-weight: 500;
            padding: 2px 8px;
            border-radius: 12px;
            background-color: #f0f2f5;
          }
        }
        
        .progress-bar {
          :deep(.el-progress-bar__outer) {
            border-radius: 8px;
          }
          
          :deep(.el-progress-bar__inner) {
            border-radius: 8px;
            transition: width 0.8s cubic-bezier(0.23, 1, 0.32, 1);
          }
        }
        
        .task-time-info {
          display: flex;
          justify-content: space-between;
          margin-top: 8px;
          font-size: 12px;
          color: #909399;
          
          .time-item {
            display: flex;
            align-items: center;
            
            .el-icon {
              margin-right: 4px;
              font-size: 14px;
            }
          }
        }
      }
    }
  }
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes completeTask {
  0% {
    background-color: #f0f9eb;
  }
  50% {
    background-color: #e1f3d8;
  }
  100% {
    background-color: #fff;
  }
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