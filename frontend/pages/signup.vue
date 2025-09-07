<template>
  <div class="login-container">
    <h1 class="login-title">회원가입</h1>
    <form class="login-form" @submit.prevent="onRegister">
      <q-input
        v-model="email"
        type="email"
        placeholder="이메일 주소"
        outlined
        dense
        class="login-input opaque-bg"
        :rules="[val => !!val || '이메일 주소를 입력하세요']"
        :error="!!emailError"
        :error-message="emailError"
        :hide-bottom-space="true"
        :hide-hint="true"
        :hide-error-icon="true"
        style="margin-bottom:18px;"
      />
      <q-input
        v-model="password"
        :type="showPassword ? 'text' : 'password'"
        placeholder="비밀번호"
        outlined
        dense
        class="login-input opaque-bg"
        :rules="[val => !!val || '비밀번호를 입력하세요']"
        :error="!!passwordError"
        :error-message="passwordError"
        :hide-bottom-space="true"
        :hide-hint="true"
        :hide-error-icon="true"
        style="margin-bottom:18px;"
      >
        <template #append>
          <q-icon
            :name="showPassword ? 'visibility_off' : 'visibility'"
            class="cursor-pointer eye-icon"
            @click="showPassword = !showPassword"
            color="grey-6"
          />
        </template>
      </q-input>
      <q-input
        v-model="name"
        type="text"
        placeholder="성명"
        outlined
        dense
        class="login-input opaque-bg"
        :rules="[val => !!val || '성명을 입력하세요']"
        :error="!!nameError"
        :error-message="nameError"
        :hide-bottom-space="true"
        :hide-hint="true"
        :hide-error-icon="true"
        style="margin-bottom:18px;"
      />
      <q-input
        v-model="nickname"
        type="text"
        placeholder="닉네임"
        outlined
        dense
        class="login-input opaque-bg"
        :rules="[val => !!val || '닉네임을 입력하세요']"
        :error="!!nicknameError"
        :error-message="nicknameError"
        :hide-bottom-space="true"
        :hide-hint="true"
        :hide-error-icon="true"
        style="margin-bottom:8px;"
      />
      <q-btn
        label="회원가입"
        color="primary"
        unelevated
        class="signup-btn rounded-btn custom-signup-btn"
        no-caps
        type="submit"
        style="width:100%; height:52px; font-size:1.15rem; margin:18px 0 8px 0;"
      />
      <div v-if="message && !showSuccessModal" class="signup-message">{{ message }}</div>
    </form>
    <div v-if="showSuccessModal" class="signup-modal-overlay">
      <div class="signup-modal-card animate-fadein">
        <div class="signup-modal-icon">🎉</div>
        <h2 class="signup-modal-title">회원 가입을 축하합니다!</h2>
        <p class="signup-modal-message">
          <i>{{ nickname }}</i> 님,<br>
          <span class="brand">Passcheckers</span>를 마음껏 이용해보세요!
          <span class="emoji">😆</span>
        </p>
        <button class="signup-modal-btn" @click="goToLogin">Get Started</button>
      </div>
    </div>
  </div>
</template> 

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const email = ref('')
const password = ref('')
const name = ref('')
const nickname = ref('')
const showPassword = ref(false)
const emailError = ref('')
const passwordError = ref('')
const nameError = ref('')
const nicknameError = ref('')
const message = ref('')
const showSuccessModal = ref(false)
const router = useRouter()

const validate = () => {
  emailError.value = !email.value ? '이메일 주소를 입력하세요' : ''
  passwordError.value = !password.value ? '비밀번호를 입력하세요' : ''
  nameError.value = !name.value ? '성명을 입력하세요' : ''
  nicknameError.value = !nickname.value ? '닉네임을 입력하세요' : ''
  return !(emailError.value || passwordError.value || nameError.value || nicknameError.value)
}

const onRegister = async () => {
  if (!validate()) return
  try {
    const res = await $fetch('http://' + window.location.hostname + ':5001/api/register', {
      method: 'POST',
      body: {
        email: email.value,
        password: password.value,
        name: name.value,
        nickname: nickname.value
      }
    })
    showSuccessModal.value = true
  } catch (err) {
    message.value = err.data?.error || '회원가입 실패'
  }
}

