<template>
  <div class="info-page-container">
    <!-- 상단 헤더 -->
    <header class="page-header">
      <h1 class="header-title">
        <span class="header-title-icon">🌍</span>
        세계 여행 비용 정보
      </h1>
      <p class="header-description">
        여행지를 선택하여 여행 비용을 확인하세요.
      </p>
    </header>

    <!-- 메인 컨텐츠: 2단 레이아웃 -->
    <main class="main-content">
      <!-- 왼쪽: 대륙/국가/도시 선택 패널 -->
      <aside class="left-panel">
        <div v-if="currentView === 'continents'">
          <h2 class="panel-title">대륙 선택</h2>
          <div v-if="isLoadingContinents" class="loading-text">... 로딩 중 ...</div>
          <div v-else class="continent-buttons">
            <button v-for="continent in continents" :key="continent.continent_id"
                    @click="selectContinent(continent)"
                    @mouseenter="highlightContinent(continent.continent_ko)"
                    @mouseleave="highlightContinent(null)"
                    class="continent-btn">
              <span class="continent-btn-text">{{ continent.continent_ko }}</span>
            </button>
          </div>
        </div>

        <div v-if="currentView === 'countries'">
          <div class="panel-header">
            <button @click="goBack" class="back-btn">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5"/><polyline points="12 19 5 12 12 5"/></svg>
            </button>
            <h2 class="panel-title">{{ selectedContinent.continent_ko }}</h2>
          </div>
          <div v-if="isLoadingCountries" class="loading-text">... 로딩 중 ...</div>
          <div v-else class="country-buttons">
            <button v-for="country in countries" :key="country.location_id" 
                    @click="selectCountry(country)" 
                    @mouseenter="highlightCountry(country.country)" 
                    @mouseleave="highlightCountry(null)"
                    class="country-btn" :class="{ 'active': selectedCountry && selectedCountry.location_id === country.location_id }">
               <span>{{ country.country_ko }}</span>
            </button>
          </div>
        </div>

        <div v-if="currentView === 'cities'">
          <div class="panel-header">
            <button @click="goBack" class="back-btn">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5"/><polyline points="12 19 5 12 12 5"/></svg>
            </button>
            <h2 class="panel-title">{{ selectedCountry.country_ko }}</h2>
          </div>
          <div v-if="isLoadingCities" class="loading-text">... 로딩 중 ...</div>
          <div v-else class="city-buttons">
            <button v-for="city in cities" :key="city.location_id" @click="selectCity(city)" 
                    class="city-btn" :class="{ 'active': selectedCity && selectedCity.location_id === city.location_id }">
               <span>{{ city.city_ko }}</span>
            </button>
          </div>
        </div>
      </aside>

      <!-- 오른쪽: 지도 또는 상세 정보 -->
      <section class="right-panel">
        <div v-if="!selectedLocationDetails" class="map-wrapper">
          <InteractiveMap 
            :continent-to-focus="selectedContinent?.continent_ko"
            :country-to-highlight="countryToHighlight"
            :continent-to-highlight="continentToHighlight"
          />
        </div>
        <div v-else class="details-view-wrapper">
          <!-- 상세 정보 표시 -->
          <div class="details-view">
            <div class="detail-header">
                <div class="country-title-wrapper">
                  <h3 class="country-name">
                      {{ selectedLocationDetails.location.location_type === 'city' ? selectedLocationDetails.location.city_ko : selectedLocationDetails.location.country_ko }}
                  </h3>
                  <p class="country-name-en">{{ selectedLocationDetails.location.location_type === 'city' ? selectedLocationDetails.location.city : selectedLocationDetails.location.country }}</p>
                </div>
                <button @click="goToDetail(selectedLocationDetails.location.location_id)" class="detail-button">전체 정보 보기</button>
            </div>
            <div v-if="selectedLocationDetails.budget" class="detail-card">
                <h4 class="card-title">여행 예산</h4>
                <div class="budget-grid">
                    <div class="budget-item">
                        <div class="budget-icon">💰</div>
                        <div class="budget-label">저가형</div>
                        <div class="budget-prices">
                            <div class="budget-price-item"><span class="period">1일</span> <span class="price">${{ selectedLocationDetails.budget.budget_daily }}</span></div>
                            <div class="budget-price-item"><span class="period">1주</span> <span class="price">${{ selectedLocationDetails.budget.budget_weekly }}</span></div>
                            <div class="budget-price-item"><span class="period">1달</span> <span class="price">${{ selectedLocationDetails.budget.budget_monthly }}</span></div>
                        </div>
                    </div>
                    <div class="budget-item">
                        <div class="budget-icon">🏨</div>
                        <div class="budget-label">중가형</div>
                        <div class="budget-prices">
                            <div class="budget-price-item"><span class="period">1일</span> <span class="price">${{ selectedLocationDetails.budget.midrange_daily }}</span></div>
                            <div class="budget-price-item"><span class="period">1주</span> <span class="price">${{ selectedLocationDetails.budget.midrange_weekly }}</span></div>
                            <div class="budget-price-item"><span class="period">1달</span> <span class="price">${{ selectedLocationDetails.budget.midrange_monthly }}</span></div>
                        </div>
                    </div>
                    <div class="budget-item">
                        <div class="budget-icon">✨</div>
                        <div class="budget-label">고급형</div>
                        <div class="budget-prices">
                            <div class="budget-price-item"><span class="period">1일</span> <span class="price">${{ selectedLocationDetails.budget.luxury_daily }}</span></div>
                            <div class="budget-price-item"><span class="period">1주</span> <span class="price">${{ selectedLocationDetails.budget.luxury_weekly }}</span></div>
                            <div class="budget-price-item"><span class="period">1달</span> <span class="price">${{ selectedLocationDetails.budget.luxury_monthly }}</span></div>
                        </div>
                    </div>
                </div>
            </div>
            <div v-if="selectedLocationDetails.cost_breakdowns && selectedLocationDetails.cost_breakdowns.length" class="detail-card">
                <h4 class="card-title">세부 비용 분석 (일일 기준)</h4>
                <div class="cost-grid">
                    <div v-for="item in selectedLocationDetails.cost_breakdowns" :key="item.breakdown_id" class="cost-card">
                        <div class="cost-card-icon">{{ getCategoryIcon(item.category) }}</div>
                        <div class="cost-card-category">{{ item.category_ko || item.category }}</div>
                        <div class="cost-card-prices">
                            <div class="price-item price-budget"><span class="price-label">저</span><span class="price-value">{{ item.budget ? '$' + item.budget : 'N/A' }}</span></div>
                            <div class="price-item price-midrange"><span class="price-label">중</span><span class="price-value">{{ item.mid_range ? '$' + item.mid_range : 'N/A' }}</span></div>
                            <div class="price-item price-luxury"><span class="price-label">고</span><span class="price-value">{{ item.luxury ? '$' + item.luxury : 'N/A' }}</span></div>
                        </div>
                    </div>
                </div>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import InteractiveMap from '~/components/InteractiveMap.vue';

