from gensim.summarization import summarize, keywords
from .models import Action, Post
import datetime
from django.utils import timezone
from textblob import TextBlob, taggers, Word
from django.contrib.contenttypes.models import ContentType
import inflect
import difflib


def summary(obj):
    len_article = len(obj.content.split())
    ratio = 0.2 if len_article < 1500 else 0.1
    try:
        summary_list = summarize(obj.content, ratio, split=True)
    except ValueError:
        return False
    blob = TextBlob(obj.content)
    key = keywords(obj.content)
    noun = blob.np_counts.items()
    # for key, value in noun:
    #     if ' ' not in key:
    #         print(key, value)
    # print(blob.sentiment, kblog)
    return summary_list


def tag_list(obj):
    p = inflect.engine()
    key = keywords(obj)
    key_list = list(key.replace('\n', ',').split(','))
    for item in key_list:
        common = difflib.get_close_matches(item, key_list)
        if len(common) > 1:
            for i in range(1, len(common)):
                key_list.remove(common[i])
                # print(i, common[i])
    for item in key_list:
        if ' ' in item:
            key_list.remove(item)
    for item in key_list:
        key_list.append(Word(item).lemma)
        key_list.remove(item)
    for item in key_list:
        if item.capitalize() in obj:
            key_list.remove(item)
            key_list.append(item.capitalize())
    for item in key_list:
        if item.upper() in obj:
            key_list.remove(item)
            key_list.append(item.upper())
    return key_list


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


