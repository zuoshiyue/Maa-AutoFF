<script setup>
import { useGatheringStore } from '../stores/gathering';
import GatheringSelector from '../components/gathering/GatheringSelector.vue';
import GatheringProgress from '../components/gathering/GatheringProgress.vue';
import GatheringList from '../components/gathering/GatheringList.vue';

// 使用采集store
const gatheringStore = useGatheringStore();

// 处理添加采集品事件
const handleAddItem = (item) => {
  gatheringStore.addItem(item);
};

// 处理删除采集品事件
const handleRemoveItem = (id) => {
  gatheringStore.removeItem(id);
};

// 处理更新采集列表事件（排序或修改数量）
const handleUpdateItems = (updatedItems) => {
  gatheringStore.updateItems(updatedItems);
};
</script>

<template>
  <div class="gathering-container">
    <h2>采集助手</h2>
    <el-divider class="compact-divider" />
    
    <div class="content-area">
      <el-row :gutter="16" class="full-height-row">
        <el-col :xs="24" :sm="24" :md="8" class="left-column">
          <div class="selector-container">
            <GatheringSelector @add-item="handleAddItem" />
          </div>
          <div class="list-container">
            <GatheringList 
              :items="gatheringStore.gatheringItems" 
              @remove-item="handleRemoveItem"
              @update-items="handleUpdateItems"
            />
          </div>
        </el-col>
        
        <el-col :xs="24" :sm="24" :md="16" class="right-column">
          <GatheringProgress />
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.gathering-container {
  padding: 0;
  height: 100%;
  width: 100%;
  overflow: hidden;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  
  h2 {
    margin-top: 0;
    margin-bottom: 4px;
  }

  .compact-divider {
    margin: 0 0 8px 0;
  }
  
  .content-area {
    margin-top: 8px;
    width: 100%;
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }
  
  .full-height-row {
    height: 100%;
    
    .left-column, .right-column {
      height: 100%;
      display: flex;
      flex-direction: column;
    }
    
    .left-column {
      .selector-container {
        flex: none; /* 不伸缩，保持固定大小 */
        height: 200px; /* 固定高度 */
        margin-bottom: 30px; /* 增加与列表之间的间距 */
      }
      
      .list-container {
        flex: 1; /* 占用剩余所有空间 */
        overflow: hidden;
        display: flex;
        flex-direction: column;
      }
    }
    
    .right-column {
      height: 100%;
    }
  }
}

@media screen and (max-width: 768px) {
  .gathering-container {
    padding: 0;
    
    .full-height-row {
      .left-column {
        margin-bottom: 16px;
        
        .selector-container {
          height: auto;
          margin-bottom: 16px;
        }
      }
    }
  }
}
</style> 