<template>
  <div class="min-h-screen flex flex-col bg-white">
    <main class="flex-1 container py-8">
      <div class="max-w-6xl mx-auto border-sky-100 shadow-md">
        <div class="bg-gradient-to-r from-sky-50 to-white border-b border-sky-100 p-4">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <span class="text-2xl">{{ currentData.flag }}</span>
              <h1 class="text-2xl text-gray-800">{{ currentData.country }} 상세 여행 정보</h1>
            </div>
            <div class="flex items-center gap-2">
              <NuxtLink to="/info">
                <button class="flex items-center gap-2 bg-transparent p-2 border rounded">
                  <span>&lt;</span>
                  여행 정보로 돌아가기
                </button>
              </NuxtLink>
            </div>
          </div>
        </div>
        <div class="p-6">
          <div class="grid md:grid-cols-12 gap-6">
            <div class="md:col-span-4 space-y-4">
              <div class="bg-white p-4 rounded-lg border border-gray-200">
                <h3 class="font-medium mb-3">목차</h3>
                <div class="max-h-[600px] overflow-y-auto space-y-2">
                  <button v-for="(section, index) in currentData.sections" :key="section.id" @click="selectedSection = section.id" :class="selectedSection === section.id ? 'border-blue-500' : 'border-gray-200'" class="w-full text-left h-auto p-3 border rounded">
                    <div>
                      <div class="flex items-center gap-2 mb-1">
                        <span class="text-xs bg-sky-100 text-sky-700 px-2 py-1 rounded">{{ index + 1 }}</span>
                        <span class="font-medium text-sm">{{ section.title }}</span>
                      </div>
                    </div>
                  </button>
                </div>
              </div>

              <div class="bg-sky-50 p-4 rounded-lg border border-sky-100">
                <h4 class="font-medium mb-2 text-sky-700">여행 기본 정보</h4>
                <div class="space-y-2 text-sm">
                  <div class="flex justify-between">
                    <span>통화:</span>
                    <span class="font-medium">{{ currentData.currency }}</span>
                  </div>
                  <div class="flex justify-between">
                    <span>환율:</span>
                    <span class="font-medium">{{ currentData.exchangeRate }}</span>
                  </div>
                </div>
              </div>
            </div>

            <div class="md:col-span-8">
              <div v-if="selectedSectionData" class="bg-white p-6 rounded-lg border border-gray-200">
                <h2 class="text-2xl font-bold mb-6">{{ selectedSectionData.title }}</h2>
                <div class="text-gray-700 leading-relaxed whitespace-pre-line text-base">
                  {{ selectedSectionData.content }}
                </div>

                <div class="flex justify-between mt-8 pt-6 border-t border-gray-200">
                  <button @click="selectPreviousSection" :disabled="isFirstSection" class="p-2 border rounded disabled:opacity-50">
                    이전
                  </button>
                  <button @click="selectNextSection" :disabled="isLastSection" class="p-2 border rounded disabled:opacity-50">
                    다음
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

const detailedTravelInfo = {
  알바니아: {
    country: "알바니아",
    flag: "🇦🇱",
    currency: "LEK",
    exchangeRate: "1레크 ≈ 12원",
    sections: [
      {
        id: "general",
        title: "일반적인",
        content: `알바니아로의 여행을 계획한다고해서 어려울 필요는 없습니다. 아름다움, 문화, 음식 및 흥미로운 활동으로 유명한이 나라는 멋진 목적지입니다...` // Content truncated for brevity
      },
      {
        id: "cost",
        title: "알바니아로 여행하는 데 드는 비용은 얼마입니까?",
        content: `전형적인 여행자는 알바니아로의 여행에 하루에 105 달러를 소비합니다...`
      },
      // ... other sections from the original file
    ],
  },
};

const selectedSection = ref("general");

// In a real app, you would get the country from the route, e.g., useRoute().params.country
// For this example, we'll hardcode it to "알바니아"
const currentData = computed(() => detailedTravelInfo.알바니아);

const selectedSectionData = computed(() => {
  return currentData.value.sections.find(section => section.id === selectedSection.value);
});

const currentIndex = computed(() => {
    return currentData.value.sections.findIndex(s => s.id === selectedSection.value);
});

const isFirstSection = computed(() => currentIndex.value === 0);
const isLastSection = computed(() => currentIndex.value === currentData.value.sections.length - 1);

const selectPreviousSection = () => {
    if (!isFirstSection.value) {
        selectedSection.value = currentData.value.sections[currentIndex.value - 1].id;
    }
};

const selectNextSection = () => {
    if (!isLastSection.value) {
        selectedSection.value = currentData.value.sections[currentIndex.value + 1].id;
    }
};

</script>
