"""Render a 1080x1920 reel: python reel.py spec.json out.mp4 (spec has data.caps, scenes, dur, audio)"""
import json,sys,subprocess,tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright
from render import TEMPLATE
FPS=30
def main(spec_path,out,start=0,end=None):
    spec=json.loads(Path(spec_path).read_text());d=spec['data'];dur=d['dur'];n=int(dur*FPS)
    with tempfile.TemporaryDirectory() as tmp, sync_playwright() as p:
        b=p.chromium.launch();pg=b.new_page(viewport={'width':1080,'height':1920})
        pg.goto(TEMPLATE);pg.evaluate("document.getElementById('slide').style.height='1920px'")
        pg.evaluate("([s,m])=>setup(s,m)",[spec,{}]);pg.evaluate("document.fonts.ready")
        for f in range(n):
            pg.evaluate(f"render({f/FPS})");pg.screenshot(path=f"{tmp}/{f:05d}.jpg",type='jpeg',quality=92)
        b.close()
        subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate',str(FPS),'-i',f'{tmp}/%05d.jpg','-i',d['audio'],'-c:v','libx264','-pix_fmt','yuv420p','-crf','19','-preset','medium','-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart',out],check=True)
if __name__=='__main__':main(sys.argv[1],sys.argv[2])
