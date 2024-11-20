<template>
    <a-layout-sider :style="{ height: '100vh', position: 'fixed', left: 0 }" breakpoint="md" collapsed-width="0"
        v-model:collapsed="localCollapsed" @collapse="handleCollapse" @breakpoint="onBreakpoint">

        <a-menu v-model:selectedKeys="selectedKeys" theme="dark" mode="inline" style="margin-top: 20px;">
            <a-menu-item key="home">
                <HomeOutlined />
                <span class="nav-text">首頁</span>
            </a-menu-item>
            <a-menu-item key="1">
                <NotificationOutlined />
                <span class="nav-text">即時消息</span>
            </a-menu-item>
            <a-menu-item key="2">
                <VideoCameraOutlined />
                <span class="nav-text">新聞專區</span>
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
                <a-menu-item key="adminPanel2">
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
                                <img src="/public/img/unnamed.jpg" :alt="board.cna" />
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
import { computed, ref, onMounted ,watch} from 'vue';
import { UserOutlined, VideoCameraOutlined, FireOutlined, NotificationOutlined } from '@ant-design/icons-vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { defineProps } from 'vue';
//同步
// 正確定義 props
const props = defineProps<{
  collapsed: boolean;
  onCollapse: (collapsed: boolean, type: string) => void;
}>();

// 定義 emit
const emit = defineEmits<{
  (e: 'update:collapsed', value: boolean): void;
}>();

// 本地狀態
const localCollapsed = ref(props.collapsed);

// 監聽 props 變化
watch(() => props.collapsed, (newVal) => {
  localCollapsed.value = newVal;
});

// 處理折疊狀態變化
const handleCollapse = (isCollapsed: boolean, type: string) => {
  localCollapsed.value = isCollapsed;
  emit('update:collapsed', isCollapsed);
  props.onCollapse(isCollapsed, type);
};

// 路由實例
const router = useRouter();

// 認證store
const authStore = useAuthStore();
// 判斷是否為管理員
const isAdmin = computed(() => authStore.isAdmin);
// 側邊欄狀態
const collapsed = ref(false);
const broken = ref(false);




const onBreakpoint = (isBroken: boolean) => {
    broken.value = isBroken;
    if (isBroken) {
        collapsed.value = true; // 當進入斷點時自動折疊
    }
};


// 選中的菜單項
const selectedKeys = ref<string[]>(['4']);


// 跳轉到社群頁面
const goToCommunity = (communityId: string) => {
    router.push({ name: 'community', params: { id: communityId } });
};
onMounted(async () => {
    await authStore.getAllCommunities();
});
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