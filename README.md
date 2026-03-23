# 📺 TV 편성표 매니저 (TV Manager)

이 프로젝트는 지정된 웹 사이트에서 TV 편성표 정보를 스크래핑하여 SQLite3 데이터베이스로 관리하고, 실시간 웹 대시보드와 자동 스케줄링 기능을 제공하는 통합 관리 도구입니다.

## 🚀 주요 기능
- **멀티 카테고리 스크래핑**: 지상파, 종합편성, 케이블(15개 그룹) 전체 채널 수집.
- **자동 스케줄링**: APScheduler를 이용해 매일 자정(00:00)에 익일 편성표 자동 수집.
- **실시간 웹 대시보드**: 
  - 현재 시간 기준 채널별 상영 프로그램 표시.
  - 프로그램명 뒤의 태그(LIVE, HD, 자막, 재방)를 시각적인 배지로 표시.
- **편성표 상세 조회**: 일자, 채널, 카테고리별 필터링 조회 기능.
- **로깅 및 알림 시스템**:
  - 크롤링 성공/실패 이력을 DB에 기록 (`job_logs`).
  - 자동 크롤링 실패 시 웹 대시보드 상단에 실시간 알림 노출.
- **웹 제어**: 브라우저에서 직접 특정 일자의 크롤링을 트리거 가능.

## 🛠 설치 및 준비
이 프로젝트는 `uv` 패키지 매니저를 사용하여 관리됩니다.

```bash
# 의존성 패키지 설치
uv add requests beautifulsoup4 pytest fastapi uvicorn jinja2 python-multipart apscheduler
```

## 🌐 웹 서버 관리 (포트: 8080)
웹 대시보드와 자동 스케줄러가 포함된 서버를 관리합니다.

### 서버 시작 및 재기동
```bash
./restart.sh
```
*이 스크립트는 고유 식별자(`TV_MANAGER_SERVER_8080`)를 사용하여 기존 서버를 안전하게 종료하고 `nohup`으로 백그라운드 재실행합니다.*

### 웹 접속
브라우저에서 다음 주소로 접속하세요:
`http://[서버 IP]:8080`

## 🖥️ CLI 사용 방법
터미널에서 직접 특정 데이터를 갱신하거나 수집할 수 있습니다.

```bash
# 형식: uv run main.py [일자(YYYY_MM_DD)] [카테고리(all/public/organization/cable)]

# 예시: 특정 날짜 지상파 데이터 수집
uv run main.py 2026_03_23 public
```

## 📊 데이터베이스 구조 (tvguide.db)
- `tv_guide`: 편성 정보 (date, category, channel, time, title)
- `job_logs`: 작업 이력 (job_name, target_date, status, message, timestamp)

## 🧪 테스트
```bash
PYTHONPATH=. uv run pytest tests/
```
