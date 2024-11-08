<template>
    <div v-if="community">
      <h2>{{ community.name }}</h2>
      <p>{{ community.descript }}</p>
      <p>評論數量: {{ community.comment_count }}</p>
      <p>最後更新: {{ community.last_update | formatDate }}</p>
    </div>
    <div v-else>
      <p>正在加載社群信息...</p>
    </div>
  </template>
  
  <script>
  import { useAuthStore } from '../stores/auth'; // 假設你把管理社群信息的部分放到 `community` store 中
  import { onMounted, computed } from 'vue';
  import { useRoute } from 'vue-router';
  
  export default {
    setup() {
      const communityStore = useAuthStore();
      const route = useRoute();
  
      // 當組件掛載時，根據路由參數查詢社群信息
      onMounted(async () => {
        const communityId = route.params.cid; // 獲取路由中的社群 ID
        await communityStore.getCommunityInfo(communityId); // 調用 Pinia store 的方法
      });
  
      // 計算屬性用來訪問 store 中的社群數據
      const community = computed(() => communityStore.communityState.community);
  
      return {
        community,
      };
    },
  };
  </script>
  
  <script setup>
  // 日期格式化的過濾器函數
  import { format } from 'date-fns';
  
  function formatDate(date) {
    if (!date) return '';
    return format(new Date(date), 'yyyy-MM-dd HH:mm:ss');
  }
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
  