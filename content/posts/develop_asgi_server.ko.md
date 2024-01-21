---
title: "ASGI 서버 개발기 1 - 프로젝트 시작하기"
summary: "ASGI HTTP/Websocket 서버를 직접 개발해보는 기록"
date: 2024-01-21T15:53:05+09:00
draft: false
tags: ["python", "ASGI", "Rust", "HTTP"]
---
## 개요
이 글은 프로젝트 ADR에 추가적인 정보를 담아 작성되었습니다.

## 이걸 왜 만드나요..??

기존의 ASGI 서버로는 순수 python으로 된 [hypercorn](https://github.com/pgjones/hypercorn), django와 함께 관리되는 [daphne](https://github.com/django/daphne)도 있고, 퍼포먼스를 위해서라면 핵심부가 c로 개발된 [uvicorn(httptools)](https://github.com/encode/uvicorn)도 있습니다. 잘 알려지진 않았지만 rust로 개발된 [granian](https://github.com/emmett-framework/granian)도 있습니다. 즉, 표준만 있고 구현체가 없는 상황에서 선두를 치기 위한 것은 아닙니다.

제가 이 프로젝트를 진행하는 이유는 우선  Python Backend에서 끝을 보고 싶은 게 첫 번째입니다. 2년간 Python Backend로 일하면서 최종 사용자 애플리케이션 개발을 해 왔습니다. 개인적으로 프레임워크도 개발해 봤고요(사실 이건 중단해서 애매한 부분이 있습니다.). 그렇다면, 끝을 보자는 느낌으로 남은 프레임워크 하부 ASGI 서버를 개발해보자는 생각이 들었습니다.

엄밀히 말하자면 프레임워크 하부를 개발한다고 해서 끝인 것은 아닙니다. 공부의 길은 끝이 없기에 최종 애플리케이션 개발이나 프레임워크 개발을 더 해볼 수도 있었습니다. 그렇지만 이 프레임워크 하부에 관한 지식이 저에게 비어 있는 것처럼 느껴졌고, 여기를 채우고 싶다는 마음이 먼저 들었습니다.

두 번째는 Rust에 관한 개인적인 흥미입니다. 요즘 뜨는 언어라는 Rust에 관심이 있었고, Rust로 프로젝트를 해보자고 생각하고 있었습니다. 마침 좋은 기회를 얻어 Rust 강의를 들을 수 있는 기회가 있었고, 강의랑 병행하면서 복습 겸 해서 뭘 만들어볼까 고민하다가 ASGI 서버를 만들기로 선택했습니다. 
프로젝트의 임시 이름은 rust + uvicorn으로 ruvicorn이라고 임시로 지었습니다. 아무래도 기존 프로젝트에서 대충 따다 지은 이름이기 때문에 정식 이름은 따로 지을 예정입니다. 


## 의사결정기록 - 왜 이렇게 했나?
### 최종 목표 및 방향성
현재 프로젝트의 최종 목표은 python asyncio 생태계와 완전 호환되는 선에서 최고성능을 내는 HTTP/1.1, HTTP/2, HTTP/3 ASGI 서버를 목표로 하고 있습니다. uvicorn과 비슷하거나 그 이상의 퍼포먼스를 내는 매우 크고 방대한 목표이지만, 꿈은 일단 크게 잡는 게 좋다고 생각합니다. 

완전 호환성을 위해서 Python asyncio 로우 레벨 인터페이스인 Protocol과 Transport만을 활용할 예정입니다. 사실 ASGI 스펙은 하부 네트워크 계층에 대해서는 어떤 표준도 정의하지 않고 있고, 실제로 소스 코드를 살펴 보면 daphne나 granaian의 네트워크 계층은 Protocol과 Transport와 무관합니다. 

### 프로젝트 구조 및 기술 스택
#### 구조
프로젝트 구조 실제 ASGI 서버 Protocol을 작성하는 core와, core를 래핑하고 설정 읽고 주입해 실행하기, 핫 리로딩 등을 담당할 asgi 두 개의 프로젝트 모노레포로 구성했습니다. 초기의 작은 프로젝트이므로 멀티레포는 고려하지 않았습니다. 단일 프로젝트에 아래에서 Python과 Rust 소스 코드를 동시에 관리하는 경우도 많지만 저는 역할 분리가 좀 더 명확한 게 좋아서 이 방식을 택했습니다. 다만, 진행하면서 두 프로젝트를 하나로 병합하는 것을 배제하진 않을 예정입니다.
#### 도구
저는 pytest와 poetry 사용자이기 때문에 기본적으로 이 둘을 사용합니다. core의 경우 Rust를 위한 빌드 백엔드가 별도로 필요합니다. 이 Rust용 빌드 백엔드와 바인딩은 maturin과 pyo3를 선택했습니다. maturin과 pyo3는 pydantic-core, ruff에서 사용하고 있고 star수도 많고 현재 Rust의 Python 바인딩의 표준 같은 위치에 있어 선택했습니다. 
#### 라이브러리
http 파싱/디코딩 관련해서는 [httparse](https://github.com/seanmonstar/httparse)를 선택했습니다. [rust hyper](https://github.com/hyperium/hyper)와 많이 고민했던 부분인데, HTTP/2도 목표에 포함되어 있기는 하지만 당장은 HTTP/1이 구현 목표인 점, 기본적으로 rust hyper와 python Protocol 간의 연결이 매끄럽지 못한 점(더 파악해봐야 정확하겠지만 Hyper가 직접 소켓 IO를 처리해서 IO 트레이트를 제공해야 합니다. Protocol은 데이터를 콜백 메서드로 받는 방식이라 이 부분이 달라 매끄럽지 못하다.), 사실 rust hyper도 내부적으로 httparse를 활용하는 점, [actix](https://github.com/actix/actix-web)에서 http1은 httparse를 쓰고 2는 hyper를 사용하는 점을 고려했습니다. 

### 현재 목표
현재는 최소 실행 가능한 구성을 초점에 두고 개발하고 있습니다. HTTP/1.1을 SSL과 병렬 실행 없이 서빙하는 것이 첫 목표입니다. SSL은 앞에 리버스 프록시가 해결해줄 수 있는 부분이고, 병렬 실행은 컨테이너가 해결해 줄 수 있습니다.

## 참고 자료
[actix](https://github.com/actix/actix-web), [hypercorn](https://github.com/pgjones/hypercorn), [h11](https://github.com/python-hyper/h11) 구현을 주로 레퍼런스로 삼아 개발하고 있습니다. 전반적인 디자인은 Python ASGI인 hypercorn을 참조하고 있고, rust를 활용하는 부분은 actix와 hyper의 코드를 공부하면서 내 생각을 접목시켜 작성하고 있습니다. 

## 마무리
프로젝트는 [여기](https://github.com/maintain0404/ruvicorn-asgi)서 개발되고 있습니다. 관심 있으신 분들은 이슈나 PR 주시면 감사하겠습니다.