const goToLogin = () => {
  router.push('/login')
}
</script>

<style scoped>
.login-container {
  max-width: 420px;
  margin: 0 auto;
  padding: 48px 0 0 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-height: 0 !important;
  height: auto !important;
  max-height: none !important;
}
.login-title {
  font-size: 2.5rem;
  font-weight: bold;
  text-align: center;
  margin-bottom: 36px;
}
.login-form {
  width: 100%;
  display: flex;
  flex-direction: column;
}
.login-input {
  width: 100%;
}
.opaque-bg .q-field__control, .opaque-bg .q-field__native {
  background: #fff !important;
  opacity: 1 !important;
}
.eye-icon {
  font-size: 22px;
}
.rounded-btn {
  border-radius: 16px !important;
}
.signup-message {
  margin-top: 18px;
  color: #d32f2f;
  font-size: 15px;
  text-align: center;
}
/* 회원가입 버튼: 기본 파란 배경, hover 시 밝기만 올림 */
.signup-btn,
.custom-signup-btn {
  background: #2196f3 !important;
  color: #fff !important;
  border: none !important;
  box-shadow: none !important;
  margin-top: 12px;
  font-weight: bold;
  transition: filter 0.18s, box-shadow 0.18s;
}
.signup-btn:hover,
.custom-signup-btn:hover {
  background: #2196f3 !important;
  color: #fff !important;
  filter: brightness(1.07);
  box-shadow: 0 4px 18px 0 rgba(33,150,243,0.22) !important;
}
/* 슬라이드 효과 완전 제거 */
.custom-signup-btn::after {
  display: none !important;
}

/* --- 세련된 회원가입 성공 모달 --- */
.signup-modal-overlay {
  position: fixed; z-index: 2000; left: 0; top: 0; width: 100vw; height: 100vh;
  background: rgba(0,0,0,0.28); display: flex; align-items: center; justify-content: center;
  animation: fadein-bg 0.4s;
}
@keyframes fadein-bg {
  from { background: rgba(0,0,0,0); }
  to   { background: rgba(0,0,0,0.28); }
}
.signup-modal-card {
  background: linear-gradient(135deg, #fafdff 60%, #e3f0ff 100%);
  border-radius: 22px;
  box-shadow: 0 8px 32px rgba(33,150,243,0.13), 0 1.5px 8px rgba(0,0,0,0.07);
  padding: 48px 36px 36px 36px;
  min-width: 340px;
  text-align: center;
  position: relative;
}
.animate-fadein {
  animation: fadein-card 0.5s cubic-bezier(.4,1.4,.6,1) both;
}
@keyframes fadein-card {
  from { opacity: 0; transform: translateY(30px) scale(0.98);}
  to   { opacity: 1; transform: none;}
}
.signup-modal-icon {
  font-size: 2.6rem;
  margin-bottom: 10px;
  animation: pop 0.7s cubic-bezier(.4,1.4,.6,1);
}
@keyframes pop {
  0% { transform: scale(0.7);}
  60% { transform: scale(1.15);}
  100% { transform: scale(1);}
}
.signup-modal-title {
  font-size: 2.1rem;
  font-weight: 800;
  margin-bottom: 16px;
  color: #222;
  letter-spacing: -1px;
}
.signup-modal-message {
  font-size: 1.15rem;
  margin-bottom: 30px;
  color: #444;
  line-height: 1.7;
}
.signup-modal-message i {
  font-style: italic;
  font-weight: 500;
  color: #1976d2;
}
.signup-modal-message .brand {
  font-weight: 700;
  color: #2196f3;
  letter-spacing: 0.5px;
}
.signup-modal-btn {
  background: #2196f3;
  color: #fff;
  font-size: 1.22rem;
  font-weight: 600;
  border: none;
  border-radius: 12px;
  padding: 13px 40px;
  cursor: pointer;
  box-shadow: none;
  transition: background 0.18s, transform 0.13s;
}
.signup-modal-btn:hover,
.signup-modal-btn:active {
  background: #2196f3;
  filter: brightness(1.07);
  transform: translateY(-2px) scale(1.03);
}
.emoji {
  margin-left: 4px;
}
</style> 