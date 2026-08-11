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
PRODUCT_STYLE = ('Photorealistic commercial product photograph, natural realistic lighting, bright clean environment, shallow depth of field, high detail, realistic recognizable retail hardware, machines placed against a wall, interior item-recognition camera hidden inside the cabinet, no visible cameras or sensors on the outside of the machine, no people, no readable text, no logos, no watermark, no futuristic elements, no holograms, no glowing overlays')
# 科技风（banner / 数据看板 / 技术场景）
TECH_STYLE = ('Clean realistic UI screen shown on a modern monitor, photorealistic, natural office lighting, high detail, realistic business software design, no people, no readable brand logos, no watermark, no holograms, no futuristic glowing overlays')

# (prompt, style)
P = {
 "ai-retail-kiosk-edge-vision": ("realistic AI vending kiosk with a glass-front product display and a small touchscreen, placed against a wall in a bright building lobby, standard commercial vending hardware, interior camera hidden inside", "product"),
 "ai-smart-cooler-edge-ai": ("realistic smart cooler vending cabinet with a glass door stocked with drinks, placed against a wall in a bright office break room, card reader on the door, standard commercial hardware, interior camera hidden behind the glass", "product"),
 "ai-smart-fridge-vending-machine": ("realistic AI smart fridge vending machine with a glass door stocked with snacks and drinks, placed against a wall in a modern lobby, cashless payment pad on the door, standard commercial design, interior camera hidden inside", "product"),
 "ai-vending-machine-cloud-dashboard": ("clean fleet telemetry dashboard on a modern monitor showing vending machine status, sales charts and inventory panels, realistic business software UI, natural light", "tech"),
 "ai-vending-machine-glass-door": ("realistic AI vending machine with a glass door full of colorful drinks and snacks, standing against a wall in a bright corridor, standard commercial vending machine design, clean natural lighting", "product"),
 "ai-vending-machine-modern-cafe": ("realistic smart vending machine with a glass door in a modern minimalist cafe, placed against a wall near the counter, natural daylight, standard commercial hardware", "product"),
 "airport-terminal-vending-lounge": ("realistic airport terminal lounge with standard vending machines and glass-door coolers lined against a wall, bright natural lighting, clean modern architecture, everyday commercial look", "product"),
 "buyers-guide-planning-desk": ("clean modern desk with a tablet showing charts and graphs, a printed buyer's guide and a laptop, bright professional workspace, natural light", "product"),
 "cashless-payment-card-reader": ("close-up of a contactless card reader on a vending machine, a hand holding a payment card near the reader, shallow depth of field, realistic", "product"),
 "cashless-payment-vending-card": ("close-up of a hand tapping a contactless payment card on a vending machine payment pad, bright realistic lighting", "product"),
 "checklist-clipboard-retail": ("clipboard with a checklist on a bright modern retail counter, pen resting on the paper, clean minimal composition", "product"),
 "company-directory-retail-logos": ("modern office reception with a digital directory display wall and clean brand signage, natural professional lighting, realistic", "product"),
 "computer-vision-retail-shelf-camera": ("realistic modern retail store with neatly stocked shelves and one small discreet ceiling camera, bright natural lighting, no futuristic overlays", "product"),
 "convenience-store-cashierless-checkout": ("realistic cashierless checkout convenience store, standard shelving and a self-checkout area with subtle ceiling sensors, bright everyday retail lighting, no futuristic glow", "product"),
 "convenience-store-smart-shelves": ("realistic convenience store aisle with standard shelves neatly stocked, bright clean everyday lighting", "product"),
 "deployment-plan-venue-retail": ("retail venue floor plan on a desk with markers, a tablet showing a store layout diagram, deployment planning workspace, clean modern office", "product"),
 "frictionless-store-entrance-turnstiles": ("modern store entrance with automatic glass doors, clean everyday retail design, natural lighting", "product"),
 "glass-door-cooler-store": ("glass door cooler stocked with colorful drinks, placed against a wall in a modern convenience store, bright realistic lighting, standard commercial cooler", "product"),
 "grab-and-go-retail-fridge": ("open glass-door grab-and-go fridge with fresh food and drinks, a customer hand reaching for a product, realistic store setting, natural lighting", "product"),
 "gym-smart-fridge-protein": ("smart fridge stocked with protein shakes and recovery drinks, placed against a wall in a modern gym, glass door, realistic equipment around, bright natural lighting, interior camera hidden inside", "product"),
 "hospital-lobby-vending-kiosk": ("clean modern hospital lobby with a standard vending kiosk and a glass-door cooler against a wall, calm professional atmosphere, bright natural lighting", "product"),
 "hotel-lobby-smart-fridge": ("elegant modern hotel lobby with a smart fridge vending unit placed against a wall near the reception, warm wood and marble interior, natural lighting, realistic", "product"),
 "industry-report-data-charts": ("open industry report on a desk with glossy data charts and graphs, analytics documents, clean professional lighting", "product"),
 "knowledge-base-bookshelf-retail": ("organized modern bookshelf with retail technology and business books, clean minimal interior, soft lighting", "product"),
 "location-scouting-storefront": ("retail storefront being scouted, a tablet on a stand showing location analytics, clipboard nearby, bright daylight, realistic street", "product"),
 "maintenance-technician-vending": ("service technician in a uniform opening the door of a vending machine with a tablet in hand, bright realistic retail environment", "product"),
 "micro-market-kiosk-payment": ("compact self-checkout kiosk with a payment touchscreen in a micro market, shelves of products behind, realistic modern store, bright natural lighting", "product"),
 "micro-market-kiosk-retail": ("self-service micro market kiosk with a touchscreen in a modern office pantry, glass coolers and product shelves, realistic, bright clean space", "product"),
 "micro-market-self-checkout": ("self-checkout station in a modern micro market with shelves and coolers of products, touchscreen payment terminal, realistic retail, bright natural lighting", "product"),
 "network-connectivity-devices": ("rack of network routers and switches for retail IoT in a clean server room, realistic, natural lighting", "product"),
 "office-break-room-vending": ("modern office break room with a smart fridge vending unit against a wall and a coffee area, snacks on shelves, realistic, bright natural light", "product"),
 "payment-telemetry-platform": ("payment and telemetry dashboard on a monitor showing transaction graphs, device status and analytics, realistic business software UI, natural light", "tech"),
 "retail-comparison-charts": ("side-by-side comparison charts and graphs on a screen, realistic analytics interface, clean design", "tech"),
 "retail-industry-news-headlines": ("stack of modern newspapers and a tablet showing industry news headlines on a desk, bright clean editorial workspace", "product"),
 "roi-calculator-analytics": ("ROI analytics dashboard on a monitor with large numbers, revenue charts and KPI panels, realistic business software UI, natural office lighting", "tech"),
 "smart-cooler-card-payment": ("smart cooler with a card reader on the glass door, stocked with drinks, placed against a wall in a bright store, realistic commercial hardware, interior camera hidden inside", "product"),
 "smart-cooler-grab-and-go": ("smart cooler with an open glass door for grab-and-go shopping, products on shelves, placed against a wall in a realistic store, interior camera hidden behind the glass, natural lighting", "product"),
 "smart-fridge-vending-machines": ("two realistic AI smart fridge vending machines side by side against a wall, glass doors full of drinks and snacks, bright corridor, standard commercial hardware, no visible exterior cameras", "product"),
 "smart-locker-retail-pickup": ("smart locker pickup station with digital locker doors, placed against a wall in a modern store lobby, realistic, bright natural lighting", "product"),
 "smart-micro-store-cooler-building": ("compact autonomous micro-store with glass-door coolers placed against the wall of a modern building lobby, realistic, bright natural lighting, interior cameras hidden inside the coolers", "product"),
 "smart-retail-store-sensors": ("realistic modern retail store with neatly stocked shelves and subtle discreet ceiling sensors, bright natural lighting, no futuristic overlays", "product"),
 "smart-retail-trend-forecast": ("trend forecast dashboard with an upward growth curve and future projections on a screen, realistic analytics interface, clean design, natural light", "tech"),
 "smart-vending-cabinet-scan-open": ("smart self-serve vending cabinet with clear glass doors and a QR scan screen, neat product rows inside, placed against a wall in a bright realistic setting, interior camera hidden inside", "product"),
 "unattended-retail-formats": ("collection of unattended retail formats: a vending machine, a glass-door smart cooler and a self-checkout kiosk lined against a wall in one bright space, realistic, natural lighting", "product"),
 "university-campus-vending-lounge": ("modern university campus lounge with standard vending machines against a wall, comfortable seating area, bright natural light, realistic", "product"),
 "vending-business-startup-plan": ("startup business plan notebook with charts, a calculator and a laptop on a clean desk, professional planning workspace", "product"),
 "vending-cost-breakdown-chart": ("cost breakdown chart with bars and percentages on a screen, realistic financial analytics interface, clean design", "tech"),
 "vending-machine-comparison": ("two vending machines side by side, one traditional spiral machine and one modern smart glass-door machine, placed against a wall in a bright showroom, realistic", "product"),
 "vending-machine-factory-catalog": ("vending machine showroom with a wide row of different models against a wall, traditional spiral machines and modern smart fridges with glass doors, realistic, bright clean", "product"),
 "vending-machine-iot-dashboard": ("IoT dashboard on a monitor showing vending machine fleet status, connectivity and battery indicators, realistic telemetry interface, clean design, natural light", "tech"),
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
