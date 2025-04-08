import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import Antd from 'ant-design-vue';
import 'ant-design-vue/dist/reset.css';
import * as AntDesignIconsVue from '@ant-design/icons-vue'

const app = createApp(App)
const pinia = createPinia()

// 注册 Ant Design Vue 图标
for (const [key, component] of Object.entries(AntDesignIconsVue)) {
    app.component(key, component)
}

app.use(pinia)
    .use(router)
    .use(Antd)  // 使用 Ant Design Vue
    
    .mount('#app')

// 主入口文件：创建 Vue 应用实例，集成 Pinia、Vue Router、Element Plus 和 Ant Design Vue
// 這是應用的主入口文件。
// 它創建Vue應用實例,引入並使用Vue Router、Element Plus 和 Ant Design Vue,
// 全局註冊Element Plus和Ant Design Vue的圖標,
// 然後將應用掛載到id為"app"的DOM元素上。
