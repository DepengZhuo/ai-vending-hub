/* ============================================================
   modal.js — Lead 弹窗（Book a Demo / Contact Us）交互逻辑

   职责：
   1) 全站任何带 data-open-modal 的按钮点击后打开弹窗
      （导航栏 Book a Demo、页脚 Contact Us、页面 CTA 都靠它）；
   2) 支持 ESC 键、点击遮罩、右上角 × 关闭；
   3) 表单提交成功后约 2 秒自动关闭并恢复页面滚动；
   4) 打开时锁定页面滚动，防止背景滚动。

   弹窗的 HTML 在 components/lead-modal.html，字段要改去那里改。
   ============================================================ */

(function () {
  /* 等待 include.js 注入完弹窗再绑定事件 */
  function waitForModal(callback, tries) {
    const modal = document.getElementById("lead-modal");
    if (modal) return callback(modal);
    if ((tries || 0) > 40) return; // 最多等约 5 秒
    setTimeout(() => waitForModal(callback, (tries || 0) + 1), 120);
  }

  waitForModal(function (modal) {
    const modalBody = modal.querySelector('[data-modal-body]') || modal;

    function open() {
      modal.classList.remove("hidden");
      modal.classList.add("flex");
      modal.setAttribute("aria-hidden", "false");
      document.body.classList.add("overflow-hidden"); // 锁定背景滚动
      const firstField = modal.querySelector("input, select, textarea, button");
      if (firstField) firstField.focus();
    }

    function close() {
      modal.classList.add("hidden");
      modal.classList.remove("flex");
      modal.setAttribute("aria-hidden", "true");
      document.body.classList.remove("overflow-hidden");
    }

    /* 点击任何 data-open-modal 按钮 → 打开；点击遮罩/× → 关闭 */
    document.addEventListener("click", (e) => {
      if (e.target.closest("[data-open-modal]")) {
        e.preventDefault();
        open();
      } else if (e.target.closest("[data-modal-close]")) {
        close();
      }
    });

    /* ESC 关闭 */
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && !modal.classList.contains("hidden")) close();
    });

    /* 表单提交成功（data-fs-success 出现文字）后自动关闭 */
    const successBox = modal.querySelector("[data-fs-success]");
    if (successBox) {
      const observer = new MutationObserver(() => {
        const hasText = successBox.textContent.trim().length > 0;
        const visible = !successBox.classList.contains("hidden");
        if (hasText && visible) setTimeout(close, 2000);
      });
      observer.observe(successBox, {
        childList: true,
        subtree: true,
        attributes: true,
        attributeFilter: ["class"],
      });
    }

    /* 打开后重置表单，避免上次内容残留 */
    modal.addEventListener("submit", () => {
      /* 交给 @formspree/ajax 处理，这里只负责弹窗行为 */
    });
  });
})();
