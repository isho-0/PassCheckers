<template>
  <div style="min-height: 100vh;">
    <!-- 상단 안내문구 -->
    <section style="text-align:center; margin-top:48px; margin-bottom:32px;">
      <h1 style="font-size:2.2rem; font-weight:bold;">
        <span style="color:var(--main-blue);">수하물</span> 분석 결과
      </h1>
      <p style="color:#888; margin-top:8px;">
        업로드하신 이미지를 기반으로 분석된 수하물 정보입니다.
      </p>
    </section>

    <!-- 메인 카드: 좌우 분할 -->
    <div class="page-section" style="background:#fdfdff; border:1px solid #e8e8e8;">
      <div class="row q-col-gutter-md">
        <!-- 왼쪽: 원본 이미지 -->
        <div class="col-12 col-md-6">
          <div style="font-weight:600; font-size:1.2rem; margin-bottom:16px; text-align:center;">
            원본 이미지
          </div>
          <q-card flat bordered class="image-card">
            <div ref="imageContainerRef" class="image-container">
              <q-img :src="imageUrl" style="border-radius: 16px; max-height: 400px;" fit="contain">
                <template v-slot:error>
                  <div class="absolute-full flex flex-center bg-negative text-white">
                    이미지를 불러올 수 없습니다
                  </div>
                </template>
              </q-img>

              <!-- Bounding Box 표시 시작 -->
              <div
                v-for="(item, index) in processedResults"
                :key="`box-${index}`"
                :class="['bounding-box', { 'bounding-box--hovered': hoveredIndex === index }]"
                :style="item.style"
              >
                <div class="box-label">{{ item.name_ko }}</div>
              </div>
              <!-- Bounding Box 표시 끝 -->

            </div>
          </q-card>
        </div>

        <!-- 오른쪽: 탐지 결과 -->
        <div class="col-12 col-md-6">
          <div style="font-weight:600; font-size:1.2rem; margin-bottom:16px; text-align:center;">
            탐지 결과
          </div>
          <q-card flat bordered class="results-card">
            <div v-if="isLoading" class="column items-center justify-center" style="height:100%;">
              <q-spinner-dots color="primary" size="3em" />
              <div class="q-mt-md text-grey-7">결과를 불러오고 있습니다...</div>
            </div>
            <div v-else-if="detectionResults.length === 0" class="column items-center justify-center" style="height:100%;">
              <q-icon name="search_off" size="3em" color="grey-5" />
              <div class="q-mt-md text-grey-7">탐지된 물품이 없습니다.</div>
            </div>
            <div v-else>
              <q-list separator>
                <q-item-label header class="text-weight-bold">탐지된 물품 목록</q-item-label>
                <q-item 
                  v-for="(item, index) in detectionResults" 
                  :key="index"
                  @mouseenter="hoveredIndex = index"
                  @mouseleave="hoveredIndex = null"
                  clickable
                >
                  <q-item-section avatar>
                    <q-icon :name="getIconFor(item.name_ko)" color="primary" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label class="text-weight-medium">{{ item.name_ko }}</q-item-label>
                    <q-item-label caption>정확도: {{ item.confidence.toFixed(2) }}%</q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <q-badge :color="getCarryOnColor(item.carry_on_allowed)" outline>
                      기내: {{ item.carry_on_allowed || '확인 불가' }}
                    </q-badge>
                    <q-badge :color="getCheckedColor(item.checked_baggage_allowed)" outline class="q-mt-xs">
                      위탁: {{ item.checked_baggage_allowed || '확인 불가' }}
                    </q-badge>
                  </q-item-section>
                </q-item>
              </q-list>
            </div>
          </q-card>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const isLoading = ref(true)
const imageUrl = ref('')
const detectionResults = ref([])
const processedResults = ref([]) // 스타일이 계산된 결과
const imageContainerRef = ref(null) // 이미지 컨테이너 DOM 요소를 위한 ref
const route = useRoute()
const hoveredIndex = ref(null) // 마우스 오버된 아이템의 인덱스

