import json,subprocess,urllib.request,pathlib
K=open('/root/.secrets/fish_key').read().strip();V=open('/root/.secrets/fish_reel_voice_id').read().strip()
# (tts text, caption, gap after)
U=[("이번 주 해킹 뉴스, 이 단어 모르면 절반만 이해한 거예요.","이번 주 해킹 뉴스,\n이 단어 모르면 절반만 이해한 거예요.",0.4),
("첫 번째, 에이피아이.","① API",0.15),
("앱이 서버랑 정보를 주고받는 통로인데요.","앱이 서버랑 정보를\n주고받는 통로인데요.",0.12),
("진에어도, 일부 금융사도, 이 통로가 뚫렸어요.","진에어도, 일부 금융사도\n이 통로가 뚫렸어요.",0.4),
("두 번째, 디알엠.","② DRM",0.15),
("파일에 자물쇠를 걸어서, 가져가도 못 열게 하는 기술이에요.","파일에 자물쇠를 걸어서\n가져가도 못 열게 하는 기술이에요.",0.12),
("빗썸 고객 오천육백 명은, 이 덕분에 노출을 피했다고 해요.","빗썸 고객 5,600명은\n이 덕분에 노출을 피했다고 해요.",0.4),
("세 번째, 명의도용.","③ 명의도용",0.15),
("내 정보로 남이 계좌를 열고, 대출까지 받는 거예요.","내 정보로 남이 계좌를 열고\n대출까지 받는 거예요.",0.12),
("신분증 사본이 새면, 제일 무서운 게 바로 이거죠.","신분증 사본이 새면\n제일 무서운 게 바로 이거죠.",0.45),
("저장해 두고, 뉴스 볼 때 꺼내 보세요.","저장해 두고\n뉴스 볼 때 꺼내 보세요.",0.7)]
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
