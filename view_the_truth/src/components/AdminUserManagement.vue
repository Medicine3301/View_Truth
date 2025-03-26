<template>
  <a-layout>
    <Sidebar v-model:collapsed="collapsed" :onCollapse="onCollapse" />
    <a-layout :style="{ marginLeft: layoutMargin }">
      <Header />
      <a-layout-content :style="{ background: '#ececec', margin: '24px 16px 0' }">
        <!-- 數據概覽卡片 -->
        <div class="overview-cards">
          <a-row :gutter="16">
            <a-col :span="6">
              <a-card>
                <a-statistic title="總用戶數" :value="statistics.totalUsers" :value-style="{ color: '#3f8600' }">
                  <template #prefix>
                    <TeamOutlined />
                  </template>
                </a-statistic>
              </a-card>
            </a-col>
            <a-col :span="6">
              <a-card>
                <a-statistic title="本月新增" :value="statistics.monthlyNewUsers" :value-style="{ color: '#0050b3' }">
                  <template #prefix>
                    <UserAddOutlined />
                  </template>
                </a-statistic>
              </a-card>
            </a-col>
            <a-col :span="6">
              <a-card>
                <a-statistic title="待處理檢舉" :value="statistics.pendingReports" :value-style="{ color: '#cf1322' }">
                  <template #prefix>
                    <WarningOutlined />
                  </template>
                </a-statistic>
              </a-card>
            </a-col>
            <a-col :span="6">
              <a-card>
                <a-statistic title="今日活躍" :value="statistics.todayActiveUsers" :value-style="{ color: '#1890ff' }">
                  <template #prefix>
                    <LineChartOutlined />
                  </template>
                </a-statistic>
              </a-card>
            </a-col>
          </a-row>
        </div>

        <!-- 搜尋區域 -->
        <a-card class="search-area" :style="{ background: '#f7f7f7', border: '1px solid #d9d9d9' }">
          <a-form layout="vertical">
            <a-row :gutter="{ xs: 8, sm: 16, md: 24 }">
              <!-- 搜尋條件欄位 -->
              <a-col :xs="24" :sm="8" :md="8">
                <a-form-item label="用戶名/信箱">
                  <a-input-search v-model:value="searchQuery" placeholder="請輸入關鍵字" />
                </a-form-item>
              </a-col>
              <a-col :xs="24" :sm="8" :md="8">
                <a-form-item label="用戶狀態">
                  <a-select v-model:value="filterStatus" style="width: 100%">
                    <a-select-option value="all">全部</a-select-option>
                    <a-select-option value="active">正常</a-select-option>
                    <a-select-option value="banned">已封禁</a-select-option>
                    <a-select-option value="suspended">已停用</a-select-option>
                  </a-select>
                </a-form-item>
              </a-col>
              <a-col :xs="24" :sm="8" :md="8">
                <a-form-item label="註冊時間">
                  <a-range-picker v-model:value="dateRange" style="width: 100%" />
                </a-form-item>
              </a-col>
            </a-row>

            <!-- 搜尋按鈕區域 -->
            <a-row>
              <a-col :span="24" style="text-align: center; margin-top: 8px;">
                <a-space size="middle">
                  <a-button type="primary" @click="handleSearch">
                    <template #icon>
                      <SearchOutlined />
                    </template>
                    搜尋
                  </a-button>
                  <a-button @click="resetSearch">
                    <template #icon>
                      <ReloadOutlined />
                    </template>
                    重置
                  </a-button>
                </a-space>
              </a-col>
            </a-row>
          </a-form>
        </a-card>
        <!-- 表格工具欄 -->
        <a-card class="table-toolbar" :style="{ marginBottom: '16px', background: '#fafafa' }">
          <a-row :gutter="16" align="middle">
            <a-col :span="12">
              <a-space>
                <a-button type="primary" @click="exportUsers">
                  <DownloadOutlined /> 導出用戶資料
                </a-button>
                <a-button danger :disabled="!selectedRowKeys.length" @click="batchBanUsers">
                  <StopOutlined /> 批量封禁
                </a-button>
              </a-space>
            </a-col>
          </a-row>
        </a-card>

        <!-- 用戶列表 -->
        <a-table :columns="columns" :data-source="users" :loading="loading" :pagination="pagination"
          :row-selection="{ selectedRowKeys, onChange: onSelectChange }" @change="handleTableChange"
          :style="{ background: '#fff', borderRadius: '8px', overflow: 'hidden' }">
          <!-- 列模板 -->
          <template #lastLogin="{ text }">
            {{ formatDate(text) }}
            <br />
            <small style="color: #999">
              {{ getTimeAgo(text) }}
            </small>
          </template>

          <template #activity="{ record }">
            <a-progress type="circle" :percent="record.activityScore" :width="30" :show-info="false"
              :stroke-color="getActivityColor(record.activityScore)" />
            <span style="margin-left: 8px">{{ getActivityLabel(record.activityScore) }}</span>
          </template>

          <!-- 用戶狀態列 -->
          <template #status="{ text }">
            <a-tag :color="text === 'active' ? 'green' : 'red'">
              {{ text === 'active' ? '正常' : '已封禁' }}
            </a-tag>
          </template>

          <!-- 操作列 -->
          <template #action="{ record }">
            <a-space>
              <a-button type="primary" size="small" @click="openUserDrawer(record)">
                詳情
              </a-button>
              <a-button :type="record.status === 'active' ? 'danger' : 'primary'" size="small"
                @click="toggleUserStatus(record)">
                {{ record.status === 'active' ? '封禁' : '解封' }}
              </a-button>
            </a-space>
          </template>
        </a-table>

        <!-- 泛用用戶管理抽屜 -->
        <a-drawer title="用戶管理" :visible="drawerVisible" @close="closeDrawer" width="720" :style="{ padding: '16px' }">
          <template v-if="selectedUser">
            <a-descriptions bordered>
              <a-descriptions-item label="用戶名" :span="3">
                {{ selectedUser.username }}
              </a-descriptions-item>
              <a-descriptions-item label="信箱" :span="3">
                {{ selectedUser.email }}
              </a-descriptions-item>
              <a-descriptions-item label="狀態" :span="3">
                <a-tag :color="selectedUser.status === 'active' ? 'green' : 'red'">
                  {{ selectedUser.status === 'active' ? '正常' : '已封禁' }}
                </a-tag>
              </a-descriptions-item>
              <a-descriptions-item label="註冊時間" :span="3">
                {{ formatDate(selectedUser.createdAt) }}
              </a-descriptions-item>
            </a-descriptions>
            <div class="drawer-footer">
              <a-space>
                <a-button danger @click="resetUserPassword">重置密碼</a-button>
                <a-button type="primary" @click="editUserInfo">編輯資料</a-button>
              </a-space>
            </div>
          </template>
        </a-drawer>

        <!-- 添加編輯用戶資料對話框 -->
        <a-modal v-model:visible="editModalVisible" title="編輯用戶資料" @ok="handleEditSubmit" :style="{ padding: '16px' }">
          <a-form :model="editForm" :rules="editRules">
            <a-form-item label="用戶名" name="username">
              <a-input v-model:value="editForm.username" />
            </a-form-item>
            <a-form-item label="信箱" name="email">
              <a-input v-model:value="editForm.email" />
            </a-form-item>
            <a-form-item label="角色" name="role">
              <a-select v-model:value="editForm.role">
                <a-select-option value="user">一般用戶</a-select-option>
                <a-select-option value="admin">管理員</a-select-option>
              </a-select>
            </a-form-item>
          </a-form>
        </a-modal>
      </a-layout-content>
      <a-layout-footer style="text-align: center">
        識真網 ©2024 Created by Ant UED
      </a-layout-footer>
    </a-layout>
  </a-layout>
