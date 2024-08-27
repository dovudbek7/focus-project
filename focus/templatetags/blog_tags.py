from django import template
from ..models import Post, Comment  # Import Comment model
from django.contrib.auth.models import User  # Import User model
from django.utils.safestring import mark_safe
import markdown
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
register = template.Library()


@register.simple_tag
def total_posts():
    return Post.published.count()


@register.simple_tag
def total_comments():
    return Comment.objects.count()


@register.simple_tag
def total_users():
    return User.objects.count()


@register.inclusion_tag('latest_posts.html')
def show_latest_posts(count=2):
    latest_posts = Post.published.order_by('-publish')[:count]
    return {'latest_posts': latest_posts}


@register.filter(name='markdown')
def markdown_format(text):
    return mark_safe(markdown.markdown(text))


@register.simple_tag
def total_posts_per_day(days=7):
    # Get today's date
    today = timezone.now().date()
    # Calculate the start date (7 days ago by default)
    start_date = today - timedelta(days=days)

    # Query to get the total number of posts per day in the last `days` days
    posts_by_day = Post.published.filter(publish__date__range=(start_date, today)) \
        .values('publish__date').annotate(total=Count('id')).order_by('publish__date')

    return posts_by_day