/* ============================================================
   roi-calculator.js — AI 售货机 ROI 计算器（交互组件）

   用法：
   - 页面里放好滑块/输入框（id 见下面 querySelector 注释），
     本脚本监听输入并实时计算；
   - 计算模型：日交易量 = 日均人流 × 转化率；
     月营收 = 日交易量 × 客单价 × 30；
     月净利 = 月营收 × 毛利率 − 固定月费 − 支付手续费；
     回本周期 = 设备总成本 ÷ 月净利。
   - 结果只做估算参考，不构成投资建议。
   想调整公式？改 compute() 里的算法即可，字段名不要动。
   ============================================================ */

(function () {
  const ids = [
    "roi-machines",      // 设备台数
    "roi-traffic",       // 日均人流（经过设备的人数）
    "roi-conversion",    // 转化率（%）
    "roi-aov",           // 平均客单价（美元）
    "roi-margin",        // 毛利率（%）
    "roi-fixed-cost",    // 每台设备月固定成本（软件/流量/支付硬件，美元）
    "roi-tx-rate",       // 支付手续费率（占营收 %）
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
        if (id === "roi-aov" || id === "roi-fixed-cost" || id === "roi-device-price") {
          valEl.textContent = "$" + Number(raw).toLocaleString("en-US");
        } else if (id === "roi-tx-rate") {
          valEl.textContent = Number(raw).toFixed(2) + "%";
        } else if (id === "roi-conversion" || id === "roi-margin") {
          valEl.textContent = raw + "%";
        } else {
          valEl.textContent = Number(raw).toLocaleString("en-US");
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
    const traffic = get("roi-traffic");
    const conversion = get("roi-conversion") / 100;
    const aov = get("roi-aov");
    const margin = get("roi-margin") / 100;
    const fixedCost = get("roi-fixed-cost");
    const txRate = get("roi-tx-rate") / 100;
    const devicePrice = get("roi-device-price");

    const dailyTransactions = traffic * conversion;      // 日交易笔数
    const monthlyTransactions = dailyTransactions * 30;   // 月交易笔数
    const monthlyRevenue = monthlyTransactions * aov;     // 月营收
    const monthlyGross = monthlyRevenue * margin;         // 月毛利
    const fixedFees = fixedCost * machines;               // 月固定费用
    const processingFees = monthlyRevenue * txRate;       // 月支付手续费
    const monthlyNet = monthlyGross - fixedFees - processingFees; // 月净利
    const totalCapEx = devicePrice * machines;            // 设备总成本
    const payback =
      monthlyNet > 0 ? totalCapEx / monthlyNet : null;    // 回本周期(月)

    const set = (id, text) => {
      const el = document.getElementById(id);
      if (el) el.textContent = text;
    };
    set("roi-out-transactions", Math.round(dailyTransactions).toLocaleString("en-US"));
    set("roi-out-revenue", fmt(monthlyRevenue));
    set("roi-out-net", fmt(monthlyNet));
    set("roi-out-capex", fmt(totalCapEx));
    set("roi-out-fees", fmt(fixedFees));
    set("roi-out-fees-tx", fmt(processingFees));
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
