<template>
    <a-layout>
        <Sidebar v-model:collapsed="collapsed" :onCollapse="onCollapse" />
        <a-layout :style="{ marginLeft: layoutMargin }">
            <Header />
            <a-layout-content :style="{ background: '#f5f5f5', margin: '24px 16px 0' }">
                <!-- 頂部引導區域 -->
                <div class="page-header">
                    <div class="logo-container">
                        <img src="../assets/logo.png" alt="識真網 Logo" class="logo-image" />
                        <div class="header-text">
                            <h1>識真網</h1>
                            <p>視真於微 思辨於心 讓真相 不再被聲量掩埋</p>
                        </div>
                    </div>
                </div>

                <div class="main-content">
                    <!-- 重要提示信息 -->
                    <a-row :gutter="16" style="margin-bottom: 32px;">
                        <a-col :span="24">
                            <a-alert message="注意事項" description="1. 瀏覽新聞：查看最新的新聞分析報告
2. 搜尋功能：使用關鍵字尋找特定內容
3. 評分解讀：透過事實性、批判性、客觀性、來源檢查四個角度，全面理解內容品質
4. 深入分析：點擊「查看完整分析」了解詳細內容
5. 重要提醒：我們的分析分數僅供參考，建議讀者詳閱分析報告並進行實際查證後再做出判斷" type="info" show-icon class="guide-notice" />
                        </a-col>
                    </a-row>

                    <!-- 搜尋區域 -->
                    <div class="search-container">
                        <div class="search-header">
                            <h2>搜尋網路內容分析</h2>
                            <p>輸入關鍵字搜尋您感興趣的內容</p>
                        </div>
                        <a-input-search v-model:value="searchText" placeholder="試試輸入：台灣、選舉、政治..." class="search-input"
                            @search="onSearch" enter-button="搜尋" />
                    </div>

                    <!-- 新聞列表 -->
                    <a-spin :spinning="loading">
                        <a-list :data-source="displayedNews" :row-key="(item) => item?.nid"
                            :grid="{ gutter: 24, column: 2 }">
                            <template #renderItem="{ item: news }">
                                <a-list-item>
                                    <a-card hoverable class="news-card" :class="getRandomClass()"
                                        @click="goToNewspage(news.nid)">
                                        <div class="news-image">
                                            <img :src="news.img || 'default-news-image.jpg'" :alt="news.title" />
                                        </div>
                                        <div class="news-content">
                                            <h3 class="news-title">{{ news.title }}</h3>
                                            <a-tag color="blue">{{ news.event_type || '一般新聞' }}</a-tag>

                                            <div class="news-scores">
                                                <a-row :gutter="16">
                                                    <a-col :span="8">
                                                        <a-statistic title="可信度" :value="news.credibility_score"
                                                            :precision="1"
                                                            :value-style="getScoreStyle(news.credibility_score)" />
                                                    </a-col>
                                                    <a-col :span="8">
                                                        <a-statistic title="事實性" :value="news.factual_score"
                                                            :precision="1"
                                                            :value-style="getScoreStyle(news.factual_score)" />
                                                    </a-col>
                                                    <a-col :span="8">
                                                        <a-statistic title="客觀性" :value="news.balanced_score"
                                                            :precision="1"
                                                            :value-style="getScoreStyle(news.balanced_score)" />
                                                    </a-col>
                                                </a-row>
                                            </div>
                                            <p class="news-summary">{{ formatContent(news.content) }}</p>
                                            <div class="news-footer">
                                                <a-space>
                                                    <a-tag>{{ formatDate(news.publish_date) }}</a-tag>
                                                    <a-button type="primary" @click="goToNewspage(news.nid)">
                                                        查看完整分析
                                                        <RightOutlined />
                                                    </a-button>
                                                </a-space>
                                            </div>
                                        </div>
                                    </a-card>
                                </a-list-item>
                            </template>
                        </a-list>
                        <div class="loading-more" ref="loadingTrigger">
                            <a-spin v-if="loadingMore" />
                        </div>
                    </a-spin>
                </div>
            </a-layout-content>
            <a-layout-footer class="custom-footer">
                識真網 ©2024 Created by View Truth Team
            </a-layout-footer>
        </a-layout>
    </a-layout>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue';
