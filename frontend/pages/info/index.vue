<template>
  <div class="info-page-container">
    <!-- 상단 헤더 -->
    <header class="page-header">
      <h1 class="header-title">
        <span class="header-title-icon">🌍</span>
        세계 여행 비용 정보
      </h1>
      <p class="header-description">
        대륙을 선택하여 지역별 여행 비용을 확인하세요.
      </p>
    </header>

    <!-- 메인 컨텐츠: 2단 레이아웃 -->
    <main class="main-content">
      <!-- 왼쪽: 대륙 선택 버튼 -->
      <aside class="left-panel">
        <h2 class="panel-title">대륙 선택</h2>
        <div class="continent-buttons">
          <button v-for="continent in continents" :key="continent.name" class="continent-btn">
            <span class="continent-btn-icon">{{ continent.icon }}</span>
            <span class="continent-btn-text">{{ continent.name }}</span>
          </button>
        </div>
      </aside>

      <!-- 오른쪽: 세계 지도 -->
      <section class="right-panel">
        <div class="map-placeholder">
          <p>세계 지도가 표시될 영역입니다.</p>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const continents = ref([
  { name: '아시아', icon: '🌏' },
  { name: '유럽', icon: '🇪🇺' },
  { name: '북아메리카', icon: '🌎' },
  { name: '남아메리카', icon: '🌎' },
  { name: '아프리카', icon: '🌍' },
  { name: '오세아니아', icon: '🌊' },
]);

</script>

<style scoped>
.info-page-container {
  padding: 2rem;
  background-color: #f9fafb; /* light gray background */
  min-height: 100vh;
}

.page-header {
  text-align: center;
  margin-bottom: 2rem;
}

.header-title {
  font-size: 2.5rem;
  font-weight: 800;
  color: #111827; /* dark gray */
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
}

.header-description {
  font-size: 1.125rem;
  color: #6b7280; /* medium gray */
  margin-top: 0.5rem;
}

.main-content {
  display: flex;
  gap: 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
}

.left-panel {
  flex: 1;
  max-width: 280px;
  background-color: white;
  border-radius: 0.75rem;
  padding: 1.5rem;
  border: 1px solid #e5e7eb; /* light border */
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.panel-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
  color: #1f2937;
}

.continent-buttons {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.continent-btn {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 0.875rem 1.25rem;
  border-radius: 0.5rem;
  border: 1px solid #d1d5db; /* gray border */
  background-color: #ffffff;
  text-align: left;
  font-size: 1rem;
  font-weight: 500;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
}

.continent-btn:hover {
  background-color: #f3f4f6; /* light gray hover */
  border-color: #a5b4fc; /* indigo border on hover */
  color: #1f2937;
}

.continent-btn-icon {
  font-size: 1.5rem;
  margin-right: 1rem;
}

.right-panel {
  flex: 3;
  background-color: white;
  border-radius: 0.75rem;
  border: 1px solid #e5e7eb;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 600px; /* Ensure height */
}

.map-placeholder {
  color: #9ca3af; /* light gray text */
  font-size: 1.25rem;
}
</style>
