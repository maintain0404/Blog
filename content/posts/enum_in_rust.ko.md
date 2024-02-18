---
title: Rust enum 이해하기
summary: Rust에서 가장 중요한 enum에 대해 정리해봤습니다.
date: 2024-02-18T22:54:00+09:00
draft: false
tags:
  - Type
  - Rust
showToc: false
---
## 개요
`Rust` 를 공부하게 되면 가장 핵심적으로 다루는 키워드가 있습니다. 바로 `enum` 입니다. 다른 언어에서 쓰이는 `Enum` 과 용도가 조금 달라 혼란스러운 부분이 있습니다. 이 글에서는 `enum`이 무엇인지, 어떻게 사용하는지, 다른 언어와는 어떻게 다른지 알아보겠습니다. 

## Rust의 enum 간단하게 살펴보기
### 설명
`enum` 은 키워드 중 하나로 여러 종류가 될 수 있는 타입을 선언하는 데 사용됩니다. 구조체 선언과 비슷한 문법을 사용합니다.
### 예시
`Rust`의 `enum` 은 주로 `match` 키워드와 함께 사용됩니다. `match` 키워드를 통해서 이 `enum` 이 어떤 종류인지 파악하고 종류에 따라 적절한 로직을 실행하게 할 수 있습니다.  상품을 장바구니에 넣었고 외부 API를 통해 결제하려는 상황을 간단하게 생각해보겠습니다. 가능한 결제수단은 현금, 직불카드, 신용카드 3가지로 가정하겠습니다. 
1. 세 가지 결제 방법은 서로 다른 API URI를 사용합니다.
1. 현금결제는 추가적인 정보가 필요 없습니다. 
2. 직불카드는 어떤 카드를 쓸지 카드 번호가 필요합니다. 
3. 신용카드는 직불카드처럼 카드 번호가 필요하고, 또 몇 개월 할부로 결제할지 알아야 합니다.
이를 `enum` 으로 나타내면 다음과 같습니다.
```Rust
enum PaymentMethod {
    Cash,  // 현금결제하는 경우
    DebitCard(String)  // 직불카드로 결제하는 경우. 카드 번호를 포함
    CreditCard{  // 신용카드로 결제하는 경우. 카드 번호와 할부 개월 수를 포함함
        number: String,
        installment: i64
    },
}
```
그리고 결제를 실행하는 메소드를 작성한다면 아래처럼 작성할 수 있습니다. match를 통해서 enum을 분해하고 항목별로 다른 로직을 실행합니다.
```Rust
// 각 결제 방법별 API URI
const cash_uri: &str = "...";
const debit_uri: &str = "...";
const credit_uri: &str = "...";

fn pay(method: PaymentMethod, amount: i64) {
    match method {  // match는 enum의 가능한 모든 값을 처리해야합니다.
        Cash => {
            let req = build_pay_request_with_cash_(cash_uri, amount);
            request(cach_uri, req);
        },
        DebitCard(card_number) => {
            let req = build_pay_request_with_debit_card(debit_uri, card_number, amount)
            request(debit_uri, req);
        },
        CreditCard {
            number, installment
        } => {
            let req = build_pay_request_with_credit_card(credit_uri, card_number, amount, installment);
            request(credit_uri, req);
        }
    }    
}
```


## 다른 언어의 Enum(Python)
위 결제 코드를 `Python` 으로 다시 작성해보겠습니다. 
```Python
class PaymentMethod(str, Enum):
    CASH = "cash_uri"
    DEBIT_CARD = "debit_card_uri"
    CREDIT_CARD = "credit_card_uri"

def pay(method: PaymentMethod, amount: int, **extra_infos) {
    if method == PaymentMethod.Cash:
        req = build_pay_request_with_cach(amount, **extra_infos)
        request(method, req)
    elif method == PaymentMethod.DebitCard:
        let req = build_pay_request_with_debit_card(
            amount, **extra_infos)
        request(method, req)
    elif method == PaymentMethod.CreditCard:
        let req = build_pay_request_with_credit_card(
            amount, **extra_infos
        )
        request(method, req)

```

