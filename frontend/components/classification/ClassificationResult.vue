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

    <!-- 메인 카드: 수하물 분석 결과 -->
    <div class="page-section" style="background:#f8fbff; border:1px solid #e3f0fa;">
      <div style="text-align:center; font-weight:600; font-size:1.2rem; margin-bottom:16px; display:flex; align-items:center; justify-content:center; gap:8px;">
        <q-icon name="analytics" color="primary" size="28px" />
        수하물 분석 결과
      </div>
      <div style="text-align:center; color:#888; font-size:1rem; margin-bottom:24px;">
        업로드하신 이미지를 기반으로 분석된 수하물 정보입니다
      </div>
      
      <!-- 분석 결과 컨테이너 -->
      <div style="background:#fff; border-radius:16px; padding:24px; box-shadow:0 2px 8px rgba(33,150,243,0.08);">
        <div class="row q-col-gutter-md">
          <!-- 왼쪽: 원본 이미지 -->
          <div class="col-12 col-md-6">
            <div style="font-weight:600; font-size:1.1rem; margin-bottom:16px; text-align:center; color:#333;">
              원본 이미지
            </div>
            <q-card flat bordered class="image-card" style="text-align: center; height: 450px; display: flex; align-items: center; justify-content: center;">
              <div ref="imageContainerRef" class="image-container" style="position: relative; display: inline-block; width: 100%; height: 100%;">
                <img 
                  :src="imageUrl" 
                  style="border-radius: 16px; max-width: 100%; max-height: 100%; object-fit: contain;" 
                  @load="isImageLoaded = true"
                  @error="handleImageError"
                  alt="분석된 이미지"
                />
                

                <!-- Bounding Box 표시 시작 -->
                <template v-if="isImageLoaded">
                  <div
                    v-for="(item, index) in detectionResults"
                    :key="item.item_id || item.name_ko"
                    :class="['bounding-box', { 'bounding-box--hovered': hoveredIndex === index }]"
                    :style="calculateBoxStyleForMain(item.bbox, imageContainerRef)"
                  >
                    <div class="box-label">{{ item.name_ko }}</div>
                  </div>
                </template>
                <!-- Bounding Box 표시 끝 -->

              </div>
            </q-card>

            <!-- 여행지 입력 UI -->
            <div class="column items-center q-mt-md" style="min-height: 60px;">
              <transition
                appear
                enter-active-class="animated fadeIn"
                leave-active-class="animated fadeOut"
                @after-leave="isSaveButtonVisible = true"
              >
                <div v-if="showDestinationInput" class="row items-center q-gutter-md">
                  <q-input
                    v-model="destination"
                    label="여행지 입력"
                    outlined
                    dense
                    autofocus
                    @keyup.enter="saveAnalysisResults"
                  />
                  <q-btn 
                    label="저장" 
                    color="positive"
                    @click="saveAnalysisResults"
                    :loading="isSavingResults"
                  />
                  <q-btn 
                    label="취소" 
                    color="grey-7"
                    flat
                    @click="showDestinationInput = false"
                  />
                </div>
              </transition>
            </div>

            

          </div>

          <!-- 오른쪽: 탐지 결과 -->
          <div class="col-12 col-md-6">
            <div style="font-weight:600; font-size:1.1rem; margin-bottom:16px; text-align:center; color:#333;">
              탐지 결과
            </div>
            <q-card flat bordered class="results-card" style="height: 450px;">
              <div v-if="isLoading" class="column items-center justify-center" style="height:100%;">
                <q-spinner-dots color="primary" size="3em" />
                <div class="q-mt-md text-grey-7">결과를 불러오고 있습니다...</div>
              </div>
              <div v-else-if="detectionResults.length === 0" class="column items-center justify-center" style="height:100%;">
                <q-icon name="search_off" size="3em" color="grey-5" />
                <div class="q-mt-md text-grey-7">탐지된 물품이 없습니다.</div>
              </div>
              <div v-else class="column" style="height:100%;">
                <q-card-section class="row items-center justify-between q-py-sm">
                  <div class="text-weight-bold">탐지된 물품 목록</div>
                  <q-btn icon="edit" label="물품 수정/추가" flat dense @click="openEditModal" />
                </q-card-section>
                <q-separator />
                <q-scroll-area style="height: 350px;" class="col">
                  <q-list separator>
                  <div v-for="(item, index) in detectionResults" :key="item.item_id || item.name_ko">
                    <q-item 
                      @mouseenter="hoveredIndex = index"
                      @mouseleave="hoveredIndex = null"
                      clickable
                      @click="toggleAccordion(index)"
                    >
                      <q-item-section avatar>
                        <q-icon :name="getIconFor(item.name_ko)" color="primary" />
                      </q-item-section>
                      <q-item-section>
                        <q-item-label class="text-weight-medium">{{ item.name_ko }}</q-item-label>
                        <q-item-label caption v-if="item.confidence">정확도: {{ (item.confidence * 100).toFixed(0) }}%</q-item-label>
                      </q-item-section>
                      <q-item-section side>
                        <div class="row items-center no-wrap">
                          <div class="column items-end">
                            <q-badge :color="getSpecialCarryOnColor(item.carry_on_allowed)" class="q-mb-xs status-badge-simple">
                              기내
                            </q-badge>
                            <q-badge :color="getCheckedColor(item.checked_baggage_allowed)" class="status-badge-simple">
                              위탁
                            </q-badge>
                          </div>
                          <q-icon class="q-ml-sm" :name="expandedIndex === index ? 'expand_less' : 'expand_more'" />
                        </div>
                      </q-item-section>
                    </q-item>
                    <q-slide-transition>
                      <div v-show="expandedIndex === index">
                        <q-separator />
                        <div class="details-section q-pa-md">
                          <div class="row items-center q-mb-sm">
                            <div class="text-weight-bold q-mr-md">기내 반입:</div>
                            <q-badge :color="getSpecialCarryOnColor(item.carry_on_allowed)" class="status-badge-large">
                              {{ item.carry_on_allowed || '확인 불가' }}
                            </q-badge>
                          </div>
                          <div class="row items-center q-mb-md">
                            <div class="text-weight-bold q-mr-md">위탁 수하물:</div>
                            <q-badge :color="getCheckedColor(item.checked_baggage_allowed)" class="status-badge-large">
                              {{ item.checked_baggage_allowed || '확인 불가' }}
                            </q-badge>
                          </div>
                          <div class="text-caption text-grey-8">{{ item.notes || '상세한 규정 내용이 없습니다.' }}</div>
                        </div>
                      </div>
                    </q-slide-transition>
                  </div>
                  </q-list>
                </q-scroll-area>
              </div>
            </q-card>
          </div>
        </div>
      </div>
    </div>

                <!-- 하단 액션 버튼들 -->
    <div class="row justify-center q-mt-lg q-gutter-md">
      <q-btn 
        icon="photo_camera" 
        label="다른 이미지 선택" 
        color="primary" 
        outline
        @click="selectNewImage"
      />
      <transition
        appear
        enter-active-class="animated fadeIn"
        leave-active-class="animated fadeOut"
      >
        <q-btn 
          v-if="isSaveButtonVisible"
          icon="save" 
          label="분석 결과 저장" 
          color="positive"
          @click="isSaveButtonVisible = false; showDestinationInput = true"
          :disable="isSavingResults"
        />
      </transition>
    </div>

    <!-- 물품 수정/추가 팝업 -->
    <q-dialog v-model="showEditModal" full-width full-height>
      <q-card class="column no-wrap">
        <q-card-section class="row no-wrap q-pa-none col">
          <!-- 팝업 왼쪽 (70%) -->
          <div class="col-7 q-pa-md">
            <q-card flat bordered class="fit column no-wrap items-center justify-center">
              <div style="font-weight:600; font-size:1.2rem; margin: 16px 0; text-align:center;">
                원본 이미지 (BBox를 그려주세요)
              </div>
              <div ref="editorImageContainer" class="editor-image-container">
                <q-img :src="imageUrl" fit="contain" class="fit"/>
                <!-- BBox 그리기 오버레이 -->
                <div 
                  class="drawing-overlay"
                  @mousedown="handleMouseDown"
                  @mousemove="handleMouseMove"
                  @mouseup="handleMouseUp"
                  @mouseleave="handleMouseUp" 
                >
                  <!-- 현재 그리는 BBox -->
                  <div v-if="isDrawing" class="drawing-rect" :style="drawingRectStyle"></div>
                  <!-- 이미 추가된 BBox들 -->
                  <template v-for="(item, index) in itemsInEditor" :key="`edit-box-${item.item_id || index}`">
                    <div 
                      v-if="item.bbox && !item.isDeleted && !item.isDrawingBbox"
                      class="drawn-box"
                      :style="getEditorBoxStyle(item.bbox)"
                      :class="{ 'drawn-box--hovered': editorHoveredIndex === index }"
                    >
                      <div class="box-label">{{ item.name_ko }}</div>
                    </div>
                  </template>
                </div>
              </div>
            </q-card>
          </div>
          
          <!-- 팝업 오른쪽 (30%) -->
          <div class="col-5 q-pa-md column">
            <q-card flat bordered class="fit column no-wrap">
              <q-card-section class="row items-center justify-between q-py-sm">
                <div class="text-weight-bold">물품 목록</div>
                <q-btn icon="add" label="물품 추가" flat dense @click="addNewItem" />
              </q-card-section>
              <q-separator />
              <q-scroll-area class="col">
                <q-list separator class="q-pt-none">
                  <q-item 
                    v-for="(item, index) in itemsInEditor" 
                    :key="item.item_id || `new-${index}`" 
                    :class="{ 'bg-grey-3': item.isDeleted, 'item-confirmed': item.isConfirmed }"
                    :style="{ opacity: item.isDeleted ? 0.6 : 1 }"
                    @mouseenter="editorHoveredIndex = index"
                    @mouseleave="editorHoveredIndex = null"
                  >
                    <q-item-section>
                      <!-- 이름 입력 UI (신규 또는 수정 시) -->
                      <q-select
                        :ref="(el) => { if (el) searchSelectRefs[index] = el }"
                        v-if="(item.isNew && !item.isConfirmed) || item.isEditing"
                        v-model="item.name_ko"
                        :label="item.isNew ? '물품명 입력 후 Enter' : '물품명 수정 후 Enter'"
                        autofocus dense use-input fill-input hide-selected
                        :options="autocompleteSuggestions"
                        @new-value="handleNewValue"
                        new-value-mode="add-unique"
                        @keyup.enter="handleEnterKey($event, index)"
                        @input-value="(val) => item.name_ko = val"
                        autocomplete="off"
                      >
                        <template v-slot:no-option>
                          <q-item><q-item-section class="text-grey">일치하는 항목이 없습니다.</q-item-section></q-item>
                        </template>
                      </q-select>

                      <!-- 이름 텍스트 (확정 또는 기본 상태 시) -->
                      <q-item-label v-if="!((item.isNew && !item.isConfirmed) || item.isEditing)" :class="{ 'text-grey-6': item.isDeleted, 'text-strike': item.isDeleted }">
                        {{ item.name_ko }}
                      </q-item-label>
                    </q-item-section>

                    <q-item-section side>
                      <div class="row no-wrap items-center">

                        <!-- For NEW items -->
                        <template v-if="item.isNew">
                          <q-btn
                            v-if="!item.isConfirmed"
                            icon="check_circle" flat round dense no-ripple
                            @click="resolveItem(item)"
                            :disable="!item.name_ko"
                            class="action-btn action-btn--confirm"
                          >
                            <q-tooltip>항목 확정</q-tooltip>
                          </q-btn>
                          
                          <q-btn
                            v-if="item.isConfirmed && !item.isDeleted"
                            :icon="item.bbox ? 'replay' : 'edit_location'"
                            flat round dense no-ripple
                            @click="startRedrawBbox(item, index)"
                            :color="item.bbox ? 'positive' : (activeDrawIndex === index ? 'primary' : 'grey')"
                          >
                            <q-tooltip>{{ item.bbox ? '위치 다시 지정' : '위치 지정' }}</q-tooltip>
                          </q-btn>

                          <q-btn
                            v-if="!item.isDeleted"
                            icon="delete" flat round dense no-ripple
                            @click="toggleDeleteItem(item)"
                            class="action-btn action-btn--delete"
                          >
                            <q-tooltip>삭제</q-tooltip>
                          </q-btn>
                        </template>

                        <!-- For EXISTING items -->
                        <template v-if="!item.isNew">
                          <!-- EDITING state -->
                          <template v-if="item.isEditing">
                            <q-btn
                              icon="check_circle" flat round dense no-ripple
                              @click="confirmItemEdit(item)"
                              class="action-btn action-btn--confirm"
                            >
                              <q-tooltip>항목 확정</q-tooltip>
                            </q-btn>
                            <q-btn
                              icon="cancel" flat round dense no-ripple
                              @click="toggleEditMode(item)"
                              class="action-btn action-btn--cancel"
                            >
                              <q-tooltip>수정 취소</q-tooltip>
                            </q-btn>
                            <q-btn
                              icon="edit_location" flat round dense no-ripple
                              @click="startRedrawBbox(item, index)"
                              class="action-btn action-btn--location"
                            >
                              <q-tooltip>위치 다시 지정</q-tooltip>
                            </q-btn>
                          </template>
                          <!-- NORMAL state -->
                          <template v-else>
                            <q-btn
                              v-if="!item.isDeleted"
                              icon="edit" flat round dense no-ripple
                              @click="toggleEditMode(item)"
                              class="action-btn action-btn--edit"
                            >
                              <q-tooltip>물품 수정</q-tooltip>
                            </q-btn>
                          </template>

                          <!-- Delete/Restore button (always visible for existing items) -->
                          <q-btn
                            :icon="item.isDeleted ? 'undo' : 'delete'" flat round dense no-ripple
                            @click="toggleDeleteItem(item)"
                            :class="item.isDeleted ? 'action-btn action-btn--undo' : 'action-btn action-btn--delete'"
                          >
                            <q-tooltip>{{ item.isDeleted ? '복구' : '삭제' }}</q-tooltip>
                          </q-btn>
                        </template>

                      </div>
                    </q-item-section>
                  </q-item>
                </q-list>
              </q-scroll-area>
            </q-card>
          </div>
        </q-card-section>

        <q-separator />
        <q-card-actions align="right" class="q-pa-md">
          <q-btn label="취소" color="grey-7" @click="showEditModal = false" />
          <q-btn label="저장" color="primary" @click="saveChanges" :loading="isSaving" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- 분류 토스트 -->
    <ClassificationToast 
      v-if="showToast"
      :title="toastTitle"
      :message="toastMessage"
      redirect-to="/"
    />

  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, nextTick, onBeforeUpdate } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useQuasar } from 'quasar'
