<template>
    <div class="user-profile-container">
      <a-row :gutter="[24, 24]">
        <!-- Left Column - User Card -->
        <a-col :xs="24" :sm="24" :md="8" :lg="6">
          <a-card :loading="!otherUser" class="user-card">
            <template #cover>
              <div class="cover-background">
                <div class="avatar-container">
                  <a-avatar 
                    :size="104" 
                    :src="otherUser?.avatar"
                    class="user-avatar"
                  >
                    {{ otherUser?.una.charAt(0).toUpperCase() }}
                  </a-avatar>
                </div>
              </div>
            </template>
            <template #title>
              <div class="text-center">
                <h2 class="user-name">{{ otherUser?.una }}</h2>
                <a-tag :color="getRoleColor(otherUser?.role)">{{ otherUser?.role }}</a-tag>
              </div>
            </template>
            <a-divider />
            <a-descriptions :column="1">
              <a-descriptions-item label="電子郵件">
                <a-typography-text copyable>{{ otherUser?.email }}</a-typography-text>
              </a-descriptions-item>
              <a-descriptions-item label="性別">
                <a-tag :color="otherUser?.usex === '男' ? 'blue' : 'pink'">
                  {{ otherUser?.usex }}
                </a-tag>
              </a-descriptions-item>
              <a-descriptions-item label="生日">
                {{ formatDate(otherUser?.birthday) }}
              </a-descriptions-item>
            </a-descriptions>
            
            <template #actions>
              <a-button-group style="width: 100%; display: flex; gap: 8px; padding: 0 16px;">
                <a-button type="primary" style="flex: 1">
                  <template #icon><MessageOutlined /></template>
                  發送訊息
                </a-button>
                <a-button style="flex: 1">
                  <template #icon><UserAddOutlined /></template>
                  加為好友
                </a-button>
              </a-button-group>
            </template>
          </a-card>
        </a-col>
  
        <!-- Right Column - Tabs Content -->
        <a-col :xs="24" :sm="24" :md="16" :lg="18">
          <a-card :bordered="false">
            <a-tabs default-active-key="1">
              <!-- 動態消息 Tab -->
              <a-tab-pane key="1" tab="動態消息">
                <a-list
                  class="activity-list"
                  :loading="!otherUser"
                  item-layout="horizontal"
                  :data-source="userActivities"
                >
                  <template #renderItem="{ item }">
                    <a-list-item>
                      <a-list-item-meta
                        :description="item.time"
                      >
                        <template #title>
                          <a href="javascript:;">{{ item.title }}</a>
                        </template>
                        <template #avatar>
                          <a-avatar :style="{ backgroundColor: item.avatarColor }">
                            {{ item.icon }}
                          </a-avatar>
                        </template>
                      </a-list-item-meta>
                    </a-list-item>
                  </template>
                </a-list>
              </a-tab-pane>
  
              <!-- 發布的貼文 Tab -->
              <a-tab-pane key="2" tab="發布的貼文">
                <a-list
                  class="post-list"
                  :loading="!otherUser"
                  item-layout="vertical"
                  :data-source="userPosts"
                >
                  <template #renderItem="{ item }">
                    <a-list-item>
                      <template #actions>
                        <a-space>
                          <a-button type="link">
                            <template #icon><LikeOutlined /></template>
                            {{ item.likes }}
                          </a-button>
                          <a-button type="link">
                            <template #icon><MessageOutlined /></template>
                            {{ item.comments }}
                          </a-button>
                          <a-button type="link">
                            <template #icon><ShareAltOutlined /></template>
                            分享
                          </a-button>
                        </a-space>
                      </template>
                      <a-list-item-meta
                        :title="item.title"
                        :description="item.createTime"
                      >
                        <template #avatar>
                          <a-avatar :src="otherUser?.avatar">
                            {{ otherUser?.una.charAt(0).toUpperCase() }}
                          </a-avatar>
                        </template>
                      </a-list-item-meta>
                      {{ item.content }}
                    </a-list-item>
                  </template>
                </a-list>
              </a-tab-pane>
  
              <!-- 個人資料 Tab -->
              <a-tab-pane key="3" tab="個人資料">
                <a-descriptions 
                  bordered 
                  :column="{ xxl: 2, xl: 2, lg: 2, md: 1, sm: 1, xs: 1 }"
                >
                  <a-descriptions-item label="用戶名稱">
                    {{ otherUser?.una }}
                  </a-descriptions-item>
                  <a-descriptions-item label="帳戶角色">
                    {{ otherUser?.role }}
                  </a-descriptions-item>
                  <a-descriptions-item label="電子郵件">
                    {{ otherUser?.email }}
                  </a-descriptions-item>
                  <a-descriptions-item label="性別">
                    {{ otherUser?.usex }}
                  </a-descriptions-item>
                  <a-descriptions-item label="生日">
                    {{ formatDate(otherUser?.birthday) }}
                  </a-descriptions-item>
                  <a-descriptions-item label="註冊時間">
                    2024-01-01
                  </a-descriptions-item>
                </a-descriptions>
              </a-tab-pane>
  
              <!-- 收藏的貼文 Tab -->
              <a-tab-pane key="4" tab="收藏的貼文">
                <a-empty description="暫無收藏的貼文" />
              </a-tab-pane>
            </a-tabs>
          </a-card>
        </a-col>
      </a-row>
    </div>
  </template>
  
  <script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useRoute } from 'vue-router'
