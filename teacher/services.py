from lessonforum.models import NestedComment, Comment


def _load_messages_of_forum(messages_type, startswith, endswith, parent_message_id=0, lesson_id=0):
    if messages_type == "nested":
        comments = list(NestedComment.objects.filter(parent_comment_id=parent_message_id))
    else:  # messages_type == "parent"
        comments = list(Comment.objects.filter(lesson_id=lesson_id))

    if len(comments) <= endswith:
        no_more_messages = True
    else:
        no_more_messages = False

    if messages_type == "parent":
        comments.reverse()

    return comments[startswith:endswith], no_more_messages


def load_nested_messages_of_forum(parent_message_id, startswith, endswith):
    return _load_messages_of_forum("nested", startswith, endswith, parent_message_id=parent_message_id)


def load_parent_messages_of_forum(lesson_id, startswith, endswith):
    return _load_messages_of_forum("parent", startswith, endswith, lesson_id=lesson_id)