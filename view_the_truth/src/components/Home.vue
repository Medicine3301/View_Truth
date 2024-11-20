<template>
    <a-layout>
        <Sidebar v-model:collapsed="collapsed" :onCollapse="onCollapse" />
        <a-layout :style="{ marginLeft: layoutMargin }">
            <Header />
            <a-layout-content :style="{ background: ' #ececec', margin: '24px 16px 0' }">
                <div :style="{ padding: '24px', background: '#fff', minHeight: '360px', textAlign: 'center' }">
                    abcde
                    <a-pagination :default-current="6" :total="500" :style="{ textAlign: 'center' }" />
                </div>
            </a-layout-content>
            <a-layout-footer style="text-align: center">
                識真網 ©2024 Created by Ant UED
            </a-layout-footer>
        </a-layout>
    </a-layout>
</template>


<script lang="ts" setup>
import { computed, ref} from 'vue';
import Sidebar from '../layout/sidebar.vue';
import Header from '../layout/header.vue';
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

</script>


