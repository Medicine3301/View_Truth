<template>
    <div v-if="post">
      <h2>{{ post.una }}</h2>
      <p>標題:{{ post.title }}</p>
      <p>內容:{{ post.content }}</p>
      <p>創建於{{post.crea_date}}</p>
    </div>
    <div v-else>
      <p>正在加載貼文信息...</p>
    </div>
</template>
  
  <script>
  import { useAuthStore } from '../stores/auth';
  import { onMounted, computed } from 'vue';
  import { useRoute } from 'vue-router';
  
  export default {
    setup() {
      const postStore = useAuthStore();
      const route = useRoute();
  
      // 當組件掛載時，根據路由參數查詢社群信息
      onMounted(async () => {
        const postId = route.params.id; // 獲取路由中的社群 ID
        await postStore.getPostInfo(postId); //調用 Pinia store 的方法取得所有該社群的貼文
      });
  
      // 計算屬性用來訪問 store 中的社群數據
      const post = computed(() => postStore.postState.post);
      
      return {
        post
      };
    },
  };
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