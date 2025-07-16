<script setup>
import { ref, onMounted } from 'vue';
import GatheringDivider from './GatheringDivider.vue';
import { ElMessage } from 'element-plus';

const selectedItem = ref('');
const quantity = ref(1);

// 采集品列表
const gatheringItems = ref([]);
const loading = ref(false);

// 从后端获取采集品列表
const fetchGatheringItems = async () => {
  loading.value = true;
  try {
    // 检查pywebview API是否可用
    if (window.pywebview && window.pywebview.api) {
      const data = await window.pywebview.api.get_gathering_items();
      
      if (data.success) {
        gatheringItems.value = data.items;
        // 初始化筛选列表
        filteredItems.value = [...gatheringItems.value];
      } else {
        console.error('获取采集物品列表失败:', data.message);
        ElMessage.error(data.message);
      }
    } else {
      console.error('pywebview API 不可用');
      // 使用一些默认数据作为备用
      gatheringItems.value = [
        { value: '铜矿', label: '铜矿', job: '采矿工', level: 1 },
        { value: '棉花', label: '棉花', job: '园艺工', level: 5 },
        { value: '槲寄生', label: '槲寄生', job: '园艺工', level: 10 },
        { value: '铁矿', label: '铁矿', job: '采矿工', level: 14 },
      ];
      filteredItems.value = [...gatheringItems.value];
    }
  } catch (error) {
    console.error('请求采集物品列表出错:', error);
    ElMessage.error('请求采集物品列表出错: ' + error);
  } finally {
    loading.value = false;
  }
};

// 组件挂载时获取数据
onMounted(() => {
  fetchGatheringItems();
});

// 定义事件
const emit = defineEmits(['add-item']);

const addItem = () => {
  if (!selectedItem.value) {
    // 可以添加提示，如使用Element Plus的消息提示
    ElMessage.warning('请先选择采集品');
    return;
  }
  
  // 查找选中的物品信息
  const item = gatheringItems.value.find(item => item.value === selectedItem.value);
  
  if (item) {
    // 发射事件，传递物品信息
    emit('add-item', {
      id: Date.now(), // 使用时间戳作为临时ID
      name: item.label,
      job: item.job,
      level: item.level,
      quantity: quantity.value
    });
    
    // 重置表单
    selectedItem.value = '';
    quantity.value = 1;
  }
};

// 搜索关键字
const searchQuery = ref('');
// 筛选后的物品列表
const filteredItems = ref([]);

// 处理搜索输入变化
const handleSearchChange = (query) => {
  searchQuery.value = query;
  if (query === '') {
    filteredItems.value = [...gatheringItems.value];
  } else {
    filteredItems.value = gatheringItems.value.filter(item => 
      item.label.toLowerCase().includes(query.toLowerCase()) ||
      item.job.toLowerCase().includes(query.toLowerCase()) ||
      item.level.toString().includes(query)
    );
  }
};
</script>

<template>
  <div class="gathering-selector">
    <h3><span class="step-number">1</span> 选择采集品</h3>
    <GatheringDivider />
    
    <div class="selector-content">
      <el-select 
        v-model="selectedItem" 
        placeholder="请选择采集品" 
        class="item-select"
        filterable
        remote
        :remote-method="handleSearchChange"
        :popper-append-to-body="false"
        :loading="loading"
      >
        <el-option 
          v-for="item in filteredItems" 
          :key="item.value" 
          :label="`${item.label} - ${item.job} Lv.${item.level}`"
          :value="item.value"
        />
      </el-select>
      
      <div class="quantity-container">
        <span class="quantity-label">采集节点次数</span>
        <el-input-number 
          v-model="quantity" 
          :min="1" 
          :max="999" 
          class="quantity-input" 
          placeholder="数量"
          controls-position="right"
        />
      </div>
      
      <el-button 
        type="primary" 
        @click="addItem" 
        class="add-button"
      >
        添加
      </el-button>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.gathering-selector {
  padding: 12px;
  border-radius: 8px;
  background-color: #f9fafc;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  height: 100%;
  display: flex;
  flex-direction: column;
  
  h3 {
    margin-top: 0;
    margin-bottom: 2px;
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
  
  .selector-content {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-top: 6px;
    flex: 1;
    justify-content: space-around;
    
    .item-select {
      width: 100%;
    }
    
    .quantity-container {
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .quantity-label {
      font-size: 14px;
      color: #606266;
      white-space: nowrap;
    }

    .quantity-input {
      flex: 1;
    }
    
    .add-button {
      width: 100%;
    }
  }
}
</style> 