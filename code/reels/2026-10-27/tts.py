import json,subprocess,urllib.request,pathlib
K=open('/root/.secrets/fish_key').read().strip();V=open('/root/.secrets/fish_reel_voice_id').read().strip()
# (tts text, caption, gap after)
U=[("'개인정보 유출, 보상해 드릴게요.'","'개인정보 유출,\n보상해 드릴게요.'",0.15),
("이런 연락 오면, 바로 끊으셔야 합니다.","이런 연락 오면\n바로 끊으셔야 합니다.",0.35),
("은행에 이어, 이번엔 보험사까지 뚫렸거든요.","은행에 이어\n이번엔 보험사까지 뚫렸거든요.",0.15),
("국민은행은 피해자가, 처음 발표보다 십팔 배로 늘었고요.","국민은행은 피해자가\n처음 발표보다 18배로 늘었고요.",0.3),
("그런데 진짜 위험은, 지금부터인데요.","그런데 진짜 위험은\n지금부터인데요.",0.15),
("이 소식을 미끼로 한, 사칭 연락이요.","이 소식을 미끼로 한\n사칭 연락이요.",0.15),
("경찰도 사천팔백만 명에게, 경고 문자를 보내기로 했죠.","경찰도 4,800만 명에게\n경고 문자를 보내기로 했죠.",0.3),
("기억할 건 딱 세 가지예요.","기억할 건 딱 세 가지예요.",0.15),
("보상이나 계좌 보호 연락은, 끊고 대표번호로 직접 확인하기.","보상·계좌 보호 연락은 끊고\n대표번호로 직접 확인하기.",0.2),
("문자 속 링크나 앱 설치는, 절대 금지.","문자 속 링크나 앱 설치는\n절대 금지.",0.2),
("의심되면 일삼구사로 신고하세요.","의심되면 1394로\n신고하세요.",0.3),
("이 영상, 부모님께 꼭 보내 드리세요.","이 영상,\n부모님께 꼭 보내 드리세요.",0.6)]
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
