<template>
    <!-- 頂部Header -->
    <a-layout-header :style="{ background: '#fff', padding: 0 }">
        <div class="logo header-logo"><img src="/public/img/Doge.png" alt="網站Logo"></div>
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
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;">
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
</template>
<script lang="ts" setup>
import { computed, ref, reactive } from 'vue';
import { UserOutlined, LockOutlined } from '@ant-design/icons-vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';

// 路由實例
const router = useRouter();

// 認證store
const authStore = useAuthStore();
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
</script>
<style scoped>
.header-logo {
    height: 48px;
    margin-left: 16px;
    display: inline-flex;
    align-items: center;
    gap: 8px;
}

.logo img {
    height: 100%;
    max-height: 48px;
    width: auto;
    margin-top: 10px;
}

.site-layout-sub-header-background {
    background: #fff;
}
</style>