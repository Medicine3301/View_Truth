import { defineStore } from 'pinia'
import axios from 'axios'
import { notification } from 'ant-design-vue'


// 宣告
interface UserState {
    user: {
        uid: string
        una: string
        email: string
        role: string
        birthday: string
        usex: string
        reg_date: string
        avatar?: string
    } | null
    isAuthenticated: boolean
    otherUser: {
        uid: string
        una: string
        email: string
        role: string
        birthday: string
        usex: string
        reg_date: string
        avatar?: string
    } | null
    otherUsers: {
        uid: string;
        una: string;
        email: string;
        role: string;
        birthday: string;
        usex: string;
        reg_date: string;
        avatar?: string;
    }[] | null
    Getuser: {
        uid: string
        una: string
        email: string
        role: string
        reg_date: string
        status: string
    }[] | null
}

interface Community {
    cid: string
    cna: string
    descr: string
    post_count: string
    last_update: string
}
interface post {
    pid: string
    cid: string
    uid: string
    una: string
    title: string
    content: string
    comm_count: string
    crea_date: string
}
interface comment {
    pid: string
    comm_id: string
    uid: string
    una: string
    title: string
    content: string
    crea_date: string
    nid: string
}
interface CommunityState {
    community: Community | null
    communities: Community[] | null
}
interface Poststate {
    post: post | null
    posts: post[] | null
    favorite: post | null
    favorites: post[] | null
    comment: comment | null
    comments: comment[] | null
}
interface Newstate {
    news: news | null
    newsies: news[] | null
    comment: comment | null
    comments: comment[] | null
}
interface news {
    newstitle: string
    news_id: string
    journ: string
    newsclass: string
    news_content: string
    suggest: string
    score: string
    crea_date: string
}
interface RegisterUserData {
    name: string
    email: string
    password: string
    sex: string
    birthday: Date
    verificationCode: string
}

