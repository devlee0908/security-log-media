import json,subprocess,urllib.request,pathlib
K=open('/root/.secrets/fish_key').read().strip();V=open('/root/.secrets/fish_reel_voice_id').read().strip()
# (tts text, caption, gap after)
U=[("이런 문자 오면 누르지 마세요. 항공권 예약한 적 있다면, 특히요.","이런 문자 오면 누르지 마세요.\n항공권 예약한 적 있다면 특히요.",0.4),
("항공사랑 여행사가 같이 쓰는 예약 시스템, 아마데우스가 뚫렸거든요.","항공사·여행사가 같이 쓰는 예약 시스템\n'아마데우스'가 뚫렸거든요.",0.3),
("도용된 계정으로 몇 년에 걸쳐 들어온 것으로 추정되는데요,","도용된 계정으로 몇 년에 걸쳐\n들어온 것으로 추정되는데요,",0.12),
("엔에이치농협여행은, 고객 예약번호가 샜을 수 있다고 공지했어요.","NH농협여행은 고객 예약번호가\n샜을 수 있다고 공지했어요.",0.4),
("그런데 예약번호랑 이름만 있으면,","그런데 예약번호랑 이름만 있으면",0.1),
("내 여행 일정을 다 볼 수 있어요.","내 여행 일정을 다 볼 수 있어요.",0.12),
("그래서 진짜 같은 사칭 문자가 오는 거죠.","그래서 진짜 같은\n사칭 문자가 오는 거죠.",0.4),
("결항이나 환불 문자는, 링크 대신 항공사 앱에서 확인하고요,","① 결항·환불 문자는\n링크 대신 항공사 앱에서 확인",0.12),
("내 예약의 연락처가 바뀌지 않았는지 보고,","② 내 예약 연락처가\n바뀌지 않았는지 확인",0.12),
("항공사 비밀번호도 바꿔 두세요.","③ 항공사 비밀번호 변경",0.4),
("여행 앞둔 친구한테, 이 영상 보내 주세요.","여행 앞둔 친구한테\n이 영상 보내 주세요.",0.7)]
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
