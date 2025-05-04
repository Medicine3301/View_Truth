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
                    <h2 class="post-title">{{ news.title }}</h2>
                    <div class="post-meta">
                      <span class="post-time">{{ formatDate(news.publish_date) }}</span>
                      <span class="post-location">{{ news.location }}</span>
                      <span class="post-type">{{ news.event_type }}</span>
                    </div>
                  </div>
                </template>

                <!-- 新增：可信度評分和可靠性資訊區塊 -->
                <div class="credibility-overview">
                  <div class="credibility-banner" :class="getCredibilityLevelClass(news.credibility_level)">
                    <div class="credibility-main">
                      <div class="score-circle">
                        <span class="score-number">{{ news.credibility_score }}</span>
                        <span class="score-label">可信度</span>
                      </div>
                      <div class="credibility-details">
                        <h2 class="credibility-level">{{ news.credibility_level }}</h2>
                        <p class="credibility-explanation">{{ getCredibilityExplanation(news.credibility_level) }}</p>
                      </div>
                    </div>
                    <div class="reliability-summary">
                      <div class="reliability-badge">
                        <safety-outlined />
                        <span>來源可靠度：{{ news.source_analysis.reliability.level }}</span>
                      </div>
                      <p class="reliability-reason">{{ news.source_analysis.reliability.reason }}</p>
                    </div>
                  </div>
                </div>

                <!-- 新聞內容 -->
                <div class="post-content">
                  <div class="news-link-container">
                    <a :href="news.link" target="_blank" class="news-link">
                      <link-outlined class="link-icon" />
                      <span class="link-text">查看原始新聞報導</span>
                      <arrow-right-outlined class="arrow-icon" />
                    </a>
                  </div>
                  <p>{{ news.content }}</p>
                  
                  <!-- 分析結果顯示 -->
                  <div class="analysis-results">
                    <h3>
                      <a-space>
                        <a-icon type="bar-chart" />
                        新聞分析結果
                      </a-space>
                    </h3>

                    <!-- 分數概覽卡片 -->
                    <a-row :gutter="[16, 16]" class="score-cards">
                      <a-col :span="6">
                        <a-card hoverable>
                          <a-statistic
                            title="真實性評分"
                            :value="news.factual_score"
                            :precision="1"
                            :value-style="{ color: getScoreColor(news.factual_score) }"
                            suffix="/ 100"
                          >
                            <template #prefix>
                              <verification-outlined />
                            </template>
                          </a-statistic>
                        </a-card>
                      </a-col>
                      <a-col :span="6">
                        <a-card hoverable>
                          <a-statistic
                            title="批判性評分"
                            :value="news.critical_score"
                            :precision="1"
                            :value-style="{ color: getScoreColor(news.critical_score) }"
                            suffix="/ 100"
                          >
                            <template #prefix>
                              <eye-outlined />
                            </template>
                          </a-statistic>
                        </a-card>
                      </a-col>
                      <a-col :span="6">
                        <a-card hoverable>
                          <a-statistic
                            title="平衡性評分"
                            :value="news.balanced_score"
                            :precision="1"
                            :value-style="{ color: getScoreColor(news.balanced_score) }"
                            suffix="/ 100"
                          >
                            <template #prefix>
                              <balance-outlined />
                            </template>
                          </a-statistic>
                        </a-card>
                      </a-col>
                      <a-col :span="6">
                        <a-card hoverable>
                          <a-statistic
                            title="來源可靠度"
                            :value="news.source_score"
                            :precision="1"
                            :value-style="{ color: getScoreColor(news.source_score) }"
                            suffix="/ 100"
                          >
                            <template #prefix>
                              <safety-outlined />
                            </template>
                          </a-statistic>
                        </a-card>
                      </a-col>
                    </a-row>

                   
                    <!-- 詳細分析結果 -->
                    <a-collapse 
                      class="analysis-collapse"
                      :bordered="false"
                      expand-icon-position="right"
                    >
                      <a-collapse-panel key="1" header="事實檢核">
                        <div class="analysis-section">
                          <a-card class="finding-card">
                            <template #title>
                              <span class="section-title">
                                <check-circle-outlined />
                                發現的事實
                              </span>
                            </template>
                            <ul class="finding-list">
                              <li v-for="(finding, index) in news.factual_analysis.findings" :key="index" 
                                  class="finding-item">
                                <check-outlined class="list-icon" />
                                <span>{{ finding }}</span>
                              </li>
                            </ul>
                          </a-card>
                          
                          <a-card class="basis-card">
                            <template #title>
                              <span class="section-title">
                                <file-search-outlined />
                                分析依據
                              </span>
                            </template>
                            <ul class="basis-list">
                              <li v-for="(basis, index) in news.factual_analysis.basis" :key="index"
                                  class="basis-item">
                                <info-circle-outlined class="list-icon" />
                                <span>{{ basis }}</span>
                              </li>
                            </ul>
                          </a-card>
                        </div>
                      </a-collapse-panel>
                    
                      <a-collapse-panel key="2" header="批判性分析">
                        <div class="analysis-section">
                          <a-card class="problems-card">
                            <template #title>
                              <span class="section-title">
                                <warning-outlined />
                                主要問題
                              </span>
                            </template>
                            <ul class="problems-list">
                              <li v-for="(problem, index) in news.critical_analysis.problems" :key="index"
                                  class="problem-item">
                                <exclamation-circle-outlined class="list-icon warning" />
                                <span>{{ problem }}</span>
                              </li>
                            </ul>
                          </a-card>
                          
                          <a-card class="fallacies-card">
                            <template #title>
                              <span class="section-title">
                                <bug-outlined />
                                邏輯謬誤
                              </span>
                            </template>
                            <ul class="fallacies-list">
                              <li v-for="(fallacy, index) in news.critical_analysis.logical_fallacies" :key="index"
                                  class="fallacy-item">
                                <stop-outlined class="list-icon error" />
                                <span>{{ fallacy }}</span>
                              </li>
                            </ul>
                          </a-card>
                        </div>
                      </a-collapse-panel>
                    
                      <a-collapse-panel key="3" header="平衡性分析">
                        <div class="analysis-section">
                          <a-card class="supporting-card">
                            <template #title>
                              <span class="section-title">
                                <like-outlined />
                                支持觀點
                              </span>
                            </template>
                            <ul class="supporting-list">
                              <li v-for="(point, index) in news.balanced_analysis.supporting_points" :key="index"
                                  class="supporting-item">
                                <plus-circle-outlined class="list-icon support" />
                                <span>{{ point }}</span>
                              </li>
                            </ul>
                          </a-card>
                          
                          <a-card class="opposing-card">
                            <template #title>
                              <span class="section-title">
                                <dislike-outlined />
                                反對觀點
                              </span>
                            </template>
                            <ul class="opposing-list">
                              <li v-for="(point, index) in news.balanced_analysis.opposing_points" :key="index"
                                  class="opposing-item">
                                <minus-circle-outlined class="list-icon oppose" />
                                <span>{{ point }}</span>
                              </li>
                            </ul>
                          </a-card>
                        </div>
                      </a-collapse-panel>
                    
                      <a-collapse-panel key="4" header="來源分析">
                        <div class="analysis-section">
                          <a-card class="reliability-card">
                            <template #title>
                              <span class="section-title">
                                <safety-outlined />
                                可靠度分析
                              </span>
                            </template>
                            <div class="reliability-content">
                              <div class="reliability-level">
                                <trophy-outlined class="level-icon" />
                                <span class="level-text">{{ news.source_analysis.reliability.level }}</span>
                              </div>
                              <div class="reliability-reason">
                                <solution-outlined class="reason-icon" />
                                <p>{{ news.source_analysis.reliability.reason }}</p>
                              </div>
                            </div>
                          </a-card>
                      
                          <a-card class="content-type-card">
                            <template #title>
                              <span class="section-title">
                                <file-text-outlined />
                                內容類型
                              </span>
                            </template>
                            <p class="content-type-text">{{ news.source_analysis.reliability.content_type }}</p>
                          </a-card>
                      
                          <a-card class="quality-score-card">
                            <template #title>
                              <span class="section-title">
                                <bar-chart-outlined />
                                品質評分
                              </span>
                            </template>
                            <ul class="quality-score-list">
                              <li class="quality-score-item">
                                <check-circle-outlined class="score-icon completeness" />
                                <span>完整性：</span>
                                <a-progress :percent="news.source_analysis.reliability.quality_scores.completeness" size="small" />
                              </li>
                              <li class="quality-score-item">
                                <safety-outlined class="score-icon reliability" />
                                <span>來源可靠性：</span>
                                <a-progress :percent="news.source_analysis.reliability.quality_scores.source_reliability" size="small" />
                              </li>
                              <li class="quality-score-item">
                                <clock-circle-outlined class="score-icon timeliness" />
                                <span>時效性：</span>
                                <a-progress :percent="news.source_analysis.reliability.quality_scores.timeliness" size="small" />
                              </li>
                              <li class="quality-score-item">
                                <audit-outlined class="score-icon verifiability" />
                                <span>可驗證性：</span>
                                <a-progress :percent="news.source_analysis.reliability.quality_scores.verifiability" size="small" />
                              </li>
                            </ul>
                          </a-card>
                        </div>
                      </a-collapse-panel>
                    
                      <a-collapse-panel key="5" header="查證指南">
                        <div class="analysis-section">
                          <a-card class="verification-card">
                            <template #title>
                              <span class="section-title">
                                <bulb-outlined />
                                查證建議
                              </span>
                            </template>
                            <ul class="verification-list">
                              <li v-for="(suggestion, index) in news.verification_guide.suggestions" :key="index"
                                  class="verification-item">
                                <notification-outlined class="list-icon suggestion" />
                                <span>{{ suggestion }}</span>
                              </li>
                            </ul>
                          </a-card>
                          
                          <a-card class="issues-card">
                            <template #title>
                              <span class="section-title">
                                <warning-outlined />
                                需要注意的問題
                              </span>
                            </template>
                            <ul class="issues-list">
                              <li v-for="(issue, index) in news.verification_guide.issues" :key="index"
                                  class="issue-item">
                                <exclamation-circle-outlined class="list-icon warning" />
                                <span>{{ issue }}</span>
                              </li>
                            </ul>
                          </a-card>
                        </div>
                      </a-collapse-panel>
                    </a-collapse>
                  </div>
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

  // 在 script 部分添加
  const getScoreColor = (score: number) => {
    if (score >= 80) return '#52c41a';
    if (score >= 50) return '#1890ff';
    if (score >= 30) return '#faad14';
    return '#f5222d';
  };

  // 在script部分添加以下import
  import { 
    CheckCircleOutlined,
    FileSearchOutlined,
    InfoCircleOutlined,
    WarningOutlined,
    ExclamationCircleOutlined,
    BugOutlined,
    StopOutlined,
    CheckOutlined,
    LikeOutlined,
    DislikeOutlined,
    PlusCircleOutlined,
    MinusCircleOutlined,
    TrophyOutlined,
    SolutionOutlined,
    FileTextOutlined,
    BarChartOutlined,
    ClockCircleOutlined,
    AuditOutlined,
    BulbOutlined,
    NotificationOutlined,
    SafetyOutlined,
    LinkOutlined,
    ArrowRightOutlined
  } from '@ant-design/icons-vue';

  // 新增：獲取可信度等級對應的 CSS class
  const getCredibilityLevelClass = (level: string) => {
    const levelMap = {
      '極高可信': 'very-high',
      '高度可信': 'high',
      '中度可信': 'medium',
      '低度可信': 'low',
      '極低可信': 'very-low'
    };
    return levelMap[level] || 'medium';
  };

  // 新增：獲取可信度等級說明
  const getCredibilityExplanation = (level: string) => {
    const explanationMap = {
      '極高可信': '新聞內容非常可靠，幾乎沒有爭議點',
      '高度可信': '新聞內容大致可靠，僅有少許爭議',
      '中度可信': '新聞內容部分可信，存在一些爭議點',
      '低度可信': '新聞內容存在較多爭議，需謹慎參考',
      '極低可信': '新聞內容可信度極低，建議尋找其他來源'
    };
    return explanationMap[level] || '正在評估可信度';
  };
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
    background: white;
    padding: 24px;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
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

  .scores-container {
    margin: 20px 0;
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .score-item {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .score-item span {
    min-width: 100px;
  }

  .analysis-results {
    margin-top: 24px;
    padding: 16px;
    background: #f8f8f8;
    border-radius: 8px;
  }

  .analysis-results h3 {
    margin-bottom: 16px;
    color: #1890ff;
  }

  .analysis-results {
    margin-top: 32px;
    padding: 24px;
    background: #ffffff;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.09);
  }

  .analysis-results h3 {
    margin-bottom: 24px;
    color: #1890ff;
    font-size: 20px;
    font-weight: 500;
  }

  .score-cards {
    margin-bottom: 32px;
  }

  .scores-container {
    margin: 24px 0;
    background: #fafafa;
    padding: 24px;
    border-radius: 8px;
  }

  .score-item {
    display: flex;
    align-items: center;
    margin-bottom: 16px;
  }

  .score-item span {
    min-width: 120px;
    font-weight: 500;
  }

  .analysis-collapse {
    background: #fafafa;
    margin-top: 24px;
  }

  :deep(.ant-collapse-header) {
    font-weight: 500;
  }

  :deep(.ant-progress-text) {
    font-weight: 500;
  }

  :deep(.ant-card) {
    transition: all 0.3s;
  }

  :deep(.ant-card:hover) {
    transform: translateY(-4px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.12);
  }

  .credibility-score {
    font-size: 14px;
    color: #1890ff;
    font-weight: 500;
  }

  .score-item :deep(.ant-progress-text) {
    color: #262626;
    font-weight: 500;
  }

  .score-item :deep(.ant-progress-bg) {
    transition: all 0.4s cubic-bezier(0.08, 0.82, 0.17, 1);
  }

  .score-item :deep(.ant-progress) {
    width: 300px;
  }

  .analysis-section {
    padding: 16px;
  }

  .analysis-section h4 {
    color: #1890ff;
    margin: 16px 0 8px 0;
  }

  .analysis-section ul {
    list-style: none;
    padding-left: 0;
  }

  .analysis-section li {
    margin-bottom: 8px;
    line-height: 1.6;
  }

  .analysis-section p {
    margin: 8px 0;
    line-height: 1.6;
  }

  .analysis-section .ant-card {
    margin-bottom: 16px;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  }

  .section-title {
    display: flex;
    align-items: center;
    gap: 8px;
    color: #1890ff;
    font-weight: 500;
  }

  .list-icon {
    margin-right: 8px;
    font-size: 16px;
  }

  .finding-item, .basis-item, .problem-item, .fallacy-item {
    display: flex;
    align-items: flex-start;
    padding: 12px;
    margin: 8px 0;
    background: #fafafa;
    border-radius: 6px;
    transition: all 0.3s;
  }

  .finding-item:hover, .basis-item:hover, 
  .problem-item:hover, .fallacy-item:hover {
    background: #f0f5ff;
    transform: translateX(4px);
  }

  .finding-item .list-icon {
    color: #52c41a;
  }

  .basis-item .list-icon {
    color: #1890ff;
  }

  .problem-item .list-icon {
    color: #faad14;
  }

  .fallacy-item .list-icon {
    color: #ff4d4f;
  }

  .finding-list, .basis-list, .problems-list, .fallacies-list {
    list-style: none;
    padding: 0;
    margin: 0;
  }

  :deep(.ant-card-head) {
    border-bottom: 2px solid #f0f0f0;
  }

  :deep(.ant-collapse-content-box) {
    padding: 0 !important;
  }

  :deep(.ant-card-body) {
    padding: 16px;
  }

  .warning {
    color: #faad14;
  }

  .error {
    color: #ff4d4f;
  }

  /* 平衡性分析樣式 */
  .supporting-item, .opposing-item {
    display: flex;
    align-items: flex-start;
    padding: 12px;
    margin: 8px 0;
    background: #fafafa;
    border-radius: 6px;
    transition: all 0.3s;
  }
  
  .supporting-item:hover {
    background: #f6ffed;
    transform: translateX(4px);
  }
  
  .opposing-item:hover {
    background: #fff1f0;
    transform: translateX(4px);
  }
  
  .support {
    color: #52c41a;
  }
  
  .oppose {
    color: #ff4d4f;
  }
  
  /* 來源分析樣式 */
  .reliability-content {
    padding: 16px;
  }
  
  .reliability-level {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 16px;
  }
  
  .level-icon {
    font-size: 24px;
    color: #faad14;
  }
  
  .level-text {
    font-size: 18px;
    font-weight: 500;
    color: #262626;
  }
  
  .reliability-reason {
    display: flex;
    gap: 8px;
    align-items: flex-start;
  }
  
  .content-type-text {
    padding: 12px;
    background: #fafafa;
    border-radius: 6px;
    margin: 8px 0;
  }
  
  .quality-score-list {
    list-style: none;
    padding: 0;
  }
  
  .quality-score-item {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 16px;
  }
  
  .score-icon {
    font-size: 16px;
  }
  
  .completeness { color: #52c41a; }
  .reliability { color: #1890ff; }
  .timeliness { color: #faad14; }
  .verifiability { color: #722ed1; }
  
  /* 查證指南樣式 */
  .verification-item, .issue-item {
    display: flex;
    align-items: flex-start;
    padding: 12px;
    margin: 8px 0;
    background: #fafafa;
    border-radius: 6px;
    transition: all 0.3s;
  }
  
  .verification-item:hover {
    background: #e6f7ff;
    transform: translateX(4px);
  }
  
  .issue-item:hover {
    background: #fff7e6;
    transform: translateX(4px);
  }
  
  .suggestion {
    color: #1890ff;
  }

  /* 新增：可信度概覽樣式 */
  .credibility-overview {
    margin-bottom: 24px;
  }

  .credibility-banner {
    padding: 32px;
    border-radius: 12px;
    color: white;
    backdrop-filter: blur(10px);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  }

  .credibility-main {
    display: flex;
    align-items: center;
    gap: 24px;
    margin-bottom: 16px;
  }

  .score-circle {
    background: rgba(255, 255, 255, 0.2);
    border-radius: 50%;
    width: 120px;
    height: 120px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    backdrop-filter: blur(5px);
  }

  .score-number {
    font-size: 40px;
    font-weight: bold;
    line-height: 1;
  }

  .score-label {
    font-size: 16px;
    opacity: 0.9;
    margin-top: 4px;
  }

  .credibility-details {
    flex-grow: 1;
  }

  .credibility-level {
    font-size: 24px;
    margin: 0 0 8px 0;
  }

  .credibility-explanation {
    margin: 0;
    font-size: 16px;
    opacity: 0.9;
    line-height: 1.6;
    margin-top: 8px;
    font-size: 15px;
  }

  .reliability-summary {
    padding-top: 16px;
    border-top: 1px solid rgba(255, 255, 255, 0.2);
    margin-top: 20px;
    padding-top: 20px;
    border-top: 1px solid rgba(255, 255, 255, 0.3);
  }

  .reliability-badge {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 16px;
    margin-bottom: 8px;
  }

  .reliability-reason {
    margin: 0;
    opacity: 0.9;
  }

  /* 修改：可信度等級對應的背景色，使用更柔和的配色 */
  .very-high {
    background: linear-gradient(135deg, rgba(82, 196, 26, 0.05), rgba(82, 196, 26, 0.15));
    border: 1px solid rgba(82, 196, 26, 0.3);
    color: #135200;
  }
  
  .high {
    background: linear-gradient(135deg, rgba(24, 144, 255, 0.05), rgba(24, 144, 255, 0.15));
    border: 1px solid rgba(24, 144, 255, 0.3);
    color: #003a8c;
  }
  
  .medium {
    background: linear-gradient(135deg, rgba(250, 173, 20, 0.05), rgba(250, 173, 20, 0.15));
    border: 1px solid rgba(250, 173, 20, 0.3);
    color: #613400;
  }
  
  .low {
    background: linear-gradient(135deg, rgba(255, 122, 69, 0.05), rgba(255, 122, 69, 0.15));
    border: 1px solid rgba(255, 122, 69, 0.3);
    color: #871400;
  }
  
  .very-low {
    background: linear-gradient(135deg, rgba(255, 77, 79, 0.05), rgba(255, 77, 79, 0.15));
    border: 1px solid rgba(255, 77, 79, 0.3);
    color: #820014;
  }
  
  .credibility-banner {
    padding: 32px;
    border-radius: 12px;
    backdrop-filter: blur(10px);
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.05);
  }
  
  .score-circle {
    background: rgba(0, 0, 0, 0.04);
    border: 1px solid rgba(0, 0, 0, 0.1);
    border-radius: 50%;
    width: 120px;
    height: 120px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
  }
  
  .score-number {
    font-size: 40px;
    font-weight: bold;
    line-height: 1;
  }
  
  .score-label {
    font-size: 16px;
    opacity: 0.8;
    margin-top: 4px;
  }
  
  .reliability-summary {
    border-top: 1px solid rgba(0, 0, 0, 0.1);
    margin-top: 24px;
    padding-top: 24px;
  }
  
  .reliability-badge {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 16px;
    margin-bottom: 12px;
    opacity: 0.85;
  }
  
  .reliability-reason {
    margin: 0;
    opacity: 0.75;
    font-size: 14px;
    line-height: 1.6;
  }
  
  .credibility-level {
    font-size: 28px;
    font-weight: 600;
    margin: 0 0 12px 0;
    opacity: 0.9;
  }
  
  .credibility-explanation {
    line-height: 1.6;
    opacity: 0.8;
    font-size: 15px;
  }
  </style>