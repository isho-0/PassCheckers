<template>
  <div style="min-height: 125vh;">
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
      <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; min-height:220px; border:1.5px dashed #cbe3f7; border-radius:16px; background:#fff; margin-bottom:18px;">
        <input
          ref="fileInput"
          type="file"
          accept="image/jpeg, image/png, image/gif"
          style="display: none"
          @change="onFileSelected"
        />
        <q-icon name="image" size="48px" color="grey-4" style="margin-bottom:12px;" />
        <div style="color:#888; font-size:1.1rem; margin-bottom:8px;">이미지를 업로드하세요</div>
        <div style="color:#bbb; font-size:0.95rem; margin-bottom:12px;">이미지를 드래그 앤 드롭하거나 파일을 선택하세요</div>
        <q-btn
          color="primary"
          label="파일 선택하기"
          unelevated
          style="margin-bottom:8px;"
          class="file-upload-btn"
          @click="onSelectFileClick"
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
</template>

<script setup>
import { ref } from 'vue'

const fileInput = ref(null)

const onSelectFileClick = () => {
  fileInput.value?.click()
}

const onFileSelected = (event) => {
  const files = event.target.files
  if (files && files.length > 0) {
    // TODO: 선택된 파일 처리
    console.log('Selected file:', files[0])
    // 여기에 파일 업로드 로직을 추가할 수 있습니다.
  }
}
</script>
