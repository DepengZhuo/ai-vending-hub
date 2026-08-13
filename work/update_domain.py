#!/usr/bin/env python3
"""One-shot domain migration for AI Vending Hub.

After buying a custom domain and setting it up on GitHub Pages, run:

    python3 work/update_domain.py https://depengzhuo.github.io/ai-vending-hub https://www.yourdomain.com

It rewrites every absolute site URL (canonical, og:url, og:image, sitemap,
robots, search index, include.js) from the old base to the new base.
"""
import sys, glob, os

def main():
    if len(sys.argv) != 3:
        print(__doc__); sys.exit(1)
    old, new = sys.argv[1].rstrip('/'), sys.argv[2].rstrip('/')
    if old == new:
        print("old == new, nothing to do"); return
    files = glob.glob('**/*.html', recursive=True) + \
            glob.glob('**/*.xml', recursive=True) + \
            glob.glob('**/*.json', recursive=True) + \
            ['assets/js/include.js', 'robots.txt']
    n = 0
    for f in files:
        if not os.path.exists(f): continue
        s = open(f, encoding='utf-8').read()
        if old in s:
            open(f, 'w', encoding='utf-8').write(s.replace(old, new))
            print('updated', f); n += 1
    print(f"\nDone. {n} files updated from {old} -> {new}")
    print("Also remember to set the custom domain in GitHub Pages settings (CNAME).")

if __name__ == '__main__':
    main()
