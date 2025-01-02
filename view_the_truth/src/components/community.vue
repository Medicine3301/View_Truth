<template>
  <a-layout>
    <Sidebar v-model:collapsed="collapsed" :onCollapse="onCollapse" />
    <a-layout :style="{ marginLeft: layoutMargin }">
      <Header />
      <a-layout-content :style="{ margin: '24px 16px 0', minHeight: '280px' }">
        <div class="content-container">
          <a-spin :spinning="loading">
            <!-- 社群資訊區塊 -->
            <template v-if="community">
              <div class="community-info">
                <h2 class="community-title">{{ community.cna }}</h2>
                <div class="post-header">
                  <p class="community-description">{{ community.descr }}</p>
                  <a-button type="primary" size="large" @click="showPostModal">發表文章</a-button>
                </div>
                <div class="post-header">
                  <p class="update-time">最後更新: {{ formatDate(community.last_update) }}</p>
                  <p style="font-size: 14px; color: #666; margin-right: 20px;">文章總數:{{ community.post_count }}</p>
                </div>
              </div>
            </template>

            <!-- 貼文列表區塊 -->
            <div class="post-list">
              <template v-if="posts && posts.length > 0">
                <div v-for="post in posts" :key="post.pid" class="post-item" @click="goToPost(post.pid)">
                  <div class="post-header">
                    <h3 class="post-title">{{ post.title }}</h3>
                    <span class="post-date">{{ formatDate(post.crea_date) }}</span>
                  </div>
                  <div class="post-footer">
                    <a-avatar size="small" class="user-avatar">{{ post.una.charAt(0) }}</a-avatar>
                    <span class="user-name">{{ post.una }}</span>
                    <!-- 添加留言圖標和留言數 -->
                    <div class="comment-icon">
                      <MessageOutlined />
                      <span class="comment-count">{{ post.comm_count }}</span>
                    </div>
                  </div>
                </div>
              </template>
              <a-empty v-else description="目前沒有貼文" />
            </div>
          </a-spin>
        </div>
      </a-layout-content>

      <!-- 發表文章彈窗 -->
      <a-modal v-model:open="postModalVisible" title="發表文章" :centered="true" :footer="null" :width="800"
        @cancel="handlePostCancel">
        <a-form :model="postForm" @finish="handlePostSubmit" :style="{ textAlign: 'left' }">
          <a-form-item name="title" :rules="[{ required: true, message: '請輸入文章標題！' }]">
            <a-input v-model:value="postForm.title" placeholder="文章標題" />
          </a-form-item>
          <tiny-fluent-editor v-model="value" :data-type="false" :data-upgrade="false" />
          內容:{{value}}
          <div style="display: flex; justify-content: center; gap: 16px;">
            <a-button type="primary" html-type="submit" :loading="postLoading">
              發表
            </a-button>
            <a-button @click="handlePostCancel">
              取消
            </a-button>
          </div>
        </a-form>
      </a-modal>

      <a-layout-footer style="text-align: center">
        識真網 ©2024 Created by Ant UED
      </a-layout-footer>
    </a-layout>
  </a-layout>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import Sidebar from '../layout/sidebar.vue'
import Header from '../layout/header.vue'
import { message } from 'ant-design-vue'
import { MessageOutlined } from '@ant-design/icons-vue'
import axios from 'axios'
import { TinyFluentEditor } from '@opentiny/vue'

const value=ref('')
// 基本狀態
const collapsed = ref(false)
const loading = ref(true)
const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// 計算屬性
const layoutMargin = computed(() => collapsed.value ? '0px' : '200px')
const community = computed(() => authStore.communityState.community)
const posts = computed(() => authStore.postState.posts)

// 發文相關狀態
const postModalVisible = ref(false)
const postLoading = ref(false)
const postForm = reactive({
  title: ''
})

// 日期格式化
const formatDate = (date: string): string => {
  return new Date(date).toLocaleString('zh-TW', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 資料載入函數
const loadCommunityData = async (communityId: string) => {
  loading.value = true
  try {
    await Promise.all([
      authStore.getCommunityInfo(communityId),
      authStore.getAllPosts(communityId)
    ])
  } catch (error) {
    message.error('載入社群資料失敗')
    console.error('Error loading community data:', error)
  } finally {
    loading.value = false
  }
}

// 監聽路由變化
watch(
  () => route.params.id,
  async (newId) => {
    if (newId && typeof newId === 'string') {
      await loadCommunityData(newId)
    }
  },
  { immediate: true }
)

// 處理最大字數
const maxLength = 50 // 最大字數限制

// 事件處理
const onCollapse = (isCollapsed: boolean, type: string) => {
  collapsed.value = isCollapsed
}

const goToPost = async (postId: string) => {
  try {
    await router.push({
      name: 'post',
      params: { id: postId }
    })
  } catch (error) {
    message.error('無法開啟貼文')
    console.error('Error navigating to post:', error)
  }
}

// 顯示發文視窗
const showPostModal = () => {
  if (!authStore.userState.isAuthenticated) {
    message.warning('請先登入後再發表文章')
    return
  }
  postModalVisible.value = true
}

// 處理發文取消
const handlePostCancel = () => {
  postModalVisible.value = false
  postForm.title = ''
}

// 處理發文提交
const handlePostSubmit = async () => {
  if (!authStore.userState.isAuthenticated) {
    message.warning('請先登入')
    return
  }

  try {
    postLoading.value = true
    const response = await axios.post('http://localhost:8000/api/post/post/create', {
      title: postForm.title,
      cid: route.params.id,
      uid: authStore.userState.user?.uid,
      una: authStore.userState.user?.una,
      content: value.value
    })

    if (response.status === 201) {
      message.success('發表成功')
      postModalVisible.value = false
      handlePostCancel()
      // 重新載入貼文列表
      await loadCommunityData(route.params.id as string)
    }

  } catch (error: any) {
    message.error(error.response?.data?.error || '發表失敗，請稍後再試')
  } finally {
    postLoading.value = false
  }
}

// 元件掛載
onMounted(async () => {
  const communityId = route.params.id
  if (communityId && typeof communityId === 'string') {
    await loadCommunityData(communityId)
  }
})
</script>

<style scoped>
.content-container {
  padding: 24px;
  background: #fff;
  min-height: 360px;
}

.community-info {
  margin-bottom: 24px;
  text-align: left;
  padding: 16px;
  background: #fafafa;
  border-radius: 4px;
}

.community-title {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 16px;
  color: #1890ff;
}

.community-description {
  font-size: 16px;
  color: #666;
  margin-bottom: 8px;
  line-height: 1.5;
}

.update-time {
  font-size: 14px;
  color: #999;
}

.post-list {
  margin-top: 20px;
}

.post-item {
  margin-bottom: 16px;
  padding: 16px;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.post-item:hover {
  background-color: #f5f5f5;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.09);
}

.post-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.post-title {
  font-size: 18px;
  color: #1890ff;
  margin: 0;
}

.post-date {
  font-size: 14px;
  color: #999;
}

.post-content {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
  line-height: 1.5;
}

.post-footer {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-avatar {
  margin-right: 8px;
}

.user-name {
  font-size: 14px;
  color: #999;
}

.comment-icon {
  display: flex;
  align-items: center;
  margin-left: auto;
  /* 留言數在最右側 */
  gap: 4px;
}

.comment-count {
  font-size: 14px;
  color: #666;
}

</style>
