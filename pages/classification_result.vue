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
            <div v-else class="column" style="height:100%;">
              <q-card-section class="row items-center justify-between q-py-sm">
                <div class="text-weight-bold">탐지된 물품 목록</div>
                <q-btn icon="edit" label="물품 수정/추가" flat dense @click="openEditModal" />
              </q-card-section>
              <q-separator />
              <q-list separator class="col">
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
                    <q-item-label caption v-if="item.confidence">정확도: {{ (item.confidence * 100).toFixed(0) }}%</q-item-label>
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
                  <div 
                    v-for="(item, index) in itemsInEditor.filter(i => i.bbox && !i.isDeleted)"
                    :key="`edit-box-${index}`"
                    class="drawn-box"
                    :style="getEditorBoxStyle(item.bbox)"
                    :class="{ 'drawn-box--hovered': editorHoveredIndex === index }"
                  >
                    <div class="box-label">{{ item.name_ko }}</div>
                  </div>
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
              <q-list separator class="col q-pt-none">
                <q-item 
                  v-for="(item, index) in itemsInEditor" 
                  :key="item.item_id || `new-${index}`" 
                  :class="{ 'bg-grey-3': item.isDeleted }"
                  @mouseenter="editorHoveredIndex = index"
                  @mouseleave="editorHoveredIndex = null"
                >
                  <q-item-section>
                    <q-select
                      v-if="item.isNew"
                      v-model="item.name_ko"
                      label="객체명을 검색하세요"
                      autofocus
                      dense
                      use-input
                      fill-input
                      hide-selected
                      :options="autocompleteSuggestions"
                      @filter="filterFn"
                      :disable="item.isDeleted"
                    >
                      <template v-slot:no-option>
                        <q-item>
                          <q-item-section class="text-grey">
                            일치하는 항목이 없습니다.
                          </q-item-section>
                        </q-item>
                      </template>
                    </q-select>
                    <q-item-label v-else :class="{ 'text-grey-6': item.isDeleted, 'text-strike': item.isDeleted }">{{ item.name_ko }}</q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <q-btn 
                      v-if="item.isNew && item.name_ko"
                      icon="edit_location"
                      flat
                      round
                      dense
                      @click="activateDrawing(index)"
                      :color="activeDrawIndex === index ? 'primary' : 'grey'"
                      :disable="item.isDeleted"
                    >
                      <q-tooltip>위치 지정</q-tooltip>
                    </q-btn>
                    <q-btn
                      :icon="item.isDeleted ? 'undo' : 'delete'"
                      flat
                      round
                      dense
                      @click="toggleDeleteItem(item)"
                    >
                      <q-tooltip>{{ item.isDeleted ? '복구' : '삭제' }}</q-tooltip>
                    </q-btn>
                  </q-item-section>
                </q-item>
              </q-list>
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

  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useQuasar } from 'quasar'

const $q = useQuasar()
const route = useRoute()

const isLoading = ref(true)
const isSaving = ref(false)
const imageUrl = ref('')
const imageId = ref(null)
const detectionResults = ref([])
const processedResults = ref([])
const imageContainerRef = ref(null)
const hoveredIndex = ref(null)

// --- Editor Modal State ---
const showEditModal = ref(false)
const itemsInEditor = ref([])
const autocompleteSuggestions = ref([])
const editorImageContainer = ref(null)
const editorHoveredIndex = ref(null) // New: For hovering in editor modal

// --- BBox Drawing State ---
const isDrawing = ref(false)
const drawStartPoint = ref({ x: 0, y: 0 })
const drawingRect = ref({ x: 0, y: 0, width: 0, height: 0 })
const activeDrawIndex = ref(null)

const drawingRectStyle = computed(() => ({
  left: `${drawingRect.value.x}px`,
  top: `${drawingRect.value.y}px`,
  width: `${drawingRect.value.width}px`,
  height: `${drawingRect.value.height}px`,
}))

