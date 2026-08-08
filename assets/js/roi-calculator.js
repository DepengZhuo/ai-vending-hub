/* ============================================================
   roi-calculator.js — AI 售货机 ROI 计算器（交互组件）

   用法：
   - 页面里放好滑块/输入框（id 见下面 querySelector 注释），
     本脚本监听输入并实时计算；
   - 计算逻辑是"估算模型"：只做参考，结果会随单价、交易量等变化，
     页面下方已注明不构成投资建议。
   想调整公式？改 compute() 里的算法即可，字段名不要动。
   ============================================================ */

(function () {
  const ids = [
    "roi-machines",      // 设备台数
    "roi-orders",        // 每台每天交易笔数
    "roi-aov",           // 平均客单价（美元）
    "roi-margin",        // 毛利率（%）
    "roi-cost",          // 每台设备月成本（租金/运维等，美元）
    "roi-device-price",  // 单台设备采购价（美元，用于回本周期）
  ];
  const els = {};
  ids.forEach((id) => {
    const el = document.getElementById(id);
    if (el) {
      els[id] = el;
      /* 同步显示滑块当前值（对应页面里的 <span id="xxx-val">） */
      const valEl = document.getElementById(id + "-val");
      const updateVal = () => {
        if (!valEl) return;
        const raw = el.value;
        if (id === "roi-aov" || id === "roi-cost" || id === "roi-device-price") {
          valEl.textContent = "$" + Number(raw).toLocaleString("en-US");
        } else if (id === "roi-margin") {
          valEl.textContent = raw + "%";
        } else {
          valEl.textContent = raw;
        }
      };
      el.addEventListener("input", updateVal);
      updateVal();
    }
  });
  if (Object.keys(els).length === 0) return; // 本页没有计算器

  const fmt = (n) =>
    "$" + Math.round(n).toLocaleString("en-US");

  function compute() {
    const get = (id) => parseFloat(els[id] ? els[id].value : 0) || 0;
    const machines = get("roi-machines");
    const orders = get("roi-orders");
    const aov = get("roi-aov");
    const margin = get("roi-margin") / 100;
    const monthlyCost = get("roi-cost");
    const devicePrice = get("roi-device-price");

    const dailyRevenue = machines * orders * aov;      // 日营收
    const monthlyRevenue = dailyRevenue * 30;           // 月营收
    const monthlyGross = monthlyRevenue * margin;       // 月毛利
    const monthlyNet = monthlyGross - monthlyCost * machines; // 月净利
    const payback =
      monthlyNet > 0 ? (devicePrice * machines) / monthlyNet : null; // 回本周期(月)

    const set = (id, text) => {
      const el = document.getElementById(id);
      if (el) el.textContent = text;
    };
    set("roi-out-revenue", fmt(monthlyRevenue));
    set("roi-out-gross", fmt(monthlyGross));
    set("roi-out-net", fmt(monthlyNet));
    set(
      "roi-out-payback",
      payback === null ? "N/A" : "~" + payback.toFixed(1) + " months"
    );
  }

  ids.forEach((id) => {
    const el = els[id];
    if (el) el.addEventListener("input", compute);
  });
  compute(); // 页面加载后先算一次
})();
