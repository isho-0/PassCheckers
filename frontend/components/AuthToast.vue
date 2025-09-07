<template>
  <Transition name="toast">
    <div v-if="show" class="auth-toast">
      <div class="toast-content">
        <div class="toast-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 1L3 5V11C3 16.55 6.84 21.74 12 23C17.16 21.74 21 16.55 21 11V5L12 1ZM10 17L5 12L6.41 10.59L10 14.17L17.59 6.58L19 8L10 17Z" fill="currentColor"/>
          </svg>
        </div>
        <div class="toast-text">
          <h3>로그인이 필요합니다</h3>
          <p>이 서비스를 이용하려면 로그인해주세요.</p>
        </div>
        <button class="close-button" @click="close">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M19 6.41L17.59 5L12 10.59L6.41 5L5 6.41L10.59 12L5 17.59L6.41 19L12 13.41L17.59 19L19 17.59L13.41 12L19 6.41Z" fill="currentColor"/>
          </svg>
        </button>
      </div>
      <div class="toast-actions">
        <button class="action-btn login-btn" @click="goToLogin">
          로그인
        </button>
        <button class="action-btn signup-btn" @click="goToSignup">
          회원가입
        </button>
      </div>
    </div>
  </Transition>
</template>

<script setup>
const router = useRouter()
const show = ref(true)

const close = () => {
  show.value = false
}

const goToLogin = () => {
  router.push('/login')
}

const goToSignup = () => {
  router.push('/signup')
}

// 5초 후 자동으로 닫기
onMounted(() => {
  setTimeout(() => {
    close()
  }, 5000)
})
</script>

<style scoped>
.auth-toast {
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
  color: #667eea;
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
  gap: 0.75rem;
  justify-content: center;
}

.action-btn {
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
  min-width: 100px;
}

.login-btn {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.login-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.signup-btn {
  background: linear-gradient(135deg, #f093fb, #f5576c);
  color: white;
  box-shadow: 0 4px 15px rgba(240, 147, 251, 0.3);
}

.signup-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(240, 147, 251, 0.4);
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
  .auth-toast {
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
  
  .toast-actions {
    flex-direction: column;
  }
  
  .action-btn {
    width: 100%;
  }
}
</style>
