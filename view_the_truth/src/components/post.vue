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
                  <div class="post-main-info">
                    <h2 class="post-title">{{ post.title }}</h2>
                    <div class="post-meta">
                      <a-avatar class="avatar" size="small" @click="goToUserProfile(post.uid)">
                        {{ post.una.charAt(0) }}
                      </a-avatar>
                      <span class="author-name">{{ post.una }}</span>
                      <span class="divider">·</span>
                      <span class="post-time">{{ formatDate(post.crea_date) }}</span>
                    </div>
                  </div>
                  <div class="post-actions">
                    <div class="action-group">
                      <span class="action-label">評分</span>
                      <a-rate v-model:value="rate_sc" @click="Rate_sc_btn" />
                    </div>
                    <div class="action-buttons">
                      <a-button 
                        type="text"
                        class="action-btn"
                        :class="{ 'favorite-active': isFavorited }"
                        @click="toggleFavorite"
                      >
                        <HeartOutlined />
                        <span>{{ isFavorited ? '已收藏' : '收藏' }}</span>
                      </a-button>
                      <a-button 
                        v-if="canEdit"
                        type="text"
                        class="action-btn"
                        @click="showEditModal"
                      >
                        <FormOutlined />
                        <span>編輯</span>
                      </a-button>
                    </div>
                  </div>
                </div>
              </template>
              <div class="post-content" v-html="sanitizedContent"></div>
            </a-card>

            <!-- 編輯貼文的彈窗 -->
            <a-modal v-model:visible="editModalVisible" title="編輯貼文" @ok="handleEditSubmit"
              :confirmLoading="editSubmitting" @cancel="handleEditCancel" width="800px">
              <a-form :model="editForm" layout="vertical">
                <a-form-item label="標題" name="title" :rules="[{ required: true, message: '請輸入標題' }]">
                  <a-input v-model:value="editForm.title" />
                </a-form-item>
                <a-form-item label="內容" name="content" :rules="[{ required: true, message: '請輸入內容' }]">
                  <Editor v-model="editForm.content" :init="editorConfig"
                    api-key="ci5pu95qkbehxg0n46696e18lgou1726k31jwvfad8hgz6f2" @onClick="handleEditorClick" />
                </a-form-item>
              </a-form>
            </a-modal>

            <!-- 評論區塊 -->
            <a-card class="comment-card" :bordered="false" title="評論">
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
                      <h4>{{ comment.title }}</h4>
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
import { onMounted, computed, ref, reactive, nextTick } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import Sidebar from '../layout/sidebar.vue';
import Header from '../layout/header.vue';
import axios from 'axios';
import { message, Modal } from 'ant-design-vue';
import { FormOutlined, HeartOutlined } from '@ant-design/icons-vue';
import DOMPurify from 'dompurify';
import Editor from '@tinymce/tinymce-vue';


const collapsed = ref<boolean>(false);
const broken = ref<boolean>(false);
const loading = ref<boolean>(true);
const submitting = ref<boolean>(false);

// 評論表單
const commentForm = reactive({
  content: '',
  title: ''
});

// 編輯相關
const editModalVisible = ref<boolean>(false);
const editSubmitting = ref<boolean>(false);
const editForm = reactive({
  title: '',
  content: ''
});

// TinyMCE 编辑器配置 
const editorConfig = {
  height: 500,
  menubar: true,
  plugins: [
    'advlist', 'autolink', 'lists', 'link', 'image', 'charmap',
    'preview', 'anchor', 'searchreplace', 'visualblocks', 'code',
    'fullscreen', 'insertdatetime', 'media', 'table', 'paste',
    'code', 'help', 'wordcount'
  ],
  toolbar: 'undo redo | formatselect | ' +
    'bold italic backcolor | alignleft aligncenter ' +
    'alignright alignjustify | bullist numlist outdent indent | ' +
    'removeformat | help',
  content_style: `
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif; font-size: 14px; }
    img { max-width: 100%; height: auto; }
  `,
  language: 'zh_TW',
  branding: false,
  elementpath: false,
  convert_urls: false,
  relative_urls: false,
  paste_data_images: true,
  automatic_uploads: true,
  images_reuse_filename: true,
 // 限制图片类型
  images_file_types: 'jpeg,jpg,png,gif,webp',
 // 添加文件选择器按钮
  file_picker_types: 'image',
  images_upload_handler: async (blobInfo: any, progress: any) => {
    try {
        const formData = new FormData();
        formData.append('file', blobInfo.blob(), blobInfo.filename());

        const response = await axios.post('http://localhost:8000/api/upload', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
            onUploadProgress: (e) => {
                if (e.total) {
                    progress(e.loaded / e.total * 100);
                }
            }
        });

        return response.data.url; // 確保後端返回的 URL 是字符串
    } catch (error) {
        console.error('Image upload failed:', error);
        throw new Error('圖片上傳失敗');
    }
},
  setup: (editor: any) => {
    editor.on('init', () => {
      editor.setContent(editForm.content);
    });
    editor.on('input', () => {
      editForm.content = editor.getContent();
    });
  }
};
const layoutMargin = computed(() => {
  return collapsed.value ? '0px' : broken.value ? '200px' : '200px';
});

