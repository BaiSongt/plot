# Plot 数据可视化平台前端
> Plot Data Visualization Platform Frontend

## 项目简介 / Project Overview

Plot 是一个现代化的数据可视化平台，基于 React + TypeScript + Vite 构建，提供强大的数据分析和可视化能力。

Plot is a modern data visualization platform built with React, TypeScript, and Vite, offering powerful data analysis and visualization capabilities.

## 技术栈 / Tech Stack

- ⚡ [Vite](https://vitejs.dev/) - 下一代前端工具链
- ⚛️ [React 18](https://reactjs.org/) - 用于构建用户界面的 JavaScript 库
- 📘 [TypeScript](https://www.typescriptlang.org/) - 类型安全的 JavaScript 超集
- 🎨 [Ant Design](https://ant.design/) - 企业级 UI 设计语言
- 📊 [ECharts](https://echarts.apache.org/) - 强大的图表库
- 🌐 [React Router](https://reactrouter.com/) - 声明式路由
- 🛠 [Zustand](https://github.com/pmndrs/zustand) - 状态管理

## 快速开始 / Getting Started

### 环境要求 / Prerequisites

- Node.js 16.0.0 或更高版本
- npm 8.0.0 或更高版本，或 yarn 1.22.0 或更高版本

### 安装依赖 / Install Dependencies

```bash
# 使用 npm
npm install

# 或使用 yarn
yarn
```

### 开发模式 / Development

```bash
# 启动开发服务器
npm run dev

# 或
yarn dev
```

### 构建生产版本 / Build for Production

```bash
# 构建生产版本
npm run build

# 预览生产版本
npm run preview
```

## 项目结构 / Project Structure

```
src/
├── assets/         # 静态资源
├── components/     # 公共组件
├── config/        # 全局配置
├── hooks/         # 自定义 Hooks
├── layouts/       # 布局组件
├── pages/         # 页面组件
├── routes/        # 路由配置
├── services/      # API 服务
├── stores/        # 状态管理
├── styles/        # 全局样式
├── types/         # TypeScript 类型定义
├── utils/         # 工具函数
└── App.tsx        # 根组件
```

## 代码规范 / Code Style

本项目使用 ESLint 和 Prettier 来保持代码风格一致。

This project uses ESLint and Prettier for code style consistency.

### 扩展 ESLint 配置 / Expanding the ESLint Configuration

## 扩展 ESLint 配置 / Expanding the ESLint Configuration

如果您正在开发生产应用，我们建议更新配置以启用类型感知的 lint 规则：

If you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:

```js
export default tseslint.config({
  extends: [
    // Remove ...tseslint.configs.recommended and replace with this
    ...tseslint.configs.recommendedTypeChecked,
    // Alternatively, use this for stricter rules
    ...tseslint.configs.strictTypeChecked,
    // Optionally, add this for stylistic rules
    ...tseslint.configs.stylisticTypeChecked,
  ],
  languageOptions: {
    // other options...
    parserOptions: {
      project: ['./tsconfig.node.json', './tsconfig.app.json'],
      tsconfigRootDir: import.meta.dirname,
    },
  },
})
```

您还可以安装 [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) 和 [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) 来获取 React 特定的 lint 规则：

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default tseslint.config({
  plugins: {
    // 添加 react-x 和 react-dom 插件
    // Add the react-x and react-dom plugins
    'react-x': reactX,
    'react-dom': reactDom,
  },
  rules: {
    // 其他规则...
    // other rules...
    
    // 启用推荐的 TypeScript 规则
    // Enable its recommended typescript rules
    ...reactX.configs['recommended-typescript'].rules,
    ...reactDom.configs.recommended.rules,
  },
})
```

## 贡献指南 / Contributing

欢迎提交 Issue 和 Pull Request。在提交代码前，请确保：

1. 运行 `npm run lint` 检查代码风格
2. 运行 `npm run build` 确保构建通过
3. 添加适当的测试用例

## 许可证 / License

[MIT](LICENSE) © 2025 Plot Team

## 致谢 / Acknowledgments

- [Vite](https://vitejs.dev/) - 快速的前端构建工具
- [React](https://reactjs.org/) - 用于构建用户界面的 JavaScript 库
- [Ant Design](https://ant.design/) - 企业级 UI 设计语言
- [ECharts](https://echarts.apache.org/) - 强大的图表库
