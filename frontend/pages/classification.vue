<template>
  <div>
    <!-- 분류 결과가 있는 경우 ClassificationResult 컴포넌트 표시 -->
    <ClassificationResult v-if="hasClassificationResults" />
    
    <!-- 분류 결과가 없는 경우 기본 랜딩 페이지 표시 -->
    <div v-else style="min-height: 125vh;">
      <!-- 상단 안내문구 -->
      <section style="text-align:center; margin-top:48px; margin-bottom:32px;">
        <h1 style="font-size:2.2rem; font-weight:bold;">
          여행을 더 편리하게, <span style="color:var(--main-blue);">수하물 도우미</span>
        </h1>
        <p style="color:#888; margin-top:8px;">
          수하물 분류, 무게 예측, 패킹 도우미까지 - 여행 준비의 모든 것을 도와드립니다
        </p>
      </section>

      <!-- 메인 카드: 수하물 분류하기 -->
      <div class="page-section" style="background:#f8fbff; border:1px solid #e3f0fa;">
        <div style="text-align:center; font-weight:600; font-size:1.2rem; margin-bottom:16px; display:flex; align-items:center; justify-content:center; gap:8px;">
          <q-icon name="inventory_2" color="primary" size="28px" />
          수하물 분류하기
        </div>
        <div style="text-align:center; color:#888; font-size:1rem; margin-bottom:24px;">
          수하물 이미지를 업로드하면 분류 결과를 확인하세요
        </div>
        <div 
          style="display:flex; flex-direction:column; align-items:center; justify-content:center; min-height:220px; border:1.5px dashed #cbe3f7; border-radius:16px; background:#fff; margin-bottom:18px; position: relative;"
          @drop="handleFileDrop"
          @dragover.prevent
          @dragenter.prevent="handleDragEnter"
          @dragleave="handleDragLeave"
          :class="{ 'drag-over': isDragOver }"
        >
          <q-icon name="image" size="48px" color="grey-4" style="margin-bottom:12px;" />
          <div style="color:#888; font-size:1.1rem; margin-bottom:8px;">이미지를 업로드하세요</div>
          <div style="color:#bbb; font-size:0.95rem; margin-bottom:12px;">이미지를 드래그 앤 드롭하거나 파일을 선택하세요</div>
          <q-btn 
            color="primary" 
            :label="isUploading ? '분류 중...' : '파일 선택하기'" 
            unelevated 
            style="margin-bottom:8px;" 
            class="file-upload-btn"
            :loading="isUploading"
            :disable="isUploading"
            @click="triggerFileInput"
          />
          <input
            ref="fileInput"
            type="file"
            accept="image/*"
            style="display: none"
            @change="handleFileSelect"
          />
        </div>
        <div style="text-align:center; color:#bbb; font-size:0.95rem;">
          지원되는 이미지 형식: JPG, PNG, GIF<br />최대 파일 크기: 10MB
        </div>
      </div>

      <div style="text-align:center; margin: 48px 0 24px 0;">
        <span style="font-size:1.15rem; font-weight:600; color:#2196f3;">
          이런 기능도 함께 이용해보세요!
        </span>
      </div>

      <!-- 하단 카드 3개 -->
      <div style="display:flex; gap:24px; justify-content:center; margin-top:32px; flex-wrap:wrap;">
        <q-card clickable flat bordered @click="$router.push('/weight')" style="flex:1 1 220px; max-width:320px; min-width:220px; border-radius:16px; box-shadow:0 2px 8px rgba(33,150,243,0.08); padding:32px 20px; text-align:center; display:flex; flex-direction:column; align-items:center; cursor:pointer; transition:box-shadow 0.2s;">
          <q-icon name="luggage" color="primary" size="36px" style="margin-bottom:12px;" />
          <div style="font-weight:600; margin-bottom:8px;">수하물 무게 예측</div>
          <div style="color:#888; font-size:0.98rem;">이미지를 통해 수하물의 무게를 예측하고 항공사 제한을 확인하세요</div>
        </q-card>
        <q-card clickable flat bordered @click="$router.push('/recommend')" style="flex:1 1 220px; max-width:320px; min-width:220px; border-radius:16px; box-shadow:0 2px 8px rgba(33,150,243,0.08); padding:32px 20px; text-align:center; display:flex; flex-direction:column; align-items:center; cursor:pointer; transition:box-shadow 0.2s;">
          <q-icon name="flight_takeoff" color="primary" size="36px" style="margin-bottom:12px;" />
          <div style="font-weight:600; margin-bottom:8px;">여행 추천</div>
          <div style="color:#888; font-size:0.98rem;">계절과 취향에 맞는 최적의 여행지를 추천해드립니다</div>
        </q-card>
        <q-card clickable flat bordered @click="$router.push('/community')" style="flex:1 1 220px; max-width:320px; min-width:220px; border-radius:16px; box-shadow:0 2px 8px rgba(33,150,243,0.08); padding:32px 20px; text-align:center; display:flex; flex-direction:column; align-items:center; cursor:pointer; transition:box-shadow 0.2s;">
          <q-icon name="forum" color="primary" size="36px" style="margin-bottom:12px;" />
          <div style="font-weight:600; margin-bottom:8px;">커뮤니티</div>
          <div style="color:#888; font-size:0.98rem;">여행자들과 정보를 나누고 소통할 수 있습니다</div>
        </q-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useQuasar } from 'quasar'
