<template>
  <div v-if="community">
    <h2>{{ community.cna }}</h2>
    <p>{{ community.descr }}</p>
    <p>最後更新: {{ community.last_update }}</p>
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
      const communityId = route.params.id; // 獲取路由中的社群 ID
      console.log("查詢的社群 ID:", communityId);  // 檢查這裡的社群 ID
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


<style scoped>
h2 {
  color: #1890ff;
}

p {
  font-size: 16px;
  line-height: 1.5;
}
</style>