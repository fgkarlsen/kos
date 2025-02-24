# 배포파일
qot_dist.tar
[
    lib : libmd_uninfo_api.so / libmd_uninfo_task.so
    bin : krecv / kproc / rmem / kmem / kmon / ksend / ktestrecv / rpc_svr / api_tst / memory_manager / memory_util
    master file : 20250224_ksp_master.dat / 20250224_ksq_master.dat / 20250224_nxt_master.dat
]

# 파일 복사 작업
** 대상 : SOR 엔진
0. 기존 통합시세 라이브러리 백업
mv ~/eng/lib/libmd_uninfo_api.so ~/eng/lib/libmd_uninfo_api.so.20250224

1. 라이브러리 복사
대상파일 : libmd_uninfo_api.so
복사위치 : ~/eng/lib

** 대상 : 통합시세
0. 기존 디렉토리 백업
/ksor/qot/ 디렉토리를 /ksor/old/qot/qot_20250224/ 로 Copy

1. 라이브러리 복사
대상파일 : libmd_uninfo_api.so / libmd_uninfo_task.so
복사위치 : ~/qot/lib

2. 실행파일 복사
대상파일 : krecv / kproc / rmem / kmem / kmon / ksend / ktestrecv / rpc_svr / api_tst / memory_manager / memory_util
복사위치 : ~/qot/bin

3. 마스터파일 복사
대상파일 : 20250224*.dat
복사위치 : ~/qot/data/market

# 반영방법
1. 원장 : 원장프로세스 다운 후 라이브러리 교체 후 재기동
2. 통합시세
2.1. 통합시세 프로세스 다운
2.2. 메모리 작업
2.2.1. 메모리 확인 - kmem list 
2.2.2. 메모리 삭제 - kmem remove
2.2.3. 메모리 생성 - kmem create
2.2.4. 메모리 확인 - kmem list
3. 통합시세 프로세스 기동
4. 메모리 초기화 확인 : memory_manager -> 1 -> 1 로 확인 (초기화된것 카운트 0)
5. 종목파일을 메모리로 로드
5.1. ~/qot/cmd/input_file.sh ~/qot/data/market/20250224_ksp_master.dat
5.2. ~/qot/cmd/input_file.sh ~/qot/data/market/20250224_ksq_master.dat
5.3. ~/qot/cmd/input_file.sh ~/qot/data/market/20250224_nxt_master.dat
6. 종목정보 확인 : memory_manager -> 1 -> 1 로 확인 (종목 수신 카운트 확인)
7. 시세수신 확인
7.1. 전문별 수신 확인 : memory_manager -> 3 -> 1
7.2. 포트별 수신 확인 : memory_manager -> 3 -> 2