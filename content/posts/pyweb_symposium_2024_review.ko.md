---
title: PyWeb Symposium 2024 다녀온 후기
summary: Python Web Symposium 2024를 다녀오고 셰션 후기를 정리해봅니다.
date: 2024-04-08T21:09:00+09:00
draft: false
tags:
  - python
  - PyWebSymposium2024
showToc: true
---
## 개요
얼마 전 [한국마이크로소프트](https://pyweb.python.or.kr/)에서 진행된 PyWeb Symposium 2024에 갔다온 후기를 공유합니다. 이른 티켓 매진으로 가지 못했던 분들, 그냥 다른 후기가 궁금하신 분들이 읽으면 좋을 것 같습니다.

## 세션별 후기
### Django-Hipstack
개인적으로 가장 재밌게 봤습니다. 궁금하긴 한데 적용해보진 않은 라이브러리 대신 써보고 후기를 공유하는 세션이라 더더욱 그랬던 것 같네요. 
1. async
	- 발표자 분이 asyncio를 적용해본 후기를 공유해주셨습니다. 발표자분이 여기저기 async를 다 시도해보셔서 이런 저런 얘기를 해주셨지만, 결론은 `sync_to_async`, `async_to_sync`를 도배하는 것이 결론이었습니다. 개인 경험으로도 그렇고, 아직 async Django를 전체적으로 도입하는 것은 여러모로 권장되지 않는 것 같습니다.
2. HTMX
	- 이미 써보고 있는 관점에서 흥미롭게 보았습니다. 발표자 분은 첫 페이지만 렌더링하고 이후 변경은 Trigger를 주로 사용하는 전략을 사용하신 점이 인상 깊었습니다. 
	- 저는 out-of-band 전략을 주로 사용하고 있는데, 끝나고 발표자 분께 추가 질문을 드리면서 이야기해보니까 Trigger 전략이 상당히 괜찮아 보였습니다. Frontend 라이브러리의 함수를 Trigger로 호출하면서 기존 생태계를 활용하기 편한 부분이 매력적이었습니다. 
3. Ninja, django-ninja-extra
	- Ninja는 view를 FastAPI 스타일로 작성하게 해주는 라이브러리입니다. 테스트에서 request 객체 모킹을 안해도 되어서 굉장히 편리해졌다고 말씀해주셨습니다. FastAPI식 스타일이 제게 익숙하기도 하고 타입 힌트를 통해 IDE 지원을 굉장히 많이 받을 수 있어서 좋아보입니다. 하지만 Django REST가 제공하는 쓰로틀링 같은 부가 기능이나 써드파티 통합이 없는 부분은 아쉽습니다.
4. dependency-injector
	- 이건 ASGI django에서 django 개발자의 오랜 친구 에러 페이지가 렌더링되지 않아서 사용하지 않게 되었다고 하셨습니다.
	- 여담으로 이 라이브러리는 제가 쓰면서 작성한 [PR](https://github.com/ets-labs/python-dependency-injector/pull/721)을 올려놓은 게 있는데, 그 즈음부터 쭉 유지보수가 중단되었습니다. Cython으로 작성되어 퍼포먼스가 좋고, 다양한 케이스가 풍부한 게 장점이었는데, 여러모로 아쉽습니다.
	- 대체 라이브러리로는 injector가 유력한데, 저는 dependency-injector가 개인적으로 더 좋아서 메인테이너가 유지보수를 다시 시작하거나 커뮤니티로 프로젝트가 빠르게 이관되었으면 좋겠네요.
### 정답은 없지만 오답은 있답니다.
Python 원로분이신 발표자 분께서(나중에 패널 토크도 하셨습니다) 진행한 유일한 커리어 세션입니다. 평소에 고민하던 부분이 많고 공감되는 부분도 많아서 재미있게 들었습니다.
1. 기술적 우위란 없다, 네 생각을 믿어라
   1. 평소에도 생각하고 있던 부분이었습니다. 아무리 권위 높은 사람의 말이라고 한들, 스스로 고민하고 내린 결론이 더 가치 있습니다.
2. 비용에 신경써라.
   1. 근래 가장 고민하고 있는 부분입니다. 단순히 서버 비용을 넘어서 나의 시간 비용, 팀 비용까지 함께 균형있게 고민할 필요가 있습니다.
3. 패키지
	1. django-가 붙은 패키지는 잘 쓰지 않아서 몰랐는데, 잘 터지는 문제가 있다고 하더군요. 개별 패키지는 괜찮습니다.
	2. 역시 패키지를 추가할 때는 star 수를 잘 참고해서 추가하는 것이 좋겠습니다.
4. 성능
   1. 가능하면 Python 안에서 해결하는 것이 좋다고 하셨습니다.
   2. 위의 비용 부분에 연결해서, 언어 교체는 굉장히 어려운 일입니다. 정말 언어 교체가 필요한지 잘 따져보는 것이 중요하다고 생각합니다.
   3. 데이터베이스 반정규화도 마찬가지구요. 성능에 대한 환상을 경계해야 합니다.
5. Type Hint
   1. 팀과 합의 하에 결정하라고 하십니다.
   2. 개인적으로는 mypy는 쓰지 않고, 함수/메서드 입출력은 꼭 Type Hint를 적는 것이 좋다고 생각합니다.
   3. mypy는 신경써야할 부분이 지나치게 많다고 생각합니다.
6. 레거시란 없다.
   1. 돈을 벌고 있으면 레거시가 아니라고 합니다.
   2. 프로덕트를 개발하면서 비용과 고객을 간과하고는 합니다. 우리 개발자들은 코드만큼이나 비용과 고객을 더 잘 고려할 필요가 있다고 생각해요.

### SQLAlchemy & PostgreSQL
SQLAlchemy와 PostgreSQL을 사용하면서 마주했던 문제들을 해결한 후기를 공유해주셨습니다. SQLAlchemy를 오래 사용해왔던 입장에서 알았던 것도 있고, 알았지만 잘 신경쓰지 않았던 부분도 있고, 몰랐던 부분도 있어서 흥미롭게 들었습니다. 잘 몰랐거나 신경쓰지 않았던 기억에 남는 부분만 정리하면 아래와 같습니다.
1. 풀 재활용
	1. DB에서 커넥션을 닫아도 SQLAlchemy 풀에서 탐지되지 않을 수 있음
	2. DB 연결 시간보다 recycle을 짧게 설정해 강제로 재연결하게 설정하면 위 문제가 일어나지 않음
2. tenacity
	1. 다용도로 쓸 수 있는 retry 라이브러리입니다. 상당히 괜찮아 보입니다.
3. PostgreSQL Serialization Failure
	1. 고립 수준 3단계 이상에서 생길 수 있는 문제로, 롤백/세이브포인트로 해결이 불가능하고 트랜잭션 재시도를 통해서만 해결이 가능하다고 합니다.
	2. 곰곰히 생각해보면 Serialization Failure는 다른 트랜잭션 간의 충돌 문제이므로 롤백/세이브포인트로는 해결 불가능한 것이 당연하다고 볼 수 있습니다.
	3. [공식 문서](https://www.postgresql.org/docs/current/mvcc-serialization-failure-handling.html)에도 나와있습니다.

### flask 멀티스레딩
멀티스레딩/멀티프로세싱/코루틴을 각각 사용해보고 비교해보는 내용을 공유해주셨습니다. Flask 이야기는 거의 없었네요.

### 캐시 패턴 진화사
서비스가 커지면서 커지는 부하를 감당하기 위해 캐시 코드를 점차 개선한 후기를 공유해주셨습니다. 총 5번의 진화 단계를 공유해주셨습니다.
1. 일단 붙이기
2. 레이어 정리하고 View에만 붙이기
3. 쓰기 락 걸기
4. 구 버전 유지하고, 락 중에 구 버전 응답
5. 최초 쓰기 시점에 바로 캐시 set

### Django Migration 팁
django에서는 DB에서 변경이 일어나지 않았더라도 Model field의 변경이 있으면 마이그레이션을 생성합니다. 이 마이그레이션이 불편해서 생기지 않게 하기 위해 노력한 후기를 공유해주셨습니다. 사실 이게 무시해도 별 상관없는 귀찮은 부분이라 저도 언젠가 고쳐야지 하고 딱히 건들지 않았습니다. 파일이

### API 개발 설계 먼저 구현 먼저?
후원사(Microsoft) 세션입니다. API는 일종의 계약임을 강조하며 Microsoft 프로덕트를 활용해 API spec Driven 개발 방법을 설명해주셨습니다. spec driven 개발의 필요성은 매우 공감하지만 code -> OpenAPI spec 변환과 달리 OpenAPI spec -> code 변환이 대체로 더 구리고 귀찮은 관계로 사용하지 않았습니다. 기획 단계에서 글로 스펙을 정의하고, OpenAPI 스펙은 code에서 뽑아내는 것이 일반적이었습니다. 
일반적으로 잘 알려진 HETEOAS(Hypermedia as The Engine Of Application)원칙 외에도 HAL(Hypertext Application Language)를 처음 알게되어 좋았습니다. 꼭 HAL을 준수해서 사용하지 않아도 HAL에서 사용하는 링크는 자주 썼었는데, 이게 이름과 스펙이 있는 것은 처음 알았습니다. 

## 패널토크 후기
Python 심포지움이지만 Java/Kotlin Spring 이야기가 30%는 차지했던 것 같습니다. 패널 세 분 중 두 분은 현재 Spring을 주로 사용하는 상황이었던 것 같았습니다. 규모가 커지면서 관례처럼 Spring으로 갈아탄 회사가 너무 많고, 그만큼 국내 점유율이 압도적인지라 어쩔 수 없는 부분이 있습니다. 특히 Spring의 Enterprise 특화되었다는 이야기에 대한 소소한 불만을 성토하는 시간이 있었습니다. 
Enterprise 특화 이야기가 나오는 것에 관해서는 Spring 특유의 strict한 부분과 DI가 크다고 생각해서 질문 드렸었는데 해외의 예를 들면서 Enterprise 특화는 과장된 것이고 Python도 Enterprise 레벨에서 충분히 활용가능하다고 답변주셨습니다. 이 부분은 행사가 끝나고 행사를 주최해주신 배권한 님과 따로 이야기를 나눌 기회가 있었는데, DI는 알아야할 부분이 많고 잘 써야 해서 능사는 아니라는 이야기를 해주셨습니다. 예전에 [Dependency Injector](https://python-dependency-injector.ets-labs.org/)를 사용하다가 Cython 구현 부분에서 원인 불명의 에러를 만났던 기억이 나면서 지나치게 DI를 고평가하지 않았나 되돌아보게 되는 계기가 되었습니다. 매우 유익한 대화였습니다.

## 전반적인 후기
최근의 PyCon은 ML/DL의 비중이 커지는 추세에서 웹 개발에 집중된 부분을 따로 들을 수 있다는 게 좋았습니다. ML/DL 세션은 이론적인 부분이 차지하는 부분이 상당해서 제 입장에서 듣기 어려운 부분이 좀 있어 아쉬움이 컸습니다. 주최측에서 이번 행사가 굉장히 빠르게 매진되었다고 하셨는데, 이런 아쉬움이 있는 개발자 분들이 많았던 것 같습니다. 더 멋들어질 다음 행사가 기대되네요.
## 참조
- [PyWeb Symposium 2024](https://pyweb.python.or.kr/)
- [HTMX](https://htmx.org/)
- [Django5 release Note](https://docs.djangoproject.com/en/5.0/releases/5.0/)
- [Django GeneratedField](https://docs.djangoproject.com/en/5.0/ref/models/fields/#django.db.models.GeneratedField)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Django ninja](https://django-ninja.dev/)
- [python-dependency-injector](https://python-dependency-injector.ets-labs.org/)
- [HETEOAS](https://en.wikipedia.org/wiki/HATEOAS)
- [HAL](https://en.wikipedia.org/wiki/Hypertext_Application_Language)