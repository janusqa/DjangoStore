from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination


# page=xxx
class DefaultPagePagination(PageNumberPagination):
    page_size = 10


# offset=xxx&limit=xxx
class DefaultOffsetPagination(LimitOffsetPagination):
    page_size = 10
