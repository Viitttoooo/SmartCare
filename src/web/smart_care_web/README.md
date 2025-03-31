# SmartCare 前端项目技术概述

本项目是SmartCare的前端部分，基于现代化的Web开发技术栈构建。

## 核心技术框架

- **Vue 3**: 采用Vue 3作为主要前端框架，使用组合式API和`<script setup>`语法
- **Vite**: 使用Vite作为构建工具，提供更快的开发服务器启动和热模块替换(HMR)

## 状态管理与路由

- **Vuex 4**: 用于集中式状态管理
- **Vue Router 4**: 管理前端路由，实现单页应用导航

## UI组件与样式

- **Element Plus**: 基于Vue 3的组件库，提供丰富的UI元素
- **自定义CSS**: 项目包含全局样式和组件样式

## 数据可视化

- **ECharts**: 强大的数据可视化库，用于展示图表和统计信息

## 网络请求

- **Axios**: 处理HTTP请求，与后端API交互

## Markdown渲染

- **Marked**: 用于Markdown文本的解析和渲染

## 开发工具

- **ESModule**: 项目采用ES模块系统
- **IDE支持**: 针对VSCode等IDE的配置优化

## 部署与构建

- 开发环境: `npm run dev`
- 生产构建: `npm run build`
- 本地预览: `npm run preview`

---

本模板可帮助您开始使用Vue 3和Vite进行开发。模板使用Vue 3的`<script setup>` SFC，详情请查看[script setup文档](https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup)。

了解更多关于Vue在IDE中的支持，请参阅[Vue文档的扩展工具指南](https://vuejs.org/guide/scaling-up/tooling.html#ide-support)。
