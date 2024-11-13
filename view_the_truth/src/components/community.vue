<template>
  <div v-if="community">
    <h2>{{ community.cna }}</h2>
    <p>{{ community.descr }}</p>
    <p>最後更新: {{ community.last_update }}</p>
  </div>
  <div v-else>
    <p>正在加載社群信息...</p>
  </div>
  
  <div v-if="posts">
    <div v-for="post in posts" :key="post.pid">
      <h2 @click="goToPost(post.pid)">{{ post.title }}</h2>
      <p>{{ post.content }}</p>
      <p>發言人: {{ post.una }}</p>
      <p>{{ post.crea_date }}</p>
    </div>
  </div>
  <div v-else>
    <p>正在加載社群貼文訊息...</p>
  </div>
</template>

<script>
import { useAuthStore } from '../stores/auth';
import { onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';

export default {
  setup() {
    const communityStore = useAuthStore();
    const route = useRoute();
    const router = useRouter();

    // 當組件掛載時，根據路由參數查詢社群信息
    onMounted(async () => {
      const communityId = route.params.id; // 獲取路由中的社群 ID
      await communityStore.getCommunityInfo(communityId); // 調用 Pinia store 的方法取得社群資訊
      await communityStore.getAllPosts(communityId); // 調用 Pinia store 的方法取得該社群的所有貼文
    });

    // 計算屬性來訪問 store 中的社群數據
    const community = computed(() => communityStore.communityState.community);
    const posts = computed(() => communityStore.postState.posts);

    // 跳轉到貼文頁面的方法
    const goToPost = (postId) => {
      router.push({ name: 'post', params: { id: postId } });
    };

    return {
      community,
      posts,
      goToPost,
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
