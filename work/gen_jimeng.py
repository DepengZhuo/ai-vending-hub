#!/usr/bin/env python3
"""即梦 AI (Volcano Engine Ark / Seedream) 批量生成 AI 售货柜场景配图。

用法:
  1) Key 存在本脚本同目录 ark_key.txt，模型名存 ark_model.txt（均仅本地）。
  2) 先出样图看风格:  python3 work/gen_jimeng.py --sample 4
  3) 全部生成:        python3 work/gen_jimeng.py
输出: /tmp/jimeng/<name>.jpg，随后用 process_new_images.py 裁切压缩并替换进网站。
"""
import argparse, json, os, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

BASE = "https://ark.cn-beijing.volces.com/api/v3/images/generations"
WORK = Path(__file__).resolve().parent
OUT = Path("/tmp/jimeng")
OUT.mkdir(parents=True, exist_ok=True)

# 统一风格基座（写实商用摄影 + 冷调 + 无文字水印）
PRODUCT_STYLE = ("Photorealistic commercial product photograph, bright clean studio lighting, "
                 "soft cool tones, shallow depth of field, high detail, realistic hardware details, "
                 "no people, no readable text, no logos, no watermark")
# 科技风（banner / 数据看板 / 技术场景）
TECH_STYLE = ("Futuristic tech aesthetic, deep blue and cyan glow accents, subtle holographic data overlays, "
              "sleek modern design, cinematic lighting, photorealistic, high detail, "
              "no people, no readable text, no logos, no watermark")

