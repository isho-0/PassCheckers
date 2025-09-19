<template>
  <div style="min-height: 125vh;">
    <!-- 상단 안내문구 -->
    <section style="text-align:center; margin-top:48px; margin-bottom:32px;">
      <h1 style="font-size:2.2rem; font-weight:bold;">
        예상 무게 확인, <span style="color:var(--main-blue);">수하물 무게 예측</span>
      </h1>
      <p style="color:#888; margin-top:8px;">
        분류된 수하물 기록을 바탕으로 예상 무게를 확인하고, 여행 계획에 참고하세요
      </p>
    </section>

    <!-- 메인 카드 -->
    <div class="page-section" style="background:#f8fbff; border:1px solid #e3f0fa;">
      <!-- 메인 레이아웃 -->
      <div style="display: flex; gap: 32px; flex-wrap: wrap;">
        
        <!-- 왼쪽: 이전 기록 목록 -->
        <div style="flex: 1; min-width: 300px;">
          <div style="display:flex; align-items:center; gap:8px; font-weight:600; font-size:1.2rem; margin-bottom:16px;">
            <q-icon name="history" color="primary" size="28px" />
            분류 기록 선택
          </div>
          <div v-if="isHistoryLoading" class="text-center">
            <q-spinner-dots color="primary" size="40px" />
            <p>분석 기록을 불러오는 중입니다...</p>
          </div>
          <div v-else-if="classificationHistory.length === 0" class="text-center text-grey">
            <q-icon name="info" size="32px" />
            <p>분석 기록이 없습니다.</p>
          </div>
          <div v-else style="max-height: 620px; overflow-y: auto; padding: 8px;">
            <q-card 
              v-for="item in classificationHistory" 
              :key="item.id"
              clickable flat bordered 
              style="margin-bottom: 16px; border-radius: 12px; cursor: pointer; overflow: hidden;"
              class="history-card"
              :class="{ 'history-card--selected': selectedHistory && selectedHistory.id === item.id }"
              @click="selectedHistory = item"
            >
              <div style="display: flex; align-items: center; gap: 16px; padding: 16px;">
                <q-img 
                  :src="item.thumbnail_url ? `${apiBaseUrl}${item.thumbnail_url}` : 'https://via.placeholder.com/80x80.png?text=No+Img'"
                  style="width: 80px; height: 80px; border-radius: 8px;"
                >
                  <template v-slot:error>
                    <div class="absolute-full flex flex-center bg-grey-3 text-grey-8">
                      <q-icon name="image_not_supported" size="sm"/>
                    </div>
                  </template>
                </q-img>
                <div style="flex: 1;">
                  <div style="font-weight:600; font-size:1.1rem; color:#333;">{{ item.destination || '알 수 없는 목적지' }}</div>
                  <div style="font-size:0.9rem; color:#888; margin-top:4px;">{{ item.analysis_date }}</div>
                  <div style="font-size:0.9rem; color:#555; margin-top:8px;">{{ item.total_items }}개 물품</div>
                </div>
              </div>
            </q-card>
          </div>
        </div>

        <!-- 오른쪽: 선택된 기록의 무게 예측 결과 -->
        <div style="flex: 2; min-width: 400px;">
          <div v-if="!selectedHistory" class="flex flex-center text-grey" style="height: 100%; flex-direction: column; gap: 16px; background: #fdfdff; border: 2px dashed #e0e0e0; border-radius: 16px;">
            <q-icon name="travel_explore" size="60px" />
            <p style="font-size: 1.2rem;">왼쪽에서 분석 기록을 선택하세요.</p>
          </div>
          <div v-else>
            <!-- 이미지 -->
            <q-card flat bordered style="border-radius: 16px; margin-bottom: 24px;">
              <q-img 
                :src="selectedHistory.image_url ? `${apiBaseUrl}${selectedHistory.image_url}` : ''" 
                style="border-radius: 16px 16px 0 0; max-height: 400px; background-color: #f5f5f5;"
                fit="contain"
              >
                <template v-slot:error>
                  <div class="absolute-full flex flex-center bg-negative text-white">
                    원본 이미지를 불러올 수 없습니다.
                  </div>
                </template>
              </q-img>
              <div style="padding: 16px; display:flex; justify-content: space-between; align-items: center; border-top: 1px solid #f0f0f0;">
                <div style="font-weight: 600; font-size: 1.1rem;">{{ selectedHistory.destination || '알 수 없는 목적지' }}</div>
                <div style="font-size: 0.9rem; color: #888;">{{ selectedHistory.analysis_date }}</div>
              </div>
            </q-card>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px;">
              <!-- 예상 무게 -->
              <q-card flat bordered class="detail-card">
                <div class="card-title">
                  <q-icon name="scale" />
                  <span>예상 무게</span>
                </div>
                <div v-if="isWeightLoading" class="card-content-placeholder">
                  <q-spinner-dots color="primary" size="40px" />
                  <p>예상 무게를 예측 중입니다...</p>
                </div>
                <div v-else-if="weightError" class="card-content-placeholder text-negative">
                  <q-icon name="error_outline" size="40px" />
                  <p>{{ weightError }}</p>
                </div>
                <div v-else-if="adjustedWeightData">
                  <div style="font-size: 2.5rem; font-weight: bold; color: #1976D2; text-align: center; margin: 16px 0;">
                    {{ animatedWeight.toFixed(1) }} kg
                  </div>
                  <div style="padding: 0 8px; margin-bottom: 8px;">
                    <q-linear-progress rounded size="12px" :value="animatedWeight / 30" color="primary" class="q-mt-sm" />
                    <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: #888; margin-top: 4px;">
                      <span>0kg</span>
                      <span>30kg</span>
                    </div>
                  </div>
                </div>
              </q-card>

              <!-- 추천 캐리어 사이즈 -->
              <q-card flat bordered class="detail-card">
                <div class="card-title">
                  <q-icon name="luggage" />
                  <span>캐리어 사이즈 추천</span>
                </div>
                <div v-if="isWeightLoading" class="card-content-placeholder">
                  <q-spinner-dots color="primary" size="24px" />
                </div>
                <div v-else-if="weightError" class="card-content-placeholder text-negative">
                  <q-icon name="error_outline" size="24px" />
                </div>
                <div v-else-if="adjustedWeightData" style="text-align: center; padding: 28px 0;">
                  <div style="font-size: 1.8rem; font-weight: bold; color: #1976D2;">{{ recommendedCarrier.size }}</div>
                  <div style="font-size: 0.9rem; color: #888; margin-top: 4px;">예상 무게 {{ adjustedWeightData.total_weight_kg.toFixed(2) }}kg 기준</div>
                </div>
              </q-card>

              <!-- 카테고리별 무게 분포 -->
              <q-card flat bordered class="detail-card" style="grid-column: span 2;">
                <div class="card-title">
                  <q-icon name="donut_large" />
                  <span>카테고리별 무게 분포</span>
                </div>
                <div v-if="isWeightLoading || isCategoryLoading" class="card-content-placeholder">
                    <q-spinner-dots color="primary" size="40px" />
                    <p>카테고리 정보를 불러오는 중입니다...</p>
                </div>
                <div v-else-if="categoryChartData && categoryChartData.series.length > 0">
                  <VueApexCharts :options="chartOptions" :series="chartSeries" height="350" />
                </div>
                <div v-else class="card-content-placeholder">
                  <q-icon name="info" size="32px" />
                  <p>차트 데이터를 표시할 수 없습니다.</p>
                </div>
              </q-card>

              <!-- 물품 분석 -->
              <q-card flat bordered class="detail-card" style="grid-column: span 2;">
                <div class="card-title">
                  <q-icon name="checklist" />
                  <span>물품 분석 정보</span>
                </div>
                 <div v-if="isWeightLoading" class="card-content-placeholder">
                  <q-spinner-dots color="primary" size="24px" />
                </div>
                <div v-else-if="weightError" class="card-content-placeholder text-negative">
                  <q-icon name="error_outline" size="24px" />
                </div>
                <q-list v-else-if="adjustedWeightData" separator style="margin-top: 8px;">
                  <q-item v-for="item in adjustedWeightData.items" :key="item.item_name_ko">
                    <q-item-section>{{ item.item_name_ko }}</q-item-section>
                    <q-item-section side>
                      <q-badge :label="itemCategories[item.item_name_ko] || '기타'" color="grey-6" />
                    </q-item-section>
                    <q-item-section side v-if="item.predicted_weight_value !== null">
                      {{ formatWeight(item.predicted_weight_value, item.predicted_weight_unit) }}
                    </q-item-section>
                    <q-item-section side v-else>
                      <span class="text-grey">무게 정보 없음</span>
                    </q-item-section>
                  </q-item>
                  <q-item v-if="adjustedWeightData.items.length === 0">
                    <q-item-section class="text-grey">무게가 예측된 물품이 없습니다.</q-item-section>
                  </q-item>
                </q-list>
              </q-card>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue';
