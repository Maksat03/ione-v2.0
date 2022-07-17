from django.db import models


class Comment(models.Model):
    user = models.ForeignKey("user.User", on_delete=models.CASCADE)
    lesson = models.ForeignKey("courses.CompletedLesson", on_delete=models.CASCADE, related_name="comments")
    comment = models.TextField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.comment


class NestedComment(models.Model):
    user = models.ForeignKey("user.User", on_delete=models.CASCADE)
    parent_comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="nested_comments")
    comment = models.TextField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.comment
