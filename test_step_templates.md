# 테스트 스텝 템플릿 가이드

## 기본 액션 템플릿

### 1. 요소 대기 (wait_for_element)
```csv
test_id,step_order,action,selector_type,selector_value,input_value,expected_value,wait_time,description,validation_type,retry_count
TC001,1,wait_for_element,CSS_SELECTOR,.login_form,,visible,10,로그인 폼 로딩 대기,element_visible,3
TC001,2,wait_for_element,ID,submit_button,,clickable,5,제출 버튼 클릭 가능 대기,element_clickable,2
TC001,3,wait_for_element,XPATH,//div[@class='loading'],,invisible,15,로딩 스피너 사라질 때까지 대기,element_invisible,5
```

### 2. 입력 액션 (clear_and_input)
```csv
test_id,step_order,action,selector_type,selector_value,input_value,expected_value,wait_time,description,validation_type,retry_count
TC002,1,clear_and_input,CSS_SELECTOR,#username,{{credential.user_id}},,2,사용자명 입력,input_validation,2
TC002,2,clear_and_input,XPATH,//input[@type='password'],{{credential.user_pw}},,2,비밀번호 입력,input_validation,2
TC002,3,clear_and_input,CSS_SELECTOR,.search_input,{{search.customer_code}},,1,고객코드 검색,input_validation,1
```

### 3. 클릭 액션 (click)
```csv
test_id,step_order,action,selector_type,selector_value,input_value,expected_value,wait_time,description,validation_type,retry_count
TC003,1,click,CSS_SELECTOR,.login_button,,enabled,2,로그인 버튼 클릭,element_clickable,3
TC003,2,click,XPATH,//button[@type='submit'],,enabled,1,폼 제출,element_clickable,2
TC003,3,click,ID,search_btn,,enabled,2,검색 실행,element_clickable,3
```

### 4. 검증 액션 (verify_*)
```csv
test_id,step_order,action,selector_type,selector_value,input_value,expected_value,wait_time,description,validation_type,retry_count
TC004,1,verify_element_text,CSS_SELECTOR,.page_title,,{{validation.page_title}},2,페이지 제목 확인,text_match,2
TC004,2,verify_url_contains,,,{{validation.success_url}},2,성공 URL 확인,url_validation,1
TC004,3,verify_result_count,CSS_SELECTOR,.result_item,,>0,3,검색 결과 존재 확인,count_validation,2
TC004,4,verify_input_value,CSS_SELECTOR,.amount_input,,{{amount.test_values}},1,입력값 확인,input_validation,1
```

## 고급 액션 템플릿

### 5. 폼 처리 (specialized_input)
```csv
test_id,step_order,action,selector_type,selector_value,input_value,expected_value,wait_time,description,validation_type,retry_count
TC005,1,input_amount,CSS_SELECTOR,.amount_field,50000,,2,금액 입력,numeric_validation,2
TC005,2,input_collection_date,CSS_SELECTOR,.date_picker,today,,2,수금일 입력 (오늘),date_validation,2
TC005,3,input_remarks,CSS_SELECTOR,.remarks_textarea,테스트 입력,,1,비고 입력,input_validation,1
TC005,4,select_customer,CSS_SELECTOR,.customer_select,{{customer.code}},,3,고객 선택,select_validation,3
```

### 6. 페이지 네비게이션
```csv
test_id,step_order,action,selector_type,selector_value,input_value,expected_value,wait_time,description,validation_type,retry_count
TC006,1,wait_for_page_load,CSS_SELECTOR,.main_content,,visible,15,메인 페이지 로딩 대기,page_load,5
TC006,2,scroll_to_bottom,,,,,3,페이지 하단으로 스크롤,scroll_action,1
TC006,3,click_each_tab,CSS_SELECTOR,.tab_menu .tab,,enabled,2,모든 탭 순차 클릭,tab_navigation,3
```

### 7. 동적 컨텐츠 처리
```csv
test_id,step_order,action,selector_type,selector_value,input_value,expected_value,wait_time,description,validation_type,retry_count
TC007,1,wait_for_loading,CSS_SELECTOR,.spinner,,invisible,20,로딩 완료 대기,loading_complete,5
TC007,2,verify_current_month,CSS_SELECTOR,.calendar_header,,current_month,2,현재 월 표시 확인,date_validation,2
TC007,3,apply_date_filter,CSS_SELECTOR,.date_filter,today,,3,오늘 날짜 필터 적용,date_filter,3
```

### 8. 에러 처리 및 스크린샷
```csv
test_id,step_order,action,selector_type,selector_value,input_value,expected_value,wait_time,description,validation_type,retry_count
TC008,1,take_screenshot,,,login_attempt,,1,로그인 시도 전 스크린샷,screenshot,1
TC008,2,verify_form_validation,CSS_SELECTOR,.form_container,,valid,2,폼 유효성 검증,form_validation,2
TC008,3,verify_success_message,CSS_SELECTOR,.success_alert,,{{message.success}},5,성공 메시지 확인,text_match,3
```

