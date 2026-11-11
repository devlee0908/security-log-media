import json,subprocess,urllib.request,pathlib
K=open('/root/.secrets/fish_key').read().strip();V=open('/root/.secrets/fish_reel_voice_id').read().strip()
# (tts text, caption, gap after)
U=[("내 이름 알고 전화 왔다면, 그래서 더 의심하세요.","내 이름 알고 전화 왔다면\n그래서 더 의심하세요.",0.3),
("제 이름까지 부르면서, 우체국인데 소송 서류가 왔대요. 진짜 같죠?","내 이름 부르며 '우체국인데\n소송 서류 왔어요' 진짜 같죠?",0.3),
("털린 정보를 모아서, 나한테 딱 맞춘 사기를 치는 거예요.","털린 정보를 모아서\n나한테 딱 맞춘 사기를 치는 거예요.",0.35),
("실제로 골프존 유출 팔 일 뒤엔, 피해자 명의로 폰이 개통되고 일억 팔천이 빠져나갔는데요,","골프존 유출 8일 뒤, 피해자 명의 폰 개통\n1억 8천만 원이 빠져나갔는데요,",0.12),
("유출 통보는, 그보다 늦게 왔어요.","유출 통보는 그보다 늦게 왔어요.",0.35),
("기관이 개인 번호로 연락하면, 끊고 공식 번호로 다시 거세요.","① 기관이 개인 번호로 연락하면\n끊고 공식 번호로 다시",0.12),
("엠세이퍼에서 내 명의 휴대폰 개통도 조회해 보시고요.","② 엠세이퍼에서\n내 명의 휴대폰 개통 조회",0.3),
("이런 전화 받아본 적 있나요? 댓글로 알려 주세요.","이런 전화 받아본 적 있나요?\n댓글로 알려 주세요 👇",0.7)]
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
