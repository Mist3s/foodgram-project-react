from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    """Пагинация для рецептов с параметром 'limit'."""
    page_size = 10
    page_size_query_param = 'limit'
