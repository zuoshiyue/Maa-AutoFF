<template>
  <div class="control-section">
    <div class="fresh-card">
      <h2 class="card-title">卡密登录</h2>
      <div class="card-content">
        <div class="login-controls">
          <el-input 
            v-model="cardKey" 
            placeholder="请输入卡密" 
            size="small"
            class="card-key-input"
          />
          <el-button 
            :type="isLoggedIn ? 'success' : 'primary'" 
            size="small" 
            @click="handleLogin"
            class="login-button no-outline"
            :disabled="loginButtonDisabled || isLoggedIn"
          >
            {{ isLoggedIn ? '已登录' : (loginButtonDisabled ? '登录中...' : '登录') }}
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const cardKey = ref('')
const loginButtonDisabled = ref(false)
const isLoggedIn = ref(false)

// 登录处理方法（仅占位，不实现功能）
const handleLogin = () => {
  // 仅样式展示，不实现功能
}
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

.login-controls {
  display: flex;
  align-items: center;
  gap: 10px;
}

.card-key-input {
  flex-grow: 1;
  opacity: 0;
  animation: fade-in 0.3s ease-out forwards;
  animation-delay: 0.3s;
}

.login-button {
  flex-shrink: 0;
  opacity: 0;
  animation: fade-in 0.3s ease-out forwards;
  animation-delay: 0.3s;
}

.no-outline {
  &:focus,
  &:focus-visible {
    outline: none !important;
    box-shadow: none !important;
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