# 기존 테스트에서 향상된 테스트로 마이그레이션 가이드

## 개요
이 가이드는 기존의 단순한 테스트 스텝을 향상된 검증 로직이 포함된 테스트로 마이그레이션하는 방법을 안내합니다.

## 기존 vs 향상된 테스트 비교

### 1. 로그인 테스트 개선

#### 기존 방식 (test_steps.csv)
```csv
test_id,step_order,action,selector_type,selector_value,input_value,description
TC001,1,input,CSS_SELECTOR,.log_id input,c89109,아이디 입력
TC001,2,input,XPATH,//input[@type='password'],mcnc1234!!,비밀번호 입력
TC001,3,click,CSS_SELECTOR,.btn01,,로그인 버튼 클릭
TC001,4,verify,XPATH,//div[@class='main_content'],,메인 화면 확인
```

#### 향상된 방식 (test_steps_enhanced.csv)
```csv
test_id,step_order,action,selector_type,selector_value,input_value,expected_value,wait_time,description,validation_type,retry_count
TC001,1,wait_for_element,CSS_SELECTOR,.log_id input,,visible,10,로그인 페이지 로딩 대기,element_visible,3
TC001,2,clear_and_input,CSS_SELECTOR,.log_id input,{{credential.user_id}},,2,아이디 입력,input_validation,2
TC001,3,verify_input_value,CSS_SELECTOR,.log_id input,,{{credential.user_id}},1,아이디 입력 확인,text_match,1
TC001,4,clear_and_input,XPATH,//input[@type='password'],{{credential.user_pw}},,2,비밀번호 입력,input_validation,2
TC001,5,click,CSS_SELECTOR,.btn01,,enabled,3,로그인 버튼 클릭,element_clickable,3
TC001,6,wait_for_page_load,XPATH,//div[@class='main_content'],,visible,15,메인 화면 로딩 대기,page_load,5
TC001,7,verify_url_contains,,,CUS1000,CUS1000,2,메인 페이지 URL 확인,url_validation,2
TC001,8,take_screenshot,,,login_success,,1,로그인 성공 스크린샷,screenshot,1
```

## 마이그레이션 단계별 가이드

### Step 1: 테스트 데이터 분리

#### 하드코딩된 값을 테스트 데이터로 분리
```csv
# 기존 - 하드코딩
TC001,2,input,CSS_SELECTOR,.log_id input,c89109,아이디 입력

# 개선 - 데이터 참조
TC001,2,clear_and_input,CSS_SELECTOR,.log_id input,{{credential.user_id}},,2,아이디 입력,input_validation,2
```

test_data.csv에 다음 추가:
```csv
test_id,data_type,key,value,description,locale
TC001,credential,user_id,c89109,기본 테스트 계정,all
TC001,credential,user_pw,mcnc1234!!,기본 테스트 패스워드,all
```

### Step 2: 검증 로직 강화

#### 입력 후 검증 단계 추가
```csv
# 기존 - 입력만
TC001,2,input,CSS_SELECTOR,.log_id input,c89109,아이디 입력

# 개선 - 입력 + 검증
TC001,2,clear_and_input,CSS_SELECTOR,.log_id input,{{credential.user_id}},,2,아이디 입력,input_validation,2
TC001,3,verify_input_value,CSS_SELECTOR,.log_id input,,{{credential.user_id}},1,아이디 입력 확인,text_match,1
```

#### 요소 대기 로직 추가
```csv
# 기존 - 바로 액션
TC001,3,click,CSS_SELECTOR,.btn01,,로그인 버튼 클릭

# 개선 - 대기 + 액션
TC001,5,click,CSS_SELECTOR,.btn01,,enabled,3,로그인 버튼 클릭,element_clickable,3
```

### Step 3: 에러 처리 및 재시도 추가

#### 재시도 횟수 설정
```csv
# 네트워크 의존적 작업
TC001,6,wait_for_page_load,XPATH,//div[@class='main_content'],,visible,15,메인 화면 로딩 대기,page_load,5

# UI 상호작용
TC001,5,click,CSS_SELECTOR,.btn01,,enabled,3,로그인 버튼 클릭,element_clickable,3

# 단순 검증
TC001,3,verify_input_value,CSS_SELECTOR,.log_id input,,{{credential.user_id}},1,아이디 입력 확인,text_match,1
```

### Step 4: 상세 검증 타입 지정

#### validation_type 필드 활용
```csv
# 기존 - 단순 verify
TC001,4,verify,XPATH,//div[@class='main_content'],,메인 화면 확인

# 개선 - 구체적 검증 타입
TC001,6,wait_for_page_load,XPATH,//div[@class='main_content'],,visible,15,메인 화면 로딩 대기,page_load,5
TC001,7,verify_url_contains,,,CUS1000,CUS1000,2,메인 페이지 URL 확인,url_validation,2
```

## 자동 마이그레이션 스크립트

### 기존 테스트 스텝을 향상된 버전으로 변환하는 Python 스크립트

