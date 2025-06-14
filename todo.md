## 任务清单

### 阶段 1: 分析现有代码并创建项目结构
- [x] 读取 `index.html`
- [x] 创建 `todo.md` (当前任务)
- [x] 创建项目目录结构 (例如: `/home/ubuntu/rehab_news_project/`)
- [x] 将 `index.html` 移动到项目目录中

### 阶段 2: 修改前端界面和样式
- [x] 修改网页背景颜色为浅色
- [x] 确保前端可以按时间倒序显示文章和论文

### 阶段 3: 开发后端API服务
- [x] 选择后端技术栈 (例如 Python Flask)
- [x] 设计API接口，用于获取资讯列表
- [x] 实现API后端逻辑

### 阶段 4: 实现数据爬虫和数据库存储
- [x] 确定目标学术网站 (Pubmed, 谷歌学术, 百度学术, 知网等)
- [x] 开发爬虫程序定期抓取最新论文和资讯
- [x] 实现数据清洗和去重逻辑
- [x] 选择并设置数据库 (例如 MongoDB, PostgreSQL)
- [x] 将清洗后的数据存入数据库

### 阶段 5: 集成前后端并测试功能
- [x] 修改前端JavaScript代码，使用 `fetch` 调用后端API替换 `mockData`
- [x] 测试数据显示是否正确，特别是时间排序
- [x] 验证前端界面浅色主题效果
- [ ] 修复数据库连接问题，确保API正常工作
- [ ] 测试整体功能和用户体验

### 阶段 6: 部署到GitHub并上线
- [x] 创建GitHub仓库
- [x] 初始化Git仓库并提交代码
- [x] 创建项目文档 (README.md)
- [x] 配置部署文件 (.gitignore, requirements.txt, Procfile)
- [x] 添加GitHub Actions自动部署配置
- [ ] 推送代码到GitHub远程仓库
- [ ] 配置GitHub Pages或其他部署平台
- [ ] 将项目代码推送到GitHub
- [ ] 配置GitHub Pages或其他部署服务
- [ ] 测试线上版本


