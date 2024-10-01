import numpy as np
import math
from .models import Novel, Tag, NovelTag
from django.db.models import Prefetch

novels = None
vectors = None
from django.db.models import Prefetch

def fetch_novels_and_tags():
    """데이터베이스에서 소설과 태그를 가져오는 함수."""
    global novels
    # 소설 데이터를 가져옵니다.
    novels = Novel.objects.all().values('id', 'title', 'author', 'description', 'category', 'views')

    # novel_id에 해당하는 tag 정보를 NovelTag에서 가져옵니다.
    novel_tags = NovelTag.objects.values('novel_id', 'tag_id')

    # novel_id를 키로 하고 태그 ID 리스트를 값으로 하는 딕셔너리 생성
    tag_dict = {}
    for nt in novel_tags:
        novel_id = nt['novel_id']
        tag_id = nt['tag_id']
        if novel_id not in tag_dict:
            tag_dict[novel_id] = []
        tag_dict[novel_id].append(tag_id)


    # 소설별로 태그 정보를 추가하여 반환할 데이터 생성
    novel_list = []
    for novel in novels:

        novel_data = {
            'id': novel['id'],
            'title': novel['title'],
            'author': novel['author'],
            'description': novel['description'],
            'category': novel['category'],
            'views': novel['views'],
            'tags': tag_dict.get(novel['id'], [])  # 해당 소설의 태그 ID 리스트를 추가
        }
        novel_list.append(novel_data)

    # 최종적으로 생성된 소설 리스트 확인
    print(novel_list[0])
    return novel_list


def compute_idf(tag_document_count, total_documents):
    """IDF(역 문서 빈도)를 계산하는 함수."""
    idf = {}
    for tag, count in tag_document_count.items():
        # IDF 계산 공식을 사용하여 각 태그의 IDF 값을 저장합니다.
        idf[tag] = math.log(total_documents / (1 + count))
    return idf

def create_tf_idf_vector(tags, idf):
    """주어진 태그에 대해 TF-IDF 벡터를 생성하는 함수."""
    vector = {}
    for tag in tags:
        # 각 태그에 대해 IDF 값을 가져와 벡터를 만듭니다.
        vector[tag] = idf.get(tag, 0)
    return vector

def compute_cosine_similarity(vector_a, vector_b):
    """두 벡터 간의 코사인 유사도를 계산하는 함수."""
    common_tags = set(vector_a.keys()).union(set(vector_b.keys()))  # 두 벡터의 공통 태그
    vec_a = np.array([vector_a.get(tag, 0) for tag in common_tags])  # 벡터 A의 값
    vec_b = np.array([vector_b.get(tag, 0) for tag in common_tags])  # 벡터 B의 값
    # 코사인 유사도 계산
    return np.dot(vec_a, vec_b) / (np.linalg.norm(vec_a) * np.linalg.norm(vec_b))

def create_novel_vectors():
    """소설의 TF-IDF 벡터를 생성하는 함수."""
    global vectors
    novels = fetch_novels_and_tags()  # 소설과 태그 가져오기
    
    tag_document_count = {}  # 각 태그가 포함된 소설의 개수
    total_documents = len(novels)  # 총 소설 개수

    for novel in novels:
        tags = novel.get('tags', [])
        unique_tags = set(tags)  # 소설의 고유 태그 ID
        for tag in unique_tags:
            # 각 태그가 포함된 소설의 개수를 계산합니다.
            tag_document_count[tag] = tag_document_count.get(tag, 0) + 1
    idf = compute_idf(tag_document_count, total_documents)  # IDF 계산

    # 각 소설의 TF-IDF 벡터 생성
    vectors = [{
        'id': novel['id'],
        'vector': create_tf_idf_vector(novel['tags'], idf)
    } for novel in novels]

def get_similar_novels(target_id, top_n=5):
    """주어진 소설 ID에 대한 유사 소설을 찾는 함수."""
    global vectors
    if vectors is None:
        create_novel_vectors()  # 벡터가 생성되지 않았다면 생성
    
    # 타겟 소설의 벡터를 찾습니다.
    target_vector = next((v['vector'] for v in vectors if v['id'] == target_id), None)

    if target_vector is None:
        return []  # 타겟 소설을 찾지 못한 경우 빈 리스트 반환

    similarities = []  # 유사도 저장할 리스트
    for v in vectors:
        if v['id'] != target_id:  # 타겟 소설이 아닌 경우
            similarity = compute_cosine_similarity(target_vector, v['vector'])  # 유사도 계산
            similarities.append({
                'novel': next(n for n in novels if n['id'] == v['id']),  # 소설 정보
                'similarity': similarity  # 유사도
            })

    # 유사도 기준으로 내림차순 정렬
    similarities.sort(key=lambda x: x['similarity'], reverse=True)

    return similarities[:top_n]  # 상위 N개 소설 반환
