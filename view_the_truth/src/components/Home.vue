<template>
    <a-layout>
        <Sidebar v-model:collapsed="collapsed" :onCollapse="onCollapse" />
        <a-layout :style="{ marginLeft: layoutMargin }">
            <Header />
            <a-layout-content :style="{ background: '#ececec', margin: '24px 16px 0' }">
                <div :style="{ padding: '20px', background: '#fff', minHeight: '360px' }">
                    <!-- 活動區域 -->
                    <a-row :gutter="16" style="margin-bottom: 24px;">
                        <a-col :span="24">
                            <a-carousel autoplay class="activity-carousel">
                                <div>
                                    <h3 class="carousel-content">活動 1: 介紹內容...</h3>
                                </div>
                                <div>
                                    <h3 class="carousel-content">活動 2: 介紹內容...</h3>
                                </div>
                                <div>
                                    <h3 class="carousel-content">活動 3: 介紹內容...</h3>
                                </div>
                            </a-carousel>
                        </a-col>
                    </a-row>

                    <!-- 最新貼文、最新新聞、熱門新聞、熱門貼文 -->
                    <a-row :gutter="16">
                        <a-col :span="12" :md="12">
                            <a-card title="最新貼文" bordered class="content-card">
                                <p>最新貼文內容...</p>
                                <a-button type="link" style="margin-top: 8px;">查看更多</a-button>
                            </a-card>
                        </a-col>
                        <a-col :span="12" :md="12">
                            <a-card title="最新新聞" bordered class="content-card">
                                <p>最新新聞內容...</p>
                                <a-button type="link" style="margin-top: 8px;">查看更多</a-button>
                            </a-card>
                        </a-col>
                    </a-row>
                    <a-row :gutter="16" style="margin-top: 16px;">
                        <a-col :span="12" :md="12">
                            <a-card title="熱門新聞" bordered class="content-card">
                                <p>熱門新聞內容...</p>
                                <a-button type="link" style="margin-top: 8px;">查看更多</a-button>
                            </a-card>
                        </a-col>
                        <a-col :span="12" :md="12">
                            <a-card title="熱門貼文" bordered class="content-card">
                                <p>熱門貼文內容...</p>
                                <a-button type="link" style="margin-top: 8px;">查看更多</a-button>
                            </a-card>
                        </a-col>
                    </a-row>

                    <!-- 推薦區域 -->
                    <a-row :gutter="16" style="margin-top: 24px;">
                        <a-col :span="24">
                            <a-card title="推薦內容" class="recommend-card">
                                <a-row :gutter="16">
                                    <a-col :span="12" :md="6">
                                        <a-card bordered class="recommend-content-card">
                                            <p>推薦內容 1...</p>
                                        </a-card>
                                    </a-col>
                                    <a-col :span="12" :md="6">
                                        <a-card bordered class="recommend-content-card">
                                            <p>推薦內容 2...</p>
                                        </a-card>
                                    </a-col>
                                    <a-col :span="12" :md="6">
                                        <a-card bordered class="recommend-content-card">
                                            <p>推薦內容 3...</p>
                                        </a-card>
                                    </a-col>
                                    <a-col :span="12" :md="6">
                                        <a-card bordered class="recommend-content-card">
                                            <p>推薦內容 4...</p>
                                        </a-card>
                                    </a-col>
                                </a-row>
                            </a-card>
                        </a-col>
                    </a-row>
                </div>
            </a-layout-content>
            <a-layout-footer style="text-align: center">
                識真網 ©2024 Created by Ant UED
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
const news =useAuthStore();
</script>

<style scoped>
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

/* Footer 樣式 */
a-layout-footer {
    text-align: center;
    font-size: 14px;
    color: #999;
    padding: 24px 0;
    background: #f0f2f5;
}
</style>
