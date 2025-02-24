# 배포파일
eng_dist.tar
[
    lib : libkSor.so
    include : api_gate.h / kSORlib.h / SORDef.h
]

# 파일 복사 작업
** 대상 : SOR 엔진
1. 엔진 관련 프로세스 다운

2. 기존 파일 백업
mv ~/eng/lib/libkSor.so ~/eng/lib/libkSor.so.20250224
mv ~/eng/include/api_gate.h ~/eng/include/api_gate.h.20250224
mv ~/eng/include/kSORlib.h ~/eng/include/kSORlib.h.20250224
mv ~/eng/include/SORDef.h ~/eng/include/SORDef.h.20250224

3. 라이브러리 복사
대상파일 : libkSor.so
복사위치 : ~/eng/lib

4. 헤더파일 복사
대상파일 : api_gate.h / kSORlib.h / SORDef.h
복사위치 : ~/eng/include

5. 엔진 관련 프로세스 기동