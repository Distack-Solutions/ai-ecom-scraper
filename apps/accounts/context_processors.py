from django.contrib.auth.models import User

# def get_user_group(request):
#     group_name = None
#     if request.user.is_authenticated:
#         group_name = request.user.groups.first().name if request.user.groups.exists() else None
#     print(group_name)
#     return {'user_group': group_name}


def get_user_group(request):
    group_names = []
    if request.user.is_authenticated:
        group_names = list(request.user.groups.all().values_list('name', flat=True))
    return {'user_groups': group_names}
