<template>
    <a-layout>
        <a-layout-sider :style="{ height: '100vh', position: 'fixed', left: 0 }" breakpoint="md" collapsed-width="0"
            @collapse="onCollapse" @breakpoint="onBreakpoint" v-model:collapsed="collapsed">
            <div class="logo"><img src="/public/img/Doge.png" alt=""></div>
            <a-menu v-model:selectedKeys="selectedKeys" theme="dark" mode="inline">
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
                    <template v-for="board in authStore.communityState.community" :key="board.cid">
                        <a-menu-item @click="goToCommunity(board.cid)">
                            <a-avatar :size="30" style="margin-right: 10px;">
                                <template #icon>
                                    <img src="/public/img/unnamed.jpg" :alt="board.name" />
                                </template>
                            </a-avatar>
                            <span class="nav-text">{{ board.name }}</span>
                        </a-menu-item>
                    </template>
                </a-menu-item-group>
            </a-menu>
        </a-layout-sider>
        <a-layout :style="{ marginLeft: layoutMargin }">
            <!-- 頂部Header -->
            <a-layout-header :style="{ background: '#fff', padding: 0 }">
                <!-- 搜尋框 -->
                <a-input-search v-model:value="searchValue" style="width: 150px; margin-top: 15px; margin-left: 20px;"
                    placeholder="搜尋關鍵字" enter-button @search="onSearch" />

                <!-- 用戶操作區域 -->
                <div style="position: absolute; right: 20px; display: inline-block;">
                    <!-- 根據登入狀態顯示不同內容 -->
                    <template v-if="authStore.userState.isAuthenticated">
                        <a-dropdown>
                            <a class="ant-dropdown-link" @click.prevent>
                                <a-avatar style="margin-right: 8px;">
                                    {{ authStore.userState.user?.una?.charAt(0).toUpperCase() }}
                                </a-avatar>
                            </a>
                            <template #overlay>
                                <a-menu>
                                    <a-menu-item @click="goToUserProfile">
                                        用戶區
                                    </a-menu-item>
                                    <a-menu-item @click="handleLogout">
                                        登出
                                    </a-menu-item>
                                </a-menu>
                            </template>
                        </a-dropdown>
                    </template>
                    <template v-else>
                        <a-button type="primary" @click="showLoginModal">登入</a-button>
                    </template>

                    <!-- 登入彈窗 -->
                    <a-modal v-model:open="loginModalVisible" title="登入" :centered="true" :footer="null" :width="400"
                        @cancel="handleLoginCancel">
                        <a-form :model="loginForm" @finish="handleLoginSubmit" :style="{ textAlign: 'center' }">
                            <!-- 用戶名輸入 -->
                            <a-form-item name="username" :rules="[{ required: true, message: '請輸入使用者名稱！' }]">
                                <a-input v-model:value="loginForm.username" placeholder="使用者名稱">
                                    <template #prefix>
                                        <UserOutlined />
                                    </template>
                                </a-input>
                            </a-form-item>

                            <!-- 密碼輸入 -->
                            <a-form-item name="password" :rules="[{ required: true, message: '請輸入密碼！' }]">
                                <a-input-password v-model:value="loginForm.password" placeholder="密碼">
                                    <template #prefix>
                                        <LockOutlined />
                                    </template>
                                </a-input-password>
                            </a-form-item>

                            <!-- 記住我和註冊連結 -->
                            <div
                                style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;">
                                <a-checkbox v-model:checked="loginForm.remember">記住我</a-checkbox>
                                <router-link to="/register" style="color: #1890ff;">還沒註冊嗎?</router-link>
                            </div>

                            <!-- 提交按鈕 -->
                            <div style="display: flex; justify-content: center; gap: 16px;">
                                <a-button type="primary" html-type="submit" :loading="loginLoading">
                                    登入
                                </a-button>
                                <a-button @click="handleLoginCancel">
                                    取消
                                </a-button>
                            </div>
                        </a-form>
                    </a-modal>
                </div>
            </a-layout-header>
            <a-layout-content :style="{ background: ' #ececec', margin: '24px 16px 0' }">
                <div :style="{ padding: '24px', background: '#fff', minHeight: '360px', textAlign: 'center' }">
                    <a-pagination :default-current="6" :total="500" :style="{ textAlign: 'center' }" />
                </div>
            </a-layout-content>
            <a-layout-footer style="text-align: center">
                Ant Design ©2018 Created by Ant UED
            </a-layout-footer>
        </a-layout>
    </a-layout>
</template>

<script lang="ts" setup>
import { computed, ref, reactive } from 'vue';
import { UserOutlined, VideoCameraOutlined, FireOutlined, NotificationOutlined, LockOutlined } from '@ant-design/icons-vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';

// 路由實例
const router = useRouter();

// 認證store
const authStore = useAuthStore();
// 判斷是否為管理員
const isAdmin = computed(() => authStore.isAdmin);
// 側邊欄狀態
const collapsed = ref(false);
const broken = ref(false);

// 計算側邊欄寬度
const layoutMargin = computed(() => {
    if (broken.value) {
        return collapsed.value ? '0px' : '200px';
    }
    return '200px';
});

// 側邊欄摺疊處理
const onCollapse = (isCollapsed: boolean, type: string) => {
    console.log(isCollapsed, type);
    collapsed.value = isCollapsed;
};

// 響應式斷點處理
const onBreakpoint = (isBroken: boolean) => {
    console.log(isBroken);
    broken.value = isBroken;
};

// 選中的菜單項
const selectedKeys = ref<string[]>(['4']);

// 搜尋相關
const searchValue = ref<string>('');
const onSearch = (searchValue: string) => {
    console.log('搜尋值:', searchValue);
};


// 登入表單相關
const loginModalVisible = ref<boolean>(false);
const loginLoading = ref<boolean>(false);
const loginForm = reactive({
    username: '',
    password: '',
    remember: true,
});

// 顯示登入視窗
const showLoginModal = () => {
    loginModalVisible.value = true;
};

// 處理登入取消
const handleLoginCancel = () => {
    loginModalVisible.value = false;
    // 重置表單
    loginForm.username = '';
    loginForm.password = '';
    loginForm.remember = true;
};

// 處理登入提交
const handleLoginSubmit = async () => {
    try {
        loginLoading.value = true;
        const success = await authStore.login(loginForm.username, loginForm.password);

        if (success) {
            loginModalVisible.value = false;
            // 重置表單
            handleLoginCancel();
        }
    } finally {
        loginLoading.value = false;
    }
};

// 處理登出
const handleLogout = () => {
    authStore.logout();
    router.push('/');
};

const goToUserProfile = () => {
    if (authStore.userState.user && authStore.userState.user.uid) {
        // 跳轉到用戶個人資料頁面
        router.push({ name: 'userprofile', params: { id: authStore.userState.user.uid } });
    } else {
        console.error('未登入或無法取得用戶ID');
    }
};

// 跳轉到社群頁面
const goToCommunity = (communityId: string) => {
    router.push({ name: 'community', params: { cid: communityId } });
};
</script>

<style scoped>
.logo {
    height: 64px;
    background: rgba(255, 255, 255, 0.2);
    margin: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.logo img {
    height: 100%;
    max-height: 48px;
    width: auto;
}

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