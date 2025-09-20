<template>
  <div class="info-detail-page" v-if="locationDetails">
    <header class="page-header">
      <div class="header-content">
        <h1 class="location-name">
          {{ locationDetails.location.location_type === 'city' ? locationDetails.location.city_ko : locationDetails.location.country_ko }}
          <span class="location-name-en">{{ locationDetails.location.location_type === 'city' ? locationDetails.location.city : locationDetails.location.country }}</span>
        </h1>
        <NuxtLink to="/info" class="back-link">
          &larr; 목록으로 돌아가기
        </NuxtLink>
      </div>
    </header>

    <main class="main-content">
      <aside class="sidebar">
        <nav class="toc">
          <h3 class="toc-title">목차</h3>
          <ul>
            <li v-for="section in contentSections" :key="section.content_id">
              <a @click.prevent="scrollToSection(section.content_id)" 
                 :class="{ 'active': activeSection == section.content_id }">
                {{ section.title_ko }}
              </a>
            </li>
            <li v-if="locationDetails.budget">
              <a @click.prevent="scrollToSection('budget')" :class="{ 'active': activeSection === 'budget' }">여행 예산</a>
            </li>
            <li v-if="locationDetails.cost_breakdowns && locationDetails.cost_breakdowns.length > 0">
              <a @click.prevent="scrollToSection('cost-breakdown')" :class="{ 'active': activeSection === 'cost-breakdown' }">세부 비용</a>
            </li>
          </ul>
        </nav>
      </aside>

      <div class="content-area">
        <section v-for="section in contentSections" :key="section.content_id" :id="`section-${section.content_id}`" class="content-section">
          <h2 class="section-title">{{ section.title_ko }}</h2>
          <p class="section-content">{{ section.content_ko }}</p>
        </section>

        <section v-if="locationDetails.budget" id="section-budget" class="content-section">
          <h2 class="section-title">여행 예산</h2>
          <div class="detail-card">
              <div class="budget-grid">
                  <div class="budget-item">
                      <div class="budget-icon">💰</div>
                      <div class="budget-label">저가형</div>
                      <div class="budget-prices">
                          <div class="budget-price-item"><span class="period">1일</span> <span class="price">${{ locationDetails.budget.budget_daily }}</span></div>
                          <div class="budget-price-item"><span class="period">1주</span> <span class="price">${{ locationDetails.budget.budget_weekly }}</span></div>
                          <div class="budget-price-item"><span class="period">1달</span> <span class="price">${{ locationDetails.budget.budget_monthly }}</span></div>
                      </div>
                  </div>
                  <div class="budget-item">
                      <div class="budget-icon">🏨</div>
                      <div class="budget-label">중가형</div>
                      <div class="budget-prices">
                          <div class="budget-price-item"><span class="period">1일</span> <span class="price">${{ locationDetails.budget.midrange_daily }}</span></div>
                          <div class="budget-price-item"><span class="period">1주</span> <span class="price">${{ locationDetails.budget.midrange_weekly }}</span></div>
                          <div class="budget-price-item"><span class="period">1달</span> <span class="price">${{ locationDetails.budget.midrange_monthly }}</span></div>
                      </div>
                  </div>
                  <div class="budget-item">
                      <div class="budget-icon">✨</div>
                      <div class="budget-label">고급형</div>
                      <div class="budget-prices">
                          <div class="budget-price-item"><span class="period">1일</span> <span class="price">${{ locationDetails.budget.luxury_daily }}</span></div>
                          <div class="budget-price-item"><span class="period">1주</span> <span class="price">${{ locationDetails.budget.luxury_weekly }}</span></div>
                          <div class="budget-price-item"><span class="period">1달</span> <span class="price">${{ locationDetails.budget.luxury_monthly }}</span></div>
                      </div>
                  </div>
              </div>
          </div>
        </section>

        <section v-if="locationDetails.cost_breakdowns && locationDetails.cost_breakdowns.length > 0" id="section-cost-breakdown" class="content-section">
          <h2 class="section-title">세부 비용 분석 (일일 기준)</h2>
           <div class="detail-card">
                <div class="cost-grid">
                    <div v-for="item in locationDetails.cost_breakdowns" :key="item.breakdown_id" class="cost-card">
                        <div class="cost-card-icon">{{ getCategoryIcon(item.category) }}</div>
                        <div class="cost-card-category">{{ item.category_ko || item.category }}</div>
                        <div class="cost-card-prices">
                            <div class="price-item price-budget">
                                <span class="price-label">저</span>
                                <span class="price-value">{{ item.budget ? '$' + item.budget : 'N/A' }}</span>
                            </div>
                            <div class="price-item price-midrange">
                                <span class="price-label">중</span>
                                <span class="price-value">{{ item.mid_range ? '$' + item.mid_range : 'N/A' }}</span>
                            </div>
                            <div class="price-item price-luxury">
                                <span class="price-label">고</span>
                                <span class="price-value">{{ item.luxury ? '$' + item.luxury : 'N/A' }}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
      </div>
    </main>

    <div class="scroll-buttons">
      <button @click="scrollToTop" title="맨 위로">▲</button>
      <button @click="scrollToBottom" title="맨 아래로">▼</button>
    </div>
  </div>
  <div v-else class="loading-container">
    <p>{{ error ? error : '상세 정보를 불러오는 중입니다...' }}</p>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed, nextTick } from 'vue';