import { useAuth } from '~/composables/useAuth';
import { useQuasar } from 'quasar';
import VueApexCharts from 'vue3-apexcharts';

// 로그인 한 회원만 볼 수 있는 접근 권한 적용
definePageMeta({
  middleware: 'auth'
});

type Season = '여름' | '봄/가을' | '겨울';

interface ClassificationHistory {
  id: number;
  destination: string | null;
  analysis_date: string;
  total_items: number;
  image_url: string;
  thumbnail_url: string | null;
}

interface WeightItem {
  item_name_ko: string;
  predicted_weight_value: number | string | null;
  predicted_weight_unit: string | null;
}

interface WeightData {
  items: WeightItem[];
  total_weight_kg: number;
}

const { user } = useAuth();
const apiBaseUrl = 'http://' + window.location.hostname + ':5001';
const $q = useQuasar();

const classificationHistory = ref<ClassificationHistory[]>([]);
const selectedHistory = ref<ClassificationHistory | null>(null);
const isHistoryLoading = ref(true);

const selectedSeason = ref<Season>('봄/가을');
const weightData = ref<WeightData | null>(null);
const isWeightLoading = ref(false);
const weightError = ref<string | null>(null);
const animatedWeight = ref(0);
let animationFrameId: number;

// --- Chart State ---
const isCategoryLoading = ref(false);
const itemCategories = ref<{ [key: string]: string }>({});
const chartSeries = ref<number[]>([]);
const chartOptions = ref<any>({
  chart: { type: 'donut', toolbar: { show: true } },
  labels: [],
    legend: { position: 'bottom' },
  tooltip: {
    y: {
      formatter: (val: number) => {
        if (val >= 1000) {
          return `${(val / 1000).toFixed(1)} kg`;
        }
        return `${val.toFixed(0)} g`;
      }
    }
  },
  dataLabels: { enabled: true, formatter: (val: number) => `${val.toFixed(1)}%` },
  plotOptions: {
    pie: {
      donut: {
        labels: {
          show: true,
          value: {
            show: true,
            formatter: (val: string) => {
              const numVal = parseFloat(val);
              if (numVal >= 1000) {
                return `${(numVal / 1000).toFixed(1)} kg`;
              }
              return `${numVal.toFixed(0)} g`;
            }
          },
          total: {
            show: true,
            label: '총 무게',
            formatter: (w: any) => {
              const total = w.globals.seriesTotals.reduce((a: number, b: number) => a + b, 0);
              return `${(total / 1000).toFixed(1)} kg`;
            }
          }
        }
      },
      states: {
        hover: {
          filter: {
            type: 'none',
            value: 0.1,
          }
        }
      }
    }
  }
});

