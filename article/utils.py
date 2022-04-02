
import datetime
from django.utils import timezone
from blog.models import Action
from django.contrib.contenttypes.models import ContentType
import inflect
import difflib


def create_action(user, verb, target=None):
    # ignore actions repeated within one min
    now = timezone.now()
    last_min = now-datetime.timedelta(seconds=60)
    # check similar action with in the last min
    similar_actions = Action.objects.filter(user_id=user.id,
                                            verb=verb,
                                            created__gte=last_min)
    if target:
        target_ct = ContentType.objects.get_for_model(target)
        similar_actions = similar_actions.filter(target_ct=target_ct,
                                                 target_id=target.id)
    if not similar_actions:
        action = Action(user=user, verb=verb, target=target)
        action.save()
        return True
    return False


# def post_ranking():
#     #     get post ranking dict
#     post_rankings = r.zrange('post_ranking', 0, -1, desc=True)[:5]
#     post_rankings_ids = [int(ids) for ids in post_rankings]
#     #     get most viewed post
#     most_viewed = list(Post.objects.filter(id__in=post_rankings_ids))
#     most_viewed.sort(key=lambda x: post_rankings_ids.index(x.id))
#     return most_viewed


