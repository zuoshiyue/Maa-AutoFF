<script setup>
import { useCounterStore } from './stores/counter'
import Sidebar from './components/app/Sidebar.vue'
import TipsHandler from './components/logs/TipsHandler.vue'

const counter = useCounterStore()
</script>

<template>
  <div class="app-container">
    <!-- 提示信息处理组件 -->
    <TipsHandler />
    
    <el-container class="main-container">
      <!-- 侧边栏组件 -->
      <Sidebar />
      
      <!-- 主内容区 -->
      <el-container class="right-container">
        <el-main>
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<style lang="scss">
/* 全局样式已在main.js中导入 */
</style>