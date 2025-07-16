<template>
  <div class="control-section">
    <div class="fresh-card title-card">
      <h1 class="title">AutoFF</h1>
    </div>
  </div>
</template>

<script setup>
// 标题卡片组件
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
  
  &.title-card {
    padding: 24px 16px;
    text-align: center;
    opacity: 0;
    animation: scale-in 0.5s ease-out forwards;
  }
}

.title {
  font-size: 2.5rem;
  color: #409EFF;
  margin: 0;
  font-weight: bold;
  letter-spacing: 2px;
}

@keyframes scale-in {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

@media screen and (max-width: 768px) {
  .title {
    font-size: 2rem;
  }
}
</style> 