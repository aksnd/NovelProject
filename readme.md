cd backend
source myenv/bin/activate 
가상환경 활성화



cd WebNovel
python manage.py runserver 0.0.0.0:8000
백엔드 서버 실행

python manage.py makemigrations
python manage.py migrate
마이그레이션