<template>
    <a-layout>
        <a-layout-sider :style="{ height: '100vh', position: 'fixed', left: 0 }" breakpoint="md" collapsed-width="0"
            @collapse="onCollapse" @breakpoint="onBreakpoint" v-model:collapsed="collapsed">
            <div class="logo"><img src="/public/img/Doge.png" alt=""></div>
            <a-menu v-model:selectedKeys="selectedKeys" theme="dark" mode="inline">
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
                <a-menu-item-group key="g1" title="討論看板" style="margin-top: 20px;"
                    :style="{ overflow: 'auto', height: 'calc(100vh - 200px)', paddingRight: '5px' }">
                    <a-menu-item key="4">
                        <a-avatar :size="30" style="margin-right: 10px;">
                            <template #icon>
                                <img src="/public/img/unnamed.jpg" alt="">
                            </template>
                        </a-avatar>
                        <span class="nav-text">閒聊</span>
                    </a-menu-item>
                    <a-menu-item key="5">
                        <a-avatar :size="30" style="margin-right: 10px;">
                            <template #icon>
                                <img src="/public/img/unnamed.jpg" alt="">
                            </template>
                        </a-avatar>
                        <span class="nav-text">闢謠</span>
                    </a-menu-item>
                    <a-menu-item key="6">
                        <a-avatar :size="30" style="margin-right: 10px;">
                            <template #icon>
                                <img src="/public/img/unnamed.jpg" alt="">
                            </template>
                        </a-avatar>
                        <span class="nav-text">八卦</span>
                    </a-menu-item>
                    <a-menu-item key="7">
                        <a-avatar :size="30" style="margin-right: 10px;">
                            <template #icon>
                                <img src="/public/img/unnamed.jpg" alt="">
                            </template>
                        </a-avatar>
                        <span class="nav-text">新聞</span>
                    </a-menu-item>
                    <a-menu-item key="8">
                        <a-avatar :size="30" style="margin-right: 10px;">
                            <template #icon>
                                <img src="/public/img/unnamed.jpg" alt="">
                            </template>
                        </a-avatar>
                        <span class="nav-text">科技</span>
                    </a-menu-item>
                    <a-menu-item key="9">
                        <a-avatar :size="30" style="margin-right: 10px;">
                            <template #icon>
                                <img src="/public/img/unnamed.jpg" alt="">
                            </template>
                        </a-avatar>
                        <span class="nav-text">動漫</span>
                    </a-menu-item>
                    <a-menu-item key="10">
                        <a-avatar :size="30" style="margin-right: 10px;">
                            <template #icon>
                                <img src="/public/img/unnamed.jpg" alt="">
                            </template>
                        </a-avatar>
                        <span class="nav-text">繪圖</span>
                    </a-menu-item>
                    <a-menu-item key="11">
                        <a-avatar :size="30" style="margin-right: 10px;">
                            <template #icon>
                                <img src="/public/img/unnamed.jpg" alt="">
                            </template>
                        </a-avatar>
                        <span class="nav-text">迷因</span>
                    </a-menu-item>
                    <a-menu-item key="12">
                        <a-avatar :size="30" style="margin-right: 10px;">
                            <template #icon>
                                <img src="/public/img/unnamed.jpg" alt="">
                            </template>
                        </a-avatar>
                        <span class="nav-text">政治</span>
                    </a-menu-item>
                    <a-menu-item key="13">
                        <a-avatar :size="30" style="margin-right: 10px;">
                            <template #icon>
                                <img src="/public/img/unnamed.jpg" alt="">
                            </template>
                        </a-avatar>
                        <span class="nav-text">遊戲</span>
                    </a-menu-item>
                    <a-menu-item key="14">
                        <a-avatar :size="30" style="margin-right: 10px;">
                            <template #icon>
                                <img src="/public/img/unnamed.jpg" alt="">
                            </template>
                        </a-avatar>
                        <span class="nav-text">感情</span>
                    </a-menu-item>
                    <a-menu-item key="15">
                        <a-avatar :size="30" style="margin-right: 10px;">
                            <template #icon>
                                <img src="/public/img/unnamed.jpg" alt="">
                            </template>
                        </a-avatar>
                        <span class="nav-text">文學</span>
                    </a-menu-item>
                    <a-menu-item key="16">
                        <a-avatar :size="30" style="margin-right: 10px;">
                            <template #icon>
                                <img src="/public/img/unnamed.jpg" alt="">
                            </template>
                        </a-avatar>
                        <span class="nav-text">股票</span>
                    </a-menu-item>
                </a-menu-item-group>
            </a-menu>
        </a-layout-sider>
        <a-layout :style="{ marginLeft: layoutMargin }">
            <a-layout-header :style="{ background: '#fff', padding: 0 }">
                <!--搜尋框-->
                <a-input-search v-model:value="value" style="width: 300px;margin-top: 15px;margin-left: 20px;"
                    placeholder="搜尋關鍵字" enter-button @search="onSearch" />
                <!--登入按鈕、視窗-->
                <div style="position: absolute;
                 right: 20px;
                 display: inline-block;">
                    <a-button type="primary" @click="showModal">登入</a-button>
                    <a-modal v-model:open="open" title="登入" :centered="true" :footer="null" :width="400">
                        <a-form :model="formState" name="basic" @finish="onFinish" @finishFailed="onFinishFailed"
                            :style="{ textAlign: 'center' }">
                            <a-form-item name="username" :rules="[{ required: true, message: '請輸入使用者名稱！' }]"
                                :style="{ marginBottom: '24px' }">
                                <a-input v-model:value="formState.username" placeholder="使用者名稱">
                                    <template #prefix>
                                        <UserOutlined />
                                    </template>
                                </a-input>
                            </a-form-item>

                            <a-form-item name="password" :rules="[{ required: true, message: '請輸入密碼！' }]"
                                :style="{ marginBottom: '24px' }">
                                <a-input-password v-model:value="formState.password" placeholder="密碼">
                                    <template #prefix>
                                        <LockOutlined />
                                    </template>
                                </a-input-password>
                            </a-form-item>

                            <div
                                style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;">
                                <a-checkbox v-model:checked="formState.remember">記住我</a-checkbox>
                                <router-link to="/register" style="color: #1890ff;">還沒註冊嗎?</router-link>
                            </div>

                            <div style="display: flex; justify-content: center; gap: 16px;">
                                <a-button type="primary" html-type="submit" :loading="loading">
                                    登入
                                </a-button>
                                <a-button @click="handleCancel">
                                    取消
                                </a-button>
                            </div>
                        </a-form>
                    </a-modal>
                </div>
            </a-layout-header>
            <a-layout-content :style="{ background: ' #ececec', margin: '24px 16px 0' }">
                <div :style="{ padding: '24px', background: '#fff', minHeight: '360px', textAlign: 'center' }">
                    ...
                    <br />
                    Really
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    long
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    ...
                    <br />
                    ...
                    <br />
                    long
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    ...
                    <br />
                    ...
                    <br />
                    long
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    ...
                    <br />
                    content

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
import { UserOutlined, VideoCameraOutlined, UploadOutlined, FireFilled, BellFilled, FireOutlined, BellOutlined, NotificationOutlined } from '@ant-design/icons-vue';
import { RouterLink } from 'vue-router';