// --- Data Fetching ---

const fetchHistory = async () => {
  const currentUser = user.value;
  if (!currentUser) {
    isHistoryLoading.value = false;
    return;
  }
  isHistoryLoading.value = true;
  try {
    const response = await fetch(`${apiBaseUrl}/api/analysis/history/${currentUser.id}`);
    if (!response.ok) throw new Error('분석 기록을 가져오는데 실패했습니다.');
    const data = await response.json();
    classificationHistory.value = data.results;
  } catch (error) {
    console.error(error);
    $q.notify({ type: 'negative', message: '분석 기록을 불러오는 중 오류가 발생했습니다.' });
  } finally {
    isHistoryLoading.value = false;
  }
};

onMounted(fetchHistory);

const fetchWeightPrediction = async (analysisId: number) => {
  isWeightLoading.value = true;
  weightData.value = null;
  weightError.value = null;
  itemCategories.value = {}; // Reset categories
  try {
    const response = await fetch(`${apiBaseUrl}/api/weight/predict/${analysisId}`);
    const resData = await response.json();
    if (!response.ok) throw new Error(resData.details || '무게 예측에 실패했습니다.');
    weightData.value = resData;
    selectedSeason.value = '봄/가을';
    // After getting weight, fetch categories
    if (resData.items && resData.items.length > 0) {
      await fetchCategories(resData.items);
    }
  } catch (error) {
    console.error(error);
    if (error instanceof Error) weightError.value = error.message;
    else weightError.value = '알 수 없는 오류가 발생했습니다.';
    $q.notify({ type: 'negative', message: weightError.value });
  } finally {
    isWeightLoading.value = false;
  }
};