</template>

<script lang="ts" setup>
import { ref, onMounted, computed } from 'vue';
import { useAuthStore } from '../stores/auth';
import type { TablePaginationConfig } from 'ant-design-vue';
import { message } from 'ant-design-vue';
import Sidebar from '../layout/sidebar.vue';
import Header from '../layout/header.vue';
import {
  TeamOutlined,
  UserAddOutlined,
  WarningOutlined,
  LineChartOutlined,
  SearchOutlined,
  ReloadOutlined,
  DownloadOutlined,
  StopOutlined,
} from '@ant-design/icons-vue';
import ExcelJS from 'exceljs';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';

dayjs.extend(relativeTime);

// 側邊欄狀態
const collapsed = ref(false);
const broken = ref(false);

const layoutMargin = computed(() => {
  if (broken.value) {
    return collapsed.value ? '0px' : '200px';
  }
  return collapsed.value ? '0px' : '200px'; // 根據需求調整寬度
});

const onCollapse = (isCollapsed: boolean, type: string) => {
  console.log(isCollapsed, type);
  // collapsed.value 會通過 v-model:collapsed 自動更新
};
// 定義表格列
const columns = [
  {
    title: '用戶名',
    dataIndex: 'username',
    key: 'username',
    sorter: true
  },
  {
    title: '信箱',
    dataIndex: 'email',
    key: 'email'
  },
  {
    title: '註冊時間',
    dataIndex: 'createdAt',
    key: 'createdAt',
    sorter: true
  },
  {
    title: '狀態',
    dataIndex: 'status',
    key: 'status',
    slots: { customRender: 'status' }
  },
  {
    title: '操作',
    key: 'action',
    slots: { customRender: 'action' }
  }
];

