<template>
  <router-view />
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
@import './style.css';
</style>

<!-- 根组件：作为整个应用的容器，使用 router-view 显示当前路由对应的组件 -->

<!--
這是主應用組件。
它只包含一個<router-view>組件,用於顯示當前路由對應的組件。
樣式部分引入了全局樣式文件style.css。
-->