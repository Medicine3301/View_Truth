<template>
  <a-layout>
    <Sidebar v-model:collapsed="collapsed" :onCollapse="onCollapse" />
    <a-layout :style="{ marginLeft: layoutMargin }">
      <Header />
      <a-layout-content :style="{ background: '#ececec', margin: '24px 16px 0' }">
        <a-spin :spinning="loading">
          <!-- 貼文內容卡片 -->
          <template v-if="post">
            <a-card class="post-card" :bordered="false">
              <template #title>
                <div class="post-header">
                  <h2 class="post-title">{{ post.title }}</h2>
                  <div class="post-meta">
                    <a-avatar class="avatar" size="small" @click="goToUserProfile(post.uid)">{{ post.una.charAt(0)
                    }}</a-avatar>
                    <span class="author-name">{{ post.una }}</span>
                    <span class="post-time">{{ formatDate(post.crea_date) }}</span>
                    <!--評分模組-->
                    <a-rate v-model:value="value" />
                    <!--收藏標籤-->
                    <label class="ui-bookmark">
                      <input type="checkbox">
                      <div class="bookmark">
                        <svg viewBox="0 0 32 32">
                          <g>
                            <path
                              d="M27 4v27a1 1 0 0 1-1.625.781L16 24.281l-9.375 7.5A1 1 0 0 1 5 31V4a4 4 0 0 1 4-4h14a4 4 0 0 1 4 4z">
                            </path>
                          </g>
                        </svg>
                      </div>
                    </label>
                    
                  </div>
                </div>
              </template>
              <div class="post-content">
                <p>{{ post.content }}</p>
              </div>
            </a-card>

            <!-- 評論區塊 -->
            <a-card class="comment-card" :bordered="false" title="評論">
              <!-- 發表評論 -->
              <div class="comment-form">
                <a-form :model="commentForm" @finish="handleCommentSubmit">
                  <a-form-item name="title" :rules="[{ required: true, message: '請輸入標題' }]">
                    <a-textarea v-model:value="commentForm.title" :rows="1" placeholder="寫下你的標題..."
                      :disabled="!postStore.userState.isAuthenticated" />
                  </a-form-item>
                  <a-form-item name="content" :rules="[{ required: true, message: '請輸入評論內容' }]">
                    <a-textarea v-model:value="commentForm.content" :rows="4" placeholder="寫下你的評論..."
                      :disabled="!postStore.userState.isAuthenticated" />
                  </a-form-item>
                  <a-form-item>
                    <a-button type="primary" html-type="submit" :loading="submitting"
                      :disabled="!postStore.userState.isAuthenticated">
                      發表評論
                    </a-button>
                  </a-form-item>
                </a-form>
              </div>

              <!-- 評論列表 -->
              <div class="comments-list">
                <template v-if="comments && comments.length > 0">
                  <div v-for="comment in comments" :key="comment.comm_id" class="comment-item">
                    <div class="comment-header">
                      <div class="comment-user">
                        <a-avatar class="avatar" size="small" @click="goToUserProfile(comment.uid)">
                          {{ comment.una.charAt(0) }}
                        </a-avatar>
                        <span class="comment-author">{{ comment.una }}</span>
                      </div>
                      <span class="comment-time">{{ formatDate(comment.crea_date) }}</span>
                    </div>
                    <div class="comment-content">
                      {{ comment.content }}
                    </div>
                  </div>
                </template>
                <a-empty v-else description="暫無評論" />
              </div>
            </a-card>
          </template>
          <a-empty v-else description="貼文不存在或已被刪除" />
        </a-spin>
      </a-layout-content>
      <a-layout-footer style="text-align: center">
        識真網 ©2024 Created by Ant UED
      </a-layout-footer>
    </a-layout>
  </a-layout>
</template>

<script lang="ts" setup>
import { useAuthStore } from '../stores/auth';
import { onMounted, computed, ref, reactive } from 'vue';
import { ErrorTypes, useRoute, useRouter } from 'vue-router';
import Sidebar from '../layout/sidebar.vue';
import Header from '../layout/header.vue';
import axios from 'axios';
import { message, notification } from 'ant-design-vue';
const value = ref<number>(2);
// 側邊欄狀態管理
const collapsed = ref<boolean>(false);
const broken = ref<boolean>(false);
const loading = ref<boolean>(true);
const submitting = ref<boolean>(false);

