from django.http import JsonResponse
from .cosineSimilar import get_similar_novels
from .models import Novel, Tag, NovelTag
from django.db.models import Prefetch

def get_novels(request):
    """소설 목록을 가져오는 API."""
    try:
        # 태그가 있는 소설만 가져오기
        novels = Novel.objects.prefetch_related(Prefetch('noveltag_set__tag')).values(
            'id', 'title', 'author', 'description', 'category', 'views'
        ).exclude(noveltag__tag=None)  # 태그가 없는 소설 제외

        # 각 소설의 태그를 리스트로 만들어 추가
        novel_list = []
        for novel in novels:
            novel_list.append(novel)

        # JSON 응답 형식으로 반환
        return JsonResponse(novel_list, safe=False, status=200)
    except Exception as error:
        print('Error fetching novels:', error)
        return JsonResponse({'message': 'Error fetching novels', 'error': str(error)}, status=500)

def get_recommendations(request):
    """추천 소설을 가져오는 API."""
    novel_id = request.GET.get('novelId')
    try:
        # novel_id가 유효한지 확인
        if novel_id is None:
            return JsonResponse({'message': 'novelId parameter is required'}, status=400)

        novel_id = int(novel_id)
        recommendations = get_similar_novels(novel_id)

        return JsonResponse(recommendations, safe=False, status=200)
    except ValueError:
        return JsonResponse({'message': 'novelId must be an integer'}, status=400)
    except Exception as error:
        print('Error fetching recommendations:', error)
        return JsonResponse({'message': 'Error fetching recommendations', 'error': str(error)}, status=500)
