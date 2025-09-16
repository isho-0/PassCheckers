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
      <!-- 왼쪽: 대륙/국가 선택 패널 -->
      <aside class="left-panel">
        
        <!-- 대륙 선택 뷰 -->
        <div v-if="!selectedContinent">
          <h2 class="panel-title">대륙 선택</h2>
          <div v-if="isLoadingContinents">... 로딩 중 ...</div>
          <div v-else class="continent-buttons">
            <button v-for="continentName in continents" :key="continentName" @click="selectContinent(continentName)" class="continent-btn">
              <span class="continent-btn-text">{{ continentName }}</span>
            </button>
          </div>
        </div>

        <!-- 국가 선택 뷰 -->
        <div v-else>
          <div class="panel-header">
            <button @click="goBackToContinents" class="back-btn">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5"/><polyline points="12 19 5 12 12 5"/></svg>
            </button>
            <h2 class="panel-title">{{ selectedContinent }}</h2>
          </div>
          <div v-if="isLoadingCountries">... 로딩 중 ...</div>
          <div v-else class="country-buttons">
            <button v-for="countryName in countries" :key="countryName" class="country-btn">
               <span>{{ countryName }}</span>
            </button>
          </div>
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
import { ref, onMounted } from 'vue';

const continents = ref([]);
const countries = ref([]);
const selectedContinent = ref(null);

const isLoadingContinents = ref(false);
const isLoadingCountries = ref(false);

// NOTE: This is a temporary solution for local development.
// For production, this should be handled with environment variables and runtime config.
const API_BASE_URL = 'http://localhost:5001/api';

// 대륙 목록을 가져오는 함수
const fetchContinents = async () => {
  isLoadingContinents.value = true;
  try {
    const response = await fetch(`${API_BASE_URL}/locations/continents`);
    if (!response.ok) throw new Error('대륙 목록을 불러오는 데 실패했습니다.');
    continents.value = await response.json();
  } catch (error) {
    console.error(error);
  } finally {
    isLoadingContinents.value = false;
  }
};

// 국가 목록을 가져오는 함수
const fetchCountries = async (continentName) => {
  isLoadingCountries.value = true;
  countries.value = []; // 목록 초기화
  try {
    const response = await fetch(`${API_BASE_URL}/locations/countries?continent=${continentName}`);
    if (!response.ok) throw new Error('국가 목록을 불러오는 데 실패했습니다.');
    countries.value = await response.json();
  } catch (error) {
    console.error(error);
  } finally {
    isLoadingCountries.value = false;
  }
};

// 대륙 선택 처리
const selectContinent = (continentName) => {
  selectedContinent.value = continentName;
  fetchCountries(continentName);
};

// 뒤로가기 처리
const goBackToContinents = () => {
  selectedContinent.value = null;
  countries.value = [];
};

// 컴포넌트가 마운트될 때 대륙 목록을 불러옵니다.
onMounted(() => {
  fetchContinents();
});

</script>

<style scoped>
.info-page-container { padding: 2rem; background-color: #f9fafb; min-height: 100vh; }
.page-header { text-align: center; margin-bottom: 2rem; }
.header-title { font-size: 2.5rem; font-weight: 800; color: #111827; display: flex; align-items: center; justify-content: center; gap: 0.75rem; }
.header-description { font-size: 1.125rem; color: #6b7280; margin-top: 0.5rem; }
.main-content { display: flex; gap: 1.5rem; max-width: 1400px; margin: 0 auto; }

.left-panel {
  flex: 1;
  max-width: 300px;
  background-color: white;
  border-radius: 0.75rem;
  padding: 1.5rem;
  border: 1px solid #e5e7eb;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  height: fit-content;
}

.panel-header {
  display: flex;
  align-items: center;
  margin-bottom: 1.5rem;
}

.back-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.5rem;
  margin-right: 0.75rem;
  border-radius: 9999px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s;
}

.back-btn:hover {
  background-color: #f3f4f6;
}

.panel-title { font-size: 1.5rem; font-weight: 700; color: #1f2937; }

.continent-buttons, .country-buttons {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  max-height: 520px; /* 최대 높이 지정 */
  overflow-y: auto; /* 내용이 넘칠 경우 스크롤바 표시 */
  padding-right: 8px; /* 스크롤바 공간 확보 */
}

.continent-btn, .country-btn {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 0.875rem 1.25rem;
  border-radius: 0.5rem;
  border: 1px solid #d1d5db;
  background-color: #ffffff;
  text-align: left;
  font-size: 1rem;
  font-weight: 500;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
}

.continent-btn:hover, .country-btn:hover {
  background-color: #f3f4f6;
  border-color: #a5b4fc;
  color: #1f2937;
  transform: translateY(-2px);
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
}

.continent-btn-icon { font-size: 1.5rem; margin-right: 1rem; }
.country-flag { font-size: 1.25rem; margin-right: 1rem; }

.right-panel {
  flex: 3;
  background-color: white;
  border-radius: 0.75rem;
  border: 1px solid #e5e7eb;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 600px;
}

.map-placeholder { color: #9ca3af; font-size: 1.25rem; }
</style>