import ClassificationToast from './ClassificationToast.vue'
import { useAuth } from '~/composables/useAuth'

const $q = useQuasar()
const route = useRoute()
const router = useRouter()
const { user } = useAuth()

const isLoading = ref(true)
const isSaving = ref(false)
const isSavingResults = ref(false)
const imageUrl = ref('')
const imageId = ref(null)
const detectionResults = ref([])
const imageContainerRef = ref(null)
const hoveredIndex = ref(null)
const originalImageSize = ref({ width: 1, height: 1 });
const expandedIndex = ref(null); // For accordion
const isImageLoaded = ref(false);

// 토스트 상태
const showToast = ref(false)
const toastTitle = ref('')
const toastMessage = ref('')

// --- Editor Modal State ---
const showEditModal = ref(false)
const itemsInEditor = ref([])
const autocompleteSuggestions = ref([])
const editorImageContainer = ref(null)
const editorHoveredIndex = ref(null)
const searchSelectRefs = ref([]);

// --- BBox Drawing State ---
const isDrawing = ref(false)
const drawStartPoint = ref({ x: 0, y: 0 })
const drawingRect = ref({ x: 0, y: 0, width: 0, height: 0 })
const activeDrawIndex = ref(null)

// --- Destination State ---
const showDestinationInput = ref(false)
const destination = ref('')
const isSaveButtonVisible = ref(true)