import {
  UserAddOutlined,
  MessageOutlined,
  LikeOutlined,
  ShareAltOutlined
} from '@ant-design/icons-vue'

// 獲取 store 和 route 實例
const authStore = useAuthStore()
const route = useRoute()

// 定義活動列表數據
const userActivities = ref([
  {
    title: '在社群"程式設計"發布了新貼文',
    time: '2024-03-20 14:30',
    avatarColor: '#1890ff',
    icon: '文'
  },
  {
    title: '加入了新社群"Web開發"',
    time: '2024-03-19 09:15',
    avatarColor: '#52c41a',
    icon: '群'
  },
  {
    title: '收藏了一篇文章',
    time: '2024-03-18 16:45',
    avatarColor: '#faad14',
    icon: '收'
  }
])

// 定義貼文列表數據
const userPosts = ref([
  {
    title: 'Vue.js 3.0 新特性介紹',
    content: 'Vue 3.0 帶來了許多令人興奮的新特性，包括 Composition API、更好的 TypeScript 支持等...',
    createTime: '2024-03-20 14:30',
    likes: 42,
    comments: 15
  },
  {
    title: '前端效能優化技巧分享',
    content: '本文將分享一些實用的前端效能優化技巧，包括圖片懶加載、代碼分割等...',
    createTime: '2024-03-18 16:45',
    likes: 38,
    comments: 12
  }
])

// 在組件掛載時獲取用戶信息
onMounted(async () => {
  const userId = route.params.id as string
  await authStore.getUserInfo(userId)
})

// 計算屬性：獲取其他用戶信息
const otherUser = computed(() => authStore.userState.otherUser)

// 日期格式化函數
const formatDate = (dateString: string) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('zh-TW', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  }).format(date)
}

// 根據用戶角色獲取對應的顏色
const getRoleColor = (role?: string) => {
  const roleColors: Record<string, string> = {
    'admin': '#f50',
    'moderator': '#108ee9',
    'user': '#87d068'
  }
  return roleColors[role || 'user']
}

// 由於使用 script setup，這些變量和函數會自動暴露給模板使用
// 不需要顯式返回
</script>
  
  <style scoped>
  .user-profile-container {
    padding: 24px;
    background: #f0f2f5;
    min-height: 100vh;
  }
  
  .user-card {
    background: #fff;
  }
  
  .cover-background {
    height: 120px;
    background: linear-gradient(135deg, #1890ff 0%, #36cfc9 100%);
    position: relative;
  }
  
  .avatar-container {
    position: absolute;
    bottom: -52px;
    left: 50%;
    transform: translateX(-50%);
  }
  
  .user-avatar {
    border: 4px solid #fff;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  }
  
  .user-name {
    margin-top: 40px;
    margin-bottom: 8px;
  }
  
  .activity-list,
  .post-list {
    margin-top: 16px;
  }
  
  :deep(.ant-tabs-nav) {
    margin-bottom: 16px;
  }
  
  :deep(.ant-card-actions) {
    background: #fafafa;
  }
  
  :deep(.ant-descriptions-item-label) {
    width: 120px;
  }
  </style>