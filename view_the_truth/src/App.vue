<template>
  <router-view v-if="isReady" />
  <div v-else class="loading">Loading...</div>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from './stores/auth'

const isReady = ref(false)
const authStore = useAuthStore()

onMounted(async () => {
    try {
        const token = localStorage.getItem('token') || authStore.tokenState.accessToken
        if (token) {
            await authStore.checkAuth()
        }
    } catch (error) {
        console.error('Authentication error:', error)
        localStorage.removeItem('token')
    } finally {
        isReady.value = true
    }
})
</script>

<style>
@import './style.css';
.loading {
  text-align: center;
  padding: 20px;
}
</style>

<!-- 根组件：作为整个应用的容器，使用 router-view 显示当前路由对应的组件 -->

<!--
這是主應用組件。
它只包含一個<router-view>組件,用於顯示當前路由對應的組件。
樣式部分引入了全局樣式文件style.css。
-->