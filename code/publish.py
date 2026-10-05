"""security.log publisher: out_dir(manifest.json) -> Cloudinary -> Instagram carousel.

Usage:
  python publish.py series <CAT>          # next series number for TIPS/TREND/WORDS (from IG captions)
  python publish.py recent                # recent captions (duplicate-topic check)
  python publish.py publish <out_dir>     # upload + publish carousel, prints permalink
Secrets: ~/.secrets/{ig_token,cld_name,cld_key,cld_secret}
"""
import hashlib, json, re, sys, time, urllib.parse, urllib.request
from pathlib import Path

S = Path.home() / ".secrets"
sec = lambda n: (S / n).read_text().strip()
IG = "https://graph.instagram.com/v23.0"
UID = "17841465997331652"


def http(url, data=None, method=None, headers=None, files=None):
    h = dict(headers or {})
    body = None
    if files:  # multipart
        b = "----slog" + str(int(time.time() * 1000))
        parts = []
        for k, v in (data or {}).items():
            parts.append(f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
        for k, p in files.items():
            parts.append(f'--{b}\r\nContent-Disposition: form-data; name="{k}"; filename="{Path(p).name}"\r\n'
                         f'Content-Type: application/octet-stream\r\n\r\n'.encode() + Path(p).read_bytes() + b"\r\n")
        body = b"".join(parts) + f"--{b}--\r\n".encode()
        h["Content-Type"] = f"multipart/form-data; boundary={b}"
    elif data is not None:
        body = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(url, data=body, method=method, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise SystemExit(f"HTTP {e.code} {url.split('?')[0]}: {e.read().decode()[:500]}")


def ig(path, data=None, method=None):
    return http(f"{IG}/{path}", data, method, {"Authorization": "Bearer " + sec("ig_token")})


def cld_upload(path, public_id):
    rt = "video" if path.endswith(".mp4") else "image"
    ts = str(int(time.time()))
    sig = hashlib.sha1(f"public_id={public_id}&timestamp={ts}{sec('cld_secret')}".encode()).hexdigest()
    r = http(f"https://api.cloudinary.com/v1_1/{sec('cld_name')}/{rt}/upload",
             {"api_key": sec("cld_key"), "timestamp": ts, "public_id": public_id, "signature": sig}, files={"file": path})
    return r["secure_url"]


def wait(cid, tries=40):
    for _ in range(tries):
        st = ig(f"{cid}?fields=status_code,status")
        if st.get("status_code") == "FINISHED":
            return
        if st.get("status_code") == "ERROR":
            raise SystemExit(f"container {cid} error: {st}")
        time.sleep(5)
    raise SystemExit(f"container {cid} timeout")


def captions(n=50):
    return [m.get("caption", "") for m in ig(f"me/media?fields=caption,timestamp&limit={n}").get("data", [])]


def series(cat):
    nums = [int(x) for c in captions(100) for x in re.findall(rf"{cat} #(\d+)", c)]
    return max(nums, default=0) + 1


def publish(out):
    out = Path(out)
    man = json.loads((out / "manifest.json").read_text())
    tag = out.name
    kids = []
    for f in man["media"]:
        url = cld_upload(str(out / f), f"posts/{tag}/{Path(f).stem}")
        d = {"is_carousel_item": "true"}
        d.update({"media_type": "VIDEO", "video_url": url} if f.endswith(".mp4") else {"image_url": url})
        kids.append(ig(f"{UID}/media", d)["id"])
        print("item", f, kids[-1], flush=True)
    for k in kids:
        wait(k)
    car = ig(f"{UID}/media", {"media_type": "CAROUSEL", "children": ",".join(kids), "caption": man["caption"]})["id"]
    wait(car)
    pid = ig(f"{UID}/media_publish", {"creation_id": car})["id"]
    print("published", pid, ig(f"{pid}?fields=permalink").get("permalink"))


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "series":
        print(series(sys.argv[2].upper()))
    elif cmd == "recent":
        print("\n---\n".join(c[:200] for c in captions(20)))
    elif cmd == "publish":
        publish(sys.argv[2])