const postStore = useAuthStore();
const route = useRoute();
const router = useRouter();

const formatDate = (date: string): string => {
  return new Date(date).toLocaleString('zh-TW', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
};

const canEdit = computed(() => {
  return postStore.userState.isAuthenticated &&
    postStore.userState.user?.uid === post.value?.uid;
});

const post = computed(() => postStore.postState.post);
const comments = computed(() => postStore.postState.comments);

const sanitizedContent = computed(() => {
  if (!post.value?.content) return '';
  const cleanContent = DOMPurify.sanitize(post.value.content, {
    ALLOWED_TAGS: [
      'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
      'ul', 'ol', 'li', 'a', 'img', 'table', 'tr', 'td', 'th', 'thead', 'tbody',
      'div', 'span', 'pre', 'code', 'blockquote', 'iframe'
    ],
    ALLOWED_ATTR: [
      'href', 'target', 'src', 'alt', 'class', 'style', 'width', 'height', 
      'frameborder', 'allow', 'allowfullscreen'
    ]
  });

  // 限制 iframe 的來源
  const parser = new DOMParser();
  const doc = parser.parseFromString(cleanContent, 'text/html');
  const iframes = doc.querySelectorAll('iframe');
  iframes.forEach((iframe) => {
    const src = iframe.getAttribute('src');
    if (!src || !src.startsWith('https://www.youtube.com/embed/')) {
      iframe.remove(); // 移除不符合條件的 iframe
    }
  });

  return doc.body.innerHTML;
});

const onCollapse = (isCollapsed: boolean, type: string) => {
  collapsed.value = isCollapsed;
};

const handleEditorClick = (e: any) => {
  console.log('Editor clicked:', e);
};

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

const goToUserProfile = (id: string) => {
  router.push({ name: 'userprofile', params: { id } });
};

const showEditModal = () => {
  if (!canEdit.value) {
    message.warning('您沒有權限編輯此貼文');
    return;
  }

  nextTick(() => {
    if (post.value) {
      editForm.title = post.value.title;
      editForm.content = post.value.content || '';
    }
    editModalVisible.value = true;
  });
};

const handleEditCancel = () => {
  editModalVisible.value = false;
  editForm.title = '';
  editForm.content = '';
};

const handleEditSubmit = async () => {
  if (!editForm.title.trim() || !editForm.content.trim()) {
    message.error('標題和內容不能為空');
    return;
  }

  editSubmitting.value = true;
  try {
    const sanitizedContent = DOMPurify.sanitize(editForm.content, {
      ALLOWED_TAGS: [
        'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'ul', 'ol', 'li', 'a', 'img', 'table', 'tr', 'td', 'th', 'thead', 'tbody',
        'div', 'span', 'pre', 'code', 'blockquote', 'iframe' // 確保允許 iframe
      ],
      ALLOWED_ATTR: [
        'href', 'target', 'src', 'alt', 'class', 'style', 'width', 'height', 
        'frameborder', 'allow', 'allowfullscreen' // 確保允許 iframe 的屬性
      ]
    });

    const response = await axios.put(`http://localhost:8000/api/post/update/${route.params.id}`, {
      title: editForm.title,
      content: sanitizedContent,
    });

    if (response.status === 200) {
      message.success('貼文更新成功');
      editModalVisible.value = false;
      await loadPostData(route.params.id as string);
    }
  } catch (error: any) {
    message.error(error.response?.data?.error || '更新貼文失敗');
  } finally {
    editSubmitting.value = false;
  }
};

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
      commentForm.title = '';
      commentForm.content = '';
      await postStore.getAllComments(route.params.id as string);
    }
  } catch (error: any) {
    message.error(error.response?.data?.error || '評論發表失敗');
  } finally {
    submitting.value = false;
  }
};
const rate_sc = ref<number>();
//評分
const Rate_sc_btn = async () => {
  if (!postStore.userState.isAuthenticated) {
    message.warning('請先登入後再評分');
    return;
  }

  // 從後端檢查當前評分
  const currentScore = await postStore.checkScore(route.params.id as string, postStore.userState.user?.uid as string);

  // 如果選擇的評分為零分，或者與當前評分相同，則不執行任何操作
  if (rate_sc.value === 0 || rate_sc.value === currentScore) {
    message.info('您已經選擇了相同的評分');
    rate_sc.value = currentScore; // 恢復為當前評分
    return;
  }

  // 彈出確認框
  Modal.confirm({
    title: '確認評分',
    content: `確定要將評分設為 ${rate_sc.value} 嗎？`,
    okText: '確定',
    cancelText: '取消',
    onOk: async () => {
      try {
        // 發送評分請求
        await axios.post('http://localhost:8000/api/score/add', {
          uid: postStore.userState.user?.uid,
          pid: route.params.id,
          score: rate_sc.value,
        });
        message.success('評分成功');
      } catch (error: any) {
        message.error(error.response?.data?.error || '評分失敗');
      }
    },
    onCancel: () => {
      // 如果取消，將評分值恢復為當前評分
      rate_sc.value = currentScore;
    },
  });
};
//收藏
const isFavorited = ref<boolean>(false);

