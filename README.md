# Neilyodog Blog

这是一个从公开 Notion 文章和旧 Hexo 站整理而来的纯静态个人网站。当前包含 20 篇 Markdown 文章、4 个分类、11 个标签，以及本地图片和视频。页面不需要 Notion、Vercel、第三方字体或评论服务。

## 本地预览

需要 Python 3.12 或更新版本。

```powershell
python -m pip install -r requirements.txt
python build.py
python -m http.server 4173 --directory dist
```

然后访问 `http://localhost:4173/`。

## 写文章

在 `content/posts/` 新建 Markdown 文件。文件顶部使用以下元数据；图片、视频放进 `public/media/`，在正文中引用 `/media/文件名`。

```yaml
---
title: 示例文章
date: '2026-10-28'
category: 技术分享
tags:
  - Unity
summary: 一句话介绍文章。
cover: /media/example.jpg
source_id: example-post
---
```

文件名可以自定，`source_id` 决定文章地址 `/article/source_id/`。使用 Obsidian 写作时，请把 `content/posts/` 作为笔记目录，并留意图片最终要放在 `public/media/`。

## 部署

当前仓库的 `main` 分支从根目录直接提供旧站。本次可编辑源码放在 `rebuild-static-blog` 分支，编译好的站点放在 `publish-static-site` 分支。审核后将 `publish-static-site` 合并或快进到 `main`，即可由现有 GitHub Pages 设置发布。

源码内也带有 GitHub Actions 工作流。如果之后希望改成每次提交 Markdown 自动构建，需要将源码放到 `main`，并在仓库 **Settings → Pages → Build and deployment** 中选择 **GitHub Actions**。这属于后续部署方式调整。

原 Hexo 的 11 个文章路径已生成跳转页；当前 NotionNext 的 19 个 `/article/<UUID>/` 路径也沿用 UUID。旧 Vercel 域名上的跨域跳转需要另行修改该域名的部署配置。

GitHub Pages 在不同地区、运营商的访问表现可能变化。本站的全部必需资源均在同一个站点下，可以另行部署到其他静态托管服务。

## 目录

- `content/posts/`：Markdown 原文。
- `public/media/`：站内图片和视频。
- `templates/`：页面模板。
- `public/style.css` 和 `public/site.js`：样式与站内搜索。
- `build.py`：生成 `dist/`。
