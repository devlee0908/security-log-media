"""Render a post spec (JSON) into carousel media: animated slides -> MP4, static -> JPG.
Usage: python render.py post.json out_dir
"""
import json, subprocess, sys, tempfile, datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

FPS, DUR = 30, 6  # 6s loops
TEMPLATE = (Path(__file__).parent / "template.html").as_uri()


def render(spec_path, out):
    spec = json.loads(Path(spec_path).read_text())
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    files = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page(viewport={"width": 1080, "height": 1350})
        kst = (datetime.datetime.utcnow() + datetime.timedelta(hours=9)).strftime("%Y-%m-%d")
        for i, s in enumerate(spec["slides"], 1):
            s.setdefault("date", kst)  # cover log-tag date in KST
            page.goto(TEMPLATE)
            page.evaluate("([s,m]) => setup(s,m)", [s, spec["meta"]])
            page.evaluate("document.fonts.ready")
            if s["type"] in ("cover", "content"):
                with tempfile.TemporaryDirectory() as tmp:
                    for f in range(FPS * DUR):
                        page.evaluate(f"render({f / FPS})")
                        page.screenshot(path=f"{tmp}/{f:04d}.png")
                    dst = out / f"{i:02d}.mp4"
                    # IG wants H.264 + AAC; add a silent track.
                    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", f"{tmp}/%04d.png",
                                    "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-shortest",
                                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-c:a", "aac",
                                    "-movflags", "+faststart", str(dst)], check=True)
                    page.screenshot(path=str(out / f"{i:02d}_preview.jpg"), type="jpeg", quality=90)
            else:
                dst = out / f"{i:02d}.jpg"
                page.screenshot(path=str(dst), type="jpeg", quality=95)
            files.append(dst.name)
            print("rendered", dst.name)
        b.close()
    (out / "caption.txt").write_text(spec["caption"])
    (out / "manifest.json").write_text(json.dumps({"media": files, "caption": spec["caption"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    render(sys.argv[1], sys.argv[2])