const fetchCategories = async (items: WeightItem[]) => {
  isCategoryLoading.value = true;
  try {
    const item_names = items.map(item => item.item_name_ko);
    const response = await fetch(`${apiBaseUrl}/api/categorize`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ item_names })
    });
    if (!response.ok) throw new Error('카테고리 정보를 가져오는데 실패했습니다.');
    const data = await response.json();
    itemCategories.value = data.categories;
  } catch (error) {
    console.error(error);
    $q.notify({ type: 'negative', message: '카테고리 정보를 불러오는 중 오류가 발생했습니다.' });
  } finally {
    isCategoryLoading.value = false;
  }
};

watch(selectedHistory, (newHistory) => {
  if (newHistory) {
    fetchWeightPrediction(newHistory.id);
  } else {
    weightData.value = null;
    weightError.value = null;
    itemCategories.value = {};
  }
});

// --- Computed Properties for Display ---

const CLOTHING_KEYWORDS = ['의류', '옷', '자켓', '코트', '셔츠', '바지', '스웨터', '티셔츠', '가디건', '패딩', '점퍼', '드레스', '치마'];

const adjustedWeightData = computed(() => {
  if (!weightData.value) return null;
  const adjustment = { '여름': -0.7, '봄/가을': 0, '겨울': 1.5 };
  const multiplier = adjustment[selectedSeason.value];
  let totalWeightGrams = 0;

  const adjustedItems = weightData.value.items.map(item => {
    const originalValue = item.predicted_weight_value !== null ? parseFloat(item.predicted_weight_value as string) : null;
    let adjustedValue = originalValue;
    let adjustedUnit = item.predicted_weight_unit;

    if (originalValue !== null && adjustedUnit !== null) {
      const isClothing = CLOTHING_KEYWORDS.some(keyword => item.item_name_ko.includes(keyword));
      if (isClothing && multiplier !== 0) {
        let originalGrams = adjustedUnit === 'kg' ? originalValue * 1000 : originalValue;
        originalGrams *= (1 + multiplier);
        if (originalGrams > 1000) {
          adjustedValue = originalGrams / 1000;
          adjustedUnit = 'kg';
        } else {
          adjustedValue = originalGrams;
          adjustedUnit = 'g';
        }
      }
    }
    return { ...item, predicted_weight_value: adjustedValue, predicted_weight_unit: adjustedUnit };
  });

  adjustedItems.forEach(item => {
    const value = item.predicted_weight_value;
    if (value !== null && item.predicted_weight_unit !== null) {
      totalWeightGrams += item.predicted_weight_unit === 'kg' ? value * 1000 : value;
    }
  });

  return { items: adjustedItems, total_weight_kg: totalWeightGrams / 1000 };
});

