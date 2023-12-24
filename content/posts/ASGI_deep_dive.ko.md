---
title: "ASGI 깊게 살펴보기"
date: 2023-12-24T21:03:30+09:00
draft: false
summary: "ASGI 도입 배경과 프로토콜을 깊게 분석해봅니다."
tags: ["python", "ASGI"]
showToc: true
---

## 개요
이 글에서는 ASGI 도입 배경과 프로토콜을 분석해봅니다. 추가적으로 ASGI 프로토콜 서버 구현을 살펴보면서 ASGI의 필요성을 따져봅니다.
아래 지식을 가지고 있으면 이 글을 읽는 데에 도움이 됩니다.
- Python 문법(3.12 기준)
- 비동기 프로그래밍과 코루틴
- HTTP
- 기타 서버 개발 관련 지식

## WSGI를 두고 ASGI를 새로 만든 이유
WSGI(Web Server Gateway Interface)는 ASGI 이전에 사용하던 Python의 웹 서버와 웹 애플리케이션 프레임워크 간의 인터페이스입니다. 이전의 프로토콜의 버전 업그레이드가 아니라 새롭게 인터페이스를 정의한 이유는 무엇일까요?
ASGI 공식 문서에서는 다음과 같이 설명하고 있습니다.

> The WSGI specification has worked well since it was introduced, and allowed for great flexibility in Python framework and web server choice. However, its design is irrevocably tied to the HTTP-style request/response cycle, and more and more protocols that do not follow this pattern are becoming a standard part of web programming (most notably, WebSocket).
> ASGI attempts to preserve a simple application interface, while providing an abstraction that allows for data to be sent and received at any time, and from different application threads or processes.

줄이자면 기존의 WSGI는 HTTP 스타일의 요청-응답 구조에 너무 맞춰져 있어서 새로운 웹 트렌드 변화(Websocket, HTTP/2)에 대응하기 어렵다는 것입니다 한 번 WSGI 구조를 살펴보겠습니다. 아래는 WSGI 문서를 참조해서 프로토콜을 type hint로 작성한 예시입니다.

```python
from typing import *
from types import *


Environ = TypedDict("Environ", {
    "wsgi.version": tuple[Literal[1], Literal[0]],
    "wsgi.url_scheme": Literal["http", "https"],
    "wsgi.input": IO,  # Read only
    "wsgi.errors": IO,  # Write only
    "wsgi.multithread": bool,
    "wsgi.multiprocess": bool,
    "wsgi.run_once": bool,                
})


class Write(Protocol):
    def __call__(self, body_data: bytes):
        ...


class StartResponse(Protocol):
    type HeaderName = str
    type HeaderValue = str
    type ExcInfo = tuple[type[Exception], Exception, TracebackType]

    def __call__(
        self,
        status: str,
        response_headers: list[tuple[HeaderName, HeaderValue]],
        exc_info: ExcInfo | None = None
    ) -> Write:
        ...


class WsgiApp(Protocol):
    type ResponseBody = Iterable[bytes]

    def __call__(self, environ: dict, start_response: StartResponse) -> ResponseBody:
        ... # do_somthing


class WsgiMiddleware(WsgiApp):
    def __init__(self, app: WsgiApp):
        ...
```


WSGI 앱이 요청을 처리하는 과정을 살펴보면 다음과 같습니다.
1. environ['wsgi.input'] 파일류 객체로 데이터를 읽습니다.
2. 임의의 처리를 진행합니다.
3. `start_response` 함수를 호출에서 응답을 시작합니다.
4. 응답을 반환값으로 처리하거나(권장), `start_response` 가 반환한 파일류 객체로 응답을 직접 씁니다.
WSGI의 영역에서 벗어나지만 WSGI 애플리케이션으로 Websocket 요청을 처리한다고 가정해봅시다.
웹소켓은 실시간 요청, 응답이 필요합니다. 즉, WSGI 애플리케이션에서 계속 읽기와 쓰기가 필요합니다. 먼저 읽기의 경우, 지속적 대기를 위해 무한루프 안에서 반복적으로 읽는 작업이 필요할 겁니다. 쓰기의 경우 권장되지 않는 방법이지만 start_response가 반환하는 쓰기 파일류 객체가 반드시 필요합니다.코드로 간단하게 나타내본다면 아래와 같은 느낌이죠.
```python
type Metadata = str


def do_something(meta: Metadata, data: str) -> str:
    ...


def parse_data(data: str) -> tuple[Metadata, str]:
    ...


def should_finish(meta: Metadata):
    ...


def wsgi(environ: dict, start_response: StartResponse) -> Iterable[bytes]:
    readio = environ["wsgi.input"]
    writeio = start_response("200 ok", [])

    while True:
        try:
            if not (read := readio.read()):
                continue

            meta, data = parse_data(read)            
            to_send = do_something(meta, data)
            writeio.write(to_send)
            
            if should_finish(meta):
                return []
            
        except WebsocketDisconnect:
            return []

    
```

