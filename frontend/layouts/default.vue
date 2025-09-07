<template>
  <q-layout view="lHh Lpr lFf" style="position:relative; z-index:0;">
    <span
      v-for="(cloud, i) in clouds"
      :key="'cloud'+i"
      class="bg-icon material-icons"
      :style="{
        top: cloud.top,
        left: cloud.left,
        fontSize: cloud.size,
        animation: `${cloud.direction === 'left' ? 'cloud-move-left' : 'cloud-move-right'} ${cloud.duration} linear infinite`
      }"
    >cloud</span>
    <div
      v-for="(plane, i) in planes"
      :key="'plane'+i"
      class="bg-plane-img"
      :style="{
        top: plane.startTop,
        left: plane.startLeft,
        width: plane.size,
        height: `calc(${plane.size} * 0.7)`,
        animation: `plane-move-diag ${plane.duration} linear infinite`
      }"
    ></div>
    <q-header elevated>
      <q-toolbar style="display: flex; align-items: center; padding-left: 0;">
        <q-btn
          flat
          dense
          no-caps
          class="text-weight-bold logo-btn"
          @click="$router.push('/')"
          style="font-size:1.2rem; display:flex; align-items:center; gap:16px; background:transparent; height:56px; padding:0 16px 0 10px; margin-right:0; border-top-left-radius:0; border-bottom-left-radius:0; border-top-right-radius:0; border-bottom-right-radius:0;"
        >
          <img src="/images/logo.png" alt="로고" style="height:48px;width:48px;object-fit:contain;background:none;display:inline-block;vertical-align:middle;" />
          <span style="display:inline-flex;align-items:center;height:48px;line-height:48px;vertical-align:middle;">PassCheckers</span>
        </q-btn>
        <div style="flex:1 1 auto; padding:0; margin:0; display:flex;">
          <q-btn
            v-for="item in menu"
            :key="item.path"
            flat dense no-caps
            :label="item.label"
            @click="navigateTo(item.path)"
            :class="{'nav-active': route.path === item.path}"
            style="position:relative;"
          >
            <template v-if="route.path === item.path">
              <div class="nav-underline"></div>
            </template>
          </q-btn>
        </div>
        <div class="q-gutter-sm q-ml-md gt-sm" style="margin-right:32px; display:flex; align-items:center;">
          <template v-if="!isAuthenticated">
            <q-btn flat dense no-caps class="profile-btn" label="로그인" @click="$router.push('/login')" />
            <q-btn flat dense no-caps class="profile-btn signup-btn" label="회원가입" @click="$router.push('/signup')" />
          </template>
          <template v-else>
            <q-btn round flat dense icon="account_circle" size="23px" @click="goToProfile" />
            <q-btn flat dense no-caps class="profile-btn" label="로그아웃" @click="logout" />
          </template>
        </div>
        <q-btn flat dense round icon="menu" class="lt-md" @click="drawer = !drawer" />
      </q-toolbar>
      <q-drawer v-model="drawer" side="right" overlay class="lt-md">
        <q-list>
          <q-item clickable v-for="item in menu" :key="item.label" @click="navigateTo(item.path)">
            <q-item-section>{{ item.label }}</q-item-section>
          </q-item>
          <q-separator />
          <q-item clickable>
            <q-item-section>회원가입</q-item-section>
          </q-item>
          <q-item clickable>
            <q-item-section>내정보</q-item-section>
          </q-item>
        </q-list>
      </q-drawer>
    </q-header>
    <q-page-container>
      <transition name="fade-scale" mode="out-in">
        <NuxtPage />
      </transition>
    </q-page-container>
    
    <!-- 로그아웃 로딩 오버레이 -->
    <LogoutOverlay ref="logoutOverlay" />
    
    <!-- 로그아웃 완료 토스트 -->
    <LogoutToast ref="logoutToast" />
    
    <!-- 페이지 이동 로딩 오버레이 -->
    <PageLoadingOverlay ref="pageLoadingOverlay" />
  </q-layout>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const drawer = ref(false)
