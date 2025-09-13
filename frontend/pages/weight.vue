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
          <div style="max-height: 620px; overflow-y: auto; padding: 8px;">
            <q-card 
              v-for="item in classificationHistory" 
              :key="item.id"
              clickable flat bordered 
              style="margin-bottom: 16px; border-radius: 12px; padding: 16px; cursor: pointer;"
              class="history-card"
            >
              <div style="font-weight:600; font-size:1.1rem; color:#333;">{{ item.destination }}</div>
              <div style="font-size:0.9rem; color:#888; margin-top:4px;">{{ item.date }}</div>
              <div style="font-size:0.9rem; color:#555; margin-top:8px;">{{ item.itemCount }}개 물품</div>
            </q-card>
          </div>
        </div>

        <!-- 오른쪽: 선택된 기록의 무게 예측 결과 -->
        <div style="flex: 2; min-width: 400px;">
          <!-- Season Buttons Section -->
          <div class="detail-card" style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px; background: white;">
            <span class="card-title" style="font-size: 1rem;">여행지에 계절은 어떤가요?</span>
            <div style="display: flex; gap: 8px;">
              <q-btn unelevated no-caps label="여름" :style="getButtonStyle('여름')" @click="selectedSeason = '여름'" />
              <q-btn unelevated no-caps label="봄/가을" :style="getButtonStyle('봄/가을')" @click="selectedSeason = '봄/가을'" />
              <q-btn unelevated no-caps label="겨울" :style="getButtonStyle('겨울')" @click="selectedSeason = '겨울'" />
            </div>
          </div>

          <!-- 이미지 -->
          <q-card flat bordered style="border-radius: 16px; margin-bottom: 24px;">
            <q-img src="https://via.placeholder.com/600x300.png?text=도쿄+여행" style="border-radius: 16px 16px 0 0;" />
            <div style="padding: 16px; display:flex; justify-content: space-between; align-items: center; border-top: 1px solid #f0f0f0;">
              <div style="font-weight: 600; font-size: 1.1rem;">일본 도쿄</div>
              <div style="font-size: 0.9rem; color: #888;">2025-01-15</div>
            </div>
          </q-card>

          <div style="display: flex; flex-direction: column; gap: 24px;">
            <!-- 예상 무게 (Full Width) -->
            <q-card flat bordered class="detail-card">
              <div class="card-title">
                <q-icon name="scale" />
                <span>예상 무게</span>
              </div>
              <div style="font-size: 2.5rem; font-weight: bold; color: #1976D2; text-align: center; margin: 16px 0;">12.5 kg</div>
              <div style="padding: 0 8px; margin-bottom: 8px;">
                <div style="background-color: #e0e0e0; border-radius: 6px; height: 12px; overflow: hidden;">
                  <div style="background-color: #1976D2; width: 41.6%; height: 100%; border-radius: 6px;"></div>
                </div>
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
                <div style="font-size: 1.8rem; font-weight: bold; color: #1976D2;">24인치 (중형)</div>
                <div style="font-size: 0.9rem; color: #888; margin-top: 4px;">예상 무게 12.5kg 기준</div>
              </div>
              <q-list dense separator style="border-top: 1px solid #f0f0f0;">
                <q-item style="padding: 8px 4px;">
                  <q-item-section side style="min-width: 110px; font-weight: 500; padding-left: 8px;">20인치 이하</q-item-section>
                  <q-item-section style="color: #666;">10kg 미만 (기내용, 1-3박)</q-item-section>
                </q-item>
                <q-item style="padding: 8px 4px; background-color: #f8fbff;">
                  <q-item-section side style="min-width: 110px; font-weight: 500; padding-left: 8px;">24인치</q-item-section>
                  <q-item-section style="color: #666;">10-15kg (위탁용, 3-5박)</q-item-section>
                </q-item>
                <q-item style="padding: 8px 4px;">
                  <q-item-section side style="min-width: 110px; font-weight: 500; padding-left: 8px;">28인치 이상</q-item-section>
                  <q-item-section style="color: #666;">15kg 이상 (위탁용, 장기 여행)</q-item-section>
                </q-item>
              </q-list>
            </q-card>

            <!-- 물품 분석 -->
            <q-card flat bordered class="detail-card">
              <div class="card-title">
                <q-icon name="checklist" />
                <span>물품 분석 정보</span>
              </div>
              <q-list separator style="margin-top: 8px;">
                <q-item v-for="item in detectedItems" :key="item.name">
                  <q-item-section>{{ item.name }}</q-item-section>
                  <q-item-section side>{{ item.weight }}</q-item-section>
                </q-item>
              </q-list>
            </q-card>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

// Type for season
type Season = '여름' | '봄/가을' | '겨울';

const selectedSeason = ref<Season>('여름'); // 기본값으로 '여름' 선택

// 버튼 스타일을 동적으로 반환하는 함수
const getButtonStyle = (season: Season) => {
  const style: { [key: string]: string } = {
    borderRadius: '16px',
    transition: 'all 0.3s ease',
    padding: '4px 16px',
    border: '1px solid #e0e0e0'
  };

  if (selectedSeason.value === season) {
    if (season === '여름') {
      style.backgroundColor = '#FFEBEE';
      style.color = '#D32F2F';
      style.borderColor = '#FFCDD2';
    } else if (season === '봄/가을') {
      style.backgroundColor = '#FFF8E1';
      style.color = '#FFA000';
      style.borderColor = '#FFECB3';
    } else { // 겨울
      style.backgroundColor = '#E1F5FE';
      style.color = '#0288D1';
      style.borderColor = '#B3E5FC';
    }
  } else {
    style.backgroundColor = 'white';
    style.color = '#757575';
  }
  return style;
};

// 가상 데이터 (디자인 확인용)
const classificationHistory = ref([
  { id: 1, destination: '일본 도쿄', date: '2025-01-15', itemCount: 5 },
  { id: 2, destination: '부산', date: '2024-12-20', itemCount: 3 },
  { id: 3, destination: '미국 뉴욕', date: '2024-11-05', itemCount: 8 },
  { id: 4, destination: '제주도', date: '2024-10-18', itemCount: 4 },
]);

const detectedItems = ref([
  { name: '노트북', weight: '1.5 kg' },
  { name: '의류', weight: '5.0 kg' },
  { name: '책 2권', weight: '1.0 kg' },
  { name: '카메라', weight: '0.8 kg' },
  { name: '세면도구', weight: '1.2 kg' },
  { name: '기타', weight: '3.0 kg' },
]);
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
}

.history-card:hover {
  border-color: #1976D2;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: scale(1.03);
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
