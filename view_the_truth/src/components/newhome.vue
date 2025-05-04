<template>
    <a-layout>
        <Sidebar v-model:collapsed="collapsed" :onCollapse="onCollapse" />
        <a-layout :style="{ marginLeft: layoutMargin }">
            <Header />
            <a-layout-content :style="{ margin: '24px 16px 0', minHeight: 'calc(100vh - 112px)' }">
                <a-card class="news-main-content">
                    <div class="page-header">
                        <h2>新聞</h2>
                        <a-input-search
                            v-model:value="searchText"
                            placeholder="搜尋新聞"
                            style="width: 300px"
                            @search="onSearch"
                            enter-button
                        />
                    </div>

                    <a-spin :spinning="loading">
                        <a-list
                            :data-source="displayedNews"
                            :row-key="(item) => item?.nid"
                            :grid="{ gutter: 16, column: 1 }"
                        >
                            <template #renderItem="{ item: news }">
                                <a-list-item>
                                    <a-card 
                                        hoverable 
                                        class="news-card"
                                        @click="goToNewspage(news.nid)"
                                    >
                                        <template #title>
                                            <div class="news-title">{{ news.title }}</div>
                                            <a-tag color="blue" class="news-type">{{ news.event_type || '一般新聞' }}</a-tag>
                                        </template>
                                        
                                        <div class="news-scores">
                                            <a-row :gutter="[16, 16]">
                                                <a-col :span="8">
                                                    <a-statistic
                                                        title="可信度"
                                                        :value="news.credibility_score ? `${news.credibility_score.toFixed(1)}` : '尚未評分'"
                                                        :value-style="getScoreStyle(news.credibility_score)"
                                                    />
                                                </a-col>
                                                <a-col :span="8">
                                                    <a-statistic
                                                        title="事實性"
                                                        :value="news.factual_score ? `${news.factual_score.toFixed(1)}` : '尚未評分'"
                                                        :value-style="getScoreStyle(news.factual_score)"
                                                    />
                                                </a-col>
                                                <a-col :span="8">
                                                    <a-statistic
                                                        title="客觀性"
                                                        :value="news.balanced_score ? `${news.balanced_score.toFixed(1)}` : '尚未評分'"
                                                        :value-style="getScoreStyle(news.balanced_score)"
                                                    />
                                                </a-col>
                                            </a-row>
                                        </div>
                                        
                                        <div class="news-content">
                                            <p class="news-summary">{{ formatContent(news.content) }}</p>
                                        </div>
                                        
                                        <div class="news-footer">
                                            <a-space>
                                                <a-tag>{{ formatDate(news.create_at) }}</a-tag>
                                                <a-button type="link" @click.stop="goToNewspage(news.nid)">
                                                    閱讀更多
                                                    <RightOutlined />
                                                </a-button>
                                            </a-space>
                                        </div>
                                    </a-card>
                                </a-list-item>
                            </template>
                        </a-list>
                        <div class="loading-more" ref="loadingTrigger">
                            <a-spin v-if="loadingMore" />
                        </div>
                    </a-spin>
                </a-card>
            </a-layout-content>
            <a-layout-footer style="text-align: center">
                識真網 © 2024 Created by Ant UED
            </a-layout-footer>
        </a-layout>
    </a-layout>
</template>

<script lang="ts" setup>
import { computed, onMounted, ref } from 'vue';
import { RightOutlined } from '@ant-design/icons-vue';
import Sidebar from '../layout/sidebar.vue';
import Header from '../layout/header.vue';
import { useAuthStore } from '../stores/auth';
import { message } from 'ant-design-vue';
import router from '../router';
import { useIntersectionObserver } from '@vueuse/core';

// 側邊欄狀態
const collapsed = ref(false);
const broken = ref(false);

const layoutMargin = computed(() => {
    if (broken.value) {
        return collapsed.value ? '0px' : '200px';
    }
    return collapsed.value ? '0px' : '200px'; // 根據需求調整寬度
});
const onCollapse = (isCollapsed: boolean, type: string) => {
    console.log(isCollapsed, type);
    // collapsed.value 會通過 v-model:collapsed 自動更新
};
//引用狀態列
const newstore = useAuthStore();
const newsies = computed(() => newstore.newstate?.newsies || []);

// Add loading state
const loading = ref(true);

// 分頁相關狀態
const pageSize = ref(10);
const currentPage = ref(1);
const loadingMore = ref(false);
const hasMore = ref(true);
const loadingTrigger = ref<HTMLElement | null>(null);
const displayedNews = ref<any[]>([]);