definePageMeta({ middleware: 'auth' });

const continents = ref([]);
const countries = ref([]);
const cities = ref([]);
const selectedContinent = ref(null);
const selectedCountry = ref(null);
const selectedCity = ref(null);
const selectedLocationDetails = ref(null);
const continentToHighlight = ref(null);
const countryToHighlight = ref(null);

const isLoadingContinents = ref(false);
const isLoadingCountries = ref(false);
const isLoadingCities = ref(false);
const isLoadingDetails = ref(false);

const currentView = ref('continents');
const API_BASE_URL = 'http://localhost:5001/api';

const getCategoryIcon = (category) => {
  const icons = { 'Accommodation': '🛏️', 'Food': '🍕', 'Transportation': '🚌', 'Entertainment': '🎭', 'Shopping': '🛍️', 'Default': '💸' };
  return icons[category] || icons['Default'];
};

const fetchContinents = async () => {
  isLoadingContinents.value = true;
  try {
    const res = await fetch(`${API_BASE_URL}/locations/continents`);
    continents.value = await res.json();
  } finally {
    isLoadingContinents.value = false;
  }
};

const fetchCountries = async (continentId) => {
  isLoadingCountries.value = true;
  try {
    const res = await fetch(`${API_BASE_URL}/locations/countries?continent=${continentId}`);
    countries.value = await res.json();
  } finally {
    isLoadingCountries.value = false;
  }
};

