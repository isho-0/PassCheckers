<template>
  <Transition name="toast">
    <div v-if="show" class="logout-toast">
      <div class="toast-content">
        <div class="toast-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M9 16.17L4.83 12L3.41 13.41L9 19L21 7L19.59 5.59L9 16.17Z" fill="currentColor"/>
          </svg>
        </div>
        <div class="toast-text">
          <h3>로그아웃 완료</h3>
          <p>안전하게 로그아웃되었습니다.</p>
        </div>
        <button class="close-button" @click="close">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M19 6.41L17.59 5L12 10.59L6.41 5L5 6.41L10.59 12L5 17.59L6.41 19L12 13.41L17.59 19L19 17.59L13.41 12L19 6.41Z" fill="currentColor"/>
          </svg>
        </button>
      </div>
      <div class="toast-actions">
        <button class="action-btn confirm-btn" @click="close">
          확인
        </button>
      </div>
    </div>
  </Transition>
</template>

<script setup>
const show = ref(false)

const showToast = () => {
  show.value = true
}

const close = () => {
  show.value = false
}

// 외부에서 사용할 수 있도록 expose
defineExpose({
  showToast,
  close
})
</script>

<style scoped>
.logout-toast {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.2);
  max-width: 400px;
  width: 90%;
  z-index: 1000;
  text-align: center;
}

.toast-content {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.toast-icon {
  color: #27ae60;
  flex-shrink: 0;
}

.toast-text {
  flex: 1;
  text-align: left;
}

.toast-text h3 {
  margin: 0 0 0.5rem 0;
  font-size: 1.2rem;
  font-weight: 600;
  color: #2c3e50;
}

.toast-text p {
  margin: 0;
  font-size: 0.9rem;
  color: #7f8c8d;
}

.close-button {
  background: none;
  border: none;
  color: #bdc3c7;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 4px;
  transition: color 0.2s ease;
}

.close-button:hover {
  color: #7f8c8d;
}

.toast-actions {
  display: flex;
  justify-content: center;
}

.action-btn {
  padding: 0.75rem 2rem;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
  min-width: 100px;
}

.confirm-btn {
  background: linear-gradient(135deg, #27ae60, #2ecc71);
  color: white;
  box-shadow: 0 4px 15px rgba(39, 174, 96, 0.3);
}

.confirm-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(39, 174, 96, 0.4);
}

/* 애니메이션 */
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translate(-50%, -50%) scale(0.9);
}

.toast-leave-to {
  opacity: 0;
  transform: translate(-50%, -50%) scale(0.9);
}

@media (max-width: 480px) {
  .logout-toast {
    padding: 1.5rem;
    margin: 1rem;
  }
  
  .toast-content {
    flex-direction: column;
    text-align: center;
    gap: 0.75rem;
  }
  
  .toast-text {
    text-align: center;
  }
  
  .action-btn {
    width: 100%;
  }
}
</style>