const openEditModal = () => {
  itemsInEditor.value = JSON.parse(JSON.stringify(detectionResults.value)).map(item => ({ ...item, isDeleted: false }))
  showEditModal.value = true
}

const addNewItem = () => {
  if (itemsInEditor.value.some(item => item.isNew)) return
  itemsInEditor.value.unshift({ isNew: true, name_ko: '', bbox: null, isDeleted: false })
}

const toggleDeleteItem = (item) => {
  item.isDeleted = !item.isDeleted
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

const handleMouseUp = () => {
  if (!isDrawing.value || activeDrawIndex.value === null) return
  isDrawing.value = false
  
  const containerRect = editorImageContainer.value.getBoundingClientRect()
  const item = itemsInEditor.value[activeDrawIndex.value]

  const x_min = drawingRect.value.x / containerRect.width
  const y_min = drawingRect.value.y / containerRect.height
  const x_max = (drawingRect.value.x + drawingRect.value.width) / containerRect.width
  const y_max = (drawingRect.value.y + drawingRect.value.height) / containerRect.height

  item.bbox = [x_min, y_min, x_max, y_max]
  activeDrawIndex.value = null
  drawingRect.value = { x: 0, y: 0, width: 0, height: 0 }
}

const getEditorBoxStyle = (bbox) => {
  if (!bbox || !editorImageContainer.value) return {}
  const containerRect = editorImageContainer.value.getBoundingClientRect()
  const [x_min, y_min, x_max, y_max] = bbox
  return {
    position: 'absolute',
    left: `${x_min * containerRect.width}px`,
    top: `${y_min * containerRect.height}px`,
    width: `${(x_max - x_min) * containerRect.width}px`,
    height: `${(y_max - y_min) * containerRect.height}px`,
  }
}

const saveChanges = async () => {
    if (isSaving.value) return; // 중복 실행 방지

    isSaving.value = true;
    try {
      const itemsToAdd = itemsInEditor.value.filter(item => item.isNew && !item.isDeleted &&
  item.name_ko && item.bbox);
      const itemsToDelete = itemsInEditor.value.filter(item => !item.isNew && item.isDeleted);

      if (itemsToAdd.length === 0 && itemsToDelete.length === 0) {
        $q.notify({ message: '변경 사항이 없습니다.', color: 'info' });
        return;
      }

      const promises = [];
      let lastResponseData = null; // 마지막 성공 응답의 데이터를 저장할 변수

      // 삭제 API 호출
      if (itemsToDelete.length > 0) {
        const deletePayload = {
          image_id: imageId.value,
          item_ids: itemsToDelete.map(item => item.item_id)
        };
        promises.push(fetch('http://localhost:5001/api/items/delete', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(deletePayload)
        }));
      }

      // 추가 API 호출
      if (itemsToAdd.length > 0) {
        const addPayload = {
          image_id: imageId.value,
          new_items: itemsToAdd.map(item => ({ name_ko: item.name_ko, bbox: item.bbox }))
        };
        promises.push(fetch('http://localhost:5001/api/items/add', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(addPayload)
        }));
      }

      const responses = await Promise.all(promises);

      // 모든 응답이 정상적인지 확인
      for (const response of responses) {
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(errorData.error || '저장 중 오류가 발생했습니다.');
        }
        // 응답이 JSON 형식인지 확인 후 파싱
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            lastResponseData = await response.json();
        } else {
            // JSON이 아니면 응답 본문을 소비하여 다음 요청에 영향을 주지 않도록 함
            await response.text();
        }
      }

      // 마지막 성공 응답 데이터로 UI 업데이트
      if (lastResponseData) {
        detectionResults.value = lastResponseData;
        processResultsForDisplay(lastResponseData);
      } else {
          // JSON 응답이 없었다면 (예: 삭제만 발생), itemsInEditor를 필터링하여 UI 업데이트
          detectionResults.value = itemsInEditor.value.filter(item => !item.isDeleted);
          processResultsForDisplay(detectionResults.value);
      }

      $q.notify({ message: '성공적으로 저장되었습니다.', color: 'positive', icon: 'check' });
      showEditModal.value = false; // 팝업 닫기

    } catch (error) {
      console.error('Error saving changes:', error);
      $q.notify({ message: `오류 발생: ${error.message}`, color: 'negative' });
    } finally {
      isSaving.value = false;
    }
  };