// BBox 스타일 계산 로직을 공통 함수로 추출
const calculateBoxStyleForMain = (bbox, containerEl) => {
  if (!bbox || !containerEl) return { display: 'none' };

  const imgEl = containerEl.querySelector('img');
  if (!imgEl) return { display: 'none' };

  // Get rendered dimensions of the image
  const displayedWidth = imgEl.clientWidth;
  const displayedHeight = imgEl.clientHeight;

  // Get position of image and container relative to viewport
  const imgRect = imgEl.getBoundingClientRect();
  const containerRect = containerEl.getBoundingClientRect();

  // Calculate the offset of the image relative to the container
  const offsetX = imgRect.left - containerRect.left;
  const offsetY = imgRect.top - containerRect.top;

  const [x_min_norm, y_min_norm, x_max_norm, y_max_norm] = bbox;

  const left = offsetX + (x_min_norm * displayedWidth);
  const top = offsetY + (y_min_norm * displayedHeight);
  const width = (x_max_norm - x_min_norm) * displayedWidth;
  const height = (y_max_norm - y_min_norm) * displayedHeight;

  return {
    position: 'absolute',
    left: `${left}px`,
    top: `${top}px`,
    width: `${width}px`,
    height: `${height}px`,
  };
};


const calculateBoxStyleForModal = (bbox, containerEl, imageSize) => {
  if (!bbox || !containerEl || !imageSize || imageSize.width === 1) return {};

  const containerRect = containerEl.getBoundingClientRect();
  if (containerRect.width === 0) return {};

  const imageRatio = imageSize.width / imageSize.height;
  const containerRatio = containerRect.width / containerRect.height;

  let scale = 1;
  let offsetX = 0;
  let offsetY = 0;

  if (imageRatio > containerRatio) {
    scale = containerRect.width / imageSize.width;
    offsetY = (containerRect.height - (imageSize.height * scale)) / 2;
  } else {
    scale = containerRect.height / imageSize.height;
    offsetX = (containerRect.width - (imageSize.width * scale)) / 2;
  }

  const [x_min, y_min, x_max, y_max] = bbox;

  return {
    position: 'absolute',
    left: `${(x_min * imageSize.width * scale) + offsetX}px`,
    top: `${(y_min * imageSize.height * scale) + offsetY}px`,
    width: `${((x_max - x_min) * imageSize.width) * scale}px`,
    height: `${((y_max - y_min) * imageSize.height) * scale}px`,
  };
};


