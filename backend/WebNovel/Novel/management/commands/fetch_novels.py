from django.core.management.base import BaseCommand
from Novel.crawler import fetch_all_novels_data  # crawler.py에서 함수 가져오기
import asyncio

class Command(BaseCommand):
    help = 'Fetch novel data from the web'

    def handle(self, *args, **kwargs):
        # asyncio.run()으로 fetch_all_novels_data()를 호출
        novels = asyncio.run(fetch_all_novels_data())  
        self.stdout.write(self.style.SUCCESS('Successfully fetched novels data'))
        # 여기서 novels를 데이터베이스에 저장하는 로직을 추가할 수 있어