import { RightOutlined } from '@ant-design/icons-vue';
import { useAuthStore } from '../stores/auth';
import { message } from 'ant-design-vue';
import router from '../router';
import { useIntersectionObserver } from '@vueuse/core';
import Sidebar from '../layout/sidebar.vue';
import Header from '../layout/header.vue';

// 引入 auth store
const newstore = useAuthStore();
const newsies = computed(() => newstore.newstate?.newsies || []);

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

// 新增搜尋和分頁相關程式碼
const searchText = ref('');
const loading = ref(true);
const loadingMore = ref(false);
const hasMore = ref(true);
const loadingTrigger = ref<HTMLElement | null>(null);
const displayedNews = ref<any[]>([]);
const pageSize = ref(10);
const currentPage = ref(1);

const getScoreStyle = (score: number) => {
    if (!score) return { color: '#8c8c8c' };
    if (score >= 8) return { color: '#52c41a' };
    if (score >= 6) return { color: '#faad14' };
    return { color: '#ff4d4f' };
};

const formatContent = (content: string) => {
    const maxLength = 200;
    return content?.length > maxLength ? content.slice(0, maxLength) + "..." : content;
};

const formatDate = (date: string) => {
    return new Date(date).toLocaleDateString('zh-TW');
};

// 搜索过滤
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

// 跳转到新闻详情页
const goToNewspage = async (newsId: string) => {
    try {
        await router.push({
            name: 'newspage',
            params: { id: newsId }
        });
    } catch (error) {
        message.error('無法開啟新聞');
        console.error('Error navigating to newspage:', error);
    }
};

// 在组件加载时获取新闻列表
onMounted(async () => {
    try {
        loading.value = true;
        await newstore.getAllnewsies();
        displayedNews.value = [];
        await loadMoreNews();
    } catch (error) {
        console.error('Error loading news:', error);
        message.error('載入新聞失敗');
    } finally {
        loading.value = false;
    }
});

// 監聽滾動
useIntersectionObserver(
    loadingTrigger,
    ([{ isIntersecting }]) => {
        if (isIntersecting && !loadingMore.value && hasMore.value) {
            loadMoreNews();
        }
    }
);

const getRandomClass = () => {
    const classes = ['card-normal', 'card-large', 'card-wide'];
    return classes[Math.floor(Math.random() * classes.length)];
};

</script>