const drawingRectStyle = computed(() => ({
  left: `${drawingRect.value.x}px`,
  top: `${drawingRect.value.y}px`,
  width: `${drawingRect.value.width}px`,
  height: `${drawingRect.value.height}px`,
}))

const openEditModal = async () => {
  try {
    const response = await fetch(`http://${window.location.hostname}:5001/api/items/results/${imageId.value}`);
    if (!response.ok) {
      throw new Error('최신 물품 정보를 불러오는 데 실패했습니다.');
    }
    const latestResultsWithAbsoluteBbox = await response.json();

    const normalizedResults = latestResultsWithAbsoluteBbox.map(item => {
      if (item.bbox && originalImageSize.value.width > 1) {
        const [x_min, y_min, x_max, y_max] = item.bbox;
        const { width, height } = originalImageSize.value;
        return {
          ...item,
          bbox: [x_min / width, y_min / height, x_max / width, y_max / height]
        };
      }
      return item;
    });

    detectionResults.value = normalizedResults;

    itemsInEditor.value = JSON.parse(JSON.stringify(normalizedResults)).map(item => ({ 
      ...item, 
      isDeleted: false, 
      isEditing: false, 
      isDrawingBbox: false, 
      originalName: item.name_ko
    }));
    showEditModal.value = true;

  } catch (error) {
    console.error('Error opening edit modal:', error);
    $q.notify({ type: 'negative', message: error.message || '오류가 발생했습니다.' });
  }
}

const addNewItem = () => {
  if (itemsInEditor.value.some(item => item.isNew && !item.isConfirmed)) return;
  itemsInEditor.value.unshift({ isNew: true, name_ko: '', bbox: null, isDeleted: false, isConfirmed: false, isEditing: false, isDrawingBbox: false });
}

const toggleDeleteItem = (item) => {
  item.isDeleted = !item.isDeleted
}

const toggleEditMode = (item) => {
  item.isEditing = !item.isEditing;
  // 수정 취소 시, 원래 이름으로 복원
  if (!item.isEditing) {
    item.name_ko = item.originalName;
  }
}

const confirmItemEdit = (item) => {
  if (!item.name_ko) {
    $q.notify({ message: '물품명을 입력하거나 선택해주세요.', color: 'warning' });
    return;
  }
  item.isEditing = false;
  item.originalName = item.name_ko; // 수정된 이름을 새로운 원본 이름으로 저장
}

const startRedrawBbox = (item, index) => {
  item.isDrawingBbox = true;
  item.bbox = null; // 이전 bbox를 즉시 제거
  // 이전 bbox가 사라지는 DOM 업데이트를 기다린 후 그리기 모드 활성화
  nextTick(() => {
    activateDrawing(index);
  });
}

