from django.core.paginator import Paginator
from django.conf import settings
from yatube import settings


def get_page_context(queryset,
                     request,
                     posts_on_page=settings.LATEST_POSTS_COUNT
                     ):
    paginator = Paginator(queryset, posts_on_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return {
        'paginator': paginator,
        'page_number': page_number,
        'page_obj': page_obj,
    }
