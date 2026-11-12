import json,subprocess,urllib.request,pathlib
K=open('/root/.secrets/fish_key').read().strip();V=open('/root/.secrets/fish_reel_voice_id').read().strip()
# (tts text, caption, gap after)
U=[("링크 안 눌렀는데, 폰이 털렸다고요?","링크 안 눌렀는데\n폰이 털렸다고요?",0.3),
("정치인이나 기자를 노리던 스파이웨어가, 이제 평범한 사람을 노려요.","기자·정치인 노리던 스파이웨어,\n이제 평범한 사람을 노려요.",0.3),
("감염된 사이트에 들어가기만 해도, 클릭 없이 감염돼요.","감염된 사이트에 들어가기만 해도\n클릭 없이 감염돼요.",0.35),
("점검한 폰 천 대 중 한 대꼴로 나왔고, 경고 알림도 없었대요.","점검한 폰 1,000대 중 1대꼴로 나왔고\n경고 알림도 없었대요.",0.35),
("오래된 취약점을 노리니까, 지금 바로 최신 버전으로 업데이트하세요.","① 지금 바로\n최신 버전으로 업데이트",0.12),
("자동 업데이트도 켜 두시고요.","② 자동 업데이트 켜 두기",0.3),
("지금 내 폰, 최신 버전인가요? 확인하고 댓글로 알려 주세요.","지금 내 폰, 최신 버전인가요?\n확인하고 댓글로 알려 주세요 👇",0.7)]
caps=[];t=0;parts=[]
for i,(tt,cap,gap) in enumerate(U):
    f=pathlib.Path(f'u{i:02d}.wav')
    if not f.exists():
        req=urllib.request.Request('https://api.fish.audio/v1/tts',json.dumps({"text":tt,"reference_id":V,"format":"wav"}).encode(),{"Authorization":"Bearer "+K,"model":"s2.1-pro-free","Content-Type":"application/json"})
        f.write_bytes(urllib.request.urlopen(req,timeout=120).read())
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
