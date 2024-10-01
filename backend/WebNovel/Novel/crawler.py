import asyncio
import re
import random
from pyppeteer import launch
from django.db import transaction
from .models import Novel, Tag, NovelTag  # 모델 임포트
from asgiref.sync import sync_to_async


# 랜덤 대기 시간을 추가하는 함수
async def wait(ms):
    await asyncio.sleep(ms / 1000)  # 밀리초를 초로 변환

# 목록 페이지의 URL을 설정합니다.
LIST_URL = 'https://page.kakao.com/menu/10011/screen/94'

async def fetch_novel_links(page):
    # 목록 페이지에 접속하여 링크를 가져옵니다.
    await page.goto(LIST_URL, {'waitUntil': 'networkidle2'})

    # 자동 스크롤 함수
    async def auto_scroll():
        await page.evaluate('''async () => {
            await new Promise((resolve) => {
                let totalHeight = 0;
                const distance = 100; // 스크롤 할 거리
                const timer = setInterval(() => {
                    window.scrollBy(0, distance);
                    totalHeight += distance;

                    if (totalHeight >= document.body.scrollHeight) {
                        clearInterval(timer);
                        resolve();
                    }
                }, 100); // 100ms마다 스크롤
            });
        }''')

    await auto_scroll()

    # 소설 링크 추출
    novel_links = await page.evaluate('''() => {
        const links = [];
        const eightDigitRegex = /\\d{8}$/;

        document.querySelectorAll('.w-full.overflow-hidden a').forEach(element => {
            const link = element.getAttribute('href');
            if (link && eightDigitRegex.test(link)) {
                links.push(link.startsWith('http') ? link : `https://page.kakao.com${link}?tab_type=about`);
            }
        });

        return links;
    }''')

    return novel_links

async def fetch_novel_data(url, page):
    print(url)
    try:
        await page.goto(url, {'waitUntil': 'networkidle2'})

        # 소설 데이터 추출
        novel_data = await page.evaluate('''() => {
            const parentDiv = document.querySelector('.relative.px-18pxr.text-center.bg-bg-a-20.mt-24pxr');
            if (!parentDiv) return null;

            const titleTargetDiv = parentDiv.querySelector('.flex.flex-col');
            if (!titleTargetDiv) return null;

            const title = titleTargetDiv.children[0]?.textContent.trim() || '';
            const author = titleTargetDiv.children[1]?.textContent.trim() || '';

            const categoryTargetDiv = parentDiv.querySelectorAll('.break-all.align-middle');
            const category = categoryTargetDiv[1]?.textContent.trim() || null;

            const viewsDiv = parentDiv.querySelectorAll('.text-el-70.opacity-70');
            const views = viewsDiv[2]?.textContent.trim() || null;

            const descriptionDiv = document.querySelector('.font-small1.mb-8pxr.block.whitespace-pre-wrap.break-words.text-el-70');
            const description = descriptionDiv?.textContent.trim() || null;

            const tagsDiv = document.querySelectorAll('.font-small2-bold.text-ellipsis.text-el-70.line-clamp-1');
            const tags = Array.from(tagsDiv).map(tag => tag.textContent.trim());

            return { title, author, category, views, description, tags };
        }''')

        return novel_data

    except Exception as error:
        print(f"Error fetching novel data from {url}: {error}")
        return None

def views_to_int(views_str):
    units = {
        '만': 10000,
        '억': 100000000
    }
    regex = r'^([\\d,.]+)([만억]?)$'
    match = re.match(regex, views_str)

    if match:
        number = float(match[1].replace(',', ''))
        unit = match[2]
        if unit and unit in units:
            number *= units[unit]
        return int(number)

    return None

async def save_novel_to_db(novel_data):
    if not all([novel_data['title'], novel_data['author'], novel_data['category'], novel_data['views'], novel_data['description'], novel_data['tags']]):
        return  # 데이터가 없으면 저장하지 않음

    int_views = views_to_int(novel_data['views'])

    # 제목과 작가로 기존 데이터 확인
    novel, created = await sync_to_async(Novel.objects.update_or_create)(
        title=novel_data['title'],
        author=novel_data['author'],
        defaults={
            'category': novel_data['category'],
            'views': int_views,
            'description': novel_data['description']
        }
    )

    # 태그 삽입
    for tag in novel_data['tags']:
        if not tag.startswith('#'):
            continue
        
        tag_name = tag[1:].strip()  # '#'을 제거하고 공백을 제거
        tag_obj, _ = await sync_to_async(Tag.objects.get_or_create)(name=tag_name)

        # novel_tags 테이블에 관계 삽입
        await sync_to_async(NovelTag.objects.get_or_create)(novel=novel, tag=tag_obj)
    

async def fetch_all_novels_data():
    novels = []
    browser = await launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])  # 리눅스 버전
    page = await browser.newPage()
    
    novel_links = await fetch_novel_links(page)
    print(len(novel_links))

    for link in novel_links:
        novel_data = await fetch_novel_data(link, page)
        if novel_data:
            await save_novel_to_db(novel_data)  # 데이터베이스에 저장
            novels.append(novel_data)  # 유효한 데이터만 추가
            
        wait_time = random.randint(1, 3)  # 초 단위로 변경
        await asyncio.sleep(wait_time)

    await page.close()
    await browser.close()
    return novels