<style scoped>
/* 更新 page-header 相關樣式 */
.page-header {
    background: linear-gradient(135deg, #1677ff 0%, #4096ff 100%);
    padding: 40px 32px;
    color: white;
    border-radius: 12px;
    margin-bottom: 32px;
}

.logo-container {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 24px;
}

.logo-image {
    width: 120px;
    height: auto;
    filter: brightness(0) invert(1);
    /* 將 logo 轉為白色 */
}

.header-text {
    text-align: left;
}

.header-text h1 {
    font-size: 2.5rem;
    margin-bottom: 16px;
    font-weight: 600;
}

.header-text p {
    font-size: 1.2rem;
    opacity: 0.9;
    margin: 0;
}

/* 新增和修改的樣式 */
.page-header {
    background: linear-gradient(135deg, #1677ff 0%, #4096ff 100%);
    padding: 40px 32px;
    color: white;
    border-radius: 12px;
    margin-bottom: 32px;
    text-align: center;
}

.page-header h1 {
    font-size: 2.5rem;
    margin-bottom: 16px;
    font-weight: 600;
}

.page-header p {
    font-size: 1.2rem;
    opacity: 0.9;
}

.main-content {
    max-width: 1400px;
    margin: 0 auto;
    padding: 0 24px;
}

.guide-notice {
    border: none;
    background: linear-gradient(to right, #e6f4ff, #f0f5ff);
    border-radius: 12px;
    padding: 24px;
}

.guide-notice :deep(.ant-alert-message) {
    font-size: 20px;
    margin-bottom: 16px;
}

.guide-notice :deep(.ant-alert-description) {
    white-space: pre-line;
    line-height: 2;
    font-size: 16px;
}

.search-container {
    background: white;
    padding: 32px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    margin-bottom: 32px;
}

.search-header {
    margin-bottom: 24px;
    text-align: center;
}

.search-header h2 {
    font-size: 1.8rem;
    color: #1f1f1f;
    margin-bottom: 8px;
}

.search-header p {
    color: #666;
    font-size: 1.1rem;
}

.search-input {
    max-width: 600px;
    margin: 0 auto;
    display: block;
}

.search-input :deep(.ant-input) {
    height: 48px;
    font-size: 16px;
}

.search-input :deep(.ant-btn) {
    height: 48px;
    font-size: 16px;
    padding: 0 32px;
}

/* 修改新聞卡片樣式 */
.news-card {
    border: none;
    background: white;
    transition: all 0.3s ease;
}

.news-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.12);
}

.news-content {
    padding: 24px;
}

.news-title {
    font-size: 1.4rem;
    margin-bottom: 16px;
}

.news-scores {
    background: #fafafa;
    border-radius: 12px;
    padding: 20px;
    margin: 20px 0;
}

.custom-footer {
    text-align: center;
    padding: 24px;
    color: #666;
    background: #f8f9fa;
    font-size: 14px;
}

/* 主體內容樣式 */
.a-layout-content {
    padding: 24px;
    background: #ececec;
}

/* 活動區域樣式 */
.activity-carousel {
    border: 2px solid #ff7f50;
    border-radius: 12px;
    padding: 16px;
    background: linear-gradient(135deg, #f7f7f7, #ffe4e1);
    box-shadow: 0 6px 12px rgba(255, 127, 80, 0.2);
}

.carousel-content {
    text-align: center;
    font-size: 22px;
    color: #d2691e;
    padding: 35px 0;
    font-weight: 600;
}

/* 每個內容卡片樣式 */
.content-card {
    transition: all 0.3s ease;
    border-radius: 8px;
    overflow: hidden;
}

.content-card:hover {
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    transform: translateY(-8px);
}

/* 推薦區域的卡片樣式 */
.recommend-card {
    background: #fafafa;
    padding: 16px;
    border-radius: 8px;
}

.recommend-content-card {
    transition: all 0.3s ease;
    border-radius: 8px;
    overflow: hidden;
}

.recommend-content-card:hover {
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
    transform: translateY(-5px);
}

/* 重要提示信息樣式 */
.important-notice {
    border: 1px solid #91caff;
    background-color: #e6f4ff;
    border-radius: 8px;
    font-size: 15px;
}

.important-notice :deep(.ant-alert-message) {
    color: #1677ff;
    font-size: 16px;
    font-weight: bold;
}

.important-notice :deep(.ant-alert-description) {
    color: #4b4b4b;
    white-space: pre-line;
    line-height: 1.8;
}

/* Footer 樣式 */
a-layout-footer {
    text-align: center;
    font-size: 14px;
    color: #999;
    padding: 24px 0;
    background: #f0f2f5;
}

/* 新聞卡片樣式 */
.news-card {
    margin-bottom: 24px;
    border-radius: 12px;
    overflow: hidden;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    background: #fff;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.news-card:hover {
    transform: translateY(-8px) rotate(1deg);
    box-shadow: 0 12px 20px rgba(0, 0, 0, 0.15);
}

.card-normal {
    height: auto;
}

.card-large {
    grid-row: span 2;
}

.card-wide {
    grid-column: span 2;
}

.news-image {
    width: 100%;
    height: 220px;
    overflow: hidden;
    border-radius: 8px 8px 0 0;
    position: relative;
}

.news-image img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.3s ease;
}

.news-card:hover .news-image img {
    transform: scale(1.05);
}

.news-content {
    padding: 20px;
    background: linear-gradient(180deg, rgba(255, 255, 255, 0.9) 0%, rgba(255, 255, 255, 1) 100%);
}

.news-scores {
    background: rgba(250, 250, 250, 0.8);
    backdrop-filter: blur(10px);
    padding: 16px;
    border-radius: 12px;
    margin: 16px 0;
    transition: all 0.3s ease;
}

.news-scores:hover {
    background: rgba(255, 255, 255, 0.95);
    transform: translateY(-2px);
}

.news-title {
    font-size: 1.25rem;
    font-weight: 600;
    margin-bottom: 12px;
    color: #1f1f1f;
    line-height: 1.4;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.news-summary {
    color: #666;
    line-height: 1.6;
    margin: 16px 0;
}

.news-footer {
    margin-top: 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.search-section {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
}

/* 統計數字樣式優化 */
:deep(.ant-statistic-title) {
    font-size: 14px;
    color: #666;
}

:deep(.ant-statistic-content) {
    font-size: 24px;
    font-weight: 600;
}

.loading-more {
    text-align: center;
    margin: 12px 0;
    height: 32px;
    line-height: 32px;
}
</style>