const activateDrawing = (index) => {
  if (itemsInEditor.value[index].isDeleted) return
  activeDrawIndex.value = index
  $q.notify({ 
    message: '이미지 위에서 드래그하여 물품의 위치를 지정하세요.',
    color: 'info',
    position: 'top',
    icon: 'edit_location'
  })
}

const handleMouseDown = (e) => {
  if (activeDrawIndex.value === null) return
  const rect = editorImageContainer.value.getBoundingClientRect()
  isDrawing.value = true
  drawStartPoint.value = { x: e.clientX - rect.left, y: e.clientY - rect.top }
  drawingRect.value = { x: drawStartPoint.value.x, y: drawStartPoint.value.y, width: 0, height: 0 }
}

const handleMouseMove = (e) => {
  if (!isDrawing.value) return
  const rect = editorImageContainer.value.getBoundingClientRect()
  const currentX = e.clientX - rect.left
  const currentY = e.clientY - rect.top
  const startX = drawStartPoint.value.x
  const startY = drawStartPoint.value.y

  drawingRect.value.x = Math.min(startX, currentX)
  drawingRect.value.y = Math.min(startY, currentY)
  drawingRect.value.width = Math.abs(currentX - startX)
  drawingRect.value.height = Math.abs(currentY - startY)
}

const normalizeBbox = (drawnRect, containerEl, imageSize) => {
  if (!drawnRect || !containerEl) return null;

  const container = containerEl.getBoundingClientRect();
  const containerRatio = container.width / container.height;
  const imageRatio = imageSize.width / imageSize.height;

  let scale = 1, offsetX = 0, offsetY = 0;
  if (imageRatio > containerRatio) {
    scale = container.width / imageSize.width;
    offsetY = (container.height - imageSize.height * scale) / 2;
  } else {
    scale = container.height / imageSize.height;
    offsetX = (container.width - imageSize.width * scale) / 2;
  }

  const imgX = drawnRect.x - offsetX;
  const imgY = drawnRect.y - offsetY;

  const x_min = (imgX / scale) / imageSize.width;
  const y_min = (imgY / scale) / imageSize.height;
  const x_max = ((imgX + drawnRect.width) / scale) / imageSize.width;
  const y_max = ((imgY + drawnRect.height) / scale) / imageSize.height;
  
  return [
      Math.max(0, Math.min(1, x_min)),
      Math.max(0, Math.min(1, y_min)),
      Math.max(0, Math.min(1, x_max)),
      Math.max(0, Math.min(1, y_max))
  ];
}

const handleMouseUp = () => {
  if (!isDrawing.value || activeDrawIndex.value === null) return;
  isDrawing.value = false;
  
  const item = itemsInEditor.value[activeDrawIndex.value];
  
  const normalized = normalizeBbox(drawingRect.value, editorImageContainer.value, originalImageSize.value);
  if (normalized) {
    item.bbox = normalized;
  }

  // 그리기 상태 종료
  if (item) {
    item.isDrawingBbox = false;
  }
  activeDrawIndex.value = null;
  drawingRect.value = { x: 0, y: 0, width: 0, height: 0 };
};

// 수정: 공통 함수를 사용하도록 변경
const getEditorBoxStyle = (bbox) => {
  return calculateBoxStyleForModal(bbox, editorImageContainer.value, originalImageSize.value);
}

const saveChanges = async () => {
    if (isSaving.value) return;

    isSaving.value = true;
    try {
        const itemsToAdd = itemsInEditor.value.filter(item => item.isNew && item.isConfirmed && !item.isDeleted && item.name_ko && item.bbox);
        const itemsToDelete = itemsInEditor.value.filter(item => !item.isNew && item.isDeleted);
        const itemsToUpdate = itemsInEditor.value.filter(item => 
          !item.isNew && 
          !item.isDeleted && 
          (item.name_ko !== item.originalName || JSON.stringify(item.bbox) !== JSON.stringify(detectionResults.value.find(d => d.item_id === item.item_id)?.bbox))
        );

        if (itemsToAdd.length === 0 && itemsToDelete.length === 0 && itemsToUpdate.length === 0) {
            $q.notify({ message: '변경 사항이 없습니다.', color: 'info' });
            return;
        }

        let currentResults = [...detectionResults.value];

        // 1. Update API 호출 (가장 먼저 처리)
        if (itemsToUpdate.length > 0) {
            const updatePayload = {
                image_id: imageId.value,
                items_to_update: itemsToUpdate.map(item => {
                    const denormalizedBbox = item.bbox ? [
                        item.bbox[0] * originalImageSize.value.width,
                        item.bbox[1] * originalImageSize.value.height,
                        item.bbox[2] * originalImageSize.value.width,
                        item.bbox[3] * originalImageSize.value.height
                    ] : null;

                    return {
                        item_id: item.item_id,
                        name_ko: item.name_ko,
                        bbox: denormalizedBbox
                    };
                })
            };

            const response = await fetch('http://' + window.location.hostname + ':5001/api/items/update', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(updatePayload)
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || '수정 중 오류가 발생했습니다.');
            }
            currentResults = await response.json();
        }

        // 2. 삭제 API 순차적 호출
        if (itemsToDelete.length > 0) {
            const deletePayload = {
                image_id: imageId.value,
                item_ids: itemsToDelete.map(item => item.item_id)
            };
            const response = await fetch('http://' + window.location.hostname + ':5001/api/items/delete', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(deletePayload)
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || '삭제 중 오류가 발생했습니다.');
            }
            currentResults = await response.json();
        }

        // 3. 추가 API 순차적 호출
        if (itemsToAdd.length > 0) {
            const addPayload = {
                image_id: imageId.value,
                new_items: itemsToAdd.map(item => {
                    const denormalizedBbox = item.bbox ? [
                        item.bbox[0] * originalImageSize.value.width,
                        item.bbox[1] * originalImageSize.value.height,
                        item.bbox[2] * originalImageSize.value.width,
                        item.bbox[3] * originalImageSize.value.height
                    ] : null;
                    return {
                        name_ko: item.name_ko,
                        bbox: denormalizedBbox
                    };
                })
            };
            const response = await fetch('http://' + window.location.hostname + ':5001/api/items/add', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(addPayload)
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || '추가 중 오류가 발생했습니다.');
            }
            currentResults = await response.json();
        }

        // 최종 결과로 UI 업데이트
        detectionResults.value = currentResults.map(item => {
          if (item.bbox && originalImageSize.value.width > 1) {
            const [x_min, y_min, x_max, y_max] = item.bbox;
            const { width, height } = originalImageSize.value;
            return {
              ...item,
              bbox: [x_min / width, y_min / height, x_max / width, y_max / height]
            };
          }
          return item;
        });

        $q.notify({ message: '성공적으로 저장되었습니다.', color: 'positive', icon: 'check' });

    } catch (error) {
        console.error('Error saving changes:', error);
        $q.notify({ message: `오류 발생: ${error.message}`, color: 'negative' });
    } finally {
        isSaving.value = false;
        showEditModal.value = false;
    }
};

