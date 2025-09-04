<template>
  <div class="login-container">
    <h1 class="login-title">로그인</h1>
    <form class="login-form" @submit.prevent="onLogin">
      <q-input
        v-model="userId"
        type="text"
        placeholder="아이디"
        outlined
        dense
        class="login-input opaque-bg"
        :rules="[val => !!val || '아이디를 입력하세요']"
        :error="!!userIdError"
        :error-message="userIdError"
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
        style="margin-bottom:8px;"
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
      <div class="login-links">
        <a href="#" class="find-password">비밀번호 찾기</a>
      </div>
      <div v-if="message" class="login-message">{{ message }}</div>
      <q-btn
        label="로그인"
        color="primary"
        unelevated
        class="login-btn rounded-btn custom-login-btn"
        no-caps
        type="submit"
        style="width:100%; height:52px; font-size:1.15rem; margin:18px 0 8px 0;"
      />
      <div class="auto-login-row">
        <q-checkbox v-model="autoLogin" label="자동 로그인" class="auto-login round-checkbox" color="primary" />
      </div>
    </form>
    <div class="login-divider">
      <span class="line"></span>
      <span class="divider-text">또는</span>
      <span class="line"></span>
    </div>
    <div class="social-login-group">
      <q-btn outline color="white" text-color="black" class="social-btn google rounded-btn social-icon-btn custom-social-btn" no-caps style="margin-bottom:12px;" @click="onGoogleLogin">
        <div style="display: flex; align-items: center;">
          <img src="/images/icon_google.png" alt="Google" class="social-icon" />
          <span>Google 계정으로 로그인</span>
        </div>
      </q-btn>
      <q-btn outline color="white" text-color="black" class="social-btn kakao rounded-btn social-icon-btn custom-social-btn" no-caps @click="onKakaoLogin">
        <div style="display: flex; align-items: center;">
          <img src="/images/icon_kakao.png" alt="Kakao" class="social-icon" />
          <span>Kakao 계정으로 로그인</span>
        </div>
      </q-btn>
    </div>
    
    <!-- 로그인 로딩 오버레이 -->
    <LoginOverlay ref="loginOverlay" />
    
    <!-- 로그인 완료 토스트 -->
    <LoginToast ref="loginToast" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const userId = ref('')
const password = ref('')
const autoLogin = ref(true)
const showPassword = ref(false)

const userIdError = ref('')
const passwordError = ref('')
const message = ref('')
const router = useRouter()

// 컴포넌트 참조
const loginOverlay = ref(null)
const loginToast = ref(null)

function validate() {
  userIdError.value = !userId.value ? '아이디(이메일)를 입력하세요' : ''
  passwordError.value = !password.value ? '비밀번호를 입력하세요' : ''
  return !(userIdError.value || passwordError.value)
}

async function onLogin() {
  if (!validate()) return
  
  // 로딩 오버레이 표시
  if (loginOverlay.value) {
    loginOverlay.value.showOverlay()
  }
  
  try {
    const res = await $fetch('http://' + window.location.hostname + ':5001/api/login', {
      method: 'POST',
      body: {
        email: userId.value,
        password: password.value
      }
    })
    
    // 최소 1.5초 로딩 표시
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    // 로딩 오버레이 숨기기
    if (loginOverlay.value) {
      loginOverlay.value.hideOverlay()
    }
    
    // 인증 상태 업데이트
    const { login } = useAuth()
    login(res.access_token, res.user, res.refresh_token)
    
    // 완료 토스트 표시
    if (loginToast.value) {
      loginToast.value.showToast()
    }
  } catch (err) {
    // 로딩 오버레이 숨기기
    if (loginOverlay.value) {
      loginOverlay.value.hideOverlay()
    }
    message.value = err.data?.error || '로그인 실패'
  }
}
function onGoogleLogin() {
  // 구글 로그인 처리
}
function onKakaoLogin() {
  // 카카오 로그인 처리
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
.login-links {
  text-align: left;
  margin-bottom: 0;
}
.find-password {
  color: #888;
  font-size: 0.8rem;
  font-weight: 400;
  text-decoration: underline;
  margin-top: 2px;
  display: inline-block;
}
.login-btn {
  margin-top: 12px;
  font-weight: bold;
  transition: box-shadow 0.18s;
}
.rounded-btn {
  border-radius: 16px !important;
}
.auto-login-row {
  margin: 8px 0 0 0;
  display: flex;
  align-items: center;
}
.auto-login {
  font-size: 0.8rem;
}
.login-divider {
  display: flex;
  align-items: center;
  width: 100%;
  margin: 1px 0 10px 0;
}
.login-divider .line {
  flex: 1;
  height: 1px;
  background: #eee;
}
.divider-text {
  margin: 0 16px;
  color: #888;
  font-size: 1.0rem;
  white-space: nowrap;
  line-height: 1;
}
.social-login-group {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 1px;
}
.social-btn.google {
  border: 1.5px solid #e0e0e0;
  margin-top: 8px;
}
.social-btn {
  width: 100%;
  height: 48px;
  font-size: 1.08rem;
  justify-content: flex-start;
  font-weight: 500;
  border-radius: 16px !important;
  transition: box-shadow 0.18s, filter 0.18s, transform 0s !important;
}
.social-btn.kakao {
  border: 1.5px solid #e0e0e0;
}
/* 로그인 버튼 hover: 전체적으로 그림자 */
.login-btn:hover {
  box-shadow: 0 4px 18px 0 rgba(33,150,243,0.18);
  filter: brightness(0.97);
  transform: none !important;
}
/* 소셜 버튼 hover: 파란색 glow */
.social-btn:hover {
  box-shadow: 0 0 0 4px rgba(33,150,243,0.18);
  filter: brightness(1.03);
  transform: none !important;
}
.social-icon-btn .social-icon {
  width: 22px;
  height: 22px;
  margin-right: 12px;
  vertical-align: middle;
  display: inline-block;
}
/* ----------- 슬라이드 효과 완전 제거 ----------- */
.custom-login-btn,
.custom-login-btn::after,
.custom-social-btn,
.custom-social-btn::after {
  transition: none !important;
  background: unset !important;
  color: unset !important;
  box-shadow: none !important;
}
.custom-login-btn::after,
.custom-social-btn::after {
  display: none !important;
}
.login-btn.custom-login-btn {
  background: #2196f3 !important;
  color: #fff !important;
  border: none !important;
  box-shadow: none !important;
  transition: box-shadow 0.18s, filter 0.18s;
}
.login-btn.custom-login-btn:hover {
  background: #2196f3 !important;
  color: #fff !important;
  box-shadow: 0 4px 18px 0 rgba(33,150,243,0.22) !important;
  filter: brightness(0.97);
}

.custom-social-btn {
  background: #fff !important;
  color: #222 !important;
  border: 1.5px solid #e0e0e0 !important;
  box-shadow: none !important;
  transition: box-shadow 0.18s, border-color 0.18s, filter 0.18s;
  position: relative;
  z-index: 1;
}
.custom-social-btn:hover {
  background: #fff !important;
  color: #222 !important;
  border-color: #7ecbff !important;
  box-shadow: 0 0 0 4px rgba(126,203,255,0.22), 0 0 8px 2px rgba(126,203,255,0.12) !important;
  filter: none !important;
}
.custom-social-btn .q-btn__content {
  position: relative;
  z-index: 2;
  text-transform: none !important;
  letter-spacing: normal !important;
}
.login-message {
  margin-top: 18px;
  color: #d32f2f;
  font-size: 15px;
  text-align: center;
}
</style>