const handleNewValue = (inputValue, doneFn) => {
  if (inputValue.length > 0) {
    if (!autocompleteSuggestions.value.includes(inputValue)) {
      autocompleteSuggestions.value.unshift(inputValue);
    }
    doneFn(inputValue, 'toggle');
  }
}

const filterFn = (val, update, abort) => {
  if (val.length < 1) {
    abort();
    return;
  }
  update(async () => {
    try {
      const response = await fetch(`http://localhost:5001/api/items/autocomplete?q=${val}`);
      if (!response.ok) throw new Error('Network response was not ok');
      const suggestions = await response.json();
      autocompleteSuggestions.value = suggestions;
    } catch (error) {
      console.error('Error fetching autocomplete suggestions:', error);
      autocompleteSuggestions.value = [];
    }
  });
}

const processResultsForDisplay = (results) => {
  setTimeout(() => {
    if (!imageContainerRef.value) return;
    const container = imageContainerRef.value.getBoundingClientRect();
    const originalImageSize = JSON.parse(route.query.results || '{}').image_size || { width: 1, height: 1 };
    const containerRatio = container.width / container.height;
    const imageRatio = originalImageSize.width / originalImageSize.height;

    let scale = 1, offsetX = 0, offsetY = 0;
    if (imageRatio > containerRatio) {
      scale = container.width / originalImageSize.width;
      offsetY = (container.height - originalImageSize.height * scale) / 2;
    } else {
      scale = container.height / originalImageSize.height;
      offsetX = (container.width - originalImageSize.width * scale) / 2;
    }

    processedResults.value = results.map(item => {
      if (!item.bbox) return { ...item, style: {} };
      const [x_min, y_min, x_max, y_max] = item.bbox;
      return {
        ...item,
        style: {
          position: 'absolute',
          left: `${(x_min * originalImageSize.width * scale) + offsetX}px`,
          top: `${(y_min * originalImageSize.height * scale) + offsetY}px`,
          width: `${((x_max - x_min) * originalImageSize.width) * scale}px`,
          height: `${((y_max - y_min) * originalImageSize.height) * scale}px`,
        }
      };
    });
  }, 100);
}

const getIconFor = (itemName) => {
  if (itemName.includes('노트북')) return 'laptop_chromebook';
  if (itemName.includes('배터리')) return 'battery_charging_full';
  if (itemName.includes('가위')) return 'content_cut';
  return 'check_box_outline_blank';
}

const getCarryOnColor = (status) => {
  if (status === '가능') return 'positive';
  if (status === '불가') return 'negative';
  return 'grey';
}

const getCheckedColor = (status) => {
  if (status === '가능') return 'positive';
  if (status === '불가') return 'negative';
  return 'grey';
}

let resizeTimeout;
const handleResize = () => {
  clearTimeout(resizeTimeout);
  resizeTimeout = setTimeout(() => {
    processResultsForDisplay(detectionResults.value);
  }, 150);
}

onMounted(() => {
  if (route.query.results) {
    try {
      const resultData = JSON.parse(route.query.results);
      detectionResults.value = resultData.results || [];
      imageId.value = resultData.image_id;
      processResultsForDisplay(detectionResults.value);
    } catch (e) {
      console.error("Error parsing results JSON:", e);
      detectionResults.value = [];
    }
  }
  if (route.query.image) {
    imageUrl.value = route.query.image;
  }
  isLoading.value = false;

  window.addEventListener('resize', handleResize);
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
})
</script>

<style scoped>
.page-section { border-radius: 20px; padding: 32px; margin: 0 auto; max-width: 1200px; width: 100%; box-sizing: border-box; }
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
</style>
