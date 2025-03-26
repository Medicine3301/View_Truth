<template>
  <a-layout-sider :style="{ height: '100vh', position: 'fixed', left: 0 }" breakpoint="md" collapsed-width="0"
    v-model:collapsed="localCollapsed" @collapse="handleCollapse" @breakpoint="onBreakpoint">

    <a-menu v-model:selectedKeys="selectedKeys" theme="dark" mode="inline" style="margin-top: 20px;">
      <a-menu-item @click="goTotop">
        <HomeOutlined />
        <span class="nav-text">首頁</span>
      </a-menu-item>
      <a-menu-item key="1">
        <NotificationOutlined />
        <span class="nav-text">即時消息</span>
      </a-menu-item>
      <a-menu-item key="2">
        <router-link to="/news">
          <VideoCameraOutlined />
          <span class="nav-text">新聞專區</span>
        </router-link>
      </a-menu-item>

      <a-menu-item key="3">
        <FireOutlined />
        <span class="nav-text">熱門消息</span>
      </a-menu-item>
      <!-- 僅管理員可見的菜單 -->
      <a-menu-item-group v-if="isAdmin" key="gadmin" title="管理面板" style="margin-top: 20px;">
        <a-menu-item key="adminPanel1">
          <PieChartOutlined />
          <span class="nav-text">網站數據管理</span>
        </a-menu-item>
        <a-menu-item key="adminPanel2" @click="router.push('/adminusermanagement')">
          <UserOutlined />
          <span class="nav-text">用戶管理</span>
        </a-menu-item>
        <a-menu-item key="adminPanel3">
          <VideoCameraOutlined />
          <span class="nav-text">新聞內容管理</span>
        </a-menu-item>
      </a-menu-item-group>
      <a-menu-item-group key="g1" title="討論看板" style="margin-top: 20px;"
        :style="{ overflow: 'auto', height: '350px', paddingRight: '5px' }">
        <!-- 討論版列表項目 -->
        <template v-for="board in authStore.communityState.communities" :key="board.cid">
          <a-menu-item @click="goToCommunity(board.cid)">
            <a-avatar :size="30" style="margin-right: 10px;">
              <template #icon>
                <img src="/public/img/sidebar.png" :alt="board.cna" />
              </template>
            </a-avatar>
            <span class="nav-text">{{ board.cna }}</span>
          </a-menu-item>
        </template>

      </a-menu-item-group>
    </a-menu>
  </a-layout-sider>
</template>
<script lang="ts" setup>
import { computed, ref, onMounted, watch } from 'vue';
import { UserOutlined, VideoCameraOutlined, FireOutlined, NotificationOutlined } from '@ant-design/icons-vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { defineProps } from 'vue';

const props = defineProps<{
  collapsed: boolean;
  onCollapse: (collapsed: boolean, type: string) => void;
}>();

const emit = defineEmits<{
  (e: 'update:collapsed', value: boolean): void;
}>();

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();
const isAdmin = computed(() => authStore.isAdmin);

const localCollapsed = ref(props.collapsed);
const broken = ref(false);

// 使用計算屬性來同步當前路由和選中的選單項
const selectedKeys = computed(() => {
  if (route.name === 'community') {
    return [route.params.id as string];
  }
  return [route.name as string];
});

// 監聽 props 變化
watch(() => props.collapsed, (newVal) => {
  localCollapsed.value = newVal;
});

const handleCollapse = (isCollapsed: boolean, type: string) => {
  localCollapsed.value = isCollapsed;
  emit('update:collapsed', isCollapsed);
  props.onCollapse(isCollapsed, type);
};

const onBreakpoint = (isBroken: boolean) => {
  broken.value = isBroken;
  if (isBroken) {
    localCollapsed.value = true;
  }
};

// 優化社群切換函數
const goToCommunity = async (communityId: string) => {
  try {
    // 先載入社群資料
    await authStore.getCommunityInfo(communityId);
    // 確保社群資料載入後再切換路由
    await router.push({
      name: 'community',
      params: { id: communityId },
      replace: true // 使用 replace 避免在歷史記錄中堆疊相同路由
    });
  } catch (error) {
    // 錯誤處理已在 store 中實作
    console.error('Failed to navigate to community:', error);
  }
};

// 在組件掛載時載入社群列表
onMounted(async () => {
  await authStore.getAllCommunities();

  // 如果當前在社群頁面，確保相關數據已載入
  if (route.name === 'community' && route.params.id) {
    await authStore.getCommunityInfo(route.params.id as string);
  }
});

// 監聽路由變化，確保數據同步
watch(
  () => route.params.id,
  async (newId) => {
    if (newId && route.name === 'community') {
      await authStore.getCommunityInfo(newId as string);
    }
  }
);
//回到首頁
const goTotop = () => {
  router.push("/");
};
</script>

<style scoped>
.site-layout-sub-header-background {
  background: #fff;
}

.site-layout-background {
  background: #fff;
}

.sidebar_group_text {
  font-size: 15px;
}

[data-theme='dark'] .site-layout-sub-header-background {
  background: #141414;
}

/* 自定義滾動條樣式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 10px;
}

::-webkit-scrollbar-thumb {
  background-color: rgba(0, 0, 0, 0.3);
  border-radius: 10px;
  border: 2px solid transparent;
  background-clip: content-box;
}

::-webkit-scrollbar-thumb:hover {
  background-color: rgba(0, 0, 0, 0.5);
}
</style>