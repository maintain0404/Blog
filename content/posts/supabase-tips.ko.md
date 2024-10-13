---
title: Supabase의 소소한 사용 팁들 
summary: Supabase 사용 팁을 정리해봤습니다.
date: 2024-10-13
draft: false
tags: ["supabase", "postgres"]
showToc: false
---
## 들어가며
| 이 글은 supabase를 처음 사용하며, API 서버 없이 활용하려는 사람들에게 가장 유용합니다.

최근에 프로젝트에서 풀스택으로 개발하면서 주로 supabase를 사용하고 있습니다. 저는 Backend 개발자로 시작했지만 supabase 덕분에 최근에 API를 작성할 일이 모두 없어졌습니다. Next.js를 처음 공부하면서 작업하느라 여러 어려움이 많았는데 supabase가 없었다면 지금보다 시간을 1.5배 정도 썼을 것 같습니다. 수개월 간 supabase를 사용하면서 얻은 팁들을 정리해봤습니다.


## 팁
### 테이블 선언 및 마이그레이션
- 최대한 정규화 수준을 높여서 엄격한 데이터 모델을 만드는 것이 좋습니다.
  - 낮은 정규화 수준을 보완해줄 백엔드가 없기 때문에 정규화 수준은 더욱 중요합니다.
  - 자동 생성된 typescript타입이 정확해지고, 클라이언트 사용이 편리해집니다.
  - jsonschema 확장을 통해 보완할 수 있습니다.
- 타입은 supabase gen types 명령어로 자동 생성할 수 있습니다.
```bash
# 로컬 supabase를 사용해서 typescript로 생성하는 예시
supabase gen types typescript --local > src/types/database.types.ts    
```

### 마이그레이션
- supabase migration new 명령어로 마이그레이션 파일을 생성하고, supabase db diff 명령어로 마이그레이션을 자동으로 만들 수 있습니다.
    ```bash
    # 빈 supabase/migrations/XXXXXXXXXXXXXX_create-application-function.sql 파일이 생깁니다.
    supabase migration new create-application-function
    # 마이그레이션 내용을 자동으로 생성해 채웁니다.
    supabase db diff --local > supabase/migrations/XXXXXXXXXXXXXX_create-application-function.sql
    ```
- 컬럼 타입 변경은 수동으로 해야 합니다. 이 점 유의해주세요.

### RPC 작성하기
### 트랜잭션
- Supabase 클라이언트는 트랜잭션을 지원하지 않습니다([참조](https://github.com/PostgREST/postgrest/issues/286)). 여러 쿼리를 한 번에 실행하고 싶다면 [RPC(Remote Procedure Call)](https://supabase.com/docs/reference/javascript/rpc)가 필요합니다.
  - 또한 view는 타입을 생성했을 때 모든 프로퍼티가 optional로 처리되기 때문에 RPC가 더 좋습니다.

#### AI로 쉽게 작성하기
- plpgsql이 익숙하지 않다면 ChatGPT, Claude 등 LLM에 요구사항을 정의하고 plpgsql을 작성해달라고 요청하면 빠르게 만들 수 있습니다.
  - p_, v_ 접두사를 붙여주는 경우가 많은데 키워드 충돌 때문에 그렇습니다. 접두사가 불편하더라도 웬만하면 쓰는 게 덜 귀찮습니다. 저는 접두사 빼고 싶어서 조금씩 고쳐쓰긴 했습니다.
- [jsonschema 확장](https://github.com/supabase/pg_jsonschema?tab=readme-ov-file)을 설치하면 요청 데이터 검증이 편리합니다. 데이터 형태가 복잡하다면 고려해보세요.

#### 서버에서만 실행할 수 있게 하기
- 클라이언트에서 RPC 실행을 막으려면 RPC 인자에 비밀키를 추가하고 서버 환경변수로 비밀키를 관리해서 서버에서만 실행할 수 있게 하는 방법이 제일 간단합니다.
  - 서버에서 anon_key 대신 service_role_key를 사용하는 방법이 있으나 저는 잘 되지 않았습니다.
    ```sql
    CREATE OR REPLACE FUNCTION complex_business_logic(
        IN p_user_id INTEGER,
        IN p_action VARCHAR(50),
        IN p_secret_key VARCHAR(100)
    ) RETURNS integer AS $$
    DECLARE
        v_result INTEGER;
    BEGIN
        IF p_secret_key IS NULL OR p_secret_key != 'p_secret_key' THEN
            RETURN QUERY SELECT 0::INTEGER, '인증 실패: 잘못된 비밀키'::VARCHAR;
            RETURN;
        END IF;

        -- 트랜잭션이 필요한 데이터 저장 로직
        ...
    END;
    $$ LANGUAGE plpgsql;
    ```
    ```typescript
    // 서버에서 호출
    const response = await supabase.rpc('complex_business_logic', {
        p_user_id: 1,
        p_action: 'create',
        p_secret_key: process.env.SERVER_SECRET  // p_scret_key와 동일한 값
    });
    ```

### Row Level Security
- 안전한 클라이언트 사용을 위해 RLS는 필수적입니다.
- supabase에서 추천하는 RLS는 테이블 `user_id` 컬럼을 사용합니다. `author_id`, `owner_id` 같은 이름보다 `user_id`를 추천합니다.
- Column Level Security도 가능하니 [참고](https://supabase.com/docs/guides/database/postgres/column-level-security#manage-column-privileges-in-the-dashboard)해보세요.

### 트리거
- 조회수, 좋아요, 댓글 수 기능을 트리거와 Column Level Security를 통해 구현할 수 있습니다.
    ```sql
    -- 좋아요 기능 예시
    -- 좋아요 post_like 테이블 레코드가 추가되었을 때, post의 likes_cnt 1 올리는 트리거 함수
    CREATE OR REPLACE FUNCTION "feature-community".update_post_comment_count()
    RETURNS trigger
    LANGUAGE plpgsql
    SECURITY DEFINER
    AS $function$
    begin
    update "feature-community".post
    SET comments_cnt = (select comments_cnt from "feature-community".post where id = new.post_id) + 1
    WHERE id = new.post_id;

    RETURN new;
    end
    $function$
    ;
    ```

### 기타
- 기본 FULL TEXT SEARCH 기능은 한글 검색 시 조사/어미 처리를 제대로 하지 못합니다. 한글 검색용 postgresql 확장([textsearch_ko](https://github.com/i0seph/textsearch_ko))이 있지만 관리형 supabase에서 사용하는 방법은 현재 없는 것 같습니다.
- React를 사용하는 경우 [supabase-cache-helper](https://github.com/psteinroe/supabase-cache-helpers) 라이브러리를 사용하면 요청 실패, 로딩 처리를 쉽게 할 수 있습니다. 사용방법은 기본적으로 SWR이나 react-query와 동일합니다.