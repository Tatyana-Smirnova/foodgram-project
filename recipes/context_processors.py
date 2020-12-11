from .models import ShopList, Tag


def get_shop_list(request):
    if request.user.is_authenticated:
        shop_list_count = ShopList.objects.filter(
            user=request.user
        ).count()
    else:
        shop_list_count = None
    return {'shop_list_count': shop_list_count}


def all_tags(request):
    all_tags = Tag.objects.all()
    return {'all_tags': all_tags}