import { useRoute } from 'vue-router';

definePageMeta({
  middleware: 'auth'
});

const route = useRoute();
const locationDetails = ref(null);
const error = ref(null);
const activeSection = ref('');
const observer = ref(null);
const sectionElements = ref([]);

const API_BASE_URL = 'http://' + window.location.hostname + ':5001/api';

const contentSections = computed(() => {
  return locationDetails.value?.location_content || [];
});

const fetchLocationDetails = async (locationId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/locations/${locationId}`);
    if (!response.ok) {
      throw new Error('데이터를 불러오는 데 실패했습니다.');
    }
    locationDetails.value = await response.json();
  } catch (e) {
    error.value = e.message;
    console.error(e);
  }
};

const getCategoryIcon = (category) => {
  const icons = {
    'Accommodation': '🛏️',
    'Food': '🍕',
    'Transportation': '🚌',
    'Entertainment': '🎭',
    'Shopping': '🛍️',
    'Default': '💸'
  };
  return icons[category] || icons['Default'];
};

const scrollToSection = (sectionId) => {
  const element = document.getElementById(`section-${sectionId}`);
  if (element) {
    const headerOffset = 120; // 헤더 높이 + 여유 공간
    const elementPosition = element.getBoundingClientRect().top;
    const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

    window.scrollTo({
      top: offsetPosition,
      behavior: 'smooth'
    });
    activeSection.value = sectionId;
  }
};

const scrollToTop = () => {
  window.scrollTo({ top: 0, behavior: 'smooth' });
};

const scrollToBottom = () => {
  window.scrollTo({ top: document.documentElement.scrollHeight, behavior: 'smooth' });
};

const setupObserver = () => {
  const options = {
    rootMargin: '-120px 0px -65% 0px',
    threshold: 0
  };

  observer.value = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const id = entry.target.id.replace('section-', '');
        activeSection.value = id;
      }
    });
  }, options);

  sectionElements.value.forEach(section => {
    if(section) observer.value.observe(section);
  });
};

onMounted(() => {
  const locationId = route.query.id;
  if (locationId) {
    fetchLocationDetails(locationId).then(() => {
      nextTick(() => {
        sectionElements.value = [
          ...document.querySelectorAll('.content-section')
        ];
        setupObserver();
        // Set initial active section
        if (contentSections.value.length > 0) {
          activeSection.value = contentSections.value[0].content_id;
        } else if (locationDetails.value.budget) {
          activeSection.value = 'budget';
        }
      });
    });
  } else {
    error.value = '유효한 지역 ID가 없습니다.';
  }
});

onBeforeUnmount(() => {
  if (observer.value) {
    observer.value.disconnect();
  }
});
</script>

<style scoped>
/* Page Layout & Header */
.info-detail-page { font-family: 'Pretendard', sans-serif; background-color: #f8f9fa; }
.page-header { 
  background-color: white; 
  padding: 1.5rem 2rem; 
  border-bottom: 1px solid #dee2e6; 
  position: sticky; 
  top: 0; 
  z-index: 10;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}
.header-content { max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; }
.location-name { font-size: 2.25rem; font-weight: 800; color: #212529; }
.location-name-en { font-size: 1.25rem; color: #868e96; font-weight: 500; margin-left: 0.75rem; }
.back-link { font-weight: 600; color: #4c6ef5; text-decoration: none; transition: color 0.2s; }
.back-link:hover { color: #364fc7; }

/* Main Content Layout */
.main-content { display: flex; max-width: 1200px; margin: 1rem auto; gap: 2rem; padding: 0 1rem; }
.sidebar { flex: 1; position: sticky; top: 7.5rem; align-self: flex-start; }
.content-area { flex: 3; min-width: 0; }

/* Table of Contents */
.toc { background-color: white; border-radius: 0.75rem; padding: 1.5rem; border: 1px solid #dee2e6; }
.toc-title { font-size: 1.25rem; font-weight: 700; margin-bottom: 1rem; }
.toc ul { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 0.25rem; }
.toc a { display: block; padding: 0.75rem 1rem; border-radius: 0.5rem; text-decoration: none; color: #495057; font-weight: 500; transition: background-color 0.2s, color 0.2s; cursor: pointer; border-left: 3px solid transparent; }
.toc a:hover { background-color: #f1f3f5; }
.toc a.active { background-color: #e7f5ff; color: #1c7ed6; font-weight: 600; border-left: 3px solid #228be6; }

/* Content Sections */
.content-section { background-color: white; border-radius: 0.75rem; padding: 2rem; border: 1px solid #dee2e6; margin-bottom: 2rem; }
.section-title { font-size: 1.75rem; font-weight: 700; color: #343a40; margin-bottom: 1.5rem; padding-bottom: 1rem; border-bottom: 2px solid #e9ecef; }
.section-content { font-size: 1.1rem; line-height: 1.8; color: #495057; white-space: pre-line; }

/* Loading State */
.loading-container { display: flex; justify-content: center; align-items: center; min-height: 80vh; font-size: 1.25rem; color: #6c757d; }

/* Scroll to Top/Bottom Buttons */
.scroll-buttons { position: fixed; bottom: 2rem; right: 2rem; display: flex; flex-direction: column; gap: 0.5rem; z-index: 20; }
.scroll-buttons button { width: 3rem; height: 3rem; border-radius: 50%; background-color: rgba(0, 0, 0, 0.5); color: white; border: none; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; transition: background-color 0.2s; }
.scroll-buttons button:hover { background-color: rgba(0, 0, 0, 0.7); }

/* Re-using styles from index.vue for budget and cost breakdowns */
.detail-card { background-color: transparent; border-radius: 0; padding: 0; border: none; box-shadow: none; }
.budget-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem; }
.budget-item { display: flex; flex-direction: column; align-items: center; background-color: #ffffff; padding: 1.5rem 1rem; border-radius: 0.75rem; border: 1px solid #e9ecef; }
.budget-icon { font-size: 2.5rem; line-height: 1; margin-bottom: 0.75rem; }
.budget-label { font-weight: 600; color: #495057; margin-bottom: 1rem; font-size: 1.1rem; }
.budget-prices { display: flex; flex-direction: column; gap: 0.75rem; align-items: stretch; text-align: left; width: 100%; }
.budget-price-item { display: flex; justify-content: space-between; font-size: 1rem; color: #495057; font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace; border-top: 1px solid #e9ecef; padding-top: 0.75rem; }
.budget-price-item:first-child { border-top: none; padding-top: 0; }
.budget-price-item .period { font-weight: 500; color: #868e96; }
.budget-price-item .price { font-weight: 600; color: #212529; }

.cost-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 1rem; }
.cost-card { display: flex; flex-direction: column; align-items: center; text-align: center; background-color: #ffffff; padding: 1.5rem 1rem; border-radius: 0.75rem; border: 1px solid #e9ecef; transition: all 0.2s ease-in-out; }
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
</style>