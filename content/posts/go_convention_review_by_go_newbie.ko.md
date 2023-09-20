---
title: "뱅크샐러드 Go 컨벤션 리뷰"
date: 2023-09-20T20:51:23+09:00
summary: "뱅크샐러드 Go 컨벤션을 읽어본 후기"
tags: ["Coding Convention", "Go", "Golang"]
---


## 개요
얼마 전 backsalad에서 [Go 코딩 컨벤션(이하 컨벤션)](https://blog.banksalad.com/tech/go-best-practice-in-banksalad/) 포스팅을 올렸습니다. 지인 추천으로 한 번 읽어보았는데, 치밀하게 구성되어 있어서 Go는 잘 모르지만..! 😅 리뷰를 해보게 되었습니다. 

### 참고
1. 필자의 Go 언어 수준은 문법을 알고 Go 언어 프로젝트 몇 개를 살펴본 정도라고 보시면 되겠습니다.
2. 필자는 컨벤션 모든 부분을 리뷰하지 않습니다. 인상 깊게 본 부분 위주로 리뷰합니다. 

## 부분 별 리뷰
### Panic과 Error
컨벤션에 따르면 panic은 애플리케이션 초기화 과정 중 정상 스타트가 불가능한 경우에만 사용합니다. Go에는 에러 처리가 error와 panic(fatal)로 이원화 되어 있습니다. Rust에서도 비슷한 접근을 볼 수 있습니다. 이 방식은 함수 작성 시 암시적인 에러를 배제하고 좀 더 순수하게 작성할 수 있다는 점에서 좋다고 생각합니다. 
```go
// Go의 panic과 error 이용 예외 처리
func MustPanic() {
  panic("Panic")
}

func ReturnError() error {
  return errors.New("Error")
}

func Handle() string {
  if err := ReturnError(); err != nil {
    return "Success"
  } else {
    return "Fail"
  }
}

func Go() {
  defer func() {
    if x := recover(); x != nil {
      fmt.Print("Panic occured. Stop application.")
    }
  }
  MustPanic()
  Handle()
}
```
다른 언어(Java, Python, Javascript, ...)에서 볼 수 있는 `try`...`catch`... 방식과 비교해서 살펴보자면, `try`...`catch`... 방식으로는 상속을 통해 발생할 수 있는 에러 경계를 나누는 것이 가능하긴 합니다. 하지만 시간에 쫒겨 에러 슈퍼클래스로 모든 에러를 전부 처리해버릴 수 있고, 에러 상속 구조를 팀에서 자체적으로 논의해야 한다는 문제가 있습니다. 에러 처리 [범위가 모호해 처리하지 말아야 할 에러를 처리해서 생기는 문제](https://docs.pydantic.dev/latest/migration/#typeerror-is-no-longer-converted-to-validationerror-in-validators)는 생각보다 쉽게 일어납니다. 반면에 `try`...`catch`... 방식은 필요하면, 에러 처리를 호출자에게 넘겨버릴 수 있기 때문에 코드를 줄일 수 있습니다. 각자 취향 차이지만, Go라는 언어의 철학 - 단순성을 생각해봤을 때 에러 이원화 방식이 Go에 좀 더 어울린다고 생각합니다.
```python
# Python의 Try... Catch... 스타일 에외 처리
def raise_exception():
    raise ValueError

def pass_exception():
    raise_exception()

def handle_exception():
    try:
        pass_exception()
    except ValueError:
        pass
```

### HTTP Client
컨벤션에 따르면 외부 API를 호출하는 경우 따로 Http Client를 사용해야 합니다. 추가적으로 커넥션 풀까지 client에서 내부적으로 설정하도록 가이드되어 있습니다. 외부 API는 변경에 대한 통제가 불가능하므로 반드시 변경에 유연한 구조가 되어야 합니다. 스키마 변경 시, 구조체 관련 코드를 살짝 변경하는 것만으로 손쉽게 하위 호환성을 유지할 수 있다는 점에서 현명한 선택인 것 같습니다. 
```go
// Functional Option 패턴
struct PostApiBody{
  int a
}
func ParamA(int a) {
  return func(b *PostApiBody) {
    b.a = a
  }
}
// 파라미터가 추가된다면 ParamX 함수를 추가하고, 
// 변경된다면 ParamX 함수를 수정하는 것으로 하위 호환성 보장 가능
func (c *HttpClient) CreatePost(params ...func(*PostApiBody)) {
  body := &PostApiBody{}
  for _, p := range params {
    p(body)
  }
  client.Post("URL", "application/json", body.Json())
}
```

### 테스트
컨번션에 따르면 given, when, then 구조의 테이블 테스트를 권장하고, 테스트 스위트를 사용하지 않습니다. 몽키패치도 배제하고 사이드 이펙트가 있는 코드는 무조건 외부에서 주입하도록 하고 있습니다. 외부효과를 절대적으로 배제하고 단순명료함을 구현하기 위한 노력이 엿보입니다. 매 테스트에서 어떤 방식으로 데이터베이스를 세팅하는지, 어떻게 데이터베이스의 외부성을 제어하는지 종합적으로 외부 데이터베이스를 사용하는 테스트는 어떻게 진행하는지 궁금하네요.


### reflect
컨벤션에서는 reflect를 쓰지 않기를 권장하고 있습니다. '서버 핸들러에서 reflect를 사용한다면 보통 무언가 잘못되어가고 있다는 신호'라고 언급했는데 굉장히 동의합니다. 무슨 데이터가 들어오고 나갈 것인지 명확하게 정의되지 않았거나 다른 영역에서 우연히 동일한 형태의 데이터를 사용하는 경우가 대부분일 것이라 생각합니다. 전자의 경우, 애초에 코드를 작성하고 있으면 안 되는 시점입니다. 방향성에 대해 좀 더 고민하고 있어야 하죠. 후자의 경우에는, 근본적으로 분리될 가능성이 높은 코드라고 생각하고 다르게 쓰는 것이 옳습니다. 현실에서 [수렴진화](https://ko.wikipedia.org/wiki/%EC%88%98%EB%A0%B4_%EC%A7%84%ED%99%94)처럼, 전혀 상관없는 종이지만 어떤 환경적 여건에 의해 동일한 모습일 뿐입니다. 이 '환경적 여건'이 달라진다면, 그 형태가 달라질 가능성이 높죠.

### 네이밍
#### detail, Summary, Info 비권장
컨벤션에서는 `Xdetail`, `Xsummary`, `Xinfo` 형식의 이름을 권장하지 않습니다. 그 이유는 시간에 따라 같은 단어라도 내용이 달라질 수 있게 되기 때문입니다. 시간을 고려하는 관점은 굉장히 흥미로웠습니다. 동 시점에 요약과 상세가 가리키는 필드 목록은 같아야 합니다. 같은 이름을 두 번 쓸 수는 없으니까요. 이런 이유로 요약과 상세가 두 종류 이상인 경우는 다른 버전을 동시에 서빙하는 경우 밖에 없다고 생각하고 이름 혹은 패키지에 버전을 명시하는 것을 관습적으로 사용했었는데, 이런 방법도 있구나 싶었습니다. 

#### 패키지 네이밍
컨벤션에서는 `core`, `util`, `helper`, `common`, `infra`같은 이름을 사용하지 않도록 권장하고 있습니다. 위 이름은 생각하기 쉽고 모두가 아는 만큼, 모두가 이해하는 범위가 미묘하게 다릅니다. 흔하지 않은 단어를 사용했다면, 그것은 팀만의 언어가 되고 팀에서의 의미는 명확해집니다. 저는 위 이름으로 디렉토리 만드는 것을 선호하긴 하지만, 많은 다른 Go 프로젝트와 Go라는 언어의 철학을 고려할 때 적절한 선택인 것 같습니다.

### 프로젝트 구조
컨벤션에 따르면 디렉토리 추가는 최소한으로 해야 합니다. 개인적으로는 한 디렉토리에 너무 파일이 많은 것을 좋아하지 않지만 Go에서는 이런 스타일이 일반적인 관례인 것 같더군요.
  
## 전반적인 소감
전반적으로 단순하고, 코드에서 맥락을 최대한 배제해 순수하게 코드만 바라볼 수 있게 하는 데 집중하는, 깊은 고민과 노하우가 느껴지는 컨벤션이라고 생각합니다. 전반적으로 단순함에 집중한 것이 인상깊었습니다. 좋은 글 공개해주신 뱅크샐러드 팀에게 감사드립니다. 😄

