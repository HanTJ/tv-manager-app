import argparse
from scraper import get_tv_guide_html, parse_tv_guide
from database import setup_database, delete_existing_data, save_tv_guide

def scrape_and_save(url, day, category, label=None):
    """지정된 URL을 스크래핑하여 DB에 저장함."""
    display_label = label if label else f"{category} ({url.split('page=')[1]})"
    print(f"  - [{display_label}] 수집 중: {url}")
    
    html_content = get_tv_guide_html(url)
    if not html_content:
        return 0

    tv_data = parse_tv_guide(html_content, day, category)
    if not tv_data:
        return 0
    
    save_tv_guide(tv_data)
    print(f"    -> {len(tv_data)}건 저장 완료.")
    return len(tv_data)

def main():
    parser = argparse.ArgumentParser(description='TV 편성표 스크래퍼')
    parser.add_argument('date', help='일자 (예: 2026_03_23)')
    parser.add_argument('category', choices=['all', 'public', 'organization', 'cable'], help='수집 카테고리')
    
    args = parser.parse_args()
    DAY = args.date
    SELECTED_CAT = args.category
    BASE_URL = "http://211.43.210.44/tvguide/index.php"
    
    print(f"=== TV 편성표 스크래핑 실행 (일자: {DAY}, 카테고리: {SELECTED_CAT}) ===")
    
    # 1. DB 초기화 (테이블 생성 및 해당 데이터 삭제)
    setup_database()
    delete_existing_data(DAY, SELECTED_CAT)
    
    # 2. 스크래핑 실행 계획
    tasks = []
    if SELECTED_CAT in ['all', 'public']:
        tasks.append(('public', 2, None))
    if SELECTED_CAT in ['all', 'organization']:
        tasks.append(('organization', 1, None))
    if SELECTED_CAT in ['all', 'cable']:
        for i in range(15):
            tasks.append(('cable', 3, f"cable{i}"))

    total_count = 0
    for main_cat, max_page, sub_cat in tasks:
        # 케이블의 경우 sub 파라미터가 별도로 관리됨
        cat_label = sub_cat if sub_cat else main_cat
        
        for page in range(1, max_page + 1):
            url = f"{BASE_URL}?main={main_cat}&day={DAY}&page={page}"
            if sub_cat:
                url += f"&sub={sub_cat}"
                
            count = scrape_and_save(url, DAY, main_cat, f"{cat_label}-P{page}")
            total_count += count
            
            # 데이터가 없으면 다음 그룹으로 (주로 케이블 페이지네이션용)
            if count == 0 and page > 1:
                break
                
    print(f"\n--- 실행 완료! 이번 실행에서 {total_count}건의 데이터가 업데이트되었습니다. ---")

if __name__ == "__main__":
    main()
