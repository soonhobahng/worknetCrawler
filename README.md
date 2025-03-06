# Worknet Crawler

대한민국 구인구직 포털 워크넷(Worknet)의 Open API를 이용하여 워크넷에 등록되어있는 직업 정보를 크롤링하기 위한 툴.

API Key 신청 방법등은 아래 URL 참조
Woknet Open API: 
<https://www.work24.go.kr/>

아래 코드 내 <Your API Key> 에 신청한 API Key 삽입.
```

jobDetailAPI = f"https://www.work24.go.kr/cm/openApi/call/wk/callOpenApiSvcInfo212D01.do?authKey=< Your API Key >&returnType=XML&target=JOBDTL&jobGb=1&jobCd={jobList.find("jobCd").text}&dtlGb=1"
url = jobDetailAPI  ## + quote_plus(keyword)
driver.get(url)

```

PC에 설치된 Chrome 버전에 맞는 Chrome driver 설치:
<https://googlechromelabs.github.io/chrome-for-testing/>

