from django.db import models
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from mdeditor.fields import MDTextField
from .managers import PostManager
from taggit.managers import TaggableManager


class BaseModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(BaseModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-updated']
        indexes = [models.Index(fields=['-updated'])]

    def get_absolute_url(self):
        return reverse('exam:category', args=[self.pk])


class Post(BaseModel):
    class Status(models.TextChoices):
        DRAFT = 'DF', 'Draft'
        PUBLISHED = 'PB', 'Published'

    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique_for_date='publish')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    body = MDTextField(null=True, blank=True)
    category = models.ManyToManyField(Category, related_name='posts', blank=True)
    publish = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=2, choices=Status.choices, default=Status.DRAFT)
    objects = models.Manager()
    published = PostManager()
    tags = TaggableManager()

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('focus:post_details', args=[self.publish.year, self.publish.month, self.publish.day, self.slug])

    class Meta:
        ordering = ['-publish']
        indexes = [
            models.Index(fields=['-publish']),
        ]

class Comment(BaseModel):
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    active = models.BooleanField(default=True)
    publish = models.DateTimeField(default=timezone.now)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')

    def __str__(self):
        return f'Comment by {self.name} on {self.post.title}'

    class Meta:
        ordering = ['-updated']
        indexes = [
            models.Index(fields=['-updated']),
            models.Index(fields=['-publish']),
        ]

class About(BaseModel):
    title = models.CharField(max_length=255)
    body = MDTextField(null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-updated']
        indexes = [
            models.Index(fields=['-updated']),
        ]