const toggleFavorite = async () => {
  if (!postStore.userState.isAuthenticated) {
    message.warning('請先登入後再收藏');
    return;
  }

  try {
    if (!isFavorited.value) {  // 未收藏狀態，執行新增收藏
      await axios.post('http://localhost:8000/api/favorites/add', {
        uid: postStore.userState.user?.uid,
        pid: route.params.id,
      });
      isFavorited.value = true;  // 更新狀態為已收藏
      message.success('已收藏');
    } else {  // 已收藏狀態，執行取消收藏
      await axios.delete('http://localhost:8000/api/favorites/remove', {
        data: {
          uid: postStore.userState.user?.uid,
          pid: route.params.id,
        },
      });
      isFavorited.value = false;  // 更新狀態為未收藏
      message.success('已取消收藏');
    }
  } catch (error: any) {
    message.error(error.response?.data?.error || '操作失敗');
    // 保持狀態不變，因為操作失敗
  }
};
onMounted(async () => {
  const postId = route.params.id as string;
  const uid = postStore.userState.user?.uid as string;
  if (postId) {
    await loadPostData(postId);
  }
  // 檢查收藏狀態
  if (postStore.userState.isAuthenticated) {
    const checkFavorite = await postStore.checkFavorite(postId, uid);
    isFavorited.value = checkFavorite;
  }
  //檢查評分
  if (postStore.userState.isAuthenticated) {
    const checkScore = await postStore.checkScore(postId, uid);
    rate_sc.value = checkScore;
  }

});
</script>

<style scoped>
.post-card {
  margin-bottom: 24px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.post-header {
  padding: 16px 0;
  border-bottom: 1px solid #f0f0f0;
}

.post-main-info {
  margin-bottom: 16px;
}

.post-title {
  font-size: 28px;
  font-weight: 600;
  color: #262626;
  margin-bottom: 12px;
  line-height: 1.4;
}

.post-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #595959;
}

.author-name {
  font-size: 15px;
  font-weight: 500;
}

.divider {
  color: #d9d9d9;
}

.post-time {
  color: #8c8c8c;
}

.post-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.action-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.action-label {
  font-size: 14px;
  color: #595959;
}

:deep(.ant-rate) {
  font-size: 20px;
}

.action-buttons {
  display: flex;
  gap: 16px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  padding: 4px 12px;
  border-radius: 4px;
  transition: all 0.3s;
}

.action-btn:hover {
  background: #f5f5f5;
}

.favorite-active {
  color: #ff4d4f;
}

.favorite-active:hover {
  background: #fff1f0;
}

.avatar {
  cursor: pointer;
  transition: transform 0.2s;
}

.avatar:hover {
  transform: scale(1.05);
}

.comment-card {
  margin-bottom: 24px;
}

.post-content {
  font-size: 16px;
  line-height: 1.8;
  margin-top: 24px;
  word-wrap: break-word;
  word-break: break-word;
  white-space: normal;
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
}

.avatar:hover {
  transform: scale(1.02);
}

.favorite-icon-active {
  color: #ff4d4f;
  cursor: pointer;
  transition: color 0.3s ease, transform 0.3s ease;
  /* 添加平滑過渡效果 */
}

.favorite-icon-active:hover {
  color: #ff7875;
  transform: scale(1.1);
  /* 放大效果 */
}

.edit-icon {
  cursor: pointer;
  color: #1890ff;
  margin-left: 8px;
  transition: color 0.3s ease, transform 0.3s ease;
  /* 添加平滑過渡效果 */
}

.edit-icon:hover {
  color: #40a9ff;
  /* 改變顏色 */
  transform: scale(1.1);
  /* 放大效果 */
}
</style>