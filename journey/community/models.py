from django.db import models

class Feed(models.Model):
    """피드 (게시글) 모델"""
    user = models.ForeignKey('user_manager.User', on_delete=models.CASCADE, related_name='feeds')
    content = models.TextField()
    view_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feed {self.id} by {self.user}"

class Comment(models.Model):
    """댓글 모델"""
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey('user_manager.User', on_delete=models.CASCADE, related_name='user_comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user} on {self.feed}"

class Like(models.Model):
    """피드 좋아요 모델"""
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey('user_manager.User', on_delete=models.CASCADE, related_name='user_likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('feed', 'user') # 사용자는 한 피드에 한 번만 좋아요 가능

    def __str__(self):
        return f"{self.user} likes {self.feed}"