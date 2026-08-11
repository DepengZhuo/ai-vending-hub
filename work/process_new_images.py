#!/usr/bin/env python3
"""把新生成的配图自动裁切/压缩/替换进网站。

配合 work/gen_jimeng.py 使用：
  1) python3 work/gen_jimeng.py          # 生成到 /tmp/jimeng/<name>.jpg
  2) python3 work/process_new_images.py  # 自动处理并替换 assets/images/shared/

逻辑：
  - 输入 /tmp/jimeng/<name>.jpg（可 --src 指定其它目录）
  - <name> 对应网站图片的"用途名"（如 ai-smart-cooler-edge-ai）
  - 在 assets/images/shared/ 里按 <name>-*.webp 找到真实文件（带哈希后缀）
  - 居中裁切为 16:10，缩放到 1200x750，转 WebP(quality 82) 覆盖替换
  - --dry-run 只预览不动文件
"""
import argparse, glob, os, sys
from pathlib import Path

SITE = Path(__file__).resolve().parents[1]
SHARED = SITE / "assets" / "images" / "shared"
TARGET_W, TARGET_H = 1200, 750
RATIO = TARGET_W / TARGET_H

def process_one(src_path, dry_run=False):
    from PIL import Image
    key = src_path.stem
    candidates = sorted(SHARED.glob(key + "-*.webp"))
    if not candidates:
        return f"  [跳过] {key}: 没有找到对应的网站图片 ({key}-*.webp)"
    if len(candidates) > 1:
        return f"  [警告] {key}: 匹配到多个目标，跳过: {[c.name for c in candidates]}"
    target = candidates[0]
    im = Image.open(src_path).convert("RGB")
    w, h = im.size
    # 居中裁切到 16:10
    if w / h > RATIO:
        nw = int(h * RATIO)
        im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    else:
        nh = int(w / RATIO)
        im = im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
    im = im.resize((TARGET_W, TARGET_H), Image.LANCZOS)
    if dry_run:
        return f"  [预览] {key} -> {target.name} ({w}x{h} -> {TARGET_W}x{TARGET_H})"
    tmp = target.with_suffix(".webp.tmp")
    im.save(tmp, "WEBP", quality=82, method=6)
    tmp.replace(target)
    return f"  [已替换] {key} -> {target.name} ({round(target.stat().st_size/1024)}KB)"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="/tmp/jimeng", help="生成图片所在目录")
    ap.add_argument("--names", nargs="*", default=None, help="只处理指定的 name（默认全部）")
    ap.add_argument("--dry-run", action="store_true", help="只预览不写入")
    args = ap.parse_args()

    src_dir = Path(args.src)
    if not src_dir.is_dir():
        print(f"找不到目录: {src_dir}（先运行 work/gen_jimeng.py）")
        sys.exit(1)
    files = sorted(src_dir.glob("*.jpg")) + sorted(src_dir.glob("*.jpeg")) + sorted(src_dir.glob("*.png"))
    if args.names:
        files = [f for f in files if f.stem in args.names]
    if not files:
        print("没有可处理的图片。")
        return
    print(f"共 {len(files)} 张 -> {'仅预览' if args.dry_run else '处理替换'}")
    ok = 0
    for f in files:
        msg = process_one(f, dry_run=args.dry_run)
        if "已替换" in msg:
            ok += 1
        print(msg)
    print(f"完成: 替换 {ok}/{len(files)}")

if __name__ == "__main__":
    main()