// 數據和狀態
const users = ref([]);
const loading = ref(false);
const searchQuery = ref('');
const filterStatus = ref('all');
const drawerVisible = ref(false);
const selectedUser = ref(null);
const pagination = ref<TablePaginationConfig>({
  total: 0,
  current: 1,
  pageSize: 10,
  showSizeChanger: true,
  showTotal: (total) => `共 ${total} 筆`
});

const authStore = useAuthStore();

// 載入用戶數據
const loadUsers = async () => {
  loading.value = true;
  try {
    const response = await authStore.getAllUsers({
      page: pagination.value.current,
      pageSize: pagination.value.pageSize,
      search: searchQuery.value,
      status: filterStatus.value
    });
    users.value = response.users;
    pagination.value.total = response.total;
  } catch (error) {
    message.error('載入用戶數據失敗');
  } finally {
    loading.value = false;
  }
};

// 處理搜尋
const handleSearch = () => {
  pagination.value.current = 1;
  loadUsers();
};

// 處理表格變化
const handleTableChange = (pag: TablePaginationConfig) => {
  pagination.value = pag;
  loadUsers();
};

// 顯示用戶詳情
const showUserDetails = async (user: any) => {
  selectedUser.value = user;
  drawerVisible.value = true;
  // 載入用戶詳細資訊
  try {
    const details = await authStore.getUserDetails(user.id);
    selectedUser.value = { ...user, ...details };
  } catch (error) {
    message.error('載入用戶詳情失敗');
  }
};

// 關閉抽屜
const closeDrawer = () => {
  drawerVisible.value = false;
  selectedUser.value = null;
};

// 切換用戶狀態（封禁/解封）
const toggleUserStatus = async (user: any) => {
  try {
    await authStore.updateUserStatus(user.id, user.status === 'active' ? 'banned' : 'active');
    message.success('操作成功');
    loadUsers();
  } catch (error) {
    message.error('操作失敗');
  }
};

// 格式化日期
const formatDate = (date: string) => {
  return new Date(date).toLocaleString('zh-TW');
};

// 查看貼文
const viewPost = (post: any) => {
  // 實現查看貼文的邏輯
};

// 初始化
onMounted(() => {
  loadUsers();
});

// 新增統計數據
const statistics = ref({
  totalUsers: 0,
  monthlyNewUsers: 0,
  pendingReports: 0,
  todayActiveUsers: 0
});

// 視圖模式
const viewMode = ref('table');

// 選中的行
const selectedRowKeys = ref<string[]>([]);

// 日期範圍
const dateRange = ref<[dayjs.Dayjs, dayjs.Dayjs]>();

// 編輯表單相關
const editModalVisible = ref(false);
const editForm = ref({
  username: '',
  email: '',
  role: ''
});

// 新增方法
const resetSearch = () => {
  searchQuery.value = '';
  filterStatus.value = 'all';
  dateRange.value = undefined;
  handleSearch();
};

const onSelectChange = (keys: string[]) => {
  selectedRowKeys.value = keys;
};