// 評論表單
const commentForm = reactive({
  content: '',
  title: ''
});

// 動態計算佈局邊距
const layoutMargin = computed<string>(() => {
  return collapsed.value ? '0px' : broken.value ? '200px' : '200px';
});

// 處理側邊欄收合事件
const onCollapse = (isCollapsed: boolean, type: string) => {
  console.log(`Sidebar collapsed: ${isCollapsed}, Type: ${type}`);
};

// 使用 Pinia Store 和 Vue Router
const postStore = useAuthStore();
const route = useRoute();
const router = useRouter();
// 日期格式化函數
const formatDate = (date: string): string => {
  return new Date(date).toLocaleString('zh-TW', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
};

// 加載貼文數據
const loadPostData = async (postId: string) => {
  loading.value = true;
  try {
    await Promise.all([
      postStore.getPostInfo(postId),
      postStore.getAllComments(postId)
    ]);
  } catch (error) {
    message.error('載入貼文失敗');
    console.error('Error loading post data:', error);
  } finally {
    loading.value = false;
  }
};
const goToUserProfile = (id) => {
  router.push({ name: 'userprofile', params: { id: id } });
};
// 處理評論提交
const handleCommentSubmit = async () => {
  if (!postStore.userState.isAuthenticated) {
    message.warning('請先登入後再發表評論');
    return;
  }

  submitting.value = true;
  try {
    const response = await axios.post('http://localhost:8000/api/post/comment/create', {
      uid: postStore.userState.user?.uid,
      una: postStore.userState.user?.una,
      pid: route.params.id,
      title: commentForm.title,
      content: commentForm.content
    });

    if (response.status === 201) {
      message.success('評論發表成功');
      commentForm.content = ''; // 清空評論框
      await postStore.getAllComments(route.params.id as string); // 重新加載評論
    }
  } catch (error: any) {
    message.error(error.response?.data?.error || '評論發表失敗');
  } finally {
    submitting.value = false;
  }
};

// 計算屬性用來訪問 store 中的貼文和留言數據
const post = computed(() => postStore.postState.post);
const comments = computed(() => postStore.postState.comments);

// 當組件掛載時，根據路由參數查詢貼文資訊
onMounted(async () => {
  const postId = route.params.id as string;
  if (postId) {
    await loadPostData(postId);
  }
});
</script>

<style scoped>
.post-card {
  margin-bottom: 24px;
}

.comment-card {
  margin-bottom: 24px;
}

.post-header {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.post-title {
  color: #1890ff;
  margin: 0;
  font-size: 24px;
}

.post-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #666;
}

.author-name {
  font-size: 14px;
  margin-left: 8px;
}

.post-time {
  font-size: 14px;
  color: #999;
}

.post-content {
  font-size: 16px;
  line-height: 1.8;
  margin-top: 24px;
}

.comment-form {
  margin-bottom: 24px;
  border-bottom: 1px solid #f0f0f0;
  padding-bottom: 24px;
}

.comments-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.comment-item {
  border-bottom: 1px solid #f0f0f0;
  padding-bottom: 16px;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.comment-user {
  display: flex;
  align-items: center;
  gap: 8px;
}

.comment-author {
  font-size: 14px;
  font-weight: 500;
}

.comment-time {
  font-size: 12px;
  color: #999;
}

.comment-content {
  font-size: 14px;
  line-height: 1.6;
  color: #666;
  margin-left: 32px;
}

.avatar {
  cursor: pointer;
  /* 指定指標為手形 */
}

.avatar:hover {
  transform: scale(1.02);}

/*以下全都是收藏按鈕的css*/
/* From Uiverse.io by Galahhad */ 
.ui-bookmark {
  --icon-size: 24px;
  --icon-secondary-color: rgb(77, 77, 77);
  --icon-hover-color: rgb(97, 97, 97);
  --icon-primary-color: gold;
  --icon-circle-border: 1px solid var(--icon-primary-color);
  --icon-circle-size: 35px;
  --icon-anmt-duration: 0.3s;
}

.ui-bookmark input {
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
  display: none;
}

.ui-bookmark .bookmark {
  width: var(--icon-size);
  height: auto;
  fill: var(--icon-secondary-color);
  cursor: pointer;
  -webkit-transition: 0.2s;
  -o-transition: 0.2s;
  transition: 0.2s;
  display: -webkit-box;
  display: -ms-flexbox;
  display: flex;
  -webkit-box-pack: center;
  -ms-flex-pack: center;
  justify-content: center;
  -webkit-box-align: center;
  -ms-flex-align: center;
  align-items: center;
  position: relative;
  -webkit-transform-origin: top;
  -ms-transform-origin: top;
  transform-origin: top;
}

.bookmark::after {
  content: "";
  position: absolute;
  width: 10px;
  height: 10px;
  -webkit-box-shadow: 0 30px 0 -4px var(--icon-primary-color),
    30px 0 0 -4px var(--icon-primary-color),
    0 -30px 0 -4px var(--icon-primary-color),
    -30px 0 0 -4px var(--icon-primary-color),
    -22px 22px 0 -4px var(--icon-primary-color),
    -22px -22px 0 -4px var(--icon-primary-color),
    22px -22px 0 -4px var(--icon-primary-color),
    22px 22px 0 -4px var(--icon-primary-color);
  box-shadow: 0 30px 0 -4px var(--icon-primary-color),
    30px 0 0 -4px var(--icon-primary-color),
    0 -30px 0 -4px var(--icon-primary-color),
    -30px 0 0 -4px var(--icon-primary-color),
    -22px 22px 0 -4px var(--icon-primary-color),
    -22px -22px 0 -4px var(--icon-primary-color),
    22px -22px 0 -4px var(--icon-primary-color),
    22px 22px 0 -4px var(--icon-primary-color);
  border-radius: 50%;
  -webkit-transform: scale(0);
  -ms-transform: scale(0);
  transform: scale(0);
}

.bookmark::before {
  content: "";
  position: absolute;
  border-radius: 50%;
  border: var(--icon-circle-border);
  opacity: 0;
}

/* actions */

.ui-bookmark:hover .bookmark {
  fill: var(--icon-hover-color);
}

.ui-bookmark input:checked + .bookmark::after {
  -webkit-animation: circles var(--icon-anmt-duration)
    cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
  animation: circles var(--icon-anmt-duration)
    cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
  -webkit-animation-delay: var(--icon-anmt-duration);
  animation-delay: var(--icon-anmt-duration);
}

.ui-bookmark input:checked + .bookmark {
  fill: var(--icon-primary-color);
  -webkit-animation: bookmark var(--icon-anmt-duration) forwards;
  animation: bookmark var(--icon-anmt-duration) forwards;
  -webkit-transition-delay: 0.3s;
  -o-transition-delay: 0.3s;
  transition-delay: 0.3s;
}

.ui-bookmark input:checked + .bookmark::before {
  -webkit-animation: circle var(--icon-anmt-duration)
    cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
  animation: circle var(--icon-anmt-duration)
    cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
  -webkit-animation-delay: var(--icon-anmt-duration);
  animation-delay: var(--icon-anmt-duration);
}

@-webkit-keyframes bookmark {
  50% {
    -webkit-transform: scaleY(0.6);
    transform: scaleY(0.6);
  }

  100% {
    -webkit-transform: scaleY(1);
    transform: scaleY(1);
  }
}

@keyframes bookmark {
  50% {
    -webkit-transform: scaleY(0.6);
    transform: scaleY(0.6);
  }

  100% {
    -webkit-transform: scaleY(1);
    transform: scaleY(1);
  }
}

@-webkit-keyframes circle {
  from {
    width: 0;
    height: 0;
    opacity: 0;
  }

  90% {
    width: var(--icon-circle-size);
    height: var(--icon-circle-size);
    opacity: 1;
  }

  to {
    opacity: 0;
  }
}

@keyframes circle {
  from {
    width: 0;
    height: 0;
    opacity: 0;
  }

  90% {
    width: var(--icon-circle-size);
    height: var(--icon-circle-size);
    opacity: 1;
  }

  to {
    opacity: 0;
  }
}

@-webkit-keyframes circles {
  from {
    -webkit-transform: scale(0);
    transform: scale(0);
  }

  40% {
    opacity: 1;
  }

  to {
    -webkit-transform: scale(0.8);
    transform: scale(0.8);
    opacity: 0;
  }
}

@keyframes circles {
  from {
    -webkit-transform: scale(0);
    transform: scale(0);
  }

  40% {
    opacity: 1;
  }

  to {
    -webkit-transform: scale(0.8);
    transform: scale(0.8);
    opacity: 0;
  }
}
</style>