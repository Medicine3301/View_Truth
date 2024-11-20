<template>
  <a-layout>
    <Sidebar v-model:collapsed="collapsed" :onCollapse="onCollapse" />
    <a-layout :style="{ marginLeft: layoutMargin }">
      <Header />
      <a-layout-content :style="{ background: ' #ececec', margin: '24px 16px 0' }">
        <div :style="{ padding: '24px', background: '#fff', minHeight: '360px', textAlign: 'center' }">
          <div v-if="post">
            <h2>{{ post.una }}</h2>
            <p>標題:{{ post.title }}</p>
            <p>內容:{{ post.content }}</p>
            <p>創建於{{ post.crea_date }}</p>
          </div>
          <div v-else>
            <p>正在加載貼文信息...</p>
          </div>

          <div v-if="comments">
            <div v-for="comm in comments" :key="comm.pid">
              <h2>{{ comm.title }}</h2>
              <p>{{ comm.content }}</p>
              <p>發言人: {{ comm.una }}</p>
              <p>{{ comm.crea_date }}</p>
            </div>
          </div>
          <div v-else>
            <p>正在加載留言信息...</p>
          </div>
        </div>
      </a-layout-content>
      <a-layout-footer style="text-align: center">
        識真網 ©2024 Created by Ant UED
      </a-layout-footer>
    </a-layout>
  </a-layout>
</template>
  
<script lang="ts" setup>
import { useAuthStore } from '../stores/auth'; 
import { onMounted, computed, ref } from 'vue';
import { useRoute } from 'vue-router';
import Sidebar from '../layout/sidebar.vue'; 
import Header from '../layout/header.vue'; 

// 側邊欄狀態管理
const collapsed = ref<boolean>(false); // 設定 collapsed 的類型為 boolean
const broken = ref<boolean>(false); // 設定 broken 的類型為 boolean

// 動態計算佈局邊距
const layoutMargin = computed<string>(() => {
  return collapsed.value ? '0px' : broken.value ? '200px' : '200px';
});

// 處理側邊欄收合事件
const onCollapse = (isCollapsed: boolean, type: string) => {
  console.log(`Sidebar collapsed: ${isCollapsed}, Type: ${type}`);
  // collapsed.value 通過 v-model:collapsed 自動更新，無需手動設置
};

// 使用 Pinia Store 和 Vue Router
const postStore = useAuthStore();
const route = useRoute();

// 當組件掛載時，根據路由參數查詢貼文資訊
onMounted(async () => {
  const postId = route.params.id as string; // 確保 postId 是 string 類型
  if (postId) {
    await postStore.getPostInfo(postId); // 調用 Pinia store 的方法取得貼文內容
    await postStore.getAllComments(postId); // 調用 Pinia store 的方法取得所有留言
  }
});

// 計算屬性用來訪問 store 中的貼文和留言數據
const post = computed(() => postStore.postState.post);
const comments = computed(() => postStore.postState.comments);
</script>

  
  
<style scoped>
h2 {
  color: #1890ff;
}

p {
  font-size: 16px;
  line-height: 1.5;
}
</style>