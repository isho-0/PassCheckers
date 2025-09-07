export default defineNuxtRouteMiddleware((to) => {
  const { isAuthenticated } = useAuth()
  
  // 인덱스 페이지는 모든 사용자가 접근 가능
  if (to.path === '/') {
    return
  }
  
  // 로그인/회원가입 페이지는 비로그인 사용자도 접근 가능
  if (to.path === '/login' || to.path === '/signup') {
    return
  }
  
  // 로그인하지 않은 사용자는 인덱스 페이지로 리다이렉트하고 토스트 표시
  if (!isAuthenticated.value) {
    return navigateTo('/?auth_required=true')
  }
})