이런 구조는 다음과 같은 문제가 생깁니다.
1. WSGI 스펙과 거리가 있습니다.
        write 파일류 객체는 WSGI 표준에 포함된 사항이지만, 스펙 제안 이후에 새로 작성하는 코드에서는 사용하지 않는 것을 강력하게 권장하고 있습니다. 
1. 애플리케이션의 영역에서 다소 벗어납니다.
      이 메시지가 어떤 종류의 메시지인지 애플리케이션이 직접 파싱해서 확인해야 합니다. 기존의 HTTP에서는 단일 요청 - 단일 응답 구조이기 때문에 어떤 메시지인지 확인할 필요가 없었습니다. 하지만 변화하는 환경에서는 추가로 데이터를 보낼지(websocket, 스트리밍), 연결이 끊어졌는지 등 추가로 확인해야 할 정보가 새로 생겼습니다. 게다가 이 정보들을 어떻게 `.read()` 에 어떻게 전달할지는 표준에 없기 때문에 애플리케이션 ASGI 서버별로 다른 구현을 하게 만듧니다.
이 외에도 클라이언트의 다음 데이터가 올 때까지 블록될 수 있는 문제와 그로 기인하는 자원 비효율성 문제가 있습니다. 그렇다면 ASGI는 이 문제를 어떻게 해결했을까요?

## ASGI가 문제를 해결한 방법
먼저 ASGI의 구조부터 살펴보겠습니다. ASGI는 크게 프로토콜 서버와 애플리케이션 두 가지로 구성되어 있습니다. 애플리케이션은 특정 파라미터 스펙(아래 AsgiApp 클래스 참조)를 가지는 Callable로 비즈니스 로직을 처리합니다. 서버는 애플리케이션이 하지 않는 모든 일을 처리합니다. 전체적인 구조는 WSGI와 동일하게 프로토콜 서버가 요청을 받으면 애플리케이션을 실행시키는 구조로 동작합니다. 
```python
from typing import *


class AsgiSpec(TypedDict):
    version: str,
    # If missing, assume 2.0                                 
    spec_version: Literal["2.0", "2.1", "2.2", "2.3"] | None


class Scope(TypedDict):
    type: str
    asgi: AsgiSpec


class Receive(Protocol):
    class ReceiveEvent(TypedDict):
        type: str
        # Different by event type

    async def __call__(self) -> ReceiveEvent:
        ...


class Send(Protocol):
    class SendEvent(TypedDict):
        type: str
        # Different by event type

    async def __call__(self) -> SendEvent:
        ...


class AsgiApp(Protocol):
    async def __call__(self, scope: Scope, receive: Receive, send: Send): 
        ...

```

