/* ============================================================
   tailwind.config.js — Tailwind 配置文件（参考用）

   目前网站用的是 Tailwind CDN（无需构建），所以本文件不会被加载。
   保留它的作用：
   1) 记录设计 Token 的唯一出处，方便以后迁移到"构建版" Tailwind；
   2) 如果你以后用 Tailwind CLI 生成压缩版 CSS，再启用这份配置。

   想改主题色：把 colors.primary 改掉即可（同时记得改 style.css 的 --brand）。
   ============================================================ */

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["../**/*.html", "../**/*.js"],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#3B82F6",   /* 主色：CTA、高亮 */
          dark: "#2563EB",
        },
        ink: "#111827",          /* 标题 */
        body: "#4B5563",         /* 正文 */
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
