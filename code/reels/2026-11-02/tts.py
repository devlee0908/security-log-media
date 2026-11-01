import json,subprocess,urllib.request,pathlib
K=open('/root/.secrets/fish_key').read().strip();V=open('/root/.secrets/fish_reel_voice_id').read().strip()
# (tts text, caption, gap after)
U=[("신분증이 털려도, 내 이름으로 대출 못 받게 막는 방법이 있어요.","신분증이 털려도\n내 이름으로 대출 못 받게 막는 법",0.4),
("첫째, 여신거래 안심차단.","① 여신거래 안심차단",0.15),
("내 이름으로 된 대출이랑 카드 발급을, 미리 막아 주는데요.","내 이름으로 된 대출·카드 발급을\n미리 막아 주는데요.",0.12),
("거래 은행 창구에서 신청하면 돼요.","거래 은행 창구에서\n신청하면 돼요.",0.4),
("둘째, 비대면 계좌개설 안심차단.","② 비대면 계좌개설 안심차단",0.15),
("은행 앱이나 어카운트인포 앱에서, 바로 켤 수 있어요.","은행 앱이나 어카운트인포 앱에서\n바로 켤 수 있어요.",0.4),
("제일 좋은 점은요,","제일 좋은 점은요,",0.1),
("풀 때는 꼭, 본인이 창구에 가야 한다는 거예요.","풀 때는 꼭\n본인이 창구에 가야 한다는 거예요.",0.12),
("그래서 사기범이 몰래 못 풀거든요.","그래서 사기범이\n몰래 못 풀거든요.",0.35),
("신용점수에도 영향 없고요.","신용점수에도 영향 없고요.",0.35),
("부모님은 가족이 대신 신청할 수도 있어요.","부모님은 가족이\n대신 신청할 수도 있어요.",0.12),
("이 영상, 꼭 보내 드리세요.","이 영상,\n꼭 보내 드리세요.",0.7)]
caps=[];t=0;parts=[]
for i,(tt,cap,gap) in enumerate(U):
    f=pathlib.Path(f'u{i:02d}.wav')
    if not f.exists():
        req=urllib.request.Request('https://api.fish.audio/v1/tts',json.dumps({"text":tt,"reference_id":V,"format":"wav"}).encode(),{"Authorization":"Bearer "+K,"model":"s2.1-pro-free","Content-Type":"application/json"})
        f.write_bytes(urllib.request.urlopen(req,timeout=120).read())
    # trim leading/trailing silence
    subprocess.run(['ffmpeg','-y','-loglevel','error','-i',str(f),'-af','silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,aresample=44100','-ac','1',f't{i:02d}.wav'],check=True)
    d=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f't{i:02d}.wav']))
    caps.append({"t0":round(t,2),"t1":round(t+d,2),"text":cap});t+=d+gap
    subprocess.run(['ffmpeg','-y','-loglevel','error','-f','lavfi','-i',f'anullsrc=r=44100:cl=mono','-t',str(gap),f'g{i:02d}.wav'],check=True)
    parts+= [f't{i:02d}.wav',f'g{i:02d}.wav']
open('list.txt','w').write(''.join(f"file '{p}'\n" for p in parts))
subprocess.run(['ffmpeg','-y','-loglevel','error','-f','concat','-safe','0','-i','list.txt','-af','loudnorm=I=-14:TP=-1.5','-ar','44100','voice.wav'],check=True)
json.dump(caps,open('caps.json','w'),ensure_ascii=False,indent=0)
for c in caps:print(c['t0'],c['t1'],c['text'].replace('\n',' / '))
print('total',round(t,2))
