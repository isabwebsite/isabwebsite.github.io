# 用 GitHub 更新网站

2026-11-06：[社团组织](https://github.com/isabwebsite) 和 [网站资料库](https://github.com/isabwebsite/isabwebsite.github.io) 已建立，[新版网站](https://isabwebsite.github.io/) 已发布。现有 Netlify 网站没有变动。下列设置步骤保留供以后重新搭建时参考。

当前使用 GitHub Free 组织、公开资料库和免费的 `github.io` 地址。发布方式为 GitHub Actions，资料库变量 `PUBLISH_SITE=true`；保存或合并到 `main` 会自动更新网站，其他分支只检查。当前只有首任负责人担任组织管理员，第二位管理员尚未加入。联系邮箱由组织设置管理，不写入公开项目，也不等于该邮箱持有人已获得编辑权限。

首次成功发布记录：[运行 42325249949](https://github.com/isabwebsite/isabwebsite.github.io/actions/runs/42325249949)，对应版本 `b434b98032b68adf5bebf1629603d74ed9944b9c`。它可作为首次上线的内容参考；撤回某次更新时优先只撤回该次变更，避免覆盖后来新增的文章。

## 每次更新怎么做

1. 用自己的 GitHub 账号，通过有编辑能力的 AI 打开网站资料库的最新版本。
2. 告诉 AI 要修改什么。先在修改分支里编辑，打开本地预览，确认文章和链接。
3. 请 AI 保存修改并提交一个 Pull request（待合并的更新）。GitHub 会运行 `Check website`，检查生成结果、文章资料和站内链接；这不能替代人工核对事实和外部网站。
4. 预览满意、检查通过后，确认合并到 `main`。**发布启用后，这一步会触发网站更新。**
5. 在 Actions 页面打开 `Publish website`，确认全部完成，再打开正式网址检查内容。

拥有 Write 权限的维护者可保存和 push 修改；是否允许直接改 `main`，还取决于资料库规则。当前方案不需要共享密码、原维护者的 AI 账号或长期个人发布密钥。

## 第一次设置：交给 AI 或管理员

这部分由首次搭建者完成，后任日常改文章不用重复设置。

1. 创建免费的社团 GitHub 组织。选择长期名称，联系邮箱用本届可收信的邮箱；不要编造邮箱地址。邀请第二位负责人需要其 GitHub 用户名。
2. 在组织名下创建公开资料库，命名为 `组织名.github.io`。上传本文件夹的内容到资料库根目录，包括 `.github`，不要再多套一层 `isab-journal` 文件夹。这样可以使用根网址，适配当前网站路径。
3. 只上传可公开的网站文稿、图片、工具及说明。不要上传上层 `handbook` 文件夹、账号登记表、浏览器登录截图或密码。公开资料库的提交记录可能显示维护者 GitHub 用户名；成员可使用自己的 GitHub 隐藏邮箱设置。
4. 先确认 `Check website` 成功，并看本地预览。仓库变量 `PUBLISH_SITE` 未设置时，发布任务会跳过，不会上线。
5. 准备正式发布时，在 Settings → Pages → Build and deployment 中将 Source 设为 **GitHub Actions**。
6. 在 Settings → Secrets and variables → Actions → Variables 中添加资料库变量 `PUBLISH_SITE`，值为小写 `true`。它是公开配置，不是密码。
7. 在 Actions → Publish website → Run workflow 中选择 `main` 并运行。以后 push 或合并到 `main` 会重新生成、检查并发布；其他分支只运行检查。
8. 确认正式网址可打开，检查首页、文章、图片和语言切换。把资料库与网站链接写到项目 README 和社团内部交接记录。旧网站的转移或跳转单独处理。

发布任务读取 Pages 的真实网址，自动生成正式链接与搜索收录文件。当前生成工具会拒绝带资料库子路径的网址；不要为了通过检查删除这一限制。若要使用子路径，先适配网站的全部资源和路由。

网站使用 GitHub 的短期任务授权发布，不在源码里保存个人令牌。正式发布只上传 `dist` 中生成的网页；文稿和说明仍会作为公开资料库文件可见。

## 更新失败或需要撤回

**检查失败：** 请 AI 阅读失败的检查信息，修复对应文稿或工具，再提交修改。不要跳过检查强行发布。生成或检查失败时，本流程不会覆盖已发布的网站。

**发布失败：** 查看 `Publish website` 的失败步骤；检查 Pages 设置与任务权限。先确认线上仍是哪一版，不把 push 成功当成发布成功。

**撤回已合并的文章更新：** 让 AI 撤回指定那次修改，保留其他人后来新增的内容，先看本地预览，再把撤回作为一次新的更新合并到 `main`。不要强行覆盖整个历史或上传旧压缩包。

**暂停后续自动发布：** 将 `PUBLISH_SITE` 改为 `false`。它只阻止后续运行开始发布，不会取消正在运行的任务，也不会把已经上线的网站下架。需要停止正在进行的发布，应另行检查并取消那次运行。

**恢复自动发布：** 改回 `true` 后，运行一次 `Publish website`；仅修改变量不会立即更新网页。

## 换届

至少保留两位现任组织管理员，各用自己的账号。接任者需独立完成修改、预览、发布与撤回演练；然后更新当届联系邮箱，再移除离任者。两位接任管理员的用户名未提供前，不会随意邀请或授权别人。

参考：[GitHub 组织创建](https://docs.github.com/en/organizations/collaborating-with-groups-in-organizations/creating-a-new-organization-from-scratch)、[Pages 发布配置](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)、[Pages 自定义流程](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)。
