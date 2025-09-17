// 전역 상태로 관리
interface User {
  id: number;
  [key: string]: any;
}
const isAuthenticated = ref(false)
const user = ref<User | null>(null)

export const useAuth = () => {

  // 로컬 스토리지에서 인증 상태 확인
  const checkAuth = () => {
    if (process.client) {
      const accessToken = localStorage.getItem('access_token')
      const refreshToken = localStorage.getItem('refresh_token')
      const userData = localStorage.getItem('user')
      
      if (accessToken && userData) {
        isAuthenticated.value = true
        user.value = JSON.parse(userData)
      } else {
        isAuthenticated.value = false
        user.value = null
      }
    }
  }

  // 로그인
  const login = (token: string, userData: any, refreshToken?: string) => {
    if (process.client) {
      localStorage.setItem('access_token', token)
      localStorage.setItem('user', JSON.stringify(userData))
      if (refreshToken) {
        localStorage.setItem('refresh_token', refreshToken)
      }
      isAuthenticated.value = true
      user.value = userData
      
      console.log('로그인 상태 업데이트:', { isAuthenticated: isAuthenticated.value, user: user.value })
      
      // 전역 이벤트 발생
      window.dispatchEvent(new Event('login'))
    }
  }

  // 로그아웃
  const logout = () => {
    if (process.client) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
      isAuthenticated.value = false
      user.value = null
      
      // 전역 이벤트 발생
      window.dispatchEvent(new Event('logout'))
    }
  }

  return {
    isAuthenticated: readonly(isAuthenticated),
    user: readonly(user),
    login,
    logout,
    checkAuth
  }
}

// 앱 시작 시 한 번만 초기화
if (process.client) {
  const accessToken = localStorage.getItem('access_token')
  const userData = localStorage.getItem('user')
  
  if (accessToken && userData) {
    isAuthenticated.value = true
    user.value = JSON.parse(userData)
  }
}