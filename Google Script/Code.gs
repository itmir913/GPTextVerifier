// 메인 doPost 함수
function doPost(e) {
  try {
    // 1. 요청 데이터 파싱
    const requestData = parseRequestData(e);

    // 2. 해시 검증
    const isHashValid = verifyHashWithCache(requestData.hash);
    if (!isHashValid) {
      return createErrorResponse("해시 검증 실패: 유효하지 않은 해시 값입니다. 개발자에게 연락하여 검증된 프로그램을 다시 다운로드해주세요.");
    }

    // 3. OpenAI API 호출
    const openAiResponse = processOpenAiRequest(requestData.content);
    return openAiResponse.success
      ? createSuccessResponse(openAiResponse.correctedText)
      : createErrorResponse(openAiResponse.error);

  } catch (error) {
    Logger.log("오류 발생: " + error.message);
    return createErrorResponse("서버 내부 오류: " + error.message);
  }
}

// 요청 데이터 파싱 함수
function parseRequestData(e) {
  try {
    return JSON.parse(e.postData.contents);
  } catch (error) {
    throw new Error("유효하지 않은 JSON 데이터입니다: " + error.message);
  }
}

// 캐싱을 활용한 해시 검증 함수
function verifyHashWithCache(hash) {
  const cache = CacheService.getScriptCache();
  const normalizedHash = hash.toLowerCase();

  // 캐시 확인
  const cachedResult = cache.get(normalizedHash);
  if (cachedResult !== null) {
    Logger.log(`캐시에서 결과 반환: ${cachedResult}, hash: ${hash}`);
    return cachedResult === 'true';
  }

  // 스프레드시트 검색
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("sha-256");
  if (!sheet) throw new Error("sha-256 시트를 찾을 수 없습니다.");

  const values = sheet.getRange(1, 1, sheet.getLastRow(), 1).getValues().flat();
  const isHashFound = values.some(value => value?.toString().toLowerCase() === normalizedHash);

  // 캐시에 저장, 600초 = 10분
  cache.put(normalizedHash, isHashFound.toString(), 600);

  Logger.log(isHashFound ? `해시값 검증 성공: ${hash}` : `해시값 검증 실패: ${hash}`);

  return isHashFound;
}

// OpenAI API 호출 처리 함수
function processOpenAiRequest(content) {
  if (!content || content.trim() === "") return { success: false, error: "content가 비어있습니다." };

  const apiKey = useApiKey();
  if (!apiKey) return { success: false, error: "OpenAI API 키가 설정되지 않았습니다." };

  const model = getGPTModel();
  const prompt = getGPTPrompt();

  const payload = {
    model,
    messages: [
      { role: "system", content: prompt },
      { role: "user", content }
    ]
  };

  const options = {
    method: "post",
    contentType: "application/json",
    headers: { Authorization: `Bearer ${apiKey}` },
    payload: JSON.stringify(payload)
  };

  try {
    const response = UrlFetchApp.fetch("https://api.openai.com/v1/chat/completions", options);
    const result = JSON.parse(response.getContentText());

    if (response.getResponseCode() === 200 && result.choices?.length > 0) {
      return { success: true, correctedText: result.choices[0].message.content.trim() };
    } else {
      Logger.log(`API 응답 오류 (코드 ${response.getResponseCode()}): ${response.getContentText()}`);
      return { success: false, error: `API 응답 오류 (코드 ${response.getResponseCode()}): 유효하지 않은 응답입니다.` };
    }

  } catch (error) {
    Logger.log(`API 호출 실패: 상태 코드 ${response.getResponseCode()}, 응답 본문: ${response.getContentText()}`);
    return { success: false, error: `API 호출 실패: ${error.message}` };
  }
}

// GPT 모델 가져오기 함수
function getGPTModel() {
  return PropertiesService.getScriptProperties().getProperty('OPENAI_MODEL') || "gpt-4o-mini";
}

// GPT 프롬프트 가져오기 함수
function getGPTPrompt() {
  return PropertiesService.getScriptProperties().getProperty('OPENAI_PROMPT') || "너는 한국어 맞춤법 및 문맥 교정기 역할을 수행한다. 단어를 추가하거나 삭제하지 마라. 입력된 문장의 줄바꿈, 순서, 구조를 변경하지 마라. 반드시 교정된 결과만 출력하라. 입력과 동일하면 동일한 문장을 그대로 출력하라. 불필요한 설명, 부가적인 텍스트 또는 예시는 출력하지 마라. 입력된 내용이 이미 완벽하다면 수정 없이 그대로 출력하라.";
}

// API 키 가져오기 함수
function useApiKey() {
  const scriptProperties = PropertiesService.getScriptProperties();
  const apiKey = scriptProperties.getProperty('OPENAI_API_KEY');

  if (!apiKey) {
    Logger.log("OPENAI_API_KEY가 설정되지 않았습니다.");
    throw new Error("API 키가 누락되었습니다. 웹앱 스크립트 속성에서 'OPENAI_API_KEY'를 설정하세요.");
  }

  return apiKey;
}

// 성공 응답 생성 함수
function createSuccessResponse(message) {
  return ContentService.createTextOutput(JSON.stringify({
    success: true,
    message
  })).setMimeType(ContentService.MimeType.JSON);
}

// 에러 응답 생성 함수
function createErrorResponse(errorMessage) {
  return ContentService.createTextOutput(JSON.stringify({
    success: false,
    message: errorMessage
  })).setMimeType(ContentService.MimeType.JSON);
}