## 테스트 데이터 활용 예시

### 동적 데이터 참조
```csv
# 테스트 데이터에서 값 가져오기
input_value,설명
{{credential.user_id}},test_data.csv에서 credential/user_id 값 사용
{{search.customer_code}},test_data.csv에서 search/customer_code 값 사용
{{validation.page_title}},test_data.csv에서 validation/page_title 값 사용 (언어별)
```

### 시스템 값 사용
```csv
input_value,설명
today,현재 날짜 (YYYY-MM-DD 형식)
current_month,현재 월 (숫자)
{{amount.test_values}},테스트용 금액 목록에서 선택
```

## 검증 타입별 가이드

### validation_type 옵션
- `basic`: 기본 검증 (요소 존재 여부)
- `element_visible`: 요소 가시성 확인
- `element_clickable`: 요소 클릭 가능 여부
- `text_match`: 텍스트 정확한 일치
- `text_contains`: 텍스트 포함 여부
- `text_not_empty`: 텍스트가 비어있지 않음
- `url_validation`: URL 포함 문자열 확인
- `input_validation`: 입력값 검증
- `numeric_validation`: 숫자 형식 검증
- `date_validation`: 날짜 형식 검증
- `regex_match`: 정규식 패턴 매치
- `count_validation`: 요소 개수 검증 (>0, <10, =5 등)
- `form_validation`: 폼 전체 유효성 검증
- `select_validation`: 드롭다운 선택 검증
- `page_load`: 페이지 로딩 완료 검증

## 완전한 테스트 시나리오 예시

### 로그인 + 고객 검색 + 상세보기 시나리오
```csv
test_id,step_order,action,selector_type,selector_value,input_value,expected_value,wait_time,description,validation_type,retry_count
TC_FULL_001,1,wait_for_element,CSS_SELECTOR,.login_page,,visible,10,로그인 페이지 로딩 대기,element_visible,3
TC_FULL_001,2,clear_and_input,CSS_SELECTOR,.log_id input,{{credential.user_id}},,2,아이디 입력,input_validation,2
TC_FULL_001,3,verify_input_value,CSS_SELECTOR,.log_id input,,{{credential.user_id}},1,아이디 입력값 확인,text_match,1
TC_FULL_001,4,clear_and_input,XPATH,//input[@type='password'],{{credential.user_pw}},,2,비밀번호 입력,input_validation,2
TC_FULL_001,5,click,CSS_SELECTOR,.btn01,,enabled,3,로그인 버튼 클릭,element_clickable,3
TC_FULL_001,6,wait_for_page_load,CSS_SELECTOR,.main_content,,visible,15,메인 화면 로딩 대기,page_load,5
TC_FULL_001,7,verify_url_contains,,,CUS1000,2,로그인 성공 URL 확인,url_validation,2
TC_FULL_001,8,take_screenshot,,,login_success,,1,로그인 성공 스크린샷,screenshot,1
TC_FULL_001,9,clear_and_input,XPATH,//input[@placeholder='검색어 입력'],{{search.customer_code}},,2,고객 코드 검색,input_validation,2
TC_FULL_001,10,click,CSS_SELECTOR,.btn_search,,enabled,2,검색 버튼 클릭,element_clickable,3
TC_FULL_001,11,wait_for_loading,CSS_SELECTOR,.loading_spinner,,invisible,20,검색 결과 로딩 대기,loading_complete,5
TC_FULL_001,12,verify_result_count,CSS_SELECTOR,.search_result .result_row,,>0,3,검색 결과 존재 확인,count_validation,3
TC_FULL_001,13,click,CSS_SELECTOR,.search_result .result_row:first-child,,enabled,2,첫 번째 결과 클릭,element_clickable,3
TC_FULL_001,14,wait_for_page_load,CSS_SELECTOR,.customer_detail,,visible,10,고객 상세 페이지 로딩,page_load,5
TC_FULL_001,15,verify_element_text,CSS_SELECTOR,.customer_name,,{{customer.name}},2,고객명 확인,text_contains,2
TC_FULL_001,16,take_screenshot,,,customer_detail_final,,1,최종 결과 스크린샷,screenshot,1
```

## 모범 사례

### 1. 적절한 대기 시간 설정
- 네트워크 요청: 10-20초
- 일반 요소 로딩: 5-10초  
- UI 반응: 1-3초
- 스크롤/애니메이션: 1-2초

### 2. 재시도 횟수 가이드
- 네트워크 의존적 작업: 3-5회
- UI 상호작용: 2-3회
- 단순 검증: 1-2회

### 3. 검증 단계 포함
- 중요한 입력 후에는 verify_input_value 추가
- 페이지 이동 후에는 URL 또는 페이지 요소 확인
- 비즈니스 로직 완료 후에는 결과 데이터 검증

### 4. 스크린샷 활용
- 테스트 시작/완료 시점
- 에러 발생 가능 지점 전후
- 중요한 비즈니스 프로세스 완료 후