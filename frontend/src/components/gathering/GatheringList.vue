<script setup>
import { ref, toRefs, computed, watch, onMounted, nextTick } from 'vue';
import GatheringDivider from './GatheringDivider.vue';
import { Upload, Download, Delete } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';
import { Rank, Sort } from '@element-plus/icons-vue';
import Sortable from 'sortablejs';

// 接收props
const props = defineProps({
  items: {
    type: Array,
    default: () => []
  }
});

// 本地数据，用于拖拽排序
const localItems = ref([]);

// 监听props变化，更新本地数据
const updateLocalItems = () => {
  localItems.value = JSON.parse(JSON.stringify(props.items));
};

// 初始化本地数据
updateLocalItems();

// 监听props变化
watch(() => props.items, () => {
  updateLocalItems();
}, { deep: true });

// 定义事件
const emit = defineEmits(['remove-item', 'update-items']);

const removeItem = (id) => {
  emit('remove-item', id);
};

// 拖拽相关
const listElement = ref(null); // 为列表元素创建ref
let sortable = null;

// 在组件挂载后初始化Sortable
const initSortable = () => {
  // The ref 'listElement' is on the <transition-group> component.
  // We need to pass the actual DOM element to Sortable.js.
  // The component instance is in listElement.value, and its root DOM node is .$el.
  if (listElement.value && listElement.value.$el) {
    sortable = Sortable.create(listElement.value.$el, {
      handle: '.drag-handle',
      animation: 150,
      ghostClass: 'ghost-item',
      onEnd: handleDragEnd,
      delay: 50 // 添加一点延迟，防止误触
    });
  }
};

// 组件挂载后初始化Sortable
onMounted(() => {
  nextTick(() => {
    initSortable();
  });
});

// 当列表项变化时，重新初始化Sortable
watch(() => localItems.value.length, () => {
  nextTick(() => {
    if (sortable) {
      sortable.destroy();
    }
    initSortable();
  });
});

// 处理拖拽结束事件
const handleDragEnd = (evt) => {
  // 获取新的顺序
  const newItems = [...localItems.value];
  const { oldIndex, newIndex } = evt;
  
  // 如果位置发生变化
  if (oldIndex !== newIndex) {
    // 移动元素
    const movedItem = newItems.splice(oldIndex, 1)[0];
    newItems.splice(newIndex, 0, movedItem);
    
    // 更新本地数据并发出事件
    localItems.value = newItems;
    emit('update-items', newItems);
  }
};

// 编辑数量相关变量
const editingItem = ref(null);
const editingQuantity = ref(1);

// 开始编辑数量
const startEditing = (item) => {
  editingItem.value = item;
  editingQuantity.value = item.quantity;
};

// 保存编辑后的数量
const saveQuantity = () => {
  if (!editingItem.value) return;
  
  // 验证输入是否为有效数字
  const quantity = parseInt(editingQuantity.value);
  if (isNaN(quantity) || quantity <= 0) {
    ElMessage.error('请输入有效的数量');
    editingQuantity.value = editingItem.value.quantity;
    return;
  }
  
  // 更新数量
  const updatedItems = localItems.value.map(item => {
    if (item.id === editingItem.value.id) {
      return { ...item, quantity };
    }
    return item;
  });
  
  localItems.value = updatedItems;
  emit('update-items', updatedItems);
  editingItem.value = null;
};

// 取消编辑
const cancelEditing = () => {
  editingItem.value = null;
};

// 监听键盘事件
const handleKeyDown = (e) => {
  if (e.key === 'Enter') {
    saveQuantity();
  } else if (e.key === 'Escape') {
    cancelEditing();
  }
};
</script>

