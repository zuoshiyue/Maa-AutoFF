<template>
  <div class="settings-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>系统设置</h2>
        </div>
      </template>
      <SettingsForm />
    </el-card>
  </div>
</template>

<script setup>
import SettingsForm from '../components/settings/SettingsForm.vue'
</script>

<style lang="scss" scoped>
.settings-page {
  padding: 16px;
  
  .card-header {
    display: flex;
    justify-content: center;
    align-items: center;
    
    h2 {
      margin: 0;
      color: #409EFF;
    }
  }
}
</style> 