# Google Apps Script - 맞춤법 검사 웹앱

이 프로젝트는 HTTP POST 요청을 처리하여, 요청 데이터의 해시 값을 검증한 후 OpenAI의 GPT 모델을 사용하여 한국어 맞춤법 및 문맥 교정을 수행하는 Google Apps Script입니다.

---

## **기능 설명**

- **HTTP POST 요청 처리**: 클라이언트로부터 JSON 데이터를 수신하고 처리합니다.
- **해시 값 검증**: 요청 데이터의 해시 값이 유효한지 확인합니다.
- **OpenAI API 호출**: 유효한 해시 값일 경우, OpenAI GPT 모델을 호출하여 맞춤법 및 문맥 교정을 수행합니다.
- **응답 반환**: 성공 시 교정된 텍스트를 반환하며, 실패 시 적절한 에러 메시지를 반환합니다.

---

## **설치 및 설정**

### 1. Google Apps Script 생성
- Google 스프레드시트를 생성하고, Apps Script 편집기를 엽니다.
- Code.gs 파일을 전체 복사하여 붙여넣습니다.

### 2. 스프레드시트 구성
- `sha-256`이라는 이름의 시트를 생성하고, 1열에 유효한 해시 값을 입력합니다.

해시를 사용하여 적법한 클라이언트의 요청 확인합니다. OpenAI의 API KEY는 과금 서비스이므로 반드시 적법한 클라이언트의 요청에만 응답해야 합니다.

### 3. 스크립트 속성 설정
아래와 같은 스크립트 속성을 설정해야 합니다:
- `OPENAI_API_KEY`: OpenAI API 키. **필수 속성**. 한번 배포되면 코드를 수정할 수 없으므로, Code.gs에 API 키를 절대 직접 입력하지 마세요.
- `OPENAI_MODEL`: 사용할 GPT 모델 (예: `gpt-4`)
- `OPENAI_PROMPT`: GPT 프롬프트 텍스트

OPENAI_API_KEY는 반드시 **스크립트 속성**을 사용하여 관리해야 합니다. 소스 코드에 API KEY를 직접 입력하고 배포한 경우, 즉시 해당 키를 REVOKE 하십시오. 

### 4. 웹앱 배포
- Apps Script에서 **배포 > 새 배포**를 선택합니다.
- 유형을 **웹 앱**으로 설정하고, 액세스 권한을 "모든 사용자" 또는 필요에 따라 설정합니다.
- 배포 후 제공된 URL을 클라이언트에서 사용합니다.

---

## **사용 방법**

### 요청 데이터 형식
클라이언트는 HTTP POST 요청을 통해 JSON 데이터를 전송해야 합니다:

``` json
{
"hash": "요청자의 프로그램에서 생성된 SHA-256 해시값",
"content": "맞춤법 검사를 원하는 텍스트"
}
```

### 응답 형식
#### 성공:

``` json
{
"success": true,
"message": "교정된 텍스트"
}
```

#### 실패:
``` json
{
"success": false,
"message": "에러 메시지"
}
```

---

## **코드 상세 분석**

### **1. HTTP POST 요청 처리 (`doPost`)**
- 요청 데이터를 파싱하고, 해시 값을 검증한 뒤 OpenAI API를 호출합니다.
- 주요 단계:
  - `parseRequestData`: JSON 데이터를 파싱.
  - `verifyHashWithCache`: 해시 값을 캐싱 및 스프레드시트를 통해 검증.
  - `processOpenAiRequest`: OpenAI API를 호출하여 맞춤법 교정 수행.

### **2. 해시 값 검증 (`verifyHashWithCache`)**
- Google Apps Script의 `CacheService`와 스프레드시트를 사용하여 효율적으로 해시 값을 검증합니다:
  - 캐시에 저장된 결과가 있으면 반환.
  - 없을 경우, 스프레드시트에서 해시 값을 검색하고 결과를 캐시에 저장.

### **3. OpenAI API 호출 (`processOpenAiRequest`)**
- OpenAI GPT 모델에 요청을 보내고 응답을 처리합니다:
  - `useApiKey`: 스크립트 속성에서 API 키를 가져옵니다. **절대** 이 변수에 API KEY를 직접 입력하지 마세요.
  - `getGPTModel` 및 `getGPTPrompt`: 사용할 GPT 모델과 프롬프트를 가져옵니다.
  - OpenAI API 호출 후, 응답 결과에서 교정된 텍스트를 추출하여 반환.

### **4. 에러 처리**
각 함수에서 발생 가능한 에러를 처리하고, 적절한 메시지를 반환하도록 설계되었습니다:
- JSON 파싱 에러
- 해시 값 검증 실패
- OpenAI API 호출 실패 등

---

## **주의 사항**

1. **보안**
   - API 키는 반드시 안전하게 관리해야 합니다. 스크립트 속성을 이용하여 관리하세요.
   - 웹앱 배포 시 액세스 권한을 적절히 설정하세요.

2. **요청 제한**
   - OpenAI API는 요금제에 따라 호출 제한이 있으므로, 적절히 관리해야 합니다.

3. **캐싱**
   - 해시 값 검증 과정에서 캐싱을 사용하므로, 동일한 요청에 대해 빠른 응답이 가능합니다.

---

## **기술 스택**

- Google Apps Script
- Google Sheets (스프레드시트)
- OpenAI GPT API

---

이 구글 웹앱 코드는 한국어 맞춤법 검사 및 문맥 교정을 자동화하는 데 유용하며, 다양한 클라이언트 애플리케이션과 연동하여 사용할 수 있습니다.