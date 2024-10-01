from django.db import models

class Novel(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    views = models.BigIntegerField(default=0, blank=True, null=True)
    category = models.CharField(max_length=255, blank=True, null=True)

class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

class NovelTag(models.Model):
    novel = models.ForeignKey(Novel, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)