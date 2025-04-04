"""Firstmall 패치 정보를 크롤링하는 스크립트입니다."""

import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def setup_driver():
    print("Chrome 드라이버 설정 중...")
    chrome_options = Options()
    print("  - Chrome 드라이버 초기화 중...")
    driver = webdriver.Chrome(options=chrome_options)
    print("  - Chrome 드라이버 초기화 완료")
    return driver

def create_folder(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

def download_file(url, folder_path, file_name):
    response = requests.get(url)
    if response.status_code == 200:
        with open(os.path.join(folder_path, file_name), 'wb') as f:
            f.write(response.content)

def crawl_detail_page(driver, href_number):
    folder_path = f"./patch_{href_number}"
    create_folder(folder_path)
    
    print(f"  - 패치 내용 저장 중...")
    # 상세 내용 저장
    content_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.patchCont.patchBox1"))
    )
    content = content_element.text
    
    with open(os.path.join(folder_path, "body.txt"), 'w', encoding='utf-8') as f:
        f.write(content)
    
    # 다운로드 링크 처리
    download_links = driver.find_elements(By.CSS_SELECTOR, ".btn_wrap a")
    print(f"  - {len(download_links)}개의 첨부 파일 다운로드 중...")
    for link in download_links:
        file_name = link.text.strip()
        if file_name == "목록":  # "목록" 링크는 건너뛰기
            continue
        if not file_name:
            file_name = "download.zip"
        relative_url = link.get_attribute('href')
        if not relative_url:
            print(f"    * {file_name} 다운로드 실패: URL을 찾을 수 없습니다.")
            continue
        download_url = f"https://www.firstmall.kr{relative_url}"
        print(f"  - {download_url}")
        download_file(download_url, folder_path, file_name + ".zip")
        print(f"    * {file_name} 다운로드 완료")

def main():
    driver = setup_driver()
    base_url = "https://www.firstmall.kr/customer/patch"
    
    print("크롤링을 시작합니다...")
    
    # 1페이지부터 36페이지까지 순회
    for page in range(1, 2):
        print(f"\n=== {page}페이지 처리 중 ===")
        driver.get(f"{base_url}#page-{page}")
        time.sleep(2)  # 페이지 로딩 대기
        
        # 페이지의 모든 패치 링크 찾기
        patch_links = driver.find_elements(By.CSS_SELECTOR, ".subject.left a")
        print(f"페이지에서 {len(patch_links)}개의 패치를 발견했습니다.")
        
        for idx, link in enumerate(patch_links, 1):
            href = link.get_attribute('href')
            href_number = href.split('#')[1]
            print(f"\n[{idx}/{len(patch_links)}] 패치 번호 {href_number} 처리 중...")
            
            # 상세 페이지로 이동
            driver.get(f"{base_url}#{href_number}")
            time.sleep(2)
            
            # 상세 페이지 크롤링
            crawl_detail_page(driver, href_number)
            print(f"패치 {href_number} 저장 완료")

            break
            
    print("\n크롤링이 완료되었습니다!")
    driver.quit()

if __name__ == "__main__":
    main()