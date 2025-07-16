import { ref, watch } from 'vue'
import { defineStore } from 'pinia'
import { ElMessage } from 'element-plus'

export const useGatheringStore = defineStore('gathering', () => {
  // 采集列表数据
  const gatheringItems = ref([])

  // 添加采集品
  function addItem(item) {
    // 检查是否已存在相同物品
    const existingItem = gatheringItems.value.find(i => i.name === item.name)
    
    if (existingItem) {
      // 如果已存在，增加数量
      existingItem.quantity += item.quantity
    } else {
      // 如果不存在，添加新物品，包含职业和等级信息
      gatheringItems.value.push({
        id: item.id,
        name: item.name,
        job: item.job,
        level: item.level,
        quantity: item.quantity
      })
    }
  }

  // 删除采集品
  function removeItem(id) {
    const index = gatheringItems.value.findIndex(item => item.id === id)
    if (index !== -1) {
      gatheringItems.value.splice(index, 1)
    }
  }

  // 更新采集列表（排序或修改数量）
  function updateItems(updatedItems) {
    gatheringItems.value = updatedItems
  }

  // 监听采集列表的变化，并通知后端
  watch(gatheringItems, (newItems) => {
    const formattedItems = {}
    newItems.forEach(item => {
      formattedItems[item.name] = {
        'need': item.quantity,
        'complete': 0, // 初始完成数量为0
        'num_per_min': 0, // 按要求设置为0
        'job': item.job, // 添加职业信息
        'level': item.level // 添加等级信息
      }
    })

    if (window.pywebview && window.pywebview.api && window.pywebview.api.update_gathering_items) {
      window.pywebview.api.update_gathering_items(formattedItems)
        .then(response => {
          if (!response.success) {
            console.error("更新采集列表失败:", response.message);
            ElMessage.error(response.message);
          }
        })
        .catch(error => {
          console.error("更新采集列表出错:", error);
          ElMessage.error("更新采集列表出错: " + error);
        });
    } else {
      // 在非 pywebview 环境下（例如浏览器开发时）打印日志
      console.log("Pywebview API not found, not sending to backend.", formattedItems)
    }
  }, { deep: true })

  return { 
    gatheringItems, 
    addItem, 
    removeItem, 
    updateItems 
  }
}) 