const fetchCities = async (countryKo) => {
  isLoadingCities.value = true;
  try {
    const res = await fetch(`${API_BASE_URL}/locations/cities?country=${countryKo}`);
    cities.value = await res.json();
  } finally {
    isLoadingCities.value = false;
  }
};

const fetchLocationDetails = async (locationId) => {
  isLoadingDetails.value = true;
  try {
    const res = await fetch(`${API_BASE_URL}/locations/${locationId}`);
    selectedLocationDetails.value = await res.json();
  } finally {
    isLoadingDetails.value = false;
  }
};

const selectContinent = (continent) => {
  selectedContinent.value = continent;
  selectedCountry.value = null;
  selectedCity.value = null;
  selectedLocationDetails.value = null;
  currentView.value = 'countries';
  fetchCountries(continent.continent_id);
};

const selectCountry = (country) => {
  selectedCountry.value = country;
  selectedCity.value = null;
  currentView.value = 'cities';
  fetchCities(country.country_ko);
  fetchLocationDetails(country.location_id);
};

const selectCity = (city) => {
  selectedCity.value = city;
  fetchLocationDetails(city.location_id);
};

const highlightContinent = (continentName) => {
  continentToHighlight.value = continentName;
};

const highlightCountry = (countryName) => {
  countryToHighlight.value = countryName;
};

const goBack = () => {
  selectedLocationDetails.value = null; // 상세 정보 닫기
  if (currentView.value === 'cities') {
    selectedCountry.value = null;
    selectedCity.value = null;
    currentView.value = 'countries';
  } else if (currentView.value === 'countries') {
    selectedContinent.value = null;
    currentView.value = 'continents';
  }
};

const goToDetail = (locationId) => {
  if (locationId) navigateTo(`/info/detail?id=${locationId}`);
};

onMounted(fetchContinents);

</script>