// Bounding Box 스타일 계산 함수
const getBoxStyle = (bbox) => {
  if (!bbox || bbox.length < 4) return {}
  const [x_min, y_min, x_max, y_max] = bbox
  return {
    position: 'absolute',
    left: `${x_min * 100}%`,
    top: `${y_min * 100}%`,
    width: `${(x_max - x_min) * 100}%`,
    height: `${(y_max - y_min) * 100}%`,
  }
}

// 아이콘 매핑 (예시)
const getIconFor = (itemName) => {
  if (itemName.includes('노트북')) return 'laptop_chromebook'
  if (itemName.includes('배터리')) return 'battery_charging_full'
  if (itemName.includes('가위')) return 'content_cut'
  return 'check_box_outline_blank'
}

// 반입 가능 여부에 따른 색상
const getCarryOnColor = (status) => {
  if (status === '가능') return 'positive'
  if (status === '불가') return 'negative'
  return 'grey'
}
const getCheckedColor = (status) => {
  if (status === '가능') return 'positive'
  if (status === '불가') return 'negative'
  return 'grey'
}

// 컴포넌트가 마운트되면 실행될 로직
onMounted(() => {
  // 1. 라우트 쿼리에서 결과 데이터와 이미지 URL을 읽어옵니다.
  if (route.query.results) {
    try {
      const resultData = JSON.parse(route.query.results)
      detectionResults.value = resultData.results || []
      const originalImageSize = resultData.image_size || { width: 1, height: 1 }

      // DOM이 렌더링된 후 Bbox 위치 계산
      setTimeout(() => {
        if (!imageContainerRef.value) return

        const container = {
          width: imageContainerRef.value.offsetWidth,
          height: imageContainerRef.value.offsetHeight
        }

        const containerRatio = container.width / container.height
        const imageRatio = originalImageSize.width / originalImageSize.height

        let scale = 1
        let offsetX = 0
        let offsetY = 0

        if (imageRatio > containerRatio) {
          scale = container.width / originalImageSize.width
          offsetY = (container.height - originalImageSize.height * scale) / 2
        } else {
          scale = container.height / originalImageSize.height
          offsetX = (container.width - originalImageSize.width * scale) / 2
        }

        processedResults.value = detectionResults.value.map(item => {
          const [x_min, y_min, x_max, y_max] = item.bbox // 정규화된 좌표
          return {
            ...item,
            style: {
              position: 'absolute',
              left: `${(x_min * originalImageSize.width * scale) + offsetX}px`,
              top: `${(y_min * originalImageSize.height * scale) + offsetY}px`,
              width: `${((x_max - x_min) * originalImageSize.width) * scale}px`,
              height: `${((y_max - y_min) * originalImageSize.height) * scale}px`,
            }
          }
        })
      }, 100) // 렌더링을 기다리기 위한 짧은 지연

    } catch (e) {
      console.error("Error parsing results JSON:", e)
      detectionResults.value = []
    }
  }
  if (route.query.image) {
    imageUrl.value = route.query.image
  }

  // 2. 로딩 상태를 해제합니다.
  isLoading.value = false
})
</script>

<style scoped>
.page-section {
  border-radius: 20px;
  padding: 32px;
  margin: 0 auto;
  max-width: 1200px;
}
.image-card, .results-card {
  border-radius: 16px;
  height: 100%;
  min-height: 400px;
}
.results-card {
  padding: 8px;
}
.image-container {
  position: relative;
  width: 100%;
  height: 400px; /* q-img의 높이와 일치시키거나, 동적으로 조절 */
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Bounding Box 스타일 시작 */
.bounding-box {
  border: 2px solid #2196f3;
  box-sizing: border-box;
  pointer-events: none; /* 박스가 이미지 클릭을 방해하지 않도록 함 */
  transition: border-color 0.2s, border-width 0.2s;
}

.bounding-box.bounding-box--hovered {
  border-color: #ff6f00; /* 하이라이트 색상 (주황색) */
  border-width: 3px;
}

.box-label {
  position: absolute;
  top: -22px;
  left: -2px;
  background-color: #2196f3;
  color: white;
  padding: 2px 6px;
  font-size: 12px;
  font-weight: 500;
  border-radius: 4px;
  white-space: nowrap;
  transition: background-color 0.2s;
}

.bounding-box--hovered .box-label {
  background-color: #ff6f00;
}
/* Bounding Box 스타일 끝 */
</style>
