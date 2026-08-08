# AI Vending Hub — 网站使用说明（给不会写代码的你）

这个文件夹就是整个网站。把整个文件夹上传到 GitHub Pages 就能上线。

## 一、目录速览

| 路径 | 作用 | 想改什么看这里 |
|---|---|---|
| `index.html` | 首页 | 首页文字、推荐文章 |
| `components/nav.html` | 全站导航栏 + 顶部公告栏 | 菜单链接、Logo 文案、公告 |
| `components/footer.html` | 全站页脚 | 页脚链接、社交、版权 |
| `privacy.html` `terms.html` | 隐私政策 / 使用条款 | 法律文案（上线前请人工复核）|
| `components/lead-modal.html` | Book a Demo / Contact Us 弹窗 | 弹窗里的表单字段 |
| `assets/css/style.css` | 全站样式（按钮、卡片、表单） | 主题色（--brand）、按钮样式 |
| `assets/js/include.js` | 公共组件注入 + canonical | **正式域名**（SITE_CONFIG） |
| `assets/js/forms.js` | 全站表单初始化（Lead 弹窗 / 联系页） | 一般不用改 |
| `assets/images/` | 全站图片（当前为本地占位图 SVG） | 想换图：用同名文件覆盖即可 |
| `news/` `knowledge/` `reviews/` `companies/` `case-studies/` `resources/` `reports/` | 各栏目页面 | 每篇文章的标题和正文 |
| `sitemap.xml` `robots.txt` `feed.xml` | SEO 与 RSS | 上线前替换域名 |

## 图片说明（重要）

- 全站配图是**即梦 AI（Seedream 5.0）生成的正式图**，统一 16:10、WebP 格式，
  存放在 `assets/images/shared/*.webp`（共 50 张，约 3.4MB）。
- 页面 HTML 引用的是带哈希后缀的文件名（如 `xxx-56fd6a.webp`），
  文件名即图片用途，想换某张图：用同名 `.webp` 覆盖即可。
- 旧版图片（占位 SVG / Pexels 图库 / pollinations）已从网站移除，
  如需找回请在工作区 `z/work/legacy-site-images-20260808/` 查看。

## 设计色板（参考方案配色）

- 主色（按钮/链接/CTA）：`#165dff`，悬停加深 `#1249cc`
- 强调色（绿色图标/亮点）：`#10b981`
- 标题文字：`#0f172a`；正文：`#64748b`
- 浅底色/卡片底：`#f8fafc`；边框：`#e2e8f0`
- 页脚：深色 `#0f172a`

想改颜色：改 `assets/css/style.css` 顶部的 `--brand` 等变量，
并把每个页面 `<head>` 里 `tailwind.config` 的 blue/gray 覆盖同步改掉。

## 配图重生成（即梦 AI / 火山引擎 Seedream）

- 当前配图为图库照片（临时）。正式配图用**即梦 AI**生成（质量远好于免费生图服务）。
- 脚本：`work/gen_jimeng.py`（火山引擎方舟视觉生成 API）。
- 用法：① 开通方舟并创建 API Key；② 把 Key 存到 `work/ark_key.txt`；
  ③ 先 `python3 work/gen_jimeng.py --sample 4` 看样图风格；④ 满意后
  `python3 work/gen_jimeng.py` 批量生成 50 张；⑤ 再跑
  `work/process_new_images.py` 自动裁切/压缩/替换进网站。
## 一、改完公共组件后要同步

导航、页脚、弹窗（components/）改动后，**必须**运行一次：
`python3 work/sync_components.py`
它会把 components 内容同步进 `assets/js/include.js` 的内置预览版，
保证双击 HTML 预览和线上效果一致。（注意：本仓库里的
`work/site_build/rebuild_components.py` 是另一台电脑的旧版脚本，请用
`sync_components.py`。）

## 二、三个最常改的地方

1. **改域名**：打开 `assets/js/include.js`，把 `SITE_CONFIG` 里的
   `https://www.aivendinghub.com` 换成你的正式域名
   （`sitemap.xml`、`robots.txt` 里也要换）。
2. **改表单收件方式**：表单统一用 Formspree
   （endpoint `https://formspree.io/f/mgogqyoa`）。
   以后换了表单 ID，把 `components/lead-modal.html` 和 `contact.html`
   里的 `data-formspree-id` 和 `action` 一起改。
3. **改菜单**：打开 `components/nav.html`，复制一行链接，改文字和地址即可。

## 三、怎么预览

- **双击 HTML 直接看（最简单）**：页面能正常显示，导航/页脚/弹窗会使用
  `assets/js/include.js` 内置的"预览版"，页脚底部有一行小字提示。
  注意：预览版是简化副本，改 `components/` 里的文件后想立刻看到新菜单，
  请用下面的 Live Server 方式打开。
- **推荐（所见即所得）**：用 VS Code 打开这个文件夹，安装 "Live Server"
  插件，右键 `index.html` → "Open with Live Server"。
  这种方式会加载 `components/` 里的真实共享组件，和上线效果完全一致。
- 或者：在这个文件夹里开终端运行 `python -m http.server 8000`，
  然后浏览器打开 `http://localhost:8000`。
- 说明：直接双击打开时浏览器禁止网页读取本地组件文件（安全限制），
  所以才会使用内置预览版；这不是网站坏了。

## 四、怎么上线到 GitHub Pages

1. 把 `ai-vending-hub` 整个文件夹推到一个 GitHub 仓库。
2. 仓库 Settings → Pages → 选分支和 `/ (root)` 目录 → Save。
3. 等 1-2 分钟，访问 `https://你的用户名.github.io/仓库名/`。
4. 绑定域名：在仓库 Settings → Pages 里填你的域名，并按提示加 DNS 记录。

## 五、上线前 Checklist（来自 Playbook v3）

- [ ] include.js 里换成正式域名
- [ ] sitemap.xml / robots.txt 域名已替换
- [ ] 新闻和报告类文章已人工核实（草稿页面顶部有注释提醒）
- [ ] Formspree 表单真实提交测试通过
- [ ] 企业目录信息已核对，官网链接正确
- [ ] 移动端浏览一遍没有横向溢出
- [ ] 每页只有一个 H1
- [ ] 所有图片有 alt
- [ ] RSS（feed.xml）能正常打开
- [ ] 404 页面可用
- [ ] Google Search Console 提交 sitemap