<style scoped>
.info-page-container { padding: 2rem; background-color: #f8f9fa; min-height: 100vh; font-family: 'Pretendard', sans-serif; }
.page-header { text-align: center; margin-bottom: 2rem; }
.header-title { font-size: 2.5rem; font-weight: 800; color: #212529; display: flex; align-items: center; justify-content: center; gap: 0.75rem; }
.header-description { font-size: 1.125rem; color: #6c757d; margin-top: 0.5rem; }
.main-content { display: flex; gap: 1.5rem; max-width: 1400px; margin: 0 auto; }

.left-panel { flex: 1; max-width: 300px; background-color: white; border-radius: 0.75rem; padding: 1.5rem; border: 1px solid #dee2e6; box-shadow: 0 2px 8px rgba(0,0,0,0.06); height: fit-content; }
.panel-header { display: flex; align-items: center; margin-bottom: 1.5rem; }
.back-btn { background: none; border: none; cursor: pointer; padding: 0.5rem; margin-right: 0.75rem; border-radius: 9999px; display: flex; align-items: center; justify-content: center; transition: background-color 0.2s; }
.back-btn:hover { background-color: #e9ecef; }
.panel-title { font-size: 1.5rem; font-weight: 700; color: #343a40; }

.continent-buttons, .country-buttons, .city-buttons { display: flex; flex-direction: column; gap: 0.75rem; max-height: 520px; overflow-y: auto; padding-right: 8px; }
.continent-btn, .country-btn, .city-btn { display: flex; align-items: center; width: 100%; padding: 0.875rem 1.25rem; border-radius: 0.5rem; border: 1px solid #ced4da; background-color: #ffffff; text-align: left; font-size: 1rem; font-weight: 500; color: #495057; cursor: pointer; transition: all 0.2s ease-in-out; }
.continent-btn:hover, .country-btn:hover, .city-btn:hover { background-color: #f1f3f5; border-color: #868e96; color: #212529; transform: translateY(-2px); box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
.country-btn.active, .city-btn.active { background-color: #4c6ef5; border-color: #364fc7; color: #ffffff; font-weight: 600; }

.right-panel { flex: 3; position: relative; }
.map-wrapper { 
  background-color: white;
  border-radius: 0.75rem;
  padding: 1.5rem;
  border: 1px solid #dee2e6;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  height: 682px; /* Match left panel's potential height */
}
.details-view-wrapper { 
  background-color: white;
  border-radius: 0.75rem;
  padding: 1.5rem;
  border: 1px solid #dee2e6;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.loading-text { padding: 1rem; text-align: center; color: #6c757d; }

.details-view { display: flex; flex-direction: column; gap: 1.5rem; }

.detail-header {
  background-color: #ffffff;
  padding: 1.5rem 2rem;
  border-radius: 0.75rem;
  border: 1px solid #dee2e6;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.country-title-wrapper { display: flex; align-items: baseline; gap: 1rem; }
.country-name { font-size: 2.5rem; font-weight: 900; color: #212529; margin: 0; }
.country-name-en { font-size: 1.25rem; color: #868e96; font-weight: 500; }
.detail-button {
    background-color: #4c6ef5;
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 0.5rem;
    font-weight: 600;
    cursor: pointer;
    transition: background-color 0.2s;
}
.detail-button:hover { background-color: #364fc7; }

.detail-card, .no-data-card { background-color: white; border-radius: 0.75rem; padding: 1.5rem; border: 1px solid #dee2e6; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.card-title { font-size: 1.25rem; font-weight: 700; color: #343a40; margin-bottom: 1.5rem; }

.budget-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; }
.budget-item { display: flex; flex-direction: column; align-items: center; background-color: #f8f9fa; padding: 1.5rem 1rem; border-radius: 0.75rem; border: 1px solid #e9ecef; }
.budget-icon { font-size: 2.5rem; line-height: 1; margin-bottom: 0.75rem; }
.budget-label { font-weight: 600; color: #495057; margin-bottom: 1rem; font-size: 1.1rem; }
.budget-prices { display: flex; flex-direction: column; gap: 0.75rem; align-items: stretch; text-align: left; width: 100%; }
.budget-price-item { display: flex; justify-content: space-between; font-size: 1rem; color: #495057; font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace; border-top: 1px solid #e9ecef; padding-top: 0.75rem; }
.budget-price-item:first-child { border-top: none; padding-top: 0; }
.budget-price-item .period { font-weight: 500; color: #868e96; }
.budget-price-item .price { font-weight: 600; color: #212529; }

.cost-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 1rem; }
.cost-card { display: flex; flex-direction: column; align-items: center; text-align: center; background-color: #f8f9fa; padding: 1.5rem 1rem; border-radius: 0.75rem; border: 1px solid #e9ecef; transition: all 0.2s ease-in-out; }
.cost-card:hover { transform: translateY(-4px); box-shadow: 0 6px 12px rgba(0,0,0,0.08); }
.cost-card-icon { font-size: 2.5rem; line-height: 1; margin-bottom: 1rem; }
.cost-card-category { font-size: 1rem; font-weight: 600; color: #495057; margin-bottom: 1rem; }
.cost-card-prices { display: flex; flex-direction: column; gap: 0.25rem; align-items: stretch; width: 100%; }

.price-item { display: flex; justify-content: space-between; align-items: center; }
.price-label { font-weight: 600; width: 22px; height: 22px; border-radius: 4px; display: inline-flex; justify-content: center; align-items: center; font-size: 0.8rem; }
.price-value { font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace; font-size: 0.9rem; }

.price-midrange .price-label { background-color: #dbe4ff; color: #4c6ef5; }
.price-midrange .price-value { font-weight: 700; color: #343a40; font-size: 1.2rem; }

.price-budget .price-label { background-color: #e9ecef; color: #868e96; }
.price-budget .price-value { color: #868e96; }

.price-luxury .price-label { background-color: #e5dbff; color: #845ef7; }
.price-luxury .price-value { color: #868e96; }

.no-data-card { color: #6c757d; text-align: center; padding: 3rem; }
</style>
