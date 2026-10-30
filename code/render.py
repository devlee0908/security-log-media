"""Render a post spec (JSON) into carousel media: animated slides -> MP4, static -> JPG.
Usage: python render.py post.json out_dir
"""
import json, subprocess, sys, tempfile, datetime, base64, io
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image

FPS, DUR = 30, 6  # 6s loops
TEMPLATE = (Path(__file__).parent / "template.html").as_uri()


def photo_url(path):
    """photo file -> JPEG data URL (template is loaded from file://, keep it self-contained)."""
    if path.startswith("data:"):
        return path
    im = Image.open(path).convert("RGB"); im.thumbnail((1200, 2100)); b = io.BytesIO(); im.save(b, "JPEG", quality=90)
    return "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()


def setup_slide(page, s, meta):
    if s.get("photo"):
        s = {**s, "photo": photo_url(s["photo"])}
    page.goto(TEMPLATE)
    page.evaluate("([s,m]) => setup(s,m)", [s, meta])
    if s["type"] == "photocover":
        page.wait_for_function("document.querySelector('.pcover img').complete")
    page.evaluate("document.fonts.ready")


def render(spec_path, out):
    spec = json.loads(Path(spec_path).read_text())
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    files = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page(viewport={"width": 1080, "height": 1440})
        kst = (datetime.datetime.utcnow() + datetime.timedelta(hours=9)).strftime("%Y-%m-%d")
        for i, s in enumerate(spec["slides"], 1):
            s.setdefault("date", kst)  # cover log-tag date in KST
            setup_slide(page, s, spec["meta"])
            if s["type"] in ("cover", "content"):
                with tempfile.TemporaryDirectory() as tmp:
                    # cover: open on the finished scene so the IG grid thumbnail (frame 0) isn't blank,
                    # then crossfade into the build-up. Loop end -> start is then seamless too.
                    hold = 15 if s["type"] == "cover" else 0
                    if hold:
                        page.evaluate(f"render({DUR - 0.5})")
                        page.screenshot(path=f"{tmp}/final.png")
                        final = Image.open(f"{tmp}/final.png").convert("RGB")
                    for f in range(FPS * DUR):
                        page.evaluate(f"render({max(0, f - hold) / FPS})")
                        page.screenshot(path=f"{tmp}/{f:04d}.png")
                        if f < hold:
                            cur = Image.open(f"{tmp}/{f:04d}.png").convert("RGB")
                            Image.blend(final, cur, min(1, max(0, (f - 5) / 10))).save(f"{tmp}/{f:04d}.png")
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


def reel_cover(photo, cat, kicker, title, out, tone=""):
    """9:16 reel cover in the photo-cover style; text sits inside the 3:4 grid crop."""
    with sync_playwright() as p:
        b = p.chromium.launch(); page = b.new_page(viewport={"width": 1080, "height": 1920})
        setup_slide(page, {"type": "photocover", "tall": True, "tone": tone, "cat": cat, "kicker": kicker, "title": title, "photo": photo}, {})
        page.screenshot(path=out, type="jpeg", quality=92); b.close()


if __name__ == "__main__":
    if sys.argv[1] == "reelcover":  # python render.py reelcover photo.png CAT "kicker" "title" out.jpg
        reel_cover(*sys.argv[2:8])  # optional 7th arg: bright
    else:
        render(sys.argv[1], sys.argv[2])