```python
import csv

def migrate_test_steps(old_file, new_file, test_data_file):
    """기존 테스트 스텝을 향상된 버전으로 마이그레이션"""
    
    # 테스트 데이터 생성을 위한 수집
    test_data = []
    enhanced_steps = []
    
    with open(old_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            test_id = row['test_id']
            step_order = int(row['step_order'])
            action = row['action']
            
            if action == 'input':
                # input을 clear_and_input으로 변환
                if row['input_value']:
                    # 테스트 데이터로 분리
                    data_key = f"input_{step_order}"
                    test_data.append({
                        'test_id': test_id,
                        'data_type': 'input',
                        'key': data_key,
                        'value': row['input_value'],
                        'description': row['description'],
                        'locale': 'all'
                    })
                    
                    # 향상된 스텝 생성
                    enhanced_steps.append({
                        'test_id': test_id,
                        'step_order': step_order,
                        'action': 'clear_and_input',
                        'selector_type': row['selector_type'],
                        'selector_value': row['selector_value'],
                        'input_value': f"{{{{input.{data_key}}}}}",
                        'expected_value': '',
                        'wait_time': '2',
                        'description': row['description'],
                        'validation_type': 'input_validation',
                        'retry_count': '2'
                    })
                    
                    # 검증 스텝 추가
                    enhanced_steps.append({
                        'test_id': test_id,
                        'step_order': step_order + 0.5,
                        'action': 'verify_input_value',
                        'selector_type': row['selector_type'],
                        'selector_value': row['selector_value'],
                        'input_value': '',
                        'expected_value': f"{{{{input.{data_key}}}}}",
                        'wait_time': '1',
                        'description': f"{row['description']} 확인",
                        'validation_type': 'text_match',
                        'retry_count': '1'
                    })
            
            elif action == 'click':
                # click을 enhanced_click으로 변환
                enhanced_steps.append({
                    'test_id': test_id,
                    'step_order': step_order,
                    'action': 'click',
                    'selector_type': row['selector_type'],
                    'selector_value': row['selector_value'],
                    'input_value': '',
                    'expected_value': 'enabled',
                    'wait_time': '3',
                    'description': row['description'],
                    'validation_type': 'element_clickable',
                    'retry_count': '3'
                })
            
            elif action == 'verify':
                # verify를 구체적인 검증으로 변환
                enhanced_steps.append({
                    'test_id': test_id,
                    'step_order': step_order,
                    'action': 'wait_for_element',
                    'selector_type': row['selector_type'],
                    'selector_value': row['selector_value'],
                    'input_value': '',
                    'expected_value': 'visible',
                    'wait_time': '10',
                    'description': row['description'],
                    'validation_type': 'element_visible',
                    'retry_count': '3'
                })
    
    # 향상된 테스트 스텝 저장
    with open(new_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['test_id', 'step_order', 'action', 'selector_type', 'selector_value', 
                     'input_value', 'expected_value', 'wait_time', 'description', 
                     'validation_type', 'retry_count']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        # step_order로 정렬
        enhanced_steps.sort(key=lambda x: (x['test_id'], float(x['step_order'])))
        
        for step in enhanced_steps:
            writer.writerow(step)
    
    # 테스트 데이터 저장
    with open(test_data_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['test_id', 'data_type', 'key', 'value', 'description', 'locale']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(test_data)
    
    print(f"Migration completed:")
    print(f"- Enhanced steps: {len(enhanced_steps)}")
    print(f"- Test data entries: {len(test_data)}")

# 실행
if __name__ == '__main__':
    migrate_test_steps('test_steps.csv', 'test_steps_migrated.csv', 'test_data_migrated.csv')
```

## 기존 테스트 러너 업데이트

### 기존 러너에 향상된 엔진 통합

```python
# 기존 appium_test_runner.py에 추가
from enhanced_test_engine import EnhancedTestEngine

class TestAllLanguages(unittest.TestCase):
    def test_01_enhanced_login(self):
        driver = get_driver()
        wait = WebDriverWait(driver, 20)
        
        # 향상된 테스트 엔진 사용
        engine = EnhancedTestEngine(driver, 20)
        
        try:
            driver.switch_to.context(WEBVIEW_NAME)
            
            for lang in LANGUAGES:
                change_language(driver, wait, lang)
                
                # 향상된 테스트 케이스 실행
                test_cases = load_enhanced_test_cases()
                for case in test_cases:
                    execute_enhanced_test_case(engine, case, lang)
                    
                go_login_page(driver, wait)
        finally:
            driver.quit()
```

## 점진적 마이그레이션 전략

### Phase 1: 핵심 테스트 케이스 우선
1. 로그인 테스트
2. 주요 검색 기능
3. 데이터 입력/수정 기능

### Phase 2: 검증 로직 강화
1. 입력값 검증 추가
2. 페이지 로딩 검증 추가
3. 에러 처리 개선

### Phase 3: 완전 전환
1. 모든 테스트 케이스 변환
2. 기존 러너 대체
3. 성능 최적화

## 검증 및 테스트

### 마이그레이션 후 검증 체크리스트
- [ ] 모든 기존 테스트 케이스가 정상 실행됨
- [ ] 새로운 검증 로직이 올바르게 동작함
- [ ] 테스트 데이터가 올바르게 로딩됨
- [ ] 에러 처리 및 재시도가 적절히 동작함
- [ ] 실행 시간이 합리적 범위 내에 있음
- [ ] 스크린샷 및 로그가 올바르게 생성됨

## 문제 해결

### 일반적인 마이그레이션 이슈
1. **셀렉터 호환성**: 기존 셀렉터가 새로운 엔진과 호환되지 않는 경우
2. **타이밍 이슈**: 새로운 대기 로직으로 인한 타이밍 변경
3. **데이터 참조 오류**: 테스트 데이터 참조 문법 오류
4. **성능 저하**: 추가된 검증으로 인한 실행 시간 증가

### 해결 방안
1. 셀렉터 검토 및 업데이트
2. 대기 시간 조정
3. 테스트 데이터 구조 검토
4. 불필요한 검증 단계 제거