`Rust` 와 가장 다른 점은 `Enum` 의 선언부입니다. `Enum` 의 각 항목에 값이 직접 매핑되어 있습니다.  이것이 가장 큰 차이점입니다. `Rust`의 `enum`은 값이 직접 매핑되지 않습니다. **`Rust` 의 각 항목에 매칭되는 것은 값이 아닌 타입**입니다. `Python`의 `Enum`은 값이라서 직접 비교가 가능하고, 상수를 대신할 수 있으며, 상위 타입(예시에서는 str)의 일반적인 인스턴스처럼 취급할 수 있습니다. 이름은 동일하지만 **`Rust`의 `enum`은 다른 언어와 완전히 다른 것으로 취급해야 합니다**.
## Rust의 Enum은 Union이다.
결론적으로 `Rust`의 `enum`은 `Python`/`TypeScript`/`Kotlin` 의 `Union` 타입에 해당합니다.(예시를 작성하지 않았지만 Python과 유사합니다) `enum` 과 `Union` 의 차이점은 `Union` 은 **타입의 집합**이고, `Enum`은 **값의 집합**이라는 것입니다. 즉, `Rust`의 `enum`은 타입의 집합입니다. 
### 구현 측면에서 왜 Union인가?
메모리 레이아웃(객체가 실제로 저장되는 구조)를 통해서 살펴보겠습니다. Python의 객체는 다음처럼 메모리 레이아웃이 짜여집니다.
```
| type | data |
```
 즉, `Union` 타입의 실제 타입을 결정하는 것은 위 `type` 필드를 비교하여 일치하는 실제 타입으로 해석하는 과정이라 할 수 있습니다. 코드로 살펴본다면 아래의 `isinstance` 연산은 메모리 레이아웃에서 type 부분을 읽고 비교하는 것과 동일합니다.
 ```Python
def func(a):
    if isinstance(a, int):
        ...
    elif isinstance(a, str)
        ...
    else:
        ...

```

`Rust` 의 `enum` 레이아웃은 아래처럼 구성됩니다.
```
// Enum 종류별로 descrimitor 값이 다르고, 
// 그에 따라 data를 해석하는 방법이 달라집니다.
| descrimitor | data | 
```
앞부분(type, descrimitor)를 비교하여 실제 항목을 구분하고 항목에 따라서 data를 읽는 방법이 달라집니다. 실제 메모리를 해석하는 방법에서 유사성을 보이는 것을 알 수 있습니다.
반대로 `Python` 의 `Enum` 은 값(클래스 이름 공간에 속합니다)으로 동작하므로 앞부분 `type`을 비교하는 것이 아닌, 값을 비교해서 종류를 구분합니다. 
```
// CASH, DEBIT_CARD, CREDIT_CARD 모두 type은 Payment 클래스이고, 상수입니다.
// type은 동일하지만 data는 다릅니다.
| type | data | 
```
여기까지 `Rust` 의 `Enum` 이 왜 다른 언어의 `Union` 에 가까운지 알아보았습니다. 그렇다면, 키워드 이름이 `union` 이 아닌 `enum` 이 된 이유가 무엇일까요? `union`이었다면 다른 언어로 개발하다 온 `Rust` 초심자들이 혼란을 겪었을 이유도 없었을 텐데 말입니다.

## Union이 아닌 enum이 된 이유
사실 `Rust`에는 이미 `union` 키워드가 정의되어 있습니다. `C/C++`의 공용체(`union`)에 대응하기 위한 제한적인 용도로 만들어졌고, `C/C++`의 그것과 용법도 동일합니다. 하지만, 가능하면 `union`을 쓰지 않을 것을 권장하고 있습니다. 
### Rust/C/C++ union의 위험성
`union`을 사용하지 `Rust`  `enum`을 사용해야 하는 이유는 어떤 항목의 값을 가지고 있는 지 수동으로 추적해야하기 때문입니다. 
```RUst
// Copied from https://google.github.io/comprehensive-rust/ko/unsafe/unions.html
#[repr(C)]
union MyUnion {
    i: u8,
    b: bool,
}

fn main() {
    let u = MyUnion { i: 42 };
    println!("int: {}", unsafe { u.i });  // int: 42
    println!("bool: {}", unsafe { u.b });  // bool: true
}
```
위 코드에서 b에는 어떤 값도 할당하지 않았습니다. 하지만 true값을 가지고 있죠. i와 메모리 공간을 공유하기 때문에 i를 수정하면 b의 값도 그에 따라 변화하기 때문입니다. 이게 `union` 이 위험한 이유입니다. 다른 필드를 수정했지만 값이 바뀝니다. 
## 결론
1. `Rust`의 `enum`은 그 자체로 값을 가지지 않는 타입 집합입니다.
2. `Rust` `enum`은 다른 언어의 `union` 타입과 유사합니다.
3. `Rust` `union`은 가능하면 쓰지 맙시다.
## 참조
- [cheats.rs](https://cheats.rs)
- https://github.com/python/cpython
- https://google.github.io/comprehensive-rust/ko/unsafe/unions.html
- https://dasima.xyz/c-union-declaration/