<template>
  <div class="gathering-list">
    <div class="list-header">
      <h3><span class="step-number">2</span> 采集列表</h3>
      <div class="list-actions">
        <el-tooltip content="导入列表数据" placement="top">
          <el-button type="success" size="small" class="action-btn import-btn">
            <el-icon><Download /></el-icon>
            <span>导入</span>
          </el-button>
        </el-tooltip>
        <el-tooltip content="导出列表数据" placement="top">
          <el-button type="primary" size="small" class="action-btn export-btn">
            <el-icon><Upload /></el-icon>
            <span>导出</span>
          </el-button>
        </el-tooltip>
      </div>
    </div>
    <GatheringDivider />
    
    <div class="list-content">
      <div v-if="localItems.length === 0" class="empty-state">
        <el-empty description="暂无采集物品" />
      </div>
      
      <div class="drag-tip" v-if="localItems.length > 0">
        <el-icon><Sort /></el-icon> 拖动排序 | 双击数量编辑
      </div>
      
      <div class="items-container">
        <transition-group ref="listElement" name="list" tag="div" class="transition-list">
          <div 
            v-for="element in localItems" 
            :key="element.id"
            class="list-item"
          >
            <div class="drag-handle">
              <el-icon><Rank /></el-icon>
            </div>
            <div class="item-info">
              <div class="item-main-info">
                <span class="item-name">{{ element.name }}</span>
                <div class="item-tags">
                  <el-tag size="small" :type="element.job === '采矿工' ? 'danger' : 'success'" class="job-tag">
                    {{ element.job }}
                  </el-tag>
                  <el-tag size="small" type="info" class="level-tag">
                    Lv.{{ element.level }}
                  </el-tag>
                </div>
              </div>
              <span 
                class="item-quantity" 
                @dblclick="startEditing(element)"
              >
                <template v-if="editingItem && editingItem.id === element.id">
                  <el-input
                    v-model="editingQuantity"
                    size="small"
                    type="number"
                    min="1"
                    @keydown="handleKeyDown"
                    @blur="saveQuantity"
                    v-focus
                  />
                </template>
                <template v-else>
                  × {{ element.quantity }}
                </template>
              </span>
            </div>
            <el-button 
              type="danger" 
              size="small" 
              circle
              @click="removeItem(element.id)"
              class="remove-btn"
            >
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
        </transition-group>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.gathering-list {
  padding: 12px;
  border-radius: 8px;
  background-color: #f9fafc;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  height: 100%;
  display: flex;
  flex-direction: column;
  
  .list-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    
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
    
    .list-actions {
      display: flex;
      gap: 8px;
      
      .action-btn {
        border-radius: 4px;
        padding: 4px 10px;
        height: 28px;
        transition: all 0.3s;
        display: flex;
        align-items: center;
        gap: 4px;
        font-size: 12px;
        
        &:hover {
          transform: translateY(-2px);
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
        }
        
        .el-icon {
          font-size: 12px;
        }
        
        span {
          margin-left: 2px;
        }
      }
      
      .import-btn {
        background-color: #67C23A;
        border-color: #67C23A;
        
        &:hover {
          background-color: #85ce61;
          border-color: #85ce61;
        }
      }
      
      .export-btn {
        background-color: #409EFF;
        border-color: #409EFF;
        
        &:hover {
          background-color: #66b1ff;
          border-color: #66b1ff;
        }
      }
    }
  }
  
  .list-content {
    margin-top: 6px;
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden; /* 防止滚动条出现 */
    
    .empty-state {
      padding: 16px 0;
      animation: fadeIn 0.5s ease;
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    
    .drag-tip {
      font-size: 12px;
      color: #909399;
      text-align: center;
      margin-bottom: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 4px;
    }
    
    .items-container {
      flex: 1;
      overflow-y: auto;
      overflow-x: hidden;
      
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
      
      .transition-list {
        position: relative;
        width: 100%;
      }
    }
    
    .list-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 8px 12px;
      margin-bottom: 8px;
      background-color: #fff;
      border-radius: 6px;
      cursor: default;
      
      .drag-handle {
        cursor: grab;
        padding: 0 8px;
        color: #909399;
        
        &:active {
          cursor: grabbing;
        }
      }
      
      .item-info {
        flex: 1;
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0 10px;
        overflow: hidden;
        
        .item-main-info {
          display: flex;
          flex-direction: row;
          align-items: center;
          gap: 8px;
          overflow: hidden;
          
          .item-name {
            font-weight: 500;
            color: #303133;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            font-size: 13px;
          }
          
          .item-tags {
            display: flex;
            gap: 4px;
            flex-shrink: 0;
            
            .job-tag, .level-tag {
              font-size: 10px;
              padding: 0 4px;
              height: 18px;
              line-height: 16px;
            }
          }
        }
        
        .item-quantity {
          font-weight: 500;
          color: #606266;
          cursor: pointer;
          padding: 2px 6px;
          border-radius: 4px;
          transition: background-color 0.2s;
          
          &:hover {
            background-color: #ecf5ff;
          }
        }
      }
      
      .remove-btn {
        opacity: 0.8;
      }
    }
  }
}

.ghost-item {
  opacity: 0 !important;
  background: transparent !important;
}

/* 列表项动画 */
.list-enter-active {
  animation: fadeIn 0.3s;
}

.list-leave-active {
  position: absolute;
  width: calc(100% - 24px);
  left: 0;
  right: 0;
  animation: fadeOut 0.3s;
  z-index: -1;
}

.list-move {
  transition: transform 0.3s;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeOut {
  from {
    opacity: 1;
    transform: translateY(0);
  }
  to {
    opacity: 0;
    transform: translateY(20px);
  }
}
</style>

<script>
// 自定义指令：自动聚焦
export default {
  directives: {
    focus: {
      mounted(el) {
        el.querySelector('input').focus();
      }
    }
  }
}
</script> 