// 監聽滾動
useIntersectionObserver(
    loadingTrigger,
    ([{ isIntersecting }]) => {
        if (isIntersecting && !loadingMore.value && hasMore.value) {
            loadMoreNews();
        }
    }
);

// 加載更多新聞
const loadMoreNews = async () => {
    if (loadingMore.value) return;
    
    loadingMore.value = true;
    try {
        const startIndex = (currentPage.value - 1) * pageSize.value;
        const endIndex = startIndex + pageSize.value;
        const allFilteredNews = filteredNews.value;
        const newItems = allFilteredNews.slice(startIndex, endIndex);
        
        if (newItems.length > 0) {
            displayedNews.value = [...displayedNews.value, ...newItems];
            currentPage.value++;
            hasMore.value = endIndex < allFilteredNews.length;
        } else {
            hasMore.value = false;
        }
    } catch (error) {
        console.error('Error loading more news:', error);
    } finally {
        loadingMore.value = false;
    }
};

// 日期格式化函數
const formatDate = (date: string): string => {
  return new Date(date).toLocaleString('zh-TW', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}


// 在組件掛載時載入新聞列表
onMounted(async () => {
    try {
        loading.value = true;
        await newstore.getAllnewsies();
        // 初始化 displayedNews
        displayedNews.value = [];
        // 初始載入第一頁
        await loadMoreNews();
    } catch (error) {
        console.error('Error loading news:', error);
        message.error('載入新聞失敗');
    } finally {
        loading.value = false;
    }
})
const goToNewspage = async (newsId: string) => {
  try {
    await router.push({
      name: 'newspage',
      params: { id: newsId }
    })
  } catch (error) {
    message.error('無法開啟新聞')
    console.error('Error navigating to newspage:', error)
  }
}
// 處理最大字數
const maxLength = 50 // 最大字數限制

const getLevelClass = (level: string) => {
    switch(level?.toLowerCase()) {
        case 'high': return 'level-high';
        case 'medium': return 'level-medium';
        case 'low': return 'level-low';
        default: return 'level-unknown';
    }
};

const searchText = ref('');
const filteredNews = computed(() => {
    if (!searchText.value) return newsies.value;
    const searchLower = searchText.value.toLowerCase();
    return newsies.value.filter(news => 
        news.title?.toLowerCase().includes(searchLower) ||
        news.content?.toLowerCase().includes(searchLower) ||
        news.event_type?.toLowerCase().includes(searchLower)
    );
});

const onSearch = (value: string) => {
    searchText.value = value;
    currentPage.value = 1;
    displayedNews.value = [];
    hasMore.value = true;
    loadMoreNews();
};

const formatContent = (content: string) => {
    return content.length > maxLength ? content.slice(0, maxLength) + "..." : content;
};

const getScoreStyle = (score: number) => {
    if (!score) return { color: '#8c8c8c' };
    if (score >= 8) return { color: '#52c41a' };
    if (score >= 6) return { color: '#faad14' };
    return { color: '#ff4d4f' };
};

const getLevelColor = (level: string) => {
    switch(level?.toLowerCase()) {
        case 'high': return 'success';
        case 'medium': return 'warning';
        case 'low': return 'error';
        default: return 'default';
    }
};
</script>

<style scoped>
.news-main-content {
    max-width: 1200px;
    margin: 0 auto;
}

.page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
}

.news-card {
    width: 100%;
    margin-bottom: 16px;
    border-radius: 8px;
}

.news-title {
    font-size: 18px;
    font-weight: bold;
    display: inline-block;
    margin-right: 12px;
}

.news-type {
    vertical-align: middle;
}

.news-scores {
    margin: 16px 0;
    padding: 12px;
    background-color: #fafafa;
    border-radius: 4px;
}

.news-content {
    padding: 12px 0;
}

.news-summary {
    color: #666;
    margin: 0;
    line-height: 1.6;
}

.news-footer {
    margin-top: 16px;
    padding-top: 16px;
    border-top: 1px solid #f0f0f0;
}

:deep(.ant-card-hoverable:hover) {
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    transform: translateY(-2px);
    transition: all 0.3s ease;
}

:deep(.ant-statistic-title) {
    font-size: 14px;
    margin-bottom: 8px;
}

:deep(.ant-statistic-content) {
    font-size: 20px;
}

.loading-more {
    text-align: center;
    margin: 12px 0;
    height: 32px;
    line-height: 32px;
}
</style>
