"""Generate a background image with the Gemini API.
Usage: python gen_image.py "<scene description>" out.png [--ratio 4:5|1:1|16:9]
Key: ~/.secrets/gemini_key   Model: env GEMINI_IMAGE_MODEL (falls back through MODELS)
Exit code 1 on failure -> caller should fall back to a code-drawn scene.
"""
import base64, json, os, sys, urllib.request, urllib.error

MODELS = [os.environ.get("GEMINI_IMAGE_MODEL"), "gemini-3.1-flash-image-preview", "gemini-3-pro-image-preview",
          "imagen-4.0-fast-generate-001", "imagen-4.0-generate-001"]
GUARD = ("Dark cinematic editorial illustration for a cybersecurity news card. Deep dark background, "
         "subtle neon accent lighting, lots of empty dark space in the lower 40% for text overlay. "
         "STRICTLY NO text, letters, numbers, logos, brand marks, flags or real human faces. Scene: ")
API = "https://generativelanguage.googleapis.com/v1beta/models/"


def call(model, prompt, ratio, key):
    if model.startswith("imagen"):
        url, body = API + model + ":predict", {"instances": [{"prompt": prompt}],
                                               "parameters": {"sampleCount": 1, "aspectRatio": ratio}}
    else:
        url, body = API + model + ":generateContent", {"contents": [{"parts": [{"text": prompt}]}],
                                                       "generationConfig": {"responseModalities": ["IMAGE"],
                                                                            "imageConfig": {"aspectRatio": ratio}}}
    req = urllib.request.Request(url, json.dumps(body).encode(), {"x-goog-api-key": key, "Content-Type": "application/json"})
    d = json.load(urllib.request.urlopen(req, timeout=120))
    if "predictions" in d:
        return base64.b64decode(d["predictions"][0]["bytesBase64Encoded"])
    for p in d["candidates"][0]["content"]["parts"]:
        if "inlineData" in p:
            return base64.b64decode(p["inlineData"]["data"])
    raise ValueError("no image in response")


def main():
    args = sys.argv[1:]
    ratio = args[args.index("--ratio") + 1] if "--ratio" in args else "4:5"
    scene, out = args[0], args[1]
    key = open(os.path.expanduser("~/.secrets/gemini_key")).read().strip()
    for m in filter(None, dict.fromkeys(MODELS)):
        try:
            open(out, "wb").write(call(m, GUARD + scene, ratio, key))
            print("ok", m, out); return
        except (urllib.error.HTTPError, urllib.error.URLError, KeyError, IndexError, ValueError) as e:
            print("fail", m, getattr(e, "code", ""), str(e)[:120], file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
