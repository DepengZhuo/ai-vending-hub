/* ============================================================
   forms.js — 全站 Formspree 表单初始化

   原理：
   - 页面里任何带 data-formspree-id 的表单（Lead 弹窗、联系页）
     都会在这里初始化，提交走 Ajax 不刷新页面；
   - Formspree 表单 ID 写在每个表单的 data-formspree-id 属性里，
     默认是 mgogqyoa（对应 https://formspree.io/f/mgogqyoa）；
   - 弹窗是 include.js 异步注入的，所以要等 "components-injected"
     事件触发后再初始化，并保留一个兜底延时。

   说明：Newsletter 已按需求移除，本文件只处理 Lead / Contact 表单。
   ============================================================ */

/* formspree 官方推荐的全局函数（库加载前调用会先排队） */
window.formspree =
  window.formspree ||
  function () {
    (formspree.q = formspree.q || []).push(arguments);
  };

/* 初始化所有带 data-formspree-id 的表单 */
function initAllForms() {
  document.querySelectorAll("form[data-formspree-id]").forEach((form) => {
    const formId = form.dataset.formspreeId || "mgogqyoa";
    window.formspree("initForm", {
      formElement: "#" + form.id,
      formId: formId,
    });
  });
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => {
    initAllForms(); // 先初始化页面里本来就有的表单（如联系页）
    window.addEventListener("components-injected", initAllForms);
    /* 万一组件注入事件没触发，兜底再试一次 */
    setTimeout(initAllForms, 1500);
  });
} else {
  initAllForms();
  window.addEventListener("components-injected", initAllForms);
  setTimeout(initAllForms, 1500);
}
