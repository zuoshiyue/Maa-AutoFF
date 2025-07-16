<script setup>
import { ref, computed } from 'vue'
import { Collection, Box, House, Setting, Document, DataLine, Menu } from '@element-plus/icons-vue'
import { useRouter, useRoute } from 'vue-router'

const isCollapse = ref(true)
const router = useRouter()
const route = useRoute()

// 处理鼠标移入移出侧边栏的事件
const handleMouseEnter = () => {
  isCollapse.value = false
}

const handleMouseLeave = () => {
  isCollapse.value = true
}

// 当前活动路由
const activeRoute = computed(() => route.path)

// 导航到指定路由
const navigateTo = (path) => {
  router.push(path)
}
</script>

<template>
  <div 
    class="sidebar"
    :class="{ 'is-collapsed': isCollapse }"
    :style="{ width: isCollapse ? '64px' : '200px' }"
    @mouseenter="handleMouseEnter"
    @mouseleave="handleMouseLeave"
  >
    <div class="sidebar-menu">
      <div 
        class="menu-item" 
        :class="{ 'is-active': activeRoute === '/' }"
        @click="navigateTo('/')"
      >
        <el-icon><House /></el-icon>
        <span class="menu-text">主页</span>
      </div>
      <div 
        class="menu-item" 
        :class="{ 'is-active': activeRoute === '/gathering' }"
        @click="navigateTo('/gathering')"
      >
        <el-icon><Collection /></el-icon>
        <span class="menu-text">采集</span>
      </div>
      <div 
        class="menu-item" 
        :class="{ 'is-active': activeRoute === '/crafting' }"
        @click="navigateTo('/crafting')"
      >
        <el-icon><Box /></el-icon>
        <span class="menu-text">生产</span>
      </div>
      <div 
        class="menu-item" 
        :class="{ 'is-active': activeRoute === '/fishing' }"
        @click="navigateTo('/fishing')"
      >
        <el-icon><DataLine /></el-icon>
        <span class="menu-text">钓鱼</span>
      </div>
      <div 
        class="menu-item" 
        :class="{ 'is-active': activeRoute === '/goldsaucer' }"
        @click="navigateTo('/goldsaucer')"
      >
        <el-icon><Menu /></el-icon>
        <span class="menu-text">金碟</span>
      </div>
      <div 
        class="menu-item" 
        :class="{ 'is-active': activeRoute === '/logs' }"
        @click="navigateTo('/logs')"
      >
        <el-icon><Document /></el-icon>
        <span class="menu-text">日志</span>
      </div>
      <div 
        class="menu-item" 
        :class="{ 'is-active': activeRoute === '/settings' }"
        @click="navigateTo('/settings')"
      >
        <el-icon><Setting /></el-icon>
        <span class="menu-text">设置</span>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.sidebar {
  background-color: #f0f2f5;
  transition: width 0.3s ease-in-out;
  height: 100%;
  overflow-y: auto !important;
  overflow-x: hidden !important;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  
  .sidebar-menu {
    padding: 10px 0;
    
    .menu-item {
      height: 56px;
      line-height: 56px;
      padding: 0 20px;
      cursor: pointer;
      position: relative;
      transition: background-color 0.3s;
      color: #303133;
      display: flex;
      align-items: center;
      
      &:hover {
        background-color: rgba(64, 158, 255, 0.1);
      }
      
      &.is-active {
        color: #409EFF;
        background-color: rgba(64, 158, 255, 0.2);
      }
      
      .el-icon {
        font-size: 18px;
        width: 24px;
        text-align: center;
        position: absolute;
        left: 20px;
      }
      
      .menu-text {
        display: inline-block;
        opacity: 1;
        max-width: 140px;
        white-space: nowrap;
        overflow: hidden;
        transition: opacity 0.3s ease-in-out, max-width 0.3s ease-in-out;
        position: absolute;
        left: 50px;
      }
    }
  }
  
  &.is-collapsed {
    .sidebar-menu {
      .menu-item {
        .el-icon {
          position: absolute;
          left: 20px;
        }
        
        .menu-text {
          max-width: 0;
          opacity: 0;
        }
      }
    }
  }
}

@media screen and (max-width: 768px) {
  .sidebar {
    position: fixed;
    z-index: 1000;
    height: 100%;
  }
}
</style> 