const exportUsers = async () => {
  const workbook = new ExcelJS.Workbook();
  const worksheet = workbook.addWorksheet('用戶列表');

  // 設置表頭
  worksheet.columns = [
    { header: '用戶名', key: 'username' },
    { header: '信箱', key: 'email' },
    { header: '註冊時間', key: 'createdAt' },
    { header: '狀態', key: 'status' }
  ];

  // 添加數據
  worksheet.addRows(users.value);

  // 導出文件
  const buffer = await workbook.xlsx.writeBuffer();
  const blob = new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `用戶列表_${dayjs().format('YYYY-MM-DD')}.xlsx`;
  link.click();
};

const batchBanUsers = async () => {
  try {
    await Promise.all(
      selectedRowKeys.value.map(uid =>
        authStore.updateUserStatus(uid, 'banned')
      )
    );
    message.success('批量操作成功');
    loadUsers();
    selectedRowKeys.value = [];
  } catch (error) {
    message.error('批量操作失敗');
  }
};

const getTimeAgo = (date: string) => {
  return dayjs(date).fromNow();
};

const getActivityColor = (score: number) => {
  if (score >= 80) return '#52c41a';
  if (score >= 60) return '#1890ff';
  if (score >= 40) return '#faad14';
  return '#ff4d4f';
};

const getActivityLabel = (score: number) => {
  if (score >= 80) return '非常活躍';
  if (score >= 60) return '活躍';
  if (score >= 40) return '一般';
  return '不活躍';
};

const getSecurityLogColor = (type: string) => {
  const colors: Record<string, string> = {
    login: 'green',
    logout: 'blue',
    failed_login: 'red',
    password_change: 'orange'
  };
  return colors[type] || 'gray';
};

const resetUserPassword = async () => {
  try {
    await authStore.resetUserPassword(selectedUser.value.id);
    message.success('密碼重置成功，新密碼已發送至用戶信箱');
  } catch (error) {
    message.error('密碼重置失敗');
  }
};

const editUserInfo = () => {
  editForm.value = {
    username: selectedUser.value.username,
    email: selectedUser.value.email,
    role: selectedUser.value.role
  };
  editModalVisible.value = true;
};

const handleEditSubmit = async () => {
  try {
    await authStore.updateUserInfo(selectedUser.value.id, editForm.value);
    message.success('更新成功');
    editModalVisible.value = false;
    showUserDetails(selectedUser.value.id);
  } catch (error) {
    message.error('更新失敗');
  }
};



// 打開抽屜
const openUserDrawer = (user: any) => {
  selectedUser.value = user;
  drawerVisible.value = true;
};


</script>

<style scoped>
.search-area {
  margin: 16px;
  padding: 16px;
  border-radius: 8px;
}

a-form-item {
  margin-bottom: 16px;
}

.user-activity {
  margin-top: 24px;
}

.overview-cards {
  margin: 16px;
}

.table-toolbar {
  margin: 16px;
  padding: 16px;
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.user-card {
  margin-bottom: 16px;
}

.user-card-cover {
  height: 120px;
  background: #f0f2f5;
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-card-footer {
  margin-top: 16px;
  display: flex;
  justify-content: space-between;
}

.security-log-detail {
  color: rgba(0, 0, 0, 0.45);
  margin-left: 24px;
  margin-top: 4px;
}

.drawer-footer {
  position: absolute;
  bottom: 0;
  width: 100%;
  border-top: 1px solid #e8e8e8;
  padding: 10px 16px;
  text-align: right;
  left: 0;
  background: #fff;
}

a-table {
  margin: 16px;
  border-radius: 8px;
  overflow: hidden;
}

a-card {
  border-radius: 8px;
}

a-button {
  border-radius: 4px;
}

/* 響應式調整 */
@media (max-width: 576px) {
  .search-area {
    margin: 8px;
    padding: 12px;
  }
  
  :deep(.ant-form-item) {
    margin-bottom: 12px;
  }
  
  :deep(.ant-space) {
    display: flex;
    gap: 8px;
  }
  
  :deep(.ant-btn) {
    min-width: 120px;
  }
}

@media (max-width: 768px) {
  .search-area :deep(.ant-form-item-label) {
    padding-bottom: 4px;
  }
  
  .search-area :deep(.ant-col) {
    padding-bottom: 8px;
  }
}
</style>