일단 가장 큰 변경점은 ASGI의 목적대로 응답 - 요청의 단순한 1회성 라이프사이클이 아니라 유동적인 라이프사이클이 구현되었습니다. `scope`를 통해 연결 전체 정보를 얻고, `receive`와 `send`를 유동적으로 호출함으로서 언제, 몇 번, 데이터를 주고 받는지 애플리케이션이 간단한 API를 통해 자율적으로 조절할 수 있게 되었습니다. 이 구조는 통신의 기본적인 구조로 어디든 사용할 수 있습니다. 그래서 비록 표준에는 HTTP와 Websocket만 포함되어 있지만 다른 방식에도 쉽게 확장할 수 있습니다. HTTP가 아닌 AWS Lambda와의 인터페이스인 [Magnum](https://mangum.io/)이 대표적입니다. ASGI의 확장을 목표로 하는 [Django Channels](https://channels.readthedocs.io/en/stable/introduction.html#routing-and-multiple-protocols) 프로젝트도 있습니다. 

두 번째로는 async/await 문법과 코루틴의 사용입니다. 코루틴을 사용하면 클라이언트의 다음 데이터가 올 때만 실행되어 다음 데이터가 올 때까지 블록되는 문제를 해결할 수 있습니다. 좀 더 구체적인 설명은 이 글의 영역에서 벗어나므로 정확한 이유가 궁금하다면 python 이벤트 루프를 검색해보시기 바랍니다. 이 문제는 엄밀하게는 greenlet, tornado, twisted에서 async/await 없이 해결한 바가 있습니다만, 표준으로 들어왔다는 점에서 의미가 크죠. 

그 외로는 `.` 이 들어간 `dict` 키가 없다는 점이 눈에 띕니다. `TypedDict` 와 함께 사용하기 편하게 하기 위해 의도적으로 고려되지 않았나하고 조심스레 추측해봅니다.

## ASGI 서버 살펴보기
마지막으로 ASGI 서버 구현을 살펴보면서 ASGI가 필요한 이유를 한 번 더 살펴보겠습니다.
### 살펴보기 전에
ASGI 서버는 여러 종류가 있습니다. [Hypercorn](https://github.com/pgjones/hypercorn), [Uvicorn](https://github.com/encode/uvicorn), [Daphne](https://github.com/django/daphne)가 대표적입니다. AWS Lambda를 대상으로 한 `Magnum`도 있습니다. 이 글에서는 pure-python으로 작성된 Hypercorn에서 가장 간단한 프로토콜인 HTTP1.1을 살펴보겠습니다. 전체적인 흐름은 아래와 같습니다. 참조 코드는 너무 많은 관계로 일부만 가져왔습니다. 
> `asyncio.start_server` -> 연결을 처리할 Server 객체를 넘김 
>    `Server.__await__()` ->   
>        `Protocol.initiate()` -> 연결 초기화  
>        `server._start_idle()` -> 타임아웃 설정  
>        `server._read_data()` -> 읽은 데이터를 Protocol에 넘기거나, 종료를 알림  
>            `ProtocolWrapper.handler()` -> Protocol.handle 호출  
>            `Protocol.handle()` -> Connection 유한 상태 기계에 `_handle_events`를 호출해 처리하거나 종료.  
>                `Protocol._handle_events()` -> 파싱 결과에 따라서 오류 응답을 보내거나 애플리케이션 실행  

1. 서버를 시작하면서 응답 콜백을 넘깁니다.
    
```python
# https://github.com/pgjones/hypercorn/blob/33ed00670894b29ec00f4341a4ec5100e3ade747/src/hypercorn/asyncio/run.py
...

def worker_serve():
    ...
    def _server_callback(
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter
    ):
        nonlocal server_tasks

        task = asyncio.current_task(loop)
        # 포스팅에 있는 코드에는 없는 내용이지만
        # 서버 종료 시 처리중인 요청을 전부 처리하고
        # 안정적인 종료를 위해 수집됩니다.
        server_tasks.add(task)
        task.add_done_callback(server_tasks.discard)
        await TCPServer(app, loop, config, context, reader, writer)


    ...
    servers.append(
        # 요청 시 _server_callback을 실행하게 됩니다.
        await asyncio.start_server(
            _server_callback, backlog=config.backlog, sock=sock
        )
    )

...
```

2. 연결이 시작되면 타임아웃 콜백을 등록합니다.
```python
# https://github.com/pgjones/hypercorn/blob/main/src/hypercorn/asyncio/tcp_server.py#L70
# TCP Server 클래스의 메소드 일부

async def run(self) -> None:
    # 주소, SSL 정보를 세팅합니다.
    socket = self.writer.get_extra_info("socket")
    try:
        client = parse_socket_addr(socket.family, socket.getpeername())
        server = parse_socket_addr(socket.family, socket.getsockname())
        ssl_object = self.writer.get_extra_info("ssl_object")
        if ssl_object is not None:
            ssl = True
            alpn_protocol = ssl_object.selected_alpn_protocol()
        else:
            ssl = False
            alpn_protocol = "http/1.1"

        async with TaskGroup(self.loop) as task_group:
            self.protocol = ProtocolWrapper(
                self.app,  # ASGI 애플리케이션
                self.config,
                self.context,
                task_group,
                ssl,
                client,
                server,
                self.protocol_send,
                alpn_protocol,
            )
            # 프로토콜 초기화입니다. HTTP1.1의 경우 따로 무언가를 하지는 않습니다.
            await self.protocol.initiate()  
            await self._start_idle()  # 타임아웃 콜백을 등록합니다.
            await self._read_data()  # 데이터를 읽고 프로토콜에 넘깁니다.
    except OSError:
        pass
    finally:
        await self._close()  # 연결을 종료합니다.


async def _read_data(self) -> None:
    while not self.reader.at_eof():  # EOF로 요청 데이터가 끝일때까지 반복합니다.
        try:
            data = await asyncio.wait_for(
                self.reader.read(MAX_RECV), self.config.read_timeout
            )
        except (
            ConnectionError,
            OSError,
            asyncio.TimeoutError,
            TimeoutError,
            SSLError,
        ):
            break
        else:
            await self.protocol.handle(RawData(data))

    await self.protocol.handle(Closed())  # 더 이상 요청이 없으므로 종료합니다.
```

3. 데이터를 읽고 파싱합니다. 파싱 결과에 따라 애플리케이션을 실행하거나 오류 응답을 보냅니다.
```python
# https://github.com/pgjones/hypercorn/blob/main/src/hypercorn/protocol/h11.py
# H11Protocol 클래스의 일부

async def handle(self, event: Event) -> None:
    if isinstance(event, RawData):
        self.connection.receive_data(event.data)  # 파서에 데이터를 먹이고 파싱합니다.
        await self._handle_events()
    elif isinstance(event, Closed):
        if self.stream is not None:
            await self._close_stream()


async def _handle_events(self) -> None:
    while True:
        if self.connection.they_are_waiting_for_100_continue:
            await self._send_h11_event(
                h11.InformationalResponse(
                    status_code=100, headers=self.config.response_headers("h11")
                )
            )

        try:
            event = self.connection.next_event()  # 파싱 결과를 받아옵니다.
        except h11.RemoteProtocolError:
            if self.connection.our_state in {h11.IDLE, h11.SEND_RESPONSE}:
                await self._send_error_response(400)
            await self.send(Closed())
            break
        else:
            if isinstance(event, h11.Request):
                await self.send(Updated(idle=False))
                # HTTP1.1 그대로 사용하는지, 업그레이드 필요한지 확인합니다.
                # HTTP2 업그레이드는 ProtocolWrapper가 아래 _check_protocol에서
                # 던진 에러를 받아서 처리합니다.
                await self._check_protocol(event)
                # Websocket으로 스트림 업그레이드를 하거나 HTTP 스트림을 설정합니다.
                await self._create_stream(event)
            # 흐름 제어. 연결 재사용과 관련되어 있습니다.
            # https://h11.readthedocs.io/en/latest/api.html
            elif event is h11.PAUSED:
                await self.can_read.clear()
                await self.can_read.wait()
            elif isinstance(event, h11.ConnectionClosed) or event is h11.NEED_DATA:
                break
            elif self.stream is None:
                break
            elif isinstance(event, h11.Data):
                await self.stream.handle(Body(stream_id=STREAM_ID, data=event.data))
            elif isinstance(event, h11.EndOfMessage):
                await self.stream.handle(EndBody(stream_id=STREAM_ID))
            elif isinstance(event, Data):
                # WebSocket pass through
                await self.stream.handle(event)

   
```

종합적으로 살펴보면 서버가 하는 일은 다음과 같습니다.
1. 네트워크 연결 관리
    1. 초기화(핸드셰이크)
    2. 타임아웃 처리
    3. 흐름 제어
    4. 연결 종료
2. 프로토콜 관리
    1. 프로토콜 업그레이드
    2. 잘못된 요청에 대한 오류 응답
3. 태스크 관리
    1. 안정적인 종료(Graceful Shutdown)
    2. 이벤트 루프 구현체별 래퍼
하는 일이 많은 것을 보아하니 ASGI 존재의의가 명확하게 보이는군요.


# 마무리
지금까지 ASGI의 도입 배경과 존재 의의에 대해 알아보았습니다. 더 자세한 이야기가 궁금하신 분들은 아래 참조 링크를 확인해주세요. 감사합니다.


# 참조
- [PEP3333 : Python Web Server Gateway Interface v1.0.1](https://peps.python.org/pep-3333/#original-rationale-and-goals-from-pep-333)
- [mod_wsgi](https://modwsgi.readthedocs.io/en/master/configuration-directives/WSGIChunkedRequest.html)
- [ASGI(Asynchronous Server Gateway Interface)](https://asgi.readthedocs.io/en/latest/specs/main.html)
- [PEP3156 : Asynchronous IO Support Rebooted: the "asyncio" Module]()
- [hypercorn github](https://github.com/pgjones/hypercorn)
- [Will asgi become a PEP like wsgi is ?](https://groups.google.com/g/django-developers/c/ktTPNUTlsM0)