// 狀態管理
export const useAuthStore = defineStore('auth', {
    state: (): {
        userState: UserState; communityState: CommunityState
        postState: Poststate; newstate: Newstate
    } => ({
        userState: {
            user: null,
            isAuthenticated: false,
            otherUser: null,
            otherUsers: null,
            Getuser: null
        },
        communityState: {
            community: null,
            communities: null
        },
        postState: {
            post: null,
            posts: null,
            favorite: null,
            favorites: null,
            comment: null,
            comments: null
        },
        newstate: {
            news: null,
            newsies: null,
            comment: null,
            comments: null
        }
    }),
    getters: {
        isAdmin(state): boolean {
            return state.userState.user?.role === 'admin';
        }
    },
    actions: {
        async login(username: string, password: string) {
            try {
                const response = await axios.post('http://localhost:8000/api/login', {
                    username,
                    password
                });

                if (response.status === 200) {
                    this.userState.user = response.data.user;
                    this.userState.isAuthenticated = true;
                    localStorage.setItem('token', response.data.token);
                    notification.success({
                        message: '登入成功',
                        description: '歡迎回來！',
                        duration: 3
                    });
                    return true;
                }
                return false;
            } catch (error: any) {
                const errorMessage = error.response?.data?.error || '登入失敗，請稍後再試';
                notification.error({
                    message: '登入失敗',
                    description: errorMessage,
                    duration: 3
                });
                return false;
            }
        },

        async register(userData: RegisterUserData) {
            try {
                const response = await axios.post('http://localhost:8000/api/register', userData);

                if (response.status === 201) {
                    notification.success({
                        message: '註冊成功',
                        description: '請登入以繼續',
                        duration: 3
                    });
                    return true;
                }
                return false;
            } catch (error: any) {
                const errorMessage = error.response?.data?.error || '註冊失敗，請稍後再試';
                notification.error({
                    message: '註冊失敗',
                    description: errorMessage,
                    duration: 3
                });
                return false;
            }
        },

        logout() {
            this.userState.user = null;
            this.userState.isAuthenticated = false;
            localStorage.removeItem('token');
            notification.info({
                message: '已登出',
                description: '您已成功登出系統',
                duration: 3
            });
        },

        async checkAuth() {
            const token = localStorage.getItem('token');
            if (!token) {
                this.logout();
                return;
            }

            try {
                const response = await axios.get('http://localhost:8000/api/verify', {
                    headers: {
                        Authorization: `Bearer ${token}`
                    }
                });

                if (response.status === 200) {
                    this.userState.user = response.data.user;
                    this.userState.isAuthenticated = true;
                } else {
                    this.logout();
                    notification.warn({
                        message: '會話過期',
                        description: '請重新登入',
                        duration: 3
                    });
                }
            } catch (error) {
                this.logout();
                notification.error({
                    message: '驗證失敗',
                    description: '請重新登入系統',
                    duration: 3
                });
            }
        },
        //獲取用戶列表(後台)
        async fetchUsers(params: Record<string, any>) {
            try {
                const response = await axios.get('http://localhost:8000/api/users', { params });
                if (response.status === 200) {
                    return response.data; // 返回後端數據
                } else {
                    notification.error({
                        message: '加載用戶列表失敗',
                        description: '無法獲取用戶數據，請稍後再試',
                        duration: 3
                    });
                    throw new Error('加載用戶列表失敗');
                }
            } catch (error: any) {
                notification.error({
                    message: '加載用戶列表失敗',
                    description: error.response?.data?.error || '請稍後再試',
                    duration: 3
                });
                throw error;
            }
        },
        async getUserInfo(uid: string) {
            try {
                const response = await axios.get(`http://localhost:8000/api/user/${uid}`);
                if (response.status === 200) {
                    this.userState.otherUser = response.data.user;
                } else {
                    notification.error({
                        message: '用戶不存在',
                        description: '無法找到該用戶的信息',
                        duration: 3
                    });
                }
            } catch (error: any) {
                notification.error({
                    message: '獲取用戶信息失敗',
                    description: error.response?.data?.error || '請稍後再試',
                    duration: 3
                });
            }
        },

        async getCommunityInfo(cid: string) {
            try {
                const response = await axios.get(`http://localhost:8000/api/community/${cid}`);
                if (response.status === 200) {
                    this.communityState.community = response.data.community;
                } else {
                    notification.error({
                        message: '社群不存在',
                        description: '無法找到該社群',
                        duration: 3
                    });
                }
            } catch (error: any) {
                notification.error({
                    message: '獲取社群信息失敗',
                    description: error.response?.data?.error || '請稍後再試',
                    duration: 3
                });
            }
        },
        async getAllCommunities() {
            try {
                const response = await axios.get('http://localhost:8000/api/community/all');
                if (response.status === 200) {
                    this.communityState.communities = response.data.communities as Community[];
                } else {
                    notification.error({
                        message: '沒有找到任何社群',
                        description: '目前沒有可用的社群資料',
                        duration: 3
                    });
                }
            } catch (error: any) {
                notification.error({
                    message: '獲取所有社群信息失敗',
                    description: error.response?.data?.error || '請稍後再試',
                    duration: 3
                });
            }
        },
        async getPostInfo(pid: string) {
            try {
                const response = await axios.get(`http://localhost:8000/api/post/${pid}`);
                if (response.status === 200) {
                    this.postState.post = response.data.post;
                } else {
                    notification.error({
                        message: '貼文不存在',
                        description: '無法找到該貼文',
                        duration: 3
                    });
                }
            } catch (error: any) {
                notification.error({
                    message: '獲取貼文信息失敗',
                    description: error.response?.data?.error || '請稍後再試',
                    duration: 3
                });
            }
        },
        async getAllPosts(cid: string) {
            try {
                const response = await axios.get(`http://localhost:8000/api/posts/${cid}`);
                if (response.status === 200) {
                    this.postState.posts = response.data.posts as post[];
                } else {
                    notification.error({
                        message: '沒有找到任何貼文',
                        description: '目前沒有可用的貼文資料',
                        duration: 3
                    });
                }
            } catch (error: any) {
                notification.error({
                    message: '獲取所有貼文信息失敗',
                    description: error.response?.data?.error || '請稍後再試',
                    duration: 3
                });
            }
        },
        //獲取該user貼文
        async getuserPosts(uid: string) {
            try {
                const response = await axios.get(`http://localhost:8000/api/userpost/${uid}`);
                if (response.status === 200) {
                    this.postState.posts = response.data.posts as post[];
                } else {
                    notification.error({
                        message: '沒有找到任何貼文',
                        description: '目前沒有可用的貼文資料',
                        duration: 3
                    });
                }
            } catch (error: any) {
                notification.error({
                    message: '獲取該用戶貼文信息失敗',
                    description: error.response?.data?.error || '請稍後再試',
                    duration: 3
                });
            }
        },
        async checkFavorite(pid: string, uid: string): Promise<boolean> {
            try {
                const response = await axios.post('http://localhost:8000/api/favorites/get/', {
                    pid,
                    uid,
                });

                console.log('獲取收藏狀態成功:', response.data);

                // 檢查 response.data 中的實際收藏狀態
                // 根據你的 API 返回數據結構來判斷
                // 例如：response.data.isFavorited 或 response.data.exists 等
                return response.data.isFavorited || response.data.exists || false;

            } catch (error: any) {
                console.error('獲取收藏狀態失敗:', error);
                return false;
            }
        }
        ,
        async checkScore(pid: string, uid: string): Promise<number> {
            try {
                const response = await axios.post('http://localhost:8000/api/scores/get/', {
                    pid,
                    uid,
                });
                console.log('獲取評分狀態成功:', response.data);

                // 確保返回評分值，如果後端返回的數據中有 score
                return response.data.score || 0; // 如果沒有評分，返回默認值 0
            } catch (error: any) {
                console.error('獲取評分狀態失敗:', error);
                return 0; // 發生錯誤時返回默認值 0
            }
        },
        //get user favorite
        async getuserFavorites(uid: string) {
            try {
                const response = await axios.get(`http://localhost:8000/api/userfavorites/${uid}`);
                if (response.status === 200) {
                    this.postState.favorites = response.data.favorite_posts as post[]; // 修改這裡
                } else {
                    notification.error({
                        message: '沒有找到任何收藏',
                        description: '目前沒有可用的收藏資料',
                        duration: 3
                    });
                }
            }
            catch (error: any) {
                notification.error({
                    message: '獲取該用戶收藏信息失敗',
                    description: error.response?.data?.error || '請稍後再試',
                    duration: 3
                });
            }
        }
        ,

        async getAllComments(pid: string) {
            try {
                const response = await axios.get(`http://localhost:8000/api/comment/${pid}`);
                if (response.status === 200) {
                    this.postState.comments = response.data.comments as comment[];
                } else {
                    notification.error({
                        message: '沒有找到任何留言',
                        description: '目前沒有可用的留言資料',
                        duration: 3
                    });
                }
            } catch (error: any) {
                notification.error({
                    message: '獲取所有留言信息失敗',
                    description: error.response?.data?.error || '請稍後再試',
                    duration: 3
                });
            }
        },

        async getAllnewsies() {
            try {
                const response = await axios.get('http://localhost:8000/api/news/all');
                if (response.status === 200) {
                    this.newstate.newsies = response.data.newsies as news[];
                } else {
                    notification.error({
                        message: '沒有找到任何內容',
                        description: '目前沒有可用的分析資料',
                        duration: 3
                    });
                }
            } catch (error: any) {
                notification.error({
                    message: '獲取所有內容信息失敗',
                    description: error.response?.data?.error || '請稍後再試',
                    duration: 3
                });
            }
        },
        async getnewsInfo(nid: string) {
            try {
                console.log('Fetching news with ID:', nid);
                const response = await axios.get(`http://localhost:8000/api/news/${nid}`);
                console.log('API Response:', response);
                if (response.status === 200) {
                    console.log('News data:', response.data.news);
                    this.newstate.news = response.data.news;
                } else {
                    notification.error({
                        message: '新聞不存在',
                        description: '無法找到該新聞',
                        duration: 3
                    });
                }
            } catch (error: any) {
                console.error('API Error:', error);
                console.error('Error response:', error.response);
                notification.error({
                    message: '獲取新聞信息失敗',
                    description: error.response?.data?.error || '請稍後再試',
                    duration: 3
                });
            }
        },
        //news的
        async getNewsAllComments(nid: string) {
            try {
                const response = await axios.get(`http://localhost:8000/api/ncomment/${nid}`);
                if (response.status === 200) {
                    this.newstate.comments = response.data.comments as comment[];
                } else {
                    notification.error({
                        message: '沒有找到任何留言',
                        description: '目前沒有可用的留言資料',
                        duration: 3
                    });
                }
            } catch (error: any) {
                notification.error({
                    message: '獲取所有留言信息失敗',
                    description: error.response?.data?.error || '請稍後再試',
                    duration: 3
                });
            }
        },
        setupAxiosInterceptors() {
            axios.interceptors.request.use(
                config => {
                    const token = localStorage.getItem('token');
                    if (token) {
                        config.headers.Authorization = `Bearer ${token}`;
                    }
                    return config;
                },
                error => {
                    return Promise.reject(error);
                }
            );

            axios.interceptors.response.use(
                response => response,
                error => {
                    if (error.response?.status === 401) {
                        this.logout();
                        notification.error({
                            message: '會話過期',
                            description: '請重新登入系統',
                            duration: 3
                        });
                    }
                    return Promise.reject(error);
                }
            );
        }
    }
});
