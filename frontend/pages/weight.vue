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

            <div v-if="!isWeightLoading && weightData" style="display: flex; flex-direction: column; gap: 24px;">
              <!-- 예상 무게 (Full Width) -->
              <q-card flat bordered class="detail-card">
                <div class="card-title">
                  <q-icon name="scale" />
                  <span>예상 무게</span>
                </div>
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
              </q-card>

              <!-- 추천 캐리어 사이즈 (Full Width) -->
              <q-card flat bordered class="detail-card">
                <div class="card-title">
                  <q-icon name="luggage" />
                  <span>캐리어 사이즈 추천</span>
                </div>
                <div style="text-align: center; padding: 12px 0;">
                  <div style="font-size: 1.8rem; font-weight: bold; color: #1976D2;">{{ recommendedCarrier.size }}</div>
                  <div style="font-size: 0.9rem; color: #888; margin-top: 4px;">예상 무게 {{ weightData.total_weight_kg }}kg 기준</div>
                </div>
                <q-list dense separator style="border-top: 1px solid #f0f0f0;">
                  <q-item :active="recommendedCarrier.size.startsWith('20')" active-class="bg-blue-1" style="padding: 8px 4px;"><q-item-section side style="min-width: 110px; font-weight: 500; padding-left: 8px;">20인치 이하</q-item-section><q-item-section style="color: #666;">10kg 미만 (기내용, 1-3박)</q-item-section></q-item>
                  <q-item :active="recommendedCarrier.size.startsWith('24')" active-class="bg-blue-1" style="padding: 8px 4px;"><q-item-section side style="min-width: 110px; font-weight: 500; padding-left: 8px;">24인치</q-item-section><q-item-section style="color: #666;">10-17kg (위탁용, 3-5박)</q-item-section></q-item>
                  <q-item :active="recommendedCarrier.size.startsWith('28')" active-class="bg-blue-1" style="padding: 8px 4px;"><q-item-section side style="min-width: 110px; font-weight: 500; padding-left: 8px;">28인치 이상</q-item-section><q-item-section style="color: #666;">17kg 이상 (위탁용, 장기 여행)</q-item-section></q-item>
                </q-list>
              </q-card>

              <!-- 물품 분석 -->
              <q-card flat bordered class="detail-card">
                <div class="card-title">
                  <q-icon name="checklist" />
                  <span>물품 분석 정보</span>
                </div>
                <q-list separator style="margin-top: 8px;">
                  <q-item v-for="item in weightData.items" :key="item.item_name_ko">
                    <q-item-section>{{ item.item_name_ko }}</q-item-section>
                    <q-item-section side v-if="item.predicted_weight_value !== null">
                      {{ formatWeight(item.predicted_weight_value, item.predicted_weight_unit) }}
                    </q-item-section>
                    <q-item-section side v-else>
                      <span class="text-grey">무게 정보 없음</span>
                    </q-item-section>
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
  predicted_weight_value: number | null;
  predicted_weight_unit: string | null;
}

interface WeightData {
  items: WeightItem[];
  total_weight_kg: number;
}

const { user } = useAuth();
const apiBaseUrl = 'http://localhost:5001'; // 백엔드 서버 주소
const $q = useQuasar();

const classificationHistory = ref<ClassificationHistory[]>([]);
const selectedHistory = ref<ClassificationHistory | null>(null);
const isHistoryLoading = ref(true);

const weightData = ref<WeightData | null>(null);
const isWeightLoading = ref(false);
const animatedWeight = ref(0);
let animationFrameId: number;

// Fetch classification history
const fetchHistory = async () => {
  if (!user.value) {
    isHistoryLoading.value = false;
    return;
  }
  isHistoryLoading.value = true;
  try {
    const response = await fetch(`${apiBaseUrl}/api/analysis/history/${user.value.id}`);
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

// Fetch weight prediction when a history item is selected
const fetchWeightPrediction = async (analysisId: number) => {
  isWeightLoading.value = true;
  weightData.value = null;
  $q.loading.show({
    message: '예상 무게를 예측하는 중입니다...<br/><span class="text-amber text-italic">Gemini API가 응답하고 있습니다.</span>',
    html: true,
  });
  try {
    const response = await fetch(`${apiBaseUrl}/api/weight/predict/${analysisId}`);
    if (!response.ok) throw new Error('무게 예측에 실패했습니다.');
    const data: WeightData = await response.json();
    weightData.value = data;
  } catch (error) {
    console.error(error);
    $q.notify({ type: 'negative', message: '무게 예측 중 오류가 발생했습니다.' });
  } finally {
    isWeightLoading.value = false;
    $q.loading.hide();
  }
};

watch(selectedHistory, (newHistory) => {
  if (newHistory) {
    fetchWeightPrediction(newHistory.id);
  } else {
    weightData.value = null;
  }
});

// Animate weight value
watch(weightData, (newData) => {
  cancelAnimationFrame(animationFrameId);
  if (!newData) {
    animatedWeight.value = 0;
    return;
  }

  const targetWeight = newData.total_weight_kg;
  const duration = 1000; // 1 second
  let start: number | null = null;

  const step = (timestamp: number) => {
    if (!start) start = timestamp;
    const progress = Math.min((timestamp - start) / duration, 1);
    animatedWeight.value = progress * targetWeight;
    if (progress < 1) {
      animationFrameId = requestAnimationFrame(step);
    } else {
      animatedWeight.value = targetWeight; // Ensure it ends exactly on target
    }
  };
  animationFrameId = requestAnimationFrame(step);
});

// Carrier recommendation logic
const recommendedCarrier = computed(() => {
  const totalWeight = weightData.value?.total_weight_kg ?? 0;
  if (totalWeight < 10) {
    return { size: '20인치 이하', desc: '10kg 미만 (기내용, 1-3박)' };
  } else if (totalWeight >= 10 && totalWeight <= 17) {
    return { size: '24인치', desc: '10-17kg (위탁용, 3-5박)' };
  } else {
    return { size: '28인치 이상', desc: '17kg 이상 (위탁용, 장기 여행)' };
  }
});

// Format individual item weight
const formatWeight = (value: number, unit: string | null) => {
  if (unit === 'g') {
    return `${Number(value)}g`;
  }
  if (unit === 'kg') {
    // parseFloat to remove trailing zeros, e.g., 2.20 -> 2.2
    return `${parseFloat(Number(value).toFixed(2))}kg`;
  }
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
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 1.1rem;
  color: #333;
}
</style>