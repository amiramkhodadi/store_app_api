from rest_framework.pagination import PageNumberPagination

class TenPerPagePagination(PageNumberPagination):
    page_size = 10
    page_query_param = 'p' 


class TwentyPerPagePagination(PageNumberPagination):
    page_size = 20
    page_query_param = 'p'