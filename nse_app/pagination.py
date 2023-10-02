
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class MyPaginationClass(PageNumberPagination):
    page_size = 10 
    page_size_query_param = 'page_size'
    max_page_size = 100  

    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'data': data
        })

    def get_page_size(self, request):
        page_size = request.query_params.get(self.page_size_query_param)
        if page_size is not None:
            try:
                page_size = int(page_size)
                if page_size > 0 and (not self.max_page_size or page_size <= self.max_page_size):
                    return page_size
            except (TypeError, ValueError):
                pass
        return self.page_size