const handleNewValue = (inputValue, doneFn) => {
  if (inputValue.length > 0) {
    if (!autocompleteSuggestions.value.some(s => s.toLowerCase() === inputValue.toLowerCase())) {
      doneFn(inputValue, 'add-unique');
    }
  }
}

const onSelectBlur = (evt, item) => {
  if (evt.target && evt.target.value === '') {
    item.name_ko = '';
  }
};

const resolveItem = (item) => {
  if (!item || !item.name_ko) {
    $q.notify({ message: '물품명을 입력하거나 선택해주세요.', color: 'warning' });
    return;
  }
  
  item.isConfirmed = true;
  
  $q.notify({
    message: `'${item.name_ko}'(으)로 확정되었습니다. 이제 위치를 지정해주세요.`,
    color: 'info',
    icon: 'edit_location',
    timeout: 2000
  });
};

const handleEnterKey = async (event, index) => {
  const selectComponent = searchSelectRefs.value[index];
  const currentInputValue = event.target.value;

  if (selectComponent && currentInputValue) {
    try {
            const response = await fetch(`http://${window.location.hostname}:5001/api/items/autocomplete?q=${currentInputValue}`);
      if (!response.ok) throw new Error('Network response was not ok');
      
      const suggestions = await response.json();
      autocompleteSuggestions.value = suggestions;
      
      selectComponent.showPopup();

    } catch (error) {
      console.error('Error fetching autocomplete suggestions on enter:', error);
      autocompleteSuggestions.value = [];
      selectComponent.showPopup();
    }
  }
};

const onImageLoad = () => {
  isImageLoaded.value = true;
}

const handleImageError = (error) => {
  console.error('이미지 로드 오류:', error);
  console.error('이미지 URL:', imageUrl.value);
  isImageLoaded.value = false;
}

const findDetectionResultIndex = (item) => {
  return detectionResults.value.findIndex(dr => dr.item_id === item.item_id);
};

const toggleAccordion = (index) => {
  if (expandedIndex.value === index) {
    expandedIndex.value = null;
  } else {
    expandedIndex.value = index;
  }
};

