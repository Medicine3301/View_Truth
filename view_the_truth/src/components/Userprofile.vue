<template>
    <div v-if="otherUser">
        <h2>{{ otherUser.una }}的個人資料</h2>
        <p>電子郵件: {{ otherUser.email }}</p>
        <p>角色: {{ otherUser.role }}</p>
        <img v-if="otherUser.avatar" :src="otherUser.avatar" alt="用戶頭像" />
    </div>
    <div v-else>
        <p>正在加載用戶信息...</p>
    </div>
</template>

<script>
import { useAuthStore } from '../stores/auth';
import { onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';

export default {
    setup() {
        const authStore = useAuthStore();
        const route = useRoute();

        // 當組件掛載時，根據路由參數查詢用戶信息
        onMounted(() => {
            const userId = route.params.id;
            authStore.getUserInfo(userId);
        });

        const otherUser = computed(() => authStore.otherUser);

        return {
            otherUser,
        };
    },
};
</script>