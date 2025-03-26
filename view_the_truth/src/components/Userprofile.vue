<template>
  <div class="user-profile-container">
    <a-page-header style="border: 1px solid rgb(235, 237, 240)" title="回首頁" @back="goTotop" />
    <a-row :gutter="[24, 24]">
      <!-- Left Column - User Card -->
      <a-col :xs="24" :sm="24" :md="8" :lg="6">
        <a-card :loading="!otherUser" class="user-card">
          <template #cover>
            <div class="cover-background">
              <div class="avatar-container">
                <a-avatar :size="104" :src="otherUser?.avatar" class="user-avatar">
                  {{ otherUser?.una.charAt(0).toUpperCase() }}
                </a-avatar>
                <!-- 新增圖片上傳功能 -->
                <div class="upload-avatar">
                  <a-upload v-model:file-list="fileList" action="http://localhost:8000/api/upload-avatar"
                    list-type="picture-card" @preview="handlePreview" :show-upload-list="false"
                    :before-upload="beforeUpload">
                    <div>
                      <plus-outlined />
                      <div style="margin-top: 8px">上傳頭像</div>
                    </div>
                  </a-upload>
                </div>
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
              <a-tag :color="otherUser?.usex === '1' ? 'blue' : 'pink'">
                {{ otherUser?.usex === '1' ? '男' : '女' }}
              </a-tag>
            </a-descriptions-item>
            <a-descriptions-item label="生日">
              {{ formatDate(otherUser?.birthday) }}
            </a-descriptions-item>
          </a-descriptions>

          <template #actions>
            <a-button-group style="width: 100%; display: flex; gap: 8px; padding: 0 16px;">
              <a-button type="primary" style="flex: 1">
                <template #icon>
                  <MessageOutlined />
                </template>
                發送訊息
              </a-button>
              <a-button style="flex: 1">
                <template #icon>
                  <UserAddOutlined />
                </template>
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
            <a-tab-pane key="2" tab="發布的貼文">
              <a-list v-if="(userPosts ?? []).length > 0" class="post-list" :loading="loadingPosts"
                item-layout="vertical" :data-source="userPosts">
                <template #renderItem="{ item }">
                  <a-list-item class="post-list-item" @click="goToPost(item.pid)" style="cursor: pointer;">
                    <template #actions>
                      <a-space>
                        <a-button type="link">
                          <template #icon>
                            <LikeOutlined />
                          </template>
                          {{ item.likes || 0 }}
                        </a-button>
                        <a-button type="link">
                          <template #icon>
                            <MessageOutlined />
                          </template>
                          {{ item.comm_count || 0 }}
                        </a-button>
                      </a-space>
                    </template>
                    <a-list-item-meta :title="item.title" :description="formatDate(item.crea_date)">
                      <template #avatar>
                        <a-avatar :src="otherUser?.avatar">
                          {{ otherUser?.una.charAt(0).toUpperCase() }}
                        </a-avatar>
                      </template>
                    </a-list-item-meta>
                    <span v-html="item.content"></span>
                  </a-list-item>
                </template>
              </a-list>
              <a-empty v-else description="暫無發布的貼文" />
            </a-tab-pane>

            <!-- 個人資料 Tab -->
            <a-tab-pane key="3" tab="個人資料">
              <a-descriptions bordered :column="{ xxl: 2, xl: 2, lg: 2, md: 1, sm: 1, xs: 1 }">
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
                  {{ otherUser?.usex === '1' ? '男' : '女' }}
                </a-descriptions-item>
                <a-descriptions-item label="生日">
                  {{ formatDate(otherUser?.birthday) }}
                </a-descriptions-item>
                <a-descriptions-item label="註冊時間">
                  {{ formatDate(otherUser?.reg_date) }}
                </a-descriptions-item>
              </a-descriptions>
            </a-tab-pane>

            <!-- 收藏的貼文 Tab -->
            <a-tab-pane key="4" tab="收藏的貼文">
              <a-list v-if="(userFavorites ?? []).length > 0" class="post-list " :loading="loadingPosts" item-layout="vertical"
                :data-source="userFavorites">
                <template #renderItem="{ item }">
                  <a-list-item class="post-list-item" @click="goToPost(item.pid)" style="cursor: pointer;">
                    <a-list-item-meta :title="item.title" :description="formatDate(item.crea_date)">
                      <template #avatar>
                        <a-avatar :src="otherUser?.avatar">
                          {{ otherUser?.una.charAt(0).toUpperCase() }}
                        </a-avatar>
                      </template>
                    </a-list-item-meta>
                    <span v-html="item.content"></span>
                  </a-list-item>
                </template>
              </a-list>
              <a-empty v-else description="暫無收藏的貼文" />
            </a-tab-pane>

          </a-tabs>
        </a-card>
      </a-col>
    </a-row>
    <!-- 預覽模態框 -->
    <a-modal :open="previewVisible" :title="previewTitle" :footer="null" @cancel="handleCancel">
      <img alt="example" style="width: 100%" :src="previewImage" />
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue';
import { message } from 'ant-design-vue';
import { useAuthStore } from '../stores/auth';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';