const getIconFor = (itemName) => {
  if (!itemName) return 'inventory_2';
  
  // 전자기기
  if (itemName.includes('노트북') || itemName.includes('Laptop')) return 'laptop';
  if (itemName.includes('폰') || itemName.includes('Phone')) return 'phone';
  if (itemName.includes('태블릿') || itemName.includes('Tablet')) return 'tablet';
  if (itemName.includes('카메라') || itemName.includes('Camera')) return 'camera_alt';
  if (itemName.includes('배터리') || itemName.includes('Battery')) return 'battery_charging_full';
  if (itemName.includes('충전기') || itemName.includes('Charger')) return 'power';
  
  // 액체류
  if (itemName.includes('액체') || itemName.includes('Liquid') || itemName.includes('물') || itemName.includes('Water')) return 'water_drop';
  if (itemName.includes('튜브') || itemName.includes('Tube')) return 'tube';
  if (itemName.includes('병') || itemName.includes('Bottle')) return 'local_drink';
  if (itemName.includes('샴푸') || itemName.includes('Shampoo')) return 'shower';
  if (itemName.includes('로션') || itemName.includes('Lotion')) return 'opacity';
  
  // 음식
  if (itemName.includes('음식') || itemName.includes('Food') || itemName.includes('라면') || itemName.includes('Ramen')) return 'restaurant';
  if (itemName.includes('김치') || itemName.includes('Kimchi')) return 'local_dining';
  if (itemName.includes('소스') || itemName.includes('Sauce')) return 'local_pizza';
  if (itemName.includes('과자') || itemName.includes('Snack')) return 'cookie';
  
  // 위험물품
  if (itemName.includes('가위') || itemName.includes('Scissors')) return 'content_cut';
  if (itemName.includes('나이프') || itemName.includes('Knife')) return 'dangerous';
  if (itemName.includes('칼') || itemName.includes('Blade')) return 'dangerous';
  if (itemName.includes('총') || itemName.includes('Gun')) return 'warning';
  
  // 개인용품
  if (itemName.includes('가방') || itemName.includes('Bag')) return 'shopping_bag';
  if (itemName.includes('지갑') || itemName.includes('Wallet')) return 'account_balance_wallet';
  if (itemName.includes('여권') || itemName.includes('Passport')) return 'badge';
  if (itemName.includes('캐리어') || itemName.includes('Suitcase')) return 'luggage';
  if (itemName.includes('안경') || itemName.includes('Glasses')) return 'visibility';
  
  // 화장품
  if (itemName.includes('립스틱') || itemName.includes('Lipstick')) return 'face';
  if (itemName.includes('화장') || itemName.includes('Makeup')) return 'face';
  if (itemName.includes('향수') || itemName.includes('Perfume')) return 'spa';
  
  // 의료용품
  if (itemName.includes('약') || itemName.includes('Medicine')) return 'medication';
  if (itemName.includes('마스크') || itemName.includes('Mask')) return 'masks';
  if (itemName.includes('물티슈') || itemName.includes('Wipes')) return 'cleaning_services';
  
  // 기타
  if (itemName.includes('담배') || itemName.includes('Cigarette')) return 'smoking_rooms';
  if (itemName.includes('열쇠') || itemName.includes('Key')) return 'vpn_key';
  if (itemName.includes('생리대') || itemName.includes('Pad')) return 'local_hospital';
  
  return 'inventory_2';
}

const getSpecialCarryOnColor = (status) => {
  if (!status) return 'grey';
  if (status.includes('특별') || status.includes('100 ml')) return 'amber';
  if (status === '예') return 'positive';
  if (status === '아니요') return 'negative';
  return 'grey';
};

const getCheckedColor = (status) => {
  if (status === '예') return 'positive';
  if (status === '아니요') return 'negative';
  return 'grey';
}

let resizeTimeout;
const handleResize = () => {
  clearTimeout(resizeTimeout);
  resizeTimeout = setTimeout(() => {
    // Re-calculate BBoxes on resize
    // This is a placeholder for a potential future improvement if needed
  }, 150);
}

onBeforeUpdate(() => {
  searchSelectRefs.value = [];
});

onMounted(() => {
  const resultsData = route.query.results ? JSON.parse(route.query.results) : null;

  if (resultsData) {
    detectionResults.value = resultsData.results || [];
    imageId.value = resultsData.image_id;
    originalImageSize.value = resultsData.image_size || { width: 1, height: 1 };
    // 분류 결과에 포함된 실제 이미지 URL을 우선적으로 사용
    if (resultsData.image_url) {
      imageUrl.value = resultsData.image_url;
    }
  }

  // 실제 이미지 URL이 없는 경우에만 blob URL을 사용 (폴백)
  if (!imageUrl.value && route.query.image) {
    imageUrl.value = route.query.image;
  }

  isLoading.value = false;

  // 페이드 인 애니메이션
  nextTick(() => {
    const container = document.querySelector('.page-section')
    if (container) {
      container.style.transition = 'opacity 0.3s ease-in'
      container.style.opacity = '1'
    }
  })

  window.addEventListener('resize', handleResize);
})

// 새로운 이미지 선택 함수
const selectNewImage = () => {
  // 페이드 아웃 애니메이션 시작
  const container = document.querySelector('.page-section')
  if (container) {
    container.style.transition = 'opacity 0.3s ease-out'
    container.style.opacity = '0'
  }
  
  // 애니메이션 완료 후 페이지 이동
  setTimeout(() => {
    // 현재 분석 정보 초기화
    detectionResults.value = []
    imageUrl.value = ''
    imageId.value = null
    originalImageSize.value = { width: 1, height: 1 }
    expandedIndex.value = null
    isImageLoaded.value = false
    hoveredIndex.value = null
    
    // Vue Router를 사용하여 분류 페이지로 이동 (쿼리 파라미터 제거)
    router.push('/classification')
  }, 300) // 0.3초 후 이동
}

