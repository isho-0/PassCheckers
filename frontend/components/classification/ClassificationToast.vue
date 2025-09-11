<template>
  <Transition name="toast">
    <div v-if="show" class="classification-toast">
      <div class="toast-content">
        <div class="toast-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M9 16.17L4.83 12L3.41 13.41L9 19L21 7L19.59 5.59L9 16.17Z" fill="currentColor"/>
          </svg>
        </div>
        <div class="toast-text">
          <h3>{{ title }}</h3>
          <p>{{ message }}</p>
        </div>
        <button class="close-button" @click="close">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M19 6.41L17.59 5L12 10.59L6.41 5L5 6.41L10.59 12L5 17.59L6.41 19L12 13.41L17.59 19L19 17.59L13.41 12L19 6.41Z" fill="currentColor"/>
          </svg>
        </button>
      </div>
      <div class="toast-actions">
        <button class="action-btn confirm-btn" @click="confirm">
          확인
        </button>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const show = ref(true)

const props = defineProps({
  title: {
    type: String,
    default: '저장 완료'
  },
  message: {
    type: String,
    default: '분석 결과가 성공적으로 저장되었습니다.'
  },
  redirectTo: {
    type: String,
    default: '/'
  }
})

const close = () => {
  show.value = false
}

const confirm = () => {
  show.value = false
  if (props.redirectTo) {
    router.push(props.redirectTo)
  }
}

// 5초 후 자동으로 닫기
onMounted(() => {
  setTimeout(() => {
    close()
  }, 5000)
})
</script>

<style scoped>
.classification-toast {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  z-index: 9999;
  min-width: 320px;
  max-width: 400px;
  border: 1px solid #e0e0e0;
}

.toast-content {
  display: flex;
  align-items: center;
  padding: 16px;
  gap: 12px;
}

.toast-icon {
  width: 40px;
  height: 40px;
  background: #4caf50;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.toast-text {
  flex: 1;
}

.toast-text h3 {
  margin: 0 0 4px 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.toast-text p {
  margin: 0;
  font-size: 14px;
  color: #666;
  line-height: 1.4;
}

.close-button {
  background: none;
  border: none;
  color: #999;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.close-button:hover {
  background-color: #f5f5f5;
}

.toast-actions {
  padding: 0 16px 16px 16px;
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.action-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.confirm-btn {
  background: #2196f3;
  color: white;
}

.confirm-btn:hover {
  background: #1976d2;
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(100%);
}
</style>