# (prompt, style)
P = {
 "ai-retail-kiosk-edge-vision": ("elegant standalone AI retail vending kiosk with a large touchscreen and glass-front product display, edge computer-vision camera module mounted inside, minimalist modern storefront design", "product"),
 "ai-smart-cooler-edge-ai": ("flagship AI smart cooler with a glass door and built-in computer-vision camera, secure card payment reader on the door, sleek industrial design, placed in a bright modern store", "product"),
 "ai-smart-fridge-vending-machine": ("modern AI smart vending combo machine with glass door, snack and drink shelves, interior computer-vision camera, cashless payment pad, sleek black-and-silver design", "product"),
 "ai-vending-machine-cloud-dashboard": ("futuristic cloud dashboard on a large monitor showing AI vending machine fleet telemetry, sales charts and inventory panels, deep blue and cyan interface, glowing data visualization", "tech"),
 "ai-vending-machine-glass-door": ("AI vending machine with a glass door full of colorful drinks and snacks, interior vision camera, subtle blue holographic product-recognition overlay, bright modern retail space", "product"),
 "ai-vending-machine-modern-cafe": ("futuristic AI vending machine with glass door in a modern minimalist cafe, glowing blue holographic telemetry overlay around the machine, cinematic deep-blue tech lighting, sleek high-tech atmosphere", "tech"),
 "airport-terminal-vending-lounge": ("modern high-tech airport terminal lounge with sleek smart vending machines and coolers, blue ambient lighting, glass and metal architecture, futuristic atmosphere", "tech"),
 "buyers-guide-planning-desk": ("clean modern desk with a tablet showing charts and graphs, a printed buyer's guide and a laptop, bright professional workspace, soft cool tones", "product"),
 "cashless-payment-card-reader": ("close-up of a contactless card reader on a vending machine, a hand holding a payment card near the reader, shallow depth of field", "product"),
 "cashless-payment-vending-card": ("close-up of a hand tapping a contactless payment card on a vending machine payment pad, bright clean lighting", "product"),
 "checklist-clipboard-retail": ("clipboard with a checklist on a bright modern retail counter, pen resting on the paper, clean minimal composition", "product"),
 "company-directory-retail-logos": ("modern office reception with a sleek digital directory display wall and clean brand signage, blue ambient lighting, professional corporate atmosphere", "tech"),
 "computer-vision-retail-shelf-camera": ("small sleek ceiling camera with a subtle blue LED monitoring a retail shelf with neatly arranged products, computer-vision retail concept", "product"),
 "convenience-store-cashierless-checkout": ("modern convenience store with a cashierless checkout lane, ceiling sensors and cameras, digital screens, clean futuristic retail design", "tech"),
 "convenience-store-smart-shelves": ("convenience store aisle with smart shelves featuring LED indicators and small shelf sensors, neatly stocked products, bright clean lighting", "product"),
 "deployment-plan-venue-retail": ("retail venue floor plan on a desk with markers, a tablet showing a store layout diagram, deployment planning workspace, clean modern office", "product"),
 "frictionless-store-entrance-turnstiles": ("modern frictionless store entrance with automatic glass doors and sleek sensor gates, blue accent lighting, futuristic checkout-free retail", "tech"),
 "glass-door-cooler-store": ("glass door cooler stocked with colorful drinks in a modern convenience store, bright clean lighting, product focus", "product"),
 "grab-and-go-retail-fridge": ("open glass-door grab-and-go fridge with fresh food and drinks, a customer hand reaching for a product, bright store lighting, realistic", "product"),
 "gym-smart-fridge-protein": ("smart fridge stocked with protein shakes and recovery drinks in a modern gym, glass door with vision camera, clean fitness environment", "product"),
 "hospital-lobby-vending-kiosk": ("clean modern hospital lobby with a sleek vending kiosk and smart cooler, calm professional atmosphere, bright lighting", "product"),
 "hotel-lobby-smart-fridge": ("elegant modern hotel lobby with a smart fridge vending unit near the reception, warm wood and marble interior, bright professional lighting", "product"),
 "industry-report-data-charts": ("open industry report on a desk with glossy data charts and graphs, analytics documents, clean professional lighting", "tech"),
 "knowledge-base-bookshelf-retail": ("organized modern bookshelf with retail technology and business books, clean minimal interior, soft lighting", "product"),
 "location-scouting-storefront": ("retail storefront being scouted, a tablet on a stand showing location analytics, clipboard nearby, bright daylight, realistic street scene", "product"),
 "maintenance-technician-vending": ("service technician in a uniform opening the door of a vending machine with a tablet in hand, bright retail environment, realistic", "product"),
 "micro-market-kiosk-payment": ("compact self-checkout kiosk with a payment touchscreen in a micro market, shelves of products behind, modern office break area, bright lighting", "product"),
 "micro-market-kiosk-retail": ("self-service micro market kiosk with a touchscreen in a modern office pantry, glass coolers and product shelves around, bright clean space", "product"),
 "micro-market-self-checkout": ("self-checkout station in a modern micro market with shelves and coolers of products, touchscreen payment terminal, bright clean retail", "product"),
 "network-connectivity-devices": ("rack of network routers, switches and connectivity devices for retail IoT, clean server room, blue LED indicator lights, professional", "product"),
 "office-break-room-vending": ("modern office break room with a smart fridge vending unit and coffee area, snacks on shelves, bright clean workspace", "product"),
 "payment-telemetry-platform": ("payment and telemetry dashboard on a monitor showing transaction graphs, device status and analytics, modern interface, deep blue tones", "tech"),
 "retail-comparison-charts": ("side-by-side comparison charts and graphs on a screen, modern analytics interface, blue and gray data visualization, clean", "tech"),
 "retail-industry-news-headlines": ("stack of modern newspapers and a tablet showing industry news headlines on a desk, bright clean editorial workspace", "product"),
 "roi-calculator-analytics": ("ROI analytics dashboard on a monitor with large numbers, revenue charts and KPI panels, modern interface, deep blue and cyan", "tech"),
 "smart-cooler-card-payment": ("smart cooler with a built-in card reader on the door, camera-based grab-and-go unit, clean modern design, bright retail setting", "product"),
 "smart-cooler-grab-and-go": ("smart cooler with open glass door for grab-and-go shopping, vision cameras inside, products on shelves, bright store", "product"),
 "smart-fridge-vending-machines": ("two AI smart fridge vending machines side by side with glass doors full of drinks and snacks, vision cameras and cashless payment, modern showroom", "product"),
 "smart-locker-retail-pickup": ("smart locker pickup station in a modern retail store, digital locker doors with small screens, clean bright interior", "product"),
 "smart-micro-store-cooler-building": ("compact autonomous smart micro-store inside a modern building lobby, glass-door coolers with inward-facing cameras and mini grocery shelves, 24-7 convenience concept", "product"),
 "smart-retail-store-sensors": ("smart retail store with ceiling sensors and cameras over product shelves, subtle blue data overlays, futuristic retail technology", "tech"),
 "smart-retail-trend-forecast": ("trend forecast dashboard with an upward growth curve and future projections on a screen, modern analytics, blue glow", "tech"),
 "smart-vending-cabinet-scan-open": ("smart self-serve vending cabinet with clear glass doors and a scan-to-open QR screen, neat product rows inside, RFID and vision technology, bright setting", "product"),
 "unattended-retail-formats": ("collection of unattended retail formats in one bright space, self-service kiosks and smart coolers with glass doors, clean modern retail", "product"),
 "university-campus-vending-lounge": ("modern university campus lounge with smart vending machines, comfortable seating area, bright natural light, clean academic atmosphere", "product"),
 "vending-business-startup-plan": ("startup business plan notebook with charts, a calculator and a laptop on a clean desk, professional planning workspace", "product"),
 "vending-cost-breakdown-chart": ("cost breakdown chart with bars and percentages on a screen, modern financial analytics interface, clean design", "tech"),
 "vending-machine-comparison": ("two vending machines side by side, one traditional spiral machine and one modern smart glass-door machine, showroom comparison, bright clean setting", "product"),
 "vending-machine-factory-catalog": ("vending machine showroom with a wide row of different models, traditional spiral machines and modern AI smart fridges with glass doors, large catalog display", "product"),
 "vending-machine-iot-dashboard": ("IoT dashboard on a monitor showing vending machine fleet status, connectivity and battery indicators, modern telemetry interface, blue tones", "tech"),
}