// 분석 결과 저장 함수
const saveAnalysisResults = async () => {
  if (isSavingResults.value) return;

  if (!destination.value) {
    $q.notify({
      type: 'warning',
      message: '여행지를 입력해주세요.',
      position: 'top'
    });
    return;
  }
  
  isSavingResults.value = true;
  
  try {
    const token = localStorage.getItem('access_token');
    if (!token) {
      throw new Error('인증 토큰을 찾을 수 없습니다. 다시 로그인해주세요.');
    }

    const storedUser = JSON.parse(localStorage.getItem('user'));
    if (!storedUser || !storedUser.id) {
        throw new Error('사용자 정보를 찾을 수 없습니다. 다시 로그인해주세요.');
    }

    const realImageUrl = JSON.parse(route.query.results)?.image_url || imageUrl.value;

    const analysisData = {
      user_id: storedUser.id,
      image_id: imageId.value,
      image_size: originalImageSize.value,
      detected_items: detectionResults.value.map(item => ({
        name_ko: item.name_ko,
        name_en: item.name_en,
        confidence: item.confidence,
        carry_on_allowed: item.carry_on_allowed,
        checked_baggage_allowed: item.checked_baggage_allowed,
        notes: item.notes,
        notes_EN: item.notes_EN,
        source: item.source,
        bbox: item.bbox
      })),
      total_items: detectionResults.value.length,
      analysis_date: new Date().toISOString(),
      destination: destination.value
    };

    const response = await fetch('http://' + window.location.hostname + ':5001/api/analysis/save', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(analysisData)
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || '저장 중 오류가 발생했습니다.');
    }

    const result = await response.json();
    
    toastTitle.value = '저장 완료'
    toastMessage.value = `분석 결과가 성공적으로 저장되었습니다. (총 ${detectionResults.value.length}개 물품)`
    showToast.value = true
    
    showDestinationInput.value = false;
    destination.value = '';

  } catch (error) {
    console.error('Error saving analysis results:', error);
    toastTitle.value = '저장 실패'
    toastMessage.value = `저장 중 오류가 발생했습니다: ${error.message}`
    showToast.value = true
  } finally {
    isSavingResults.value = false;
  }
}

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
})
</script>

<style scoped>
.page-section { 
  border-radius: 20px; 
  padding: 32px; 
  margin: 0 auto; 
  max-width: 1200px; 
  width: 100%; 
  box-sizing: border-box; 
  opacity: 0; /* 초기 투명도 설정 */
  transition: opacity 0.3s ease-in; /* 기본 전환 효과 */
}
.image-card, .results-card { border-radius: 16px; height: 100%; min-height: 400px; }
.editor-image-container { position: relative; width: 100%; height: 100%; max-width: 100%; max-height: 100%; }
.drawing-overlay { position: absolute; top: 0; left: 0; width: 100%; height: 100%; cursor: crosshair; }
.drawing-rect { position: absolute; border: 2px dashed #ff6f00; background-color: rgba(255, 111, 0, 0.2); }
.drawn-box { position: absolute; border: 2px solid #2196f3; pointer-events: none; }
.bounding-box { border: 2px solid #2196f3; box-sizing: border-box; pointer-events: none; transition: border-color 0.2s, border-width 0.2s; }
.bounding-box.bounding-box--hovered { border-color: #ff6f00; border-width: 3px; }
.box-label { position: absolute; top: -22px; left: -2px; background-color: #2196f3; color: white; padding: 2px 6px; font-size: 12px; font-weight: 500; border-radius: 4px; white-space: nowrap; transition: background-color 0.2s; }
.bounding-box--hovered .box-label { background-color: #ff6f00; }
.text-strike { text-decoration: line-through; }
.drawn-box--hovered { border-color: #ff6f00 !important; }
.item-confirmed {
  background-color: #f5f5f5; 
}
.confirmed-item {
  font-style: italic;
  color: #555;
}
.details-section {
  background-color: #f8f9fa;
  border-top: 1px solid #eee;
}
.status-badge-large {
  font-weight: bold;
  padding: 4px 8px;
  border-radius: 8px;
  color: white;
}
.status-badge-simple {
  font-weight: 500;
  padding: 2px 6px;
  border-radius: 4px;
  color: white;
  font-size: 0.7rem;
  width: 35px;
  text-align: center;
}

.control-btn--confirm:hover {
  background-color: rgba(46, 125, 50, 0.1);
  color: #2e7d32;
}
.control-btn--edit:hover {
  background-color: rgba(25, 118, 210, 0.1);
  color: #1976d2;
}
.control-btn--delete:hover {
  background-color: rgba(211, 47, 47, 0.1);
  color: #d32f2f;
}
.control-btn--undo:hover {
  background-color: rgba(2, 136, 209, 0.1);
  color: #0288d1;
}

/* Action Button Styles in Modal */
.action-btn {
  position: relative;
  overflow: hidden;
  transition: color 0.3s;
  padding: 6px 12px !important;
  min-height: auto !important;
  height: auto !important;
  border-radius: 4px !important;
}

.action-btn::after {
  content: '';
  position: absolute;
  left: 0; right: 0; bottom: 0; top: 100%;
  transition: top 0.2s cubic-bezier(0.4,0,0.2,1);
  z-index: 1;
  pointer-events: none;
}

.action-btn:hover::after {
  top: 0;
}

.action-btn .q-btn__content {
  position: relative;
  z-index: 2;
}

/* Edit & Location */
.action-btn--edit, .action-btn--location {
  color: #1976d2;
}
.action-btn--edit:hover, .action-btn--location:hover {
  color: white !important;
}
.action-btn--edit::after, .action-btn--location::after {
  background: #1976d2;
}

/* Confirm */
.action-btn--confirm {
  color: #2e7d32;
}
.action-btn--confirm:hover {
  color: white !important;
}
.action-btn--confirm::after {
  background: #2e7d32;
}

/* Cancel & Delete */
.action-btn--cancel, .action-btn--delete {
  color: #d32f2f;
}
.action-btn--cancel:hover, .action-btn--delete:hover {
  color: white !important;
}
.action-btn--cancel::after, .action-btn--delete::after {
  background: #d32f2f;
}

/* Undo */
.action-btn--undo {
  color: #ed6c02;
}
.action-btn--undo:hover {
  color: white !important;
}
.action-btn--undo::after {
  background: #ed6c02;
}
</style>