const authStore = useAuthStore();
const route = useRoute();
const router = useRouter();



// 是否為管理員用戶
const isAdminUser = computed(() => {
  return otherUser.value?.role === 'admin'
})

//計算屬性：獲取其他用戶信息
const otherUser = computed(() => authStore.userState.otherUser)
const userPosts = computed(() => authStore.postState.posts); // 用戶貼文數據
const userFavorites = computed(() => authStore.postState.favorites); // 用戶收藏的貼文數據
const loadingPosts = ref(true); // 貼文加載狀態

// 獲取用戶貼文
const fetchUserPosts = async () => {
  loadingPosts.value = true;
  try {
    const userId = route.params.id as string; // 從路由參數獲取用戶 ID
    await authStore.getuserPosts(userId); // 調用 store 的方法獲取用戶貼文
    await authStore.getuserFavorites(userId); // 獲取用戶信息
  } catch (error) {
    console.error('Failed to fetch user posts:', error);
  } finally {
    loadingPosts.value = false;
  }
};

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



// 日期格式化函數
const formatDate = (dateString?: string) => {
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
  return roleColors[role ?? 'user']
}
const goTotop = () => {
  router.push("/");
};

// 圖片上傳相關邏輯
const fileList = ref([])
const previewVisible = ref(false)
const previewImage = ref('')
const previewTitle = ref('')

const handlePreview = async (file: any) => {
  if (!file.url && !file.preview) {
    file.preview = await getBase64(file.originFileObj)
  }
  previewImage.value = file.url || file.preview
  previewVisible.value = true
  previewTitle.value = file.name || file.url.substring(file.url.lastIndexOf('/') + 1)
}

const handleCancel = () => {
  previewVisible.value = false
}

const beforeUpload = (file: any) => {
  const isJpgOrPng = file.type === 'image/jpeg' || file.type === 'image/png'
  if (!isJpgOrPng) {
    message.error('You can only upload JPG/PNG file!')
  }
  const isLt2M = file.size / 1024 / 1024 < 2
  if (!isLt2M) {
    message.error('Image must smaller than 2MB!')
  }
  return isJpgOrPng && isLt2M
}

const getBase64 = (file: any) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.readAsDataURL(file)
    reader.onload = () => resolve(reader.result)
    reader.onerror = error => reject(error)
  })
}

// 在組件掛載時獲取用戶信息
onMounted(async () => {
  const userId = route.params.id as string
  await authStore.getUserInfo(userId)
  await fetchUserPosts()
})


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

.upload-avatar {
  position: absolute;
  bottom: -20px;
  left: 50%;
  transform: translateX(-50%);
  text-align: center;
}

.ant-upload-select-picture-card {
  width: 104px;
  height: 104px;
  border-radius: 50%;
  overflow: hidden;
  background: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ant-upload-select-picture-card:hover {
  border-color: #1890ff;
}

.ant-upload-select-picture-card .ant-upload-text {
  margin-top: 8px;
  color: #666;
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
/* 貼文項目樣式 */
.post-list-item {
  padding: 16px;
  background-color: #ffffff;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  margin-bottom: 16px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  cursor: pointer;
}

.post-list-item:hover {
  background-color: #e6f7ff; /* 更明顯的淡藍色背景 */
  border-color: #1890ff;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15); /* 增強陰影效果 */
  transform: translateY(-4px); /* 上移效果 */
}
</style>