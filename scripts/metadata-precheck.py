#!/usr/bin/env python3
"""送审前元数据自查：扫描 Apple 商标措辞与高频元数据拒审词。

来源：appstore-submit skill（2026-09，5.2.5 实战复盘 + fastlane precheck 分类借鉴）。
判定依据以 Apple 官方商标指南为准，本脚本只是下限检查。

用法：
  metadata-precheck.py metadata.json            # 键：name/subtitle/keywords/description/promo_text
  metadata-precheck.py --name X --subtitle Y --keywords K --description D

退出码：0=通过（可有 WARN）；2=存在 FAIL（名称/副标题/关键词命中 Apple 产品词）。
"""
import argparse
import json
import re
import sys

# 5.2.5 硬规则：名称/副标题/关键词里出现 Apple 产品/服务名（宣传性使用）
APPLE_PRODUCT_TERMS = [
    "iphone", "ipad", "ipadpro", "ipados", "mac", "macos", "imac", "macbook",
    "watch", "appletv", "airpods", "visionpro", "pencil", "icloud",
    "app store", "appstore", "safari", "facetime", "retina",
]
# 词边界按中文场景放宽：直接子串匹配（中文无空格边界）
OTHER_PLATFORM_TERMS = ["android", "windows phone", "windows10mobile", "blackberry",
                        "compuserve", "symbian", "palmos", "sailfish"]
PLACEHOLDER_TERMS = ["lorem ipsum", "hipster ipsum", "bacon ipsum", "placeholder", "text here",
                     "占位", "示例文本"]
FUTURE_TERMS = ["coming soon", "coming shortly", "in the next release", "arriving soon",
                "即将推出", "即将上线", "下个版本"]
FREE_IAP_TERMS = ["free", "免费"]  # 仅当声明 has_iap 时提示


def scan(text: str, terms, label: str, level: str, hits: list):
    if not text:
        return
    low = text.lower()
    for t in terms:
        if t in low:
            hits.append((level, label, t))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("meta_json", nargs="?")
    ap.add_argument("--name"); ap.add_argument("--subtitle")
    ap.add_argument("--keywords"); ap.add_argument("--description")
    ap.add_argument("--promo-text"); ap.add_argument("--has-iap", action="store_true")
    args = ap.parse_args()

    m = {}
    if args.meta_json:
        m = json.load(open(args.meta_json))
    fields = {k: (getattr(args, k.replace("-", "_")) or m.get(k) or "") for k in
              ("name", "subtitle", "keywords", "description", "promo-text")}

    hits = []
    # 硬规则字段：name/subtitle/keywords/promo
    for k in ("name", "subtitle", "keywords", "promo-text"):
        scan(fields[k], APPLE_PRODUCT_TERMS, k, "FAIL", hits)
    # 描述：商标措辞降级为 WARN
    scan(fields["description"], APPLE_PRODUCT_TERMS, "description", "WARN", hits)
    for k in fields:
        scan(fields[k], OTHER_PLATFORM_TERMS, k, "WARN", hits)
        scan(fields[k], PLACEHOLDER_TERMS, k, "WARN", hits)
        scan(fields[k], FUTURE_TERMS, k, "WARN", hits)
    if args.has_iap:
        for k in fields:
            scan(fields[k], FREE_IAP_TERMS, k, "WARN", hits)

    # 噪声抑制：描述里的正当引用（如开源许可名）无法穷举——如需白名单在此扩展
    if not hits:
        print("PASS: 未发现元数据拒审高危词")
        return 0
    fails = [h for h in hits if h[0] == "FAIL"]
    for level, field, term in hits:
        print(f"[{level}] {field}: 命中 '{term}'")
    if fails:
        print("\nFAIL: 名称/副标题/关键词含 Apple 产品词（5.2.5 高危），送审前必须修改")
        return 2
    print("\nWARN only: 逐条人工确认后再提交")
    return 0


if __name__ == "__main__":
    sys.exit(main())
