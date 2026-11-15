#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""合成雌雄对比图，用作 Notion Gallery 封面。紧凑版：无标签、无空隙，两图直接拼接。
用法: compose_pair.py <male> <female> <out> [layout]
layout: 'v'=上下堆叠(默认,适合近正方形封面) | 'h'=左右并排
"""
import sys
from PIL import Image

male_path, female_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
layout = sys.argv[4] if len(sys.argv) > 4 else "v"

if layout == "h":
    H = 900
    def fit_h(img):
        return img.resize((int(img.width*H/img.height), H), Image.LANCZOS)
    a = fit_h(Image.open(male_path).convert("RGB"))
    b = fit_h(Image.open(female_path).convert("RGB"))
    canvas = Image.new("RGB", (a.width + b.width, H))
    canvas.paste(a, (0, 0)); canvas.paste(b, (a.width, 0))
else:  # 上下堆叠，等宽，直接紧贴
    W = 1100
    def fit_w(img):
        return img.resize((W, int(img.height*W/img.width)), Image.LANCZOS)
    a = fit_w(Image.open(male_path).convert("RGB"))
    b = fit_w(Image.open(female_path).convert("RGB"))
    canvas = Image.new("RGB", (W, a.height + b.height))
    canvas.paste(a, (0, 0)); canvas.paste(b, (0, a.height))

canvas.save(out_path, "JPEG", quality=88)
print(f"OK -> {out_path}  {canvas.width}x{canvas.height}  ratio={canvas.width/canvas.height:.2f}")