//響應式相關
const collapsed = ref(false);
const broken = ref(false);
const layoutMargin = computed(() => {
    if (broken.value) {
        return collapsed.value ? '0px' : '200px';
    }
    return '200px';
});
const onCollapse = (isCollapsed: boolean, type: string) => {
    console.log(isCollapsed, type);
    collapsed.value = isCollapsed;
};

const onBreakpoint = (isBroken: boolean) => {
    console.log(isBroken);
    broken.value = isBroken;
};

const selectedKeys = ref<string[]>(['4']);

const value = ref<string>('');
//搜尋相關
const onSearch = (searchValue: string) => {
    console.log('use value', searchValue);
    console.log('or use this.value', value.value);
};
// 表單相關
interface FormState {
    username: string;
    password: string;
    remember: boolean;
}

const formState = reactive<FormState>({
    username: '',
    password: '',
    remember: true,
});

const open = ref<boolean>(false);
const loading = ref<boolean>(false);

const showModal = () => {
    open.value = true;
};

const handleCancel = () => {
    open.value = false;
    // 重置表單
    formState.username = '';
    formState.password = '';
    formState.remember = true;
};

const onFinish = (values: any) => {
    loading.value = true;
    setTimeout(() => {
        console.log('Success:', values);
        loading.value = false;
        open.value = false;
        // 重置表單
        formState.username = '';
        formState.password = '';
        formState.remember = true;
    }, 2000);
};

const onFinishFailed = (errorInfo: any) => {
    console.log('Failed:', errorInfo);
};

//登入部分
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()

// 登入
const handleLogin = async () => {
    const success = await authStore.login(formState.username, formState.password)
    if (success) {
        // 導航到首頁或其他頁面
    }
}
</script>

<style scoped>
.logo {
    height: 64px;
    /* 设置 logo 容器高度 */
    background: rgba(255, 255, 255, 0.2);
    margin: 16px;
    display: flex;
    align-items: center;
    /* 垂直居中对齐 */
    justify-content: center;
    /* 水平居中对齐 */
}

.logo img {
    height: 100%;
    /* 让图片高度占满容器 */
    max-height: 48px;
    /* 设置图片最大高度以确保适配 */
    width: auto;
    /* 保持图片的宽高比 */
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

/* 自定义滚动条样式 */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

/* 滚动条轨道 */
::-webkit-scrollbar-track {
    background: #f1f1f1;
    /* 滚动条背景颜色 */
    border-radius: 10px;
    /* 圆角 */
}

/* 滚动条滑块 */
::-webkit-scrollbar-thumb {
    background-color: rgba(0, 0, 0, 0.3);
    /* 滑块颜色 */
    border-radius: 10px;
    /* 圆角 */
    border: 2px solid transparent;
    /* 增加内边距以使滑块显得更小 */
    background-clip: content-box;
    /* 保持滑块内容适配 */
}

/* 滑块在悬停状态下的样式 */
::-webkit-scrollbar-thumb:hover {
    background-color: rgba(0, 0, 0, 0.5);
    /* 悬停时的滑块颜色 */
}
</style>