const menu = [
  { label: '수하물 분류', path: '/classification' },
  { label: '수하물 무게 예측', path: '/weight' },
  { label: '수하물 패킹', path: '/packing' },
  { label: '커뮤니티', path: '/community' },
  { label: '여행 추천', path: '/recommend' },
  { label: '여행 정보', path: '/info' },
  { label: '공유', path: '/share' },
]

const route = useRoute()
const router = useRouter()

// 컴포넌트 참조
const logoutOverlay = ref(null)
const logoutToast = ref(null)
const pageLoadingOverlay = ref(null)

// useAuth composable 사용
const { isAuthenticated, user, logout: authLogout } = useAuth()

// 상태 변화 추적
watch(isAuthenticated, (newValue) => {
  console.log('default.vue - 인증 상태 변화:', newValue)
})

watch(user, (newValue) => {
  console.log('default.vue - 사용자 정보 변화:', newValue)
})

const profileMenu = ref(false)
const profileBtnRef = ref(null)
const profileMenu2 = ref(false)
const profileBtnRef2 = ref(null)

const clouds = ref([])
const planes = ref([])

function random(min, max) {
  return Math.random() * (max - min) + min
}

// 페이지 네비게이션 함수
async function navigateTo(path) {
  // 현재 페이지와 같은 경우 무시
  if (route.path === path) return
  
  // 로딩 오버레이 표시
  if (pageLoadingOverlay.value) {
    pageLoadingOverlay.value.showOverlay('페이지를 이동하는 중...')
  }
  
  try {
    // 최소 0.5초 로딩 표시
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // 페이지 이동
    await router.push(path)
  } catch (error) {
    console.error('페이지 이동 실패:', error)
  } finally {
    // 로딩 오버레이 숨기기
    if (pageLoadingOverlay.value) {
      pageLoadingOverlay.value.hideOverlay()
    }
  }
}

onMounted(() => {
  clouds.value = Array.from({ length: 4 }, () => ({
    top: random(10, 70) + 'vh',
    left: random(0, 80) + 'vw',
    size: random(50, 120) + 'px',
    duration: random(40, 80) + 's',
    direction: Math.random() > 0.5 ? 'left' : 'right'
  }))
  planes.value = Array.from({ length: 1 }, () => ({
    startTop: random(60, 80) + 'vh',
    startLeft: random(70, 90) + 'vw',
    size: random(60, 100) + 'px',
    duration: random(40, 60) + 's'
  }))
})

async function logout() {
  // 로딩 오버레이 표시
  if (logoutOverlay.value) {
    logoutOverlay.value.showOverlay()
  }
  
  try {
    const access_token = localStorage.getItem('access_token')
    if (access_token) {
      await $fetch('http://' + window.location.hostname + ':5001/api/logout', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${access_token}`
        }
      })
    }
  } catch (err) {
    console.log('로그아웃 API 호출 실패:', err)
  } finally {
    // 최소 1.5초 로딩 표시
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    // 로딩 오버레이 숨기기
    if (logoutOverlay.value) {
      logoutOverlay.value.hideOverlay()
    }
    
    // 로그아웃 처리
    authLogout()
    
    // 완료 토스트 표시
    if (logoutToast.value) {
      logoutToast.value.showToast()
    }
  }
}

function goToProfile() {
  // 내 정보 페이지로 이동
  $router.push('/info')
}
</script>

<style src="~/assets/theme.css"></style>
<style>
.fade-scale-enter-active, .fade-scale-leave-active {
  transition: opacity 0.35s cubic-bezier(.4,0,.2,1), transform 0.35s cubic-bezier(.4,0,.2,1);
}
.fade-scale-enter-from, .fade-scale-leave-to {
  opacity: 0;
  transform: scale(0.96);
}
.fade-scale-leave-from, .fade-scale-enter-to {
  opacity: 1;
  transform: scale(1);
}
</style>