import json, os, re, subprocess, sys, unicodedata, tempfile
repo = sys.argv[1]
html = open(os.path.join(repo, 'index.html'), encoding='utf-8').read()
m = re.search(r'const DATA = (\[.*?\]);\n', html, re.S)
data = json.loads(m.group(1))
def strip(s): return ''.join(ch for ch in unicodedata.normalize('NFD', s) if unicodedata.category(ch) != 'Mn')
def fmt_pop(n):
    if n >= 1e9: return re.sub(r'0$', '', f"{n/1e9:.2f}") + " billion"
    if n >= 1e6:
        v = f"{n/1e6:.0f}" if n >= 1e8 else f"{n/1e6:.1f}"
        return re.sub(r'\.0$', '', v) + " million"
    return f"{n:,}"
out = os.path.join(repo, 'audio'); os.makedirs(out, exist_ok=True)
def render(text, path):
    with tempfile.NamedTemporaryFile('w', suffix='.txt', delete=False) as f:
        f.write(strip(text)); tf = f.name
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-f', 'lavfi', '-i', f"flite=textfile={tf}:voice=slt",
                    '-af', 'atempo=0.95', '-ac', '1', '-ar', '22050', '-c:a', 'libmp3lame', '-b:a', '40k', path], check=True)
    os.unlink(tf)
for c in data:
    parts = [c['n'] + '.']
    if c['cap']: parts.append(f"The capital is {c['cap']}.")
    if c['pop']: parts.append(f"About {fmt_pop(c['pop'])} people live here.")
    parts.append(f"It is in {c['sub'] or c['reg']}.")
    if c['lang']: parts.append(f"People speak {', '.join(c['lang'][:3])}.")
    if c['fact']: parts.append(c['fact'])
    render(' '.join(parts), os.path.join(out, c['id'] + '.mp3'))
render("Perfect score! You're a flag champion.", os.path.join(out, 'perfect.mp3'))
print(len(data))