import ClassificationResult from '~/components/classification/ClassificationResult.vue'

definePageMeta({
  middleware: 'auth'
})

const route = useRoute()
const router = useRouter()
const $q = useQuasar()

// 파일 업로드 관련 상태
const fileInput = ref(null)
const isDragOver = ref(false)
const isUploading = ref(false)

// 분류 결과가 있는지 확인하는 computed 속성
const hasClassificationResults = computed(() => {
  return route.query.results && route.query.image
})

// 파일 입력 트리거
const triggerFileInput = () => {
  fileInput.value?.click()
}

// 파일 선택 처리
const handleFileSelect = (event) => {
  const file = event.target.files?.[0]
  if (file) {
    processFile(file)
  }
}

// 드래그 앤 드롭 처리
const handleFileDrop = (event) => {
  event.preventDefault()
  isDragOver.value = false
  
  const file = event.dataTransfer.files?.[0]
  if (file) {
    processFile(file)
  }
}

// 파일 처리 및 업로드
const processFile = async (file) => {
  // 파일 유효성 검사
  if (!file.type.startsWith('image/')) {
    if ($q && $q.notify) {
      $q.notify({
        type: 'negative',
        message: '이미지 파일만 업로드 가능합니다.',
        position: 'top'
      })
    } else {
      alert('이미지 파일만 업로드 가능합니다.')
    }
    return
  }

  if (file.size > 10 * 1024 * 1024) { // 10MB
    if ($q && $q.notify) {
      $q.notify({
        type: 'negative',
        message: '파일 크기는 10MB를 초과할 수 없습니다.',
        position: 'top'
      })
    } else {
      alert('파일 크기는 10MB를 초과할 수 없습니다.')
    }
    return
  }

  isUploading.value = true

  try {
    // FormData 생성
    const formData = new FormData()
    formData.append('image', file)

    // 백엔드로 이미지 업로드 및 분류 요청
    const response = await fetch('http://' + window.location.hostname + ':5001/classify', {
      method: 'POST',
      body: formData
    })

    if (!response.ok) {
      throw new Error('분류 요청에 실패했습니다.')
    }

    const result = await response.json()
    
    // 분류 결과와 함께 결과 페이지로 이동
    const imageUrl = URL.createObjectURL(file)
    const queryParams = {
      results: JSON.stringify({
        results: result.results || [],
        image_id: result.image_id,
        image_size: result.image_size || { width: 1, height: 1 }
      }),
      image: imageUrl
    }

    router.push({
      path: '/classification',
      query: queryParams
    })

  } catch (error) {
    console.error('분류 오류:', error)
    if ($q && $q.notify) {
      $q.notify({
        type: 'negative',
        message: `분류 중 오류가 발생했습니다: ${error.message}`,
        position: 'top'
      })
    } else {
      alert(`분류 중 오류가 발생했습니다: ${error.message}`)
    }
  } finally {
    isUploading.value = false
  }
}

// 드래그 오버 상태 관리
const handleDragEnter = () => {
  isDragOver.value = true
}

const handleDragLeave = () => {
  isDragOver.value = false
}
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

.drag-over {
  border-color: #2196f3 !important;
  background-color: #f8fbff !important;
  transform: scale(1.02);
  transition: all 0.2s ease;
}
</style>