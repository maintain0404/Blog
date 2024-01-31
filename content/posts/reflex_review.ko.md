---
title: Reflex 사용 후 느낌 점(with 간단한 팁)
summary: 새로운 풀 스택 python 프레임워크를 약 8개월간 사용해보고 느낀 점과 간단한 팁을 공유합니다.
date: 2024-01-07T23:34:26+09:00
draft: false
tags:
  - python
  - ASGI
  - Reflex
  - Frontend
showToc: true
---
## 들어가기 전에
이 글은 reflex를 사용한 경험을 공유하고, reflex 사용 시 유의해야 할 점과 팁을 공유합니다. [reflex 프레임워크](https://reflex.dev/)에 관한 지식이 있거나 사용을 고민하고 있다면 좋습니다. 이 프레임워크를 추천하는지 아닌지가 궁금하시다면 결론부터 보시면 되겠습니다.

## Reflex 후기
### 장점
#### 1. 데이터 통신을 신경쓰지 않아도 됨
Reflex의 최고 장점은 서버와 클라이언트 간 데이터 통신 관리를 신경쓰지 않아도 된다는 점입니다. 처음에는 프론트엔드를 잘 몰라도 웹개발이 가능한 점이 장점이라고 생각했었습니다. 하지만 사용하면 사용할수록 이게 정말 큰 장점입니다. API 스키마를 선언하고, 오류 케이스별로 상태 코드와 응답을 나누고 그에 따른 처리 코드를 클라이언트/서버 양쪽으로 작성할 필요가 없다 보니 코드 양이 굉장히 많이 줄어들고 테스트 코드가 같이 줄어듭니다.

#### 2. 빠른 개발속도
두번째로, 굉장히 빠르게 개발이 이루어집니다. 사실 첫 번째 장점으로 꼽은 데이터 통신 관리를 신경쓰지 않아도 되는 것은 템플릿 기반으로 HTML을 만드는 방식에게도 적용됩니다. 하지만 템플릿은 IDE의 추적이 안 됩니다. 거기에 더해 템플릿으로 혹은 유사한 매크로로 프로그래밍을 해봤을 분들이라면 다들 공감하실텐데, 특유의 난해함과 머리 속에 정확히 잘 그려지지 않는 비직관성 때문에 개발 속도가 살짝 느립니다. 반면에 reflex는 컴포넌트가 Python 코드로 작성되고 HTML/CSS 요소가 IDE의 추적을 받기 때문에 훨씬 빠르고 쾌적하게 개발할 수 있습니다.

#### 3. 프론트엔드/디자인을 잘 몰라도 됨
세 번째로, 프론트엔드와 디자인을 잘 모르더라도 그럭저럭 괜찮은 결과물을 만들어 낼 수 있습니다. 공식 문서의 튜토리얼, 레퍼런스, 샘플 코드가 잘 작성되어 있어 어렵지 않게 배우고 시작할 수 있습니다. 현재 모든 컴포넌트가 Charka-UI 기반으로 디자인이 잘 되어 있기 때문에 적당히 괜찮은 결과물이 나옵니다. 궁금하다면 [Reflex 공식 문서의 샘플](https://reflex.dev/docs/gallery/)을 참조 바랍니다.

### 단점
#### 1. 퍼포먼스
Reflex의 큰 단점으로는 퍼포먼스 문제입니다. 간단한 이벤트 처리도 서버를 경유해야 하기 네트워크로 인한 지연시간이 있고, 기본적으로 하나의 React Context로 모든 상태를 관리하기 때문에 하나의 변경에도 애플리케이션 전체의 렌더링이 일어나 눈에 띄게 느려질 수 있습니다. 이는 공식 홈페이지에서 검색창에 입력을 빠르게 지우고 입력하길 반복하면 쉽게 재현할 수 있습니다. 빠르고 쓰고 지우기를 반복하면 화면이 아무런 반응을 하지 않고 멈추며, 천천히 검색 결과창이 바뀌다가 다시 정상으로 돌아옵니다. 의도적으로 만든 상황이기는 하지만 이게 몇 초 정도 지속되는데, 사용자 입장에서 굉장히 불쾌할 수 있습니다.
#### 2. 문서와 사용성
두 번째로는 충분히 성장하지 못한 초기의 프로젝트라서 사용성이나 문서가 부실한 측면이 있습니다. 자체적으로 탑재한 UI 컴포넌트 쪽은 문서화가 괜찮게 잘 되어 있는데 반해, 이벤트나 다른 리액트 라이브러리 커스텀은 상대적으로 부실하고 사용하기 까다로운 부분이 있습니다. 조금 특수한 기능이 필요하다면 사용하기 여러모로 까다롭습니다. 사용성 부분에서도 substate를 얻는 부분(`State` 클래스가 아닌 클래스에 부여된 따로 변환해야 가져올 수 있습니다. 이건 Substate 문서 말고 다른 곳에서 찾았습니다 [링크](https://reflex.dev/docs/events/background_events/#low-level-api))이나 후술할 네이밍 등에서 아쉬운 부분이 좀 있습니다.
제 경험을 말씀드리자면, HTML요소 위에서의 상대적인 마우스 클릭 위치를 받아오려고 시도했었습니다. 마침 [깃허브 이슈](https://github.com/reflex-dev/reflex/issues/2180)에 reflex 개발팀 측에서 답변한 내용이 있었는데 제대로 작동하지 않았습니다. 긴 시간의 삽질 끝에 해결할 수 있었는데, 결과적으로 원인은 마우스 이벤트 오브젝트가 순환참조를 하고 있어 `JSON.Stringfy` 메서드가 동작하지 않았고, 따라서 마우스 이벤트도 받아올 수 없는 문제였습니다. 다행히 하위 `nativeEvent`객체에 동일한 값이 있어 [해결](https://github.com/reflex-dev/reflex/issues/2180#issuecomment-1854417862)할 수 있었습니다. 추가적으로 이 문제를 해결하기 위해 이벤트 선언에 `kemalCase`를 사용했는데, 다른 API에서는 전부 python 표준대로 snake-case로 변환해서 제공하고 있어서 이 부분도 살짝 아쉬웠습니다.

## 권장 Practice

### 1. 입력은 form을 통해서
Input을 State의 변수와 연동해서 입력을 받는 방법이 있지만, 이는 debouncer를 적용한다고 해도 찾은 리렌더링과 늦은 반응속도를 만들어낼 수 있습니다. 위의 공식 사이트 검색 기능이 대표적입니다. 가능하다면 form을 통해 제출 시 한 번에 입력하도록 하는 방법이 좋습니다.
```python
import reflex as rx

class State(rx.State):
    email: str
    phone_number: str

    def handle_submit(self, data: dict):
        ...

# Bad
def singin_with_state():
    return rx.box(
        rx.input(placeholder='email', value=State.email),
        rx.input(placeholder='phone_number', value=State.phone_number)
    )

# Good
def signin_with_form():
    return rx.box(
        rx.form(
            rx.input(name='email'),
            rx.input(name='phone_number'),
            rx.button("Submit", type_='submit'),
            on_submit=State.handle_submit
        )
    )

```

### 2. 데이터와 화면 상태 State를 분리
모두 UI 요소 이긴 하지만 데이터 State와 화면 상태 State를 분리하면 관심사 분리 원칙에 따라 여러 이점이 있습니다. 화면 상태 State의 경우 특정 알림창이 보이는지, 현재 프로세스 처리 진행 상황 등을 말합니다. 기본적으로 둘을 분리함으로써 차후에 애플리케이션이 복잡해지고 팀에 프론트엔드 개발자가 합류한다면 빠르게 프레임워크 전환이 가능한 이점을 얻을 수 있습니다. 그보다 중요한 이유는 주관적인 이유지만, 둘의 코드 성질이 조금 다릅니다. 상태 State의 경우 유즈케이스 시나리오를 따라가기 때문에 좀 더 서술적이고 스크립트에 가깝습니다. 반면에 데이터 State의 프로젝트 아키텍처를 따라갑니다. Transactional Script 패턴이라면 스크립트 성격일 것이고, 이벤트 소싱이라면 이벤트를 발행하는 코드 위주로 작성되겠죠. 경험적으로 분리하는 것이 효율성에 좀 더 도움 되었던 것 같습니다.

```python
import asyncio as aio
from dataclasses import dataclass, field
from typing import Callable

import reflex as rx

@dataclass
class LongJob:
    e: aio.Event = field(default_factory=lambda: aio.Event())
    current: int = 0

    # 긴 작업을 하면서 중간 진행상황만 이벤트로 전파
	# 작업 외의 다른 것에는 책임이 없음
    async def process(self) -> list[str]:
        ret = ["final", "processing", "data"]
        for current in [20, 40, 60, 80, 100]:
            if not self.e.is_set():
                self.e.set()
            self.current = current
            await aio.sleep(1)

        return ret

# 락을 얻고 데이터를 수정하는 콜백을 만드는 함수
def build_setter_callback(
    cls: type[rx.State],
    attrname: str,
    token: str
) -> Callable[[aio.Task], None]:
    def callback(o: aio.Task):  # 결과 데이터 반영
        async def inner():
            # app은 Reflex App 객체
            # 데이터 수정을 위한 락을 가져옴
            async with app.modify_state(token) as state:
                setattr(
                    state.get_substate(
                        cls.get_full_name().split(".")
                    ),
                    attrname,
                    o.result()
                )

        inner_task = aio.create_task(inner())
        inner_task.add_done_callback(lambda o: ...)  # 태스크 회수 위한 빈 콜백

    return callback


class DataState(rx.State):
    data: list[str] = []


class ViewState(rx.State):
    current: int = 0

    @rx.background
    async def process(self):
        # 작업을 만들고, 끝나면 결과 반영하도록 콜백 주입
        job = LongJob()
        task = aio.create_task(job.process())
        task.add_done_callback(
            build_setter_callback(
                DataState,
                "data",
                self.router.session.client_token
            )
        )

        # 현재 진행도가 업데이트 될 때마다 UI에 반영
        while not task.done():
            await job.e.wait()
            async with self:
                self.current = job.current

...  # 컴포넌트는 길이상 생략하였음
```

### 3. 템플릿/컴포넌트 함수 최대한 활용하기
컴포넌트를 작성하다보면 탭 수가 굉장히 많이 늘어나기 쉽습니다. 2스페이스 탭을 쓸 수 있는 Javasrcript나 Typscript와 달리 Python은 4탭이 강제되기 때문에 굉장히 거슬립니다. 컴포넌트 함수를 많이 쓰면 이 문제를 해결할 수 있습니다.

### 4. 기타
1. 락을 유의해야 합니다. 굉장히 기본적인 부분이라 기타에 넣었습니다. background 작업에서는 비동기 컨텍스트 매니저에 진입해야지만 데이터 수정이 가능합니다. 자칫하면 애플리케이션이 멈추는 불상사가 발생할 수도 있다는 점을 유의하면서 조심스럽게 작업해야 합니다. Background 작업 관련된 부분은 [공식 문서](https://reflex.dev/docs/advanced-guide/background-tasks/)를 반드시 꼼꼼히 읽고 숙지가 반드시 필요합니다.
2. 프로덕션 모드로 배포 시에 컴파일이 꽤 오래 걸리고 자원을 꽤 많이 잡아먹습니다. 빌드가 필요한 언어를 사용하시는 분이라면 당연할 수 있지만, python은 그렇지 않기에 추가했습니다. 따로 빌드 머신을 쓴다면 넉넉히 8gb 정도 램을 주시는 것이 좋을 것 같습니다.

### 결론 - 그래서 쓸만한가요?
저는 꽤 오래 Reflex를 개인적으로 써왔습니다. 사실 프레임워크 자체가 아직 정식 출시 전인 굉장히 초기 프로젝트 이기도 하고, 사용자가 좀 되는 프로덕션용으로 써본 것은 아니라서 말하기 조심스럽습니다. 웹 프론트엔드를 잘 모르면서 작업해야 하는 경우, 내부 서비스용으로 작업해야 하는 경우 굉장히 추천할 만하다고 생각합니다. 특히 템플릿을 사용을 고민하고 계시다면 reflex를 한 번 고민하는 것을 적극 권장드립니다.

### 수정사항
- 2024.01.30 샘플 코드 추가
- 단점 부분에 문서화 및 사용성 이야기 추가