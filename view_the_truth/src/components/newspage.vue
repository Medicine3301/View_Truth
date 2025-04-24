<template>
    <a-layout>
      <Sidebar v-model:collapsed="collapsed" :onCollapse="onCollapse" />
      <a-layout :style="{ marginLeft: layoutMargin }">
        <Header />
        <a-layout-content :style="{ background: '#ececec', margin: '24px 16px 0' }">
          <a-spin :spinning="loading">
            <!-- 貼文內容卡片 -->
            <template v-if="news">
              <a-card class="post-card" :bordered="false">
                <template #title>
                  <div class="post-header">
                    <h2 class="post-title">{{ news.newstitle}}</h2>
                    <div class="post-meta">
                      <span class="post-time">{{formatDate(news.crea_date)}}</span>
                      <!--評分模組-->
                      <a-rate v-model:value="value" />
                      
                    </div>
                  </div>
                </template>
                <div class="post-content">
                    <a :href="news.journ" target="_blank">新聞連結</a>
                    <p>{{news.news_content}}</p>
                    <p>{{news.suggest}}</p>
                    <p>分數:{{news.score}}</p>
                </div>
              </a-card>
  
              <!-- 評論區塊 -->
              <a-card class="comment-card" :bordered="false" title="評論">
                <!-- 發表評論 -->
                <div class="comment-form">
                  <a-form :model="commentForm" @finish="handleCommentSubmit">
                    <a-form-item name="content" :rules="[{ required: true, message: '請輸入評論內容' }]">
                      <a-textarea 
                        v-model:value="commentForm.content" 
                        :rows="4" 
                        :placeholder="replyTo ? `回覆 ${replyTo.una}...` : '寫下你的評論...'"
                        :disabled="!newsStore.userState.isAuthenticated" 
                      />
                    </a-form-item>
                    <a-form-item>
                      <div class="comment-form-actions">
                        <a-button 
                          type="primary" 
                          html-type="submit" 
                          :loading="submitting"
                          :disabled="!newsStore.userState.isAuthenticated"
                        >
                          {{ replyTo ? '回覆' : '發表評論' }}
                        </a-button>
                        <a-button 
                          v-if="replyTo" 
                          @click="cancelReply"
                        >
                          取消回覆
                        </a-button>
                      </div>
                    </a-form-item>
                  </a-form>
                </div>
  
                <!-- 巢狀評論列表 -->
                <div class="comments-list">
                  <template v-if="comments && comments.length > 0">
                    <a-comment v-for="comment in comments" :key="comment.comm_id">
                      <template #actions>
                        <span @click="handleReplyClick(comment)">回覆</span>
                      </template>
                      <template #author>{{ comment.una }}</template>
                      <template #avatar>
                        <a-avatar @click="goToUserProfile(comment.uid)">{{ comment.una.charAt(0) }}</a-avatar>
                      </template>
                      <template #content>
                        <p>{{ comment.content }}</p>
                      </template>
                      <template #datetime>
                        <span>{{ formatDate(comment.crea_date) }}</span>
                      </template>
                
                      <!-- 回覆表單 -->
                      <div v-if="activeReplyId === comment.comm_id" class="reply-form">
                        <a-textarea
                          v-model:value="replyContent"
                          :rows="3"
                          :placeholder="`回覆 ${comment.una}...`"
                        />
                        <div class="reply-actions">
                          <a-button type="primary" size="small" @click="submitReply(comment)">發送</a-button>
                          <a-button size="small" @click="cancelReply">取消</a-button>
                        </div>
                      </div>
                
                      <!-- 巢狀回覆 -->
                      <template v-if="comment.children && comment.children.length > 0">
                        <a-comment
                          v-for="reply in comment.children"
                          :key="reply.comm_id"
                          class="nested-comment"
                        >
                          <template #author>{{ reply.una }}</template>
                          <template #avatar>
                            <a-avatar @click="goToUserProfile(reply.uid)">{{ reply.una.charAt(0) }}</a-avatar>
                          </template>
                          <template #content>
                            <p>{{ reply.content }}</p>
                          </template>
                          <template #datetime>
                            <span>{{ formatDate(reply.crea_date) }}</span>
                          </template>
                        </a-comment>
                      </template>
                    </a-comment>
                  </template>
                  <a-empty v-else description="暫無評論" />
                </div>
              </a-card>
            </template>
            <a-empty v-else description="新聞不存在或已被刪除" />
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
  import { onMounted, computed, ref, reactive, defineComponent, PropType, createApp } from 'vue';
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
    content: ''
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
  const newsStore = useAuthStore();
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
  const loadnewsData = async (newsId: string) => {
    loading.value = true;
    try {
      await Promise.all([
        newsStore.getnewsInfo(newsId),
        newsStore.getNewsAllComments(newsId)
      ]);
    } catch (error) {
      message.error('載入新聞失敗');
      console.error('Error loading news data:', error);
    } finally {
      loading.value = false;
    }
  };
  const goToUserProfile = (id) => {
    router.push({ name: 'userprofile', params: { id: id } });
  };
  // 新增回覆相關的狀態
  const replyTo = ref<any>(null);

  // 處理回覆
  const handleReply = (comment: any) => {
    replyTo.value = comment;
  };

  // 取消回覆
  // Removed duplicate declaration of cancelReply

  // 處理評論提交
  const handleCommentSubmit = async () => {
    if (!newsStore.userState.isAuthenticated) {
      message.warning('請先登入後再發表評論');
      return;
    }
  
    submitting.value = true;
    try {
      const response = await axios.post('http://localhost:8000/api/news/comment/create', {
        uid: newsStore.userState.user?.uid,
        una: newsStore.userState.user?.una,
        nid: route.params.id,
        content: commentForm.content,
        parent_id: replyTo.value?.comm_id || null
      });
  
      if (response.status === 201) {
        message.success(replyTo.value ? '回覆成功' : '評論發表成功');
        commentForm.content = '';
        replyTo.value = null;
        await newsStore.getNewsAllComments(route.params.id as string);
      }
    } catch (error: any) {
      message.error(error.response?.data?.error || '評論發表失敗');
    } finally {
      submitting.value = false;
    }
  };
  
  // 計算屬性用來訪問 store 中的貼文和留言數據
  const news = computed(() => newsStore.newstate.news);
  const comments = computed(() => newsStore.newstate.comments);
  
  // 當組件掛載時，根據路由參數查詢新聞資訊
  onMounted(async () => {
    const newsId = route.params.id as string;
    if (newsId) {
      await loadnewsData(newsId);
    }
  });

  // 添加新的評論樹組件
  const CommentTree = defineComponent({
    name: 'CommentTree',
    props: {
      comments: {
        type: Array as PropType<any[]>,
        required: true
      },
      level: {
        type: Number,
        default: 0
      }
    },
    template: `
      <div class="comments-tree">
        <div v-for="comment in comments" :key="comment.comm_id" :class="['comment-item', 'level-' + level]">
          <div class="comment-main">
            <div class="comment-header">
              <div class="comment-user">
                <a-avatar class="avatar" size="small" @click="$emit('userClick', comment.uid)">
                  {{ comment.una.charAt(0) }}
                </a-avatar>
                <span class="comment-author">{{ comment.una }}</span>
              </div>
              <span class="comment-time">{{ formatDate(comment.crea_date) }}</span>
            </div>
            <div class="comment-content">{{ comment.content }}</div>
            <div class="comment-actions">
              <a-button type="text" size="small" @click="showReplyForm[comment.comm_id] = !showReplyForm[comment.comm_id]">
                {{ showReplyForm[comment.comm_id] ? '取消回覆' : '回覆' }}
              </a-button>
            </div>
  
            <div v-if="showReplyForm[comment.comm_id]" class="reply-form">
              <a-textarea
                v-model="replyContent[comment.comm_id]"
                :rows="3"
                :placeholder="'回覆 ' + comment.una + '...'"
              />
              <div class="reply-form-actions">
                <a-button
                  type="primary"
                  size="small"
                  :loading="submitting[comment.comm_id]"
                  @click="submitReply(comment)"
                >
                  發送
                </a-button>
              </div>
            </div>
          </div>
          
          <div v-if="comment.children && comment.children.length > 0" class="nested-comments">
            <comment-tree
              :comments="comment.children"
              :level="Math.min(level + 1, 5)"
              @reply="$emit('reply', $event)"
              @userClick="$emit('userClick', $event)"
            />
          </div>
        </div>
      </div>
    `,
    emits: ['reply', 'userClick'],
    setup(props, { emit }) {
      const showReplyForm = ref<{ [key: string]: boolean }>({});
      const replyContent = ref<{ [key: string]: string }>({});
      const submitting = ref<{ [key: string]: boolean }>({});
  
      const toggleReplyForm = (commentId: string) => {
        showReplyForm.value[commentId] = !showReplyForm.value[commentId];
      };
  
      const submitReply = async (comment: any) => {
        if (!newsStore.userState.isAuthenticated) {
          message.warning('請先登入後再發表評論');
          return;
        }
  
        submitting.value[comment.comm_id] = true;
        try {
          await axios.post('http://localhost:8000/api/news/comment/create', {
            uid: newsStore.userState.user?.uid,
            una: newsStore.userState.user?.una,
            nid: route.params.id,
            content: replyContent.value[comment.comm_id],
            parent_id: comment.comm_id
          });
  
          message.success('回覆成功');
          replyContent.value[comment.comm_id] = '';
          showReplyForm.value[comment.comm_id] = false;
          await newsStore.getNewsAllComments(route.params.id as string);
        } catch (error: any) {
          message.error(error.response?.data?.error || '回覆發表失敗');
        } finally {
          submitting.value[comment.comm_id] = false;
        }
      };
  
      return {
        showReplyForm,
        replyContent,
        submitting,
        toggleReplyForm,
        submitReply,
        formatDate // 使用外部的 formatDate 函數
      };
    }
  });

  const activeReplyId = ref(null);
  const replyContent = ref('');

  const handleReplyClick = (comment) => {
    activeReplyId.value = comment.comm_id;
    replyContent.value = '';
  };

  const cancelReply = () => {
    activeReplyId.value = null;
    replyContent.value = '';
  };

  const submitReply = async (comment) => {
    if (!newsStore.userState.isAuthenticated) {
      message.warning('請先登入後再發表評論');
      return;
    }
  
    try {
      await axios.post('http://localhost:8000/api/news/comment/create', {
        uid: newsStore.userState.user?.uid,
        una: newsStore.userState.user?.una,
        nid: route.params.id,
        content: replyContent.value,
        parent_id: comment.comm_id
      });
  
      message.success('回覆發表成功');
      replyContent.value = '';
      activeReplyId.value = null;
      await newsStore.getNewsAllComments(route.params.id as string);
    } catch (error) {
      message.error('回覆發表失敗');
    }
  };
  
  // 註冊組件
  const app = createApp({});
  app.component('comment-tree', CommentTree);
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
    word-wrap: break-word; /* 让长单词或连续字符自动换行 */
    word-break: break-word; /* 强制换行，适用于多种语言 */
    white-space: normal; /* 确保文字正常换行，而不是保留空格或强制单行显示 */
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
    margin-bottom: 16px;
  }
  
  .comment-item .comment-item {
    margin-left: 48px;
    margin-top: 16px;
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
  
  .comment-form-actions {
    display: flex;
    gap: 8px;
  }

  .comment-container {
    width: 100%;
    margin-bottom: 16px;
  }
  
  .comment-main {
    padding: 12px;
    background: #fafafa;
    border-radius: 4px;
  }
  
  .reply-list {
    margin-left: 48px;
    margin-top: 8px;
  }
  
  .reply-item {
    margin-top: 8px;
    border-left: 2px solid #f0f0f0;
    padding-left: 16px;
  }

  .comments-tree {
    margin-left: 0;
  }
  
  .level-0 {
    margin-left: 0;
  }
  
  .level-1 {
    margin-left: 40px;
  }
  
  .level-2 {
    margin-left: 80px;
  }
  
  .level-3 {
    margin-left: 120px;
  }
  
  /* 更多層級可以繼續添加 */
  .level-4 {
    margin-left: 160px;
  }
  
  .reply-form {
    margin: 12px 0;
    padding: 12px;
    background: #f9f9f9;
    border-radius: 4px;
  }
  
  .reply-form-actions {
    margin-top: 8px;
    display: flex;
    gap: 8px;
    justify-content: flex-end;
  }
  
  .nested-comments {
    margin-top: 12px;
  }

  .nested-comments {
    margin-left: 24px;
    border-left: 2px solid #f0f0f0;
    padding-left: 16px;
  }
  
  .reply-form {
    margin: 12px 0;
    padding: 12px;
    background: #f9f9f9;
    border-radius: 4px;
    border: 1px solid #e8e8e8;
  }
  
  .comment-item {
    margin-bottom: 16px;
    padding-bottom: 16px;
  }
  
  .level-0 { margin-left: 0; }
  .level-1 { margin-left: 24px; }
  .level-2 { margin-left: 48px; }
  .level-3 { margin-left: 72px; }
  .level-4 { margin-left: 96px; }
  .level-5 { margin-left: 120px; }

  .nested-comment {
    margin-left: 44px !important;
    border-left: 2px solid #f0f0f0;
    padding-left: 20px;
  }

  .reply-form {
    margin: 16px 0;
    padding: 16px;
    background: #fafafa;
    border-radius: 4px;
  }

  .reply-actions {
    margin-top: 8px;
    display: flex;
    gap: 8px;
  }
  </style>