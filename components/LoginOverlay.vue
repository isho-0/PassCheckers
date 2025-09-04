<template>
  <Transition name="overlay">
    <div v-if="show" class="login-overlay">
      <div class="loading-container">
        <div class="loading-spinner">
          <div class="spinner"></div>
        </div>
        <p class="loading-text">로그인 중...</p>
      </div>
    </div>
  </Transition>
</template>

<script setup>
const show = ref(false)

const showOverlay = () => {
  show.value = true
}

const hideOverlay = () => {
  show.value = false
}

// 외부에서 사용할 수 있도록 expose
defineExpose({
  showOverlay,
  hideOverlay
})
</script>

<style scoped>
.login-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.loading-container {
  text-align: center;
  color: white;
}

.loading-spinner {
  margin-bottom: 1.5rem;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top: 4px solid #27ae60;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto;
}

.loading-text {
  font-size: 1.1rem;
  font-weight: 500;
  margin: 0;
  color: rgba(255, 255, 255, 0.9);
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 애니메이션 */
.overlay-enter-active,
.overlay-leave-active {
  transition: all 0.3s ease;
}

.overlay-enter-from,
.overlay-leave-to {
  opacity: 0;
}

.overlay-enter-to,
.overlay-leave-from {
  opacity: 1;
}
</style>
