## Kakao Bot MCP Server

<!-- TOC -->

- [Kakao Bot MCP Server](#kakao-bot-mcp-server)
- [예시](#예시)
- [Tools](#tools)
  - [installation](#installation)
    - [Step 1. developers.kakao.com 에서 카카오 애플리케이션 생성](#step-1-developerskakaocom-에서-카카오-애플리케이션-생성)
    - [Step 2. 로컬환경 설정](#step-2-로컬환경-설정)

<!-- /TOC -->


[Model Context Protocol (MCP)](https://github.com/modelcontextprotocol) server implementation that integrates the Kakao Developers API to connect an AI Agent to the Kakao Official Account.

MCP Server 구현체로, 카카오 Developers API를 AI Agent에 통합하는 예시입니다.

<br>

> [!NOTE]
> This repository is NOT officially provided or maintained by Kakao. <br>
> It may not include complete functionality or comprehensive support. <br>
> 카카오의 경우 대부분의 API가 사업자등록이 포함된 비즈니스 애플리케이션 단위로 권한을 관리하고 있으므로, <br>
> 개인이 사용하기엔 제한적입니다. 

<br>

참고문서: https://developers.kakao.com/docs/latest/ko/kakaotalk-message/rest-api

---

## 예시

<img src="https://gitlab.com/-/project/69172217/uploads/89b84962ae9233c26bddd6318f60f97a/%E1%84%89%E1%85%B3%E1%84%8F%E1%85%B3%E1%84%85%E1%85%B5%E1%86%AB%E1%84%89%E1%85%A3%E1%86%BA_2025-05-03_%E1%84%8B%E1%85%A9%E1%84%92%E1%85%AE_2.36.09.png" alt="스크린샷_2025-05-03_오후_2.36.09" width="550">
<br>

claude desktop으로 MCP tool 실행


<img src="https://gitlab.com/-/project/69172217/uploads/e27b0f53e2776e6371fd2f5a0745299a/%E1%84%89%E1%85%B3%E1%84%8F%E1%85%B3%E1%84%85%E1%85%B5%E1%86%AB%E1%84%89%E1%85%A3%E1%86%BA_2025-05-03_%E1%84%8B%E1%85%A9%E1%84%92%E1%85%AE_2.37.25.png" alt="스크린샷_2025-05-03_오후_2.37.25" width="330">

<br>

'나에게 메시지 전달' 결과

## Tools

All tools require the `__email_address__` input to identify the user's credentials.

- 작성시점 기준, '나에게 보내기 - 기본 템플릿' API만 지원됩니다.
- 참고문서: https://developers.kakao.com/docs/latest/ko/kakaotalk-message/rest-api#default-template-msg-me

1.  **send_text_template_to_me**
    *   Description: Sends a Kakao Talk text message to me.
    *   Inputs:
        *   `__email_address__` (string, required): The email address associated with the Kakao account.
        *   `text` (string, required, max 200 characters): The text content of the message.
        *   `link` (object, required): An object defining the link associated with the text.
            *   `web_url` (string, optional, uri format)
            *   `mobile_web_url` (string, optional, uri format)
        *   `button_title` (string, optional): The title of the button.

2.  **send_feed_template_to_me**
    *   Description: Sends a Kakao Talk feed message to me.
    *   Inputs:
        *   `__email_address__` (string, required)
        *   `content` (object, required): The main content block of the feed message.
            *   `title` (string, required)
            *   `description` (string, required)
            *   `image_url` (string, required, uri format)
            *   `image_width` (integer, optional)
            *   `image_height` (integer, optional)
            *   `link` (object, required) - defines the link for the content
                *   `web_url` (string, optional, uri format)
                *   `mobile_web_url` (string, optional, uri format)
                *   `android_execution_params` (string, optional)
                *   `ios_execution_params` (string, optional)
        *   `item_content` (object, optional): Additional item content for the feed. (See API documentation for nested structure)
        *   `social` (object, optional): Social information like likes, comments, etc. (See API documentation for nested structure)
        *   `buttons` (array of objects, optional): Buttons to include with the message. (Each object requires `title` and `link`)

3.  **send_list_template_to_me**
    *   Description: Sends a Kakao Talk list message to me.
    *   Inputs:
        *   `__email_address__` (string, required)
        *   `header_title` (string, required): The title displayed at the top of the list.
        *   `contents` (array of objects, required): A list of content items. Each item requires:
            *   `title` (string, required)
            *   `description` (string, required)
            *   `image_url` (string, required, uri format)
            *   `image_width` (integer, optional)
            *   `image_height` (integer, optional)
            *   `link` (object, required) - defines the link for the list item
                *   `web_url` (string, optional, uri format)
                *   `mobile_web_url` (string, optional, uri format)
                *   `android_execution_params` (string, optional)
                *   `ios_execution_params` (string, optional)
        *   `header_link` (object, optional): A link for the header area. (See API documentation for nested structure)
        *   `buttons` (array of objects, optional): Buttons to include with the message. (Each object requires `title` and `link`)

4.  **send_location_template_to_me**
    *   Description: Sends a Kakao Talk location message to me.
    *   Inputs:
        *   `__email_address__` (string, required)
        *   `content` (object, required): The main content block for the location message.
            *   `title` (string, required)
            *   `description` (string, required)
            *   `image_url` (string, required, uri format)
            *   `image_width` (integer, optional)
            *   `image_height` (integer, optional)
            *   `link` (object, required) - defines the link for the content
                *   `web_url` (string, optional, uri format)
                *   `mobile_web_url` (string, optional, uri format)
                *   `android_execution_params` (string, optional)
                *   `ios_execution_params` (string, optional)
        *   `address` (string, required): The address of the location.
        *   `buttons` (array of objects, optional): Buttons to include with the message. (Each object requires `title` and `link`)
        *   `address_title` (string, optional): A title for the address.

5.  **send_calendar_template_to_me**
    *   Description: Sends a Kakao Talk calendar message to me.
    *   Inputs:
        *   `__email_address__` (string, required)
        *   `content` (object, required): The main content block for the calendar message.
            *   `title` (string, required)
            *   `description` (string, required)
            *   `link` (object, required) - defines the link for the content
                *   `web_url` (string, optional, uri format)
                *   `mobile_web_url` (string, optional, uri format)
                *   `android_execution_params` (string, optional)
                *   `ios_execution_params` (string, optional)
            *   `image_url` (string, optional, uri format)
        *   `id_type` (string, required, enum: "event"): The type of calendar item.
        *   `id` (string, required): The ID of the calendar item.
        *   `buttons` (array of objects, optional): Buttons to include with the message. (Each object requires `title` and `link`)

6.  **send_commerce_template_to_me**
    *   Description: Sends a Kakao Talk commerce message to me.
    *   Inputs:
        *   `__email_address__` (string, required)
        *   `content` (object, required): The main content block for the commerce message.
            *   `title` (string, required)
            *   `image_url` (string, required, uri format)
            *   `image_width` (integer, optional)
            *   `image_height` (integer, optional)
            *   `link` (object, required) - defines the link for the content
                *   `web_url` (string, optional, uri format)
                *   `mobile_web_url` (string, optional, uri format)
                *   `android_execution_params` (string, optional)
                *   `ios_execution_params` (string, optional)
        *   `commerce` (object, required): Commerce-specific information.
            *   `regular_price` (integer, required)
            *   `discount_price` (integer, optional)
            *   `discount_rate` (integer, optional, 0-100)
        *   `buttons` (array of objects, optional): Buttons to include with the message. (Each object requires `title` and `link`)

### installation

requirements: Python 3.13+

카카오 계정 필요

#### Step 1. developers.kakao.com 에서 카카오 애플리케이션 생성


카카오 신규 애플리케이션 생성 방법은 [quick start](https://developers.kakao.com/docs/latest/ko/getting-started/quick-start#create)문서를 참고합니다.

<details>
        <summary>메시지 API를 활성화하기 위한 추가작업</summary>

![사이트 등록](https://gitlab.com/-/project/69172217/uploads/c43583fef2737e7d7914957ea2d1a98f/%E1%84%89%E1%85%B3%E1%84%8F%E1%85%B3%E1%84%85%E1%85%B5%E1%86%AB%E1%84%89%E1%85%A3%E1%86%BA_2025-05-03_%E1%84%8B%E1%85%A9%E1%84%92%E1%85%AE_2.54.54.png)

"내 애플리케이션 > 앱 설정 > 플랫폼" 의 Web에서 사이트 도메인으로 http://localhost:8000 등록

<br>

![비즈 앱 등록](https://gitlab.com/-/project/69172217/uploads/1bc18c13c2d9552f53e3a217f360ef3e/%E1%84%89%E1%85%B3%E1%84%8F%E1%85%B3%E1%84%85%E1%85%B5%E1%86%AB%E1%84%89%E1%85%A3%E1%86%BA_2025-05-03_%E1%84%8B%E1%85%A9%E1%84%92%E1%85%AE_3.00.03.png)

비즈 앱 등록. 사업자번호가 없어도 "개인 개발자 비즈 앱" 등록이 가능하다.

<br>

![카카오 로그인 활성화](https://gitlab.com/-/project/69172217/uploads/e3481afc8cc24e15e533d39320c8f49f/%E1%84%89%E1%85%B3%E1%84%8F%E1%85%B3%E1%84%85%E1%85%B5%E1%86%AB%E1%84%89%E1%85%A3%E1%86%BA_2025-05-03_%E1%84%8B%E1%85%A9%E1%84%92%E1%85%AE_3.04.03.png)

카카오 로그인을 활성화한다.

<br>

![동의항목 설정](https://gitlab.com/-/project/69172217/uploads/8985389490968d9f8ee66cb4eda16047/%E1%84%89%E1%85%B3%E1%84%8F%E1%85%B3%E1%84%85%E1%85%B5%E1%86%AB%E1%84%89%E1%85%A3%E1%86%BA_2025-05-03_%E1%84%8B%E1%85%A9%E1%84%92%E1%85%AE_3.05.01.png)

- 제품 설정 > 카카오 로그인 > 동의항목에서 '닉네임', '카카오계정(이메일)', '카카오톡 메시지 전송' 을 활성화한다.
- OpenID 활성화한다.

</details>

#### Step 2. 로컬환경 설정

로컬에 uv가 설치되어 있어야 한다.

```sh
git clone git@github.com:inspirit941/kakao-bot-mcp-server.git
cd kakao-bot-mcp-server
pip install uv
uv sync

# inspector 실행
npx @modelcontextprotocol/inspector uv --directory .  run mcp-kakao

# MCP server 실행
uv run mcp-kakao
```



정상적으로 동작하려면 두 개의 파일이 필요하다. `.accounts.json`, `.kauth.json` 프로젝트 root 경로에 아래 파일을 생성한다.


.accounts.json
```json

{
    "accounts": [
        {
            "email": "your-email@kakao.com",
            "account_type": "personal",
            "extra_info": "Additional info that you want to tell Claude: E.g. 'Contains Family Calendar'"
        }
    ]
}
```
- email: 카카오 계정 이메일주소.
- account_type: personal 고정.
- extra_info: MCP server에 전달할 추가정보.

.kauth.json
```json
{
  "web": {
    "client_id": "rest-api-key",
    "auth_uri": "https://kauth.kakao.com/oauth/authorize",
    "token_uri": "https://kauth.kakao.com/oauth/token",
    "client_secret": "your_client_secret",
    "redirect_uris": ["http://localhost:8000/code"],
    "revoke_uri": "https://kapi.kakao.com/v2/user/revoke/scopes",
    "token_info_uri": "https://kauth.kakao.com/oauth/tokeninfo"
  }
}
```

- client_id: 카카오 애플리케이션에서 제공하는 REST_API key
- client_secret: 카카오 애플리케이션에서 발급받을 수 있는 client_secret. 임의의 문자열을 넣어도 동작함
- 나머지 필드는 고정.


claude desktop 설정

```json
{
  "mcpServers": {
    "mcp-kakao": {
      "command": "uv",
      "args": [
        "--directory",
        "your-project-path/kakao-bot-mcp-server",
        "run",
        "mcp-kakao"
      ]
    }
  }
}
```

**동작 방식**

<br>

LLM이 MCP Tool을 실행하면
- 프로젝트 root 경로에 `.oauth2.<카카오메일주소>.json` 파일이 있는지 확인한다.
  - 파일이 없을 경우, 웹 브라우저에 카카오 OAuth2 서버에 로그인 화면을 띄운다. (https://accounts.kakao.com/login?continue=...)
  - 파일이 있을 경우, 토큰이 만료되지 않았는지 확인한다. 만료되었다면, refresh token으로 재발급받는다. refresh token도 만료되었을 경우, tool에서 로그인할 수 있는 url 주소를 리턴한다. 
- 로그인에 성공하면, 프로젝트 root 경로에 `.oauth2.<카카오메일주소>.json` 이름으로 access_token 정보를 저장한다.

MCP tool은 json 파일의 access token을 사용하는 구조.