const categoryChartData = computed(() => {
  if (!adjustedWeightData.value || Object.keys(itemCategories.value).length === 0) return null;

  const categoryWeights = new Map<string, number>();

  for (const item of adjustedWeightData.value.items) {
    const category = itemCategories.value[item.item_name_ko] || '기타';
    const value = item.predicted_weight_value;
    let weightInGrams = 0;
    if (value !== null && item.predicted_weight_unit) {
        weightInGrams = item.predicted_weight_unit === 'kg' ? value * 1000 : value;
    }
    categoryWeights.set(category, (categoryWeights.get(category) || 0) + weightInGrams);
  }

  const labels = Array.from(categoryWeights.keys());
  const series = Array.from(categoryWeights.values());

  return { labels, series };
});

watch(categoryChartData, (newChartData) => {
  if (newChartData) {
    chartOptions.value = {
      ...chartOptions.value,
      labels: newChartData.labels,
    };
    chartSeries.value = newChartData.series;
  } else {
    chartSeries.value = [];
  }
}, { deep: true });

watch(adjustedWeightData, (newData) => {
  cancelAnimationFrame(animationFrameId);
  if (!newData || newData.total_weight_kg === null) {
    animatedWeight.value = 0;
    return;
  }
  const targetWeight = newData.total_weight_kg;
  const duration = 1000;
  let start: number | null = null;
  const step = (timestamp: number) => {
    if (!start) start = timestamp;
    const progress = Math.min((timestamp - start) / duration, 1);
    animatedWeight.value = progress * targetWeight;
    if (progress < 1) {
      animationFrameId = requestAnimationFrame(step);
    } else {
      animatedWeight.value = targetWeight;
    }
  };
  animationFrameId = requestAnimationFrame(step);
}, { immediate: true });

const recommendedCarrier = computed(() => {
  const totalWeight = adjustedWeightData.value?.total_weight_kg ?? 0;
  if (totalWeight < 10) return { size: '20인치 이하' };
  if (totalWeight >= 10 && totalWeight <= 17) return { size: '24인치' };
  return { size: '28인치 이상' };
});

const formatWeight = (value: number, unit: string | null) => {
  if (unit === 'g') return `${Math.round(value)}g`;
  if (unit === 'kg') return `${parseFloat(value.toFixed(2))}kg`;
  return value;
};

</script>

<style scoped>
.page-section {
  border-radius: 20px;
  padding: 32px;
  margin: 0 auto;
  max-width: 1200px;
  width: 100%;
  box-sizing: border-box;
}

.history-card {
  transition: all 0.2s ease-in-out;
  border: 1px solid #e3f0fa;
}

.history-card:hover {
  border-color: #1976D2;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.history-card--selected {
  border-color: #1976D2;
  box-shadow: 0 4px 16px rgba(25, 118, 210, 0.2);
  transform: translateY(-2px);
}

.detail-card {
  border-radius: 16px;
  padding: 16px;
  border: 1px solid #e3f0fa;
  display: flex;
  flex-direction: column;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 1.1rem;
  color: #333;
  margin-bottom: 16px;
}

.card-content-placeholder {
  flex-grow: 1;
  min-height: 80px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 8px;
  color: #888;
}

.season-btn {
  transition: all 0.2s ease-in-out;
  font-weight: 600;
}

.season-btn.summer.selected { background-color: #fdd835; color: #424242; }
.season-btn.summer:not(.selected) { background-color: #fffde7; color: #f57f17; }

.season-btn.autumn.selected { background-color: #ff8a65; color: white; }
.season-btn.autumn:not(.selected) { background-color: #fbe9e7; color: #d84315; }

.season-btn.winter.selected { background-color: #42a5f5; color: white; }
.season-btn.winter:not(.selected) { background-color: #e3f2fd; color: #1565c0; }

</style>