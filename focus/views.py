from datetime import timedelta, timezone

from django.contrib.auth import authenticate, login, logout
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView, DetailView, FormView
from django.contrib import messages
from django.utils import timezone
from .forms import *
from django.contrib.auth import views
from focus.forms import LoginForm, SignupForm


def home(request):
    recent_posts = Post.published.order_by('-publish')[:5]  # Fetch latest 5 posts
    return render(request, 'index.html', {'recent_posts': recent_posts})


def post_statistics_view(request):
    today = timezone.now().date()
    start_date = today - timedelta(days=7)

    posts_by_day = Post.published.filter(publish__date__range=(start_date, today)) \
        .values('publish__date').annotate(total=Count('id')).order_by('publish__date')
    recent_posts = Post.published.order_by('-publish')[:5]
    chart_data = [
        {'y': post['publish__date'].strftime('%Y-%m-%d'), 'a': post['total']}
        for post in posts_by_day
    ]

    return render(request, 'index.html', {'chart_data': chart_data, 'recent_posts': recent_posts})


class PostDetailView(DetailView, FormView):
    model = Post
    template_name = 'post-detail.html'
    context_object_name = 'detail'
    form_class = CommentForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = self.get_form()

        post = self.get_object()

        post_tags_ids = post.tags.values_list('id', flat=True)
        similar_posts = Post.published.filter(tags__in=post_tags_ids) \
            .exclude(id=post.id)
        similar_posts = similar_posts.annotate(same_tags=Count('tags')) \
                            .order_by('-same_tags', '-publish')[:4]

        context['similar_posts'] = similar_posts

        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = self.get_object()
            comment.save()
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        self.object = self.get_object()
        return super().form_valid(form)

    def get_object(self):
        year = self.kwargs['year']
        month = self.kwargs['month']
        day = self.kwargs['day']
        slug = self.kwargs['slug']

        return get_object_or_404(
            Post,
            status=Post.Status.PUBLISHED,
            slug=slug,
            publish__year=year,
            publish__month=month,
            publish__day=day,
        )

    def get_success_url(self):
        return reverse_lazy('focus:post_details', kwargs={
            'year': self.object.publish.year,
            'month': self.object.publish.month,
            'day': self.object.publish.day,
            'slug': self.object.slug,
        })


def post_list(request):
    posts = Post.published.all()
    return render(request, 'table-bootstrap-basic.html', {'posts': posts})


def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            form.save_m2m()
            return redirect('focus:post-list')
    else:
        form = PostForm()
    return render(request, 'form-element.html', {'form': form})


def post_update(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = UpdatePostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('focus:post-list')  # Redirect to home or the relevant page
    else:
        form = UpdatePostForm(instance=post)
    return render(request, 'form-element.html', {'form': form, 'post': post})


def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        post.delete()
        return redirect('focus:post-list')  # Redirect after deleting the post
    return render(request, 'confirm.html', {'post': post})


class FormBasicView(TemplateView):
    template_name = 'form.html'


class PasswordChangeView(views.PasswordChangeView):
    success_url = reverse_lazy("focus:password_change_done")


class PasswordResetView(views.PasswordResetView):
    success_url = reverse_lazy("focus:password_reset_done")


class PasswordResetConfirmView(views.PasswordResetConfirmView):
    success_url = reverse_lazy("focus:password_reset_complete")


def user_signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('focus:login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SignupForm()

    return render(request, 'accounts/page-register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            user_2 = authenticate(request, email=username, password=password)
            if user or user_2:
                login(request, user)
                return redirect('focus:home')
            else:
                messages.error(request, 'Invalid username or password.')
                return redirect('focus:login')
        else:
            messages.error(request, 'Invalid form data.')
            return redirect('focus:login')
    form = LoginForm()
    return render(request, 'accounts/page-login.html', {'form': form})


def user_logout(request):
    logout(request)
    messages.success(request, 'Successfully logged out.')
    return redirect('focus:login')
