<template>
    <a-layout>
        <Sidebar v-model:collapsed="collapsed" :onCollapse="onCollapse" />
        <a-layout :style="{ marginLeft: layoutMargin }">
            <Header />
            <a-layout-content :style="{ background: '#ececec', margin: '24px 16px 0' }">
               <div></div>
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

const newspagestore=useAuthStore();

// 日期格式化
const formatDate = (date: string): string => {
  return new Date(date).toLocaleString('zh-TW', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}
const news = computed(() => newspagestore.newstate.news)
const comments = computed(() => newspagestore.newstate.comments)
</script>

<style scoped>
/* 主體內容樣式 */
.a-layout-content {
    padding: 24px;
    background: #ececec;
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
