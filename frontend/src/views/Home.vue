<template>
  <div class="home-page">
    <div class="control-container">
      <TitleCard />
      <LoginCard v-show="false" />
      <EmulatorCard />
    </div>
  </div>
</template>

<script setup>
import TitleCard from '../components/home/TitleCard.vue'
import LoginCard from '../components/home/LoginCard.vue'
import EmulatorCard from '../components/home/EmulatorCard.vue'
</script>

<style lang="scss" scoped>
.home-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  box-sizing: border-box;
  background-color: #f8f9fa;
  overflow: hidden;
  padding: 20px;
  justify-content: center;
}

.control-container {
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 500px;
  margin: 0 auto;
  gap: 15px;
}

@media screen and (max-width: 768px) {
  .home-page {
    padding: 10px;
  }
  
  .control-container {
    padding: 0 10px;
  }
}
</style>