def load_key():
    if os.environ.get("ARK_API_KEY"):
        return os.environ["ARK_API_KEY"].strip()
    kf = WORK / "ark_key.txt"
    if kf.exists():
        return kf.read_text(encoding="utf-8").strip()
    return None

def load_model(args):
    if args.model:
        return args.model
    mf = WORK / "ark_model.txt"
    if mf.exists():
        return mf.read_text(encoding="utf-8").strip()
    return "doubao-seedream-5-0-pro-260628"

def call_ark(key, model, prompt, seed, size):
    body = json.dumps({
        "model": model,
        "prompt": prompt,
        "size": size,
        "response_format": "url",
        "seed": seed,
        "stream": False,
        "watermark": False,
    }).encode("utf-8")
    req = urllib.request.Request(BASE, data=body, method="POST", headers={
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    })
    with urllib.request.urlopen(req, timeout=240) as r:
        resp = json.loads(r.read().decode("utf-8"))
    url = resp["data"][0]["url"]
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=240) as r:
        return r.read()

def fetch_one(args, key, model, seed, name):
    dest = OUT / f"{name}.jpg"
    if dest.exists() and dest.stat().st_size > 20000:
        return f"skip {name}"
    subject, style_kind = P[name]
    style = TECH_STYLE if style_kind == "tech" else PRODUCT_STYLE
    prompt = subject + ", " + style
    for attempt in range(4):
        try:
            data = call_ark(key, model, prompt, seed, args.size)
            if len(data) < 15000:
                raise RuntimeError(f"too small {len(data)}")
            dest.write_bytes(data)
            return f"OK {name} {len(data)//1024}KB (attempt {attempt+1})"
        except Exception as e:
            print(f"  retry {name}: {e}", flush=True)
            time.sleep(4 + attempt * 5)
    return f"FAIL {name}"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, default=0, help="只生成前 N 张样图")
    ap.add_argument("--model", default="", help="模型ID或推理接入点 ep-xxx")
    ap.add_argument("--size", default="2K")
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--workers", type=int, default=3)
    args = ap.parse_args()

    key = load_key()
    if not key:
        print("没有找到 API Key。请先开通火山引擎方舟并创建 Key，然后:")
        print("  echo '你的key' > work/ark_key.txt   (或 export ARK_API_KEY=...)")
        sys.exit(1)
    model = load_model(args)
    print(f"model: {model} | size: {args.size} | seed: {args.seed}")

    names = list(P.keys())
    if args.sample:
        names = names[:args.sample]
        print(f"sample mode: {len(names)} 张")
    print(f"{len(names)} images to generate -> {OUT}")

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(fetch_one, args, key, model, args.seed, n): n for n in names}
        for i, f in enumerate(as_completed(futs), 1):
            print(f"[{i}/{len(names)}] {f.result()}", flush=True)

if __name__ == "__main__":
    main()
