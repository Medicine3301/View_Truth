<template>
    <a-layout>
        <Sidebar v-model:collapsed="collapsed" :onCollapse="onCollapse" />
        <a-layout :style="{ marginLeft: layoutMargin }">
            <Header />
            <a-layout-content :style="{ background: '#ececec', margin: '24px 16px 0' }">
                <div :style="{ padding: '24px', background: '#fff', minHeight: '360px' }">
                    <div class="news-main-content">
                        <!-- 新聞主標題 -->
                        <div class="news-header" :style="{ marginBottom: '24px', textAlign: 'center' }">
                            <h1></h1>
                        </div>

                        <!-- 新聞分類選單 -->
                        <div class="news-category-menu" :style="{ marginBottom: '16px', textAlign: 'center' }">
                            <a-space>
                                <a-button type="link" @click="filterCategory('international')">國際</a-button>
                                <a-button type="link" @click="filterCategory('technology')">科技</a-button>
                                <a-button type="link" @click="filterCategory('entertainment')">娛樂</a-button>
                                <a-button type="link" @click="filterCategory('sports')">體育</a-button>
                                <a-button type="link" @click="filterCategory('health')">健康</a-button>
                            </a-space>
                        </div>

                        <!-- 熱門新聞卡片 -->
                        <div class="hot-news-card" :style="{ display: 'flex', gap: '16px', marginBottom: '24px' }">
                            <div class="hot-news-item" :style="{ flex: 1, padding: '16px', background: '#fafafa', borderRadius: '8px', boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)' }">
                                <h2>熱門新聞</h2>
                                <div v-for="h in 3" :key="h" :style="{ marginTop: '12px' }">
                                    <a href="#" @click.prevent="readHotNews(h)">熱門新聞標題 {{ h }}</a>
                                </div>
                            </div>
                            <div class="hot-news-item" :style="{ flex: 1, padding: '16px', background: '#fafafa', borderRadius: '8px', boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)' }">
                                <h2>推薦新聞</h2>
                                <div v-for="r in 3" :key="r" :style="{ marginTop: '12px' }">
                                    <a href="#" @click.prevent="readHotNews(r)">推薦新聞標題 {{ r }}</a>
                                </div>
                            </div>
                        </div>
                        <!-- 新聞文章列表 -->
                        <div class="news-list" :style="{ display: 'flex', flexDirection: 'column', gap: '16px' }">
                            <div class="news-item" v-for="n in 5" :key="n" :style="{ padding: '16px', border: '1px solid #d9d9d9', borderRadius: '8px', background: '#fff', transition: 'transform 0.3s', cursor: 'pointer' }" @mouseover="hoverNewsItem(n)" @mouseleave="leaveNewsItem(n)" @click="readMore(n)">
                                <h3 class="news-title">新聞標題 {{ n }}</h3>
                                <p class="news-summary">這裡是新聞摘要部分，可以幫助用戶快速了解新聞的主要內容...</p>
                                <a-button type="link">閱讀更多</a-button>
                            </div>
                        </div>

                        <!-- 分頁器 -->
                        <div :style="{ marginTop: '24px', textAlign: 'center' }">
                            <a-pagination :default-current="6" :total="500" />
                        </div>
                    </div>
                </div>
            </a-layout-content>
            <a-layout-footer style="text-align: center">
                識真網 © 2024 Created by Ant UED
            </a-layout-footer>
        </a-layout>
    </a-layout>
</template>

<script lang="ts" setup>
import { computed, ref } from 'vue';
import Sidebar from '../layout/sidebar.vue';
import Header from '../layout/header.vue';
import { useAuthStore } from '../stores/auth';
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

const newsstore=useAuthStore();
const comment = computed(() => newsstore.newsState.comment)
const news = computed(() => newsstore.newsState.ananews)

// 日期格式化函數
const formatDate = (date: string): string => {
  return new Date(date).toLocaleString('zh-TW', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
};
// 用戶交互方法
const filterCategory = (category: string) => {
    console.log(`Filter category: ${category}`);
};
const hoverNewsItem = (id: number) => {
    console.log(`Hovered over news item: ${id}`);
};
const leaveNewsItem = (id: number) => {
    console.log(`Mouse left news item: ${id}`);
};
const readMore = (id: number) => {
    console.log(`Read more about news item: ${id}`);
};
const readHotNews = (id: number) => {
    console.log(`Read more about hot news item: ${id}`);
};
</script>

<style scoped>
.news-main-content {
    max-width: 1200px;
    margin: 0 auto;
}
.news-title {
    font-size: 18px;
    font-weight: bold;
    margin-bottom: 8px;
}
.news-summary {
    font-size: 14px;
    color: #666;
    margin-bottom: 12px;
}
.news-item:hover {
    transform: scale(1.02);
}
</style>
