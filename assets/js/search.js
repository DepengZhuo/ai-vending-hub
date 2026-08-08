/* ============================================================
   search.js — 站内轻量搜索（首页 / 404 页使用）

   原理：
   - 页面里放一个 <input id="site-search"> 搜索框；
   - 这里读取 search-index.json（由生成器自动生成的全站页面清单），
     按标题/描述/分类做包含匹配，实时显示下拉结果；
   - 结果点击跳转到对应页面。
   ============================================================ */

(function () {
  const input = document.getElementById("site-search");
  if (!input) return; // 本页没有搜索框就直接跳过

  const root = document.body.getAttribute("data-root") || "";
  const resultsBox = document.getElementById("search-results");
  let index = [];

  /* 加载全站索引 */
  fetch(root + "search-index.json")
    .then((res) => res.json())
    .then((data) => {
      index = data;
    })
    .catch(() => {
      /* 本地 file:// 打开时无法加载索引，静默降级即可 */
    });

  input.addEventListener("input", () => {
    const q = input.value.trim().toLowerCase();
    if (!q || !resultsBox) {
      if (resultsBox) resultsBox.classList.add("hidden");
      return;
    }
    const hits = index
      .filter(
        (item) =>
          item.title.toLowerCase().includes(q) ||
          (item.description || "").toLowerCase().includes(q) ||
          (item.section || "").toLowerCase().includes(q)
      )
      .slice(0, 8);

    if (hits.length === 0) {
      resultsBox.innerHTML =
        '<p class="px-4 py-3 text-sm text-gray-500">No results. Try "vending", "cost", "computer vision"...</p>';
    } else {
      resultsBox.innerHTML = hits
        .map(
          (h) =>
            '<a href="' +
            root +
            h.url +
            '" class="block px-4 py-2.5 text-sm hover:bg-blue-50">' +
            '<span class="font-semibold text-gray-900">' +
            h.title +
            "</span>" +
            '<span class="ml-2 text-xs uppercase tracking-wide text-blue-600">' +
            h.section +
            "</span></a>"
        )
        .join("");
    }
    resultsBox.classList.remove("hidden");
  });
})();
