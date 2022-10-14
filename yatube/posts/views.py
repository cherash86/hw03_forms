from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post, User


NUM = 10


def index(request):
    post_list = Post.objects.all().order_by('-pub_date')
    paginator = Paginator(post_list, NUM)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'posts': post_list,
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()[:NUM]
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'posts': posts,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


# код запроса к модели и создание словаря контекста
def profile(request, username):
    author = User.objects.get(username=username)
    authors_posts = Post.objects.filter(author=author)
    number_of_posts = authors_posts.count()
    paginator = Paginator(authors_posts, NUM)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'author': author,
        'authors_posts': authors_posts,
        'number_of_posts': number_of_posts,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post_info = get_object_or_404(Post, pk=post_id)
    number_of_posts = post_info.author.posts.count()
    context = {
        'post_info': post_info,
        'number_of_posts': number_of_posts,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    if request.method == 'POST':
        #  Создаём экземпляр формы из данных POST
        form = PostForm(request.POST)
        #  Проверка данных формы, валидация
        if form.is_valid():
            #  Создаем, но не сохраняем экземпляр формы
            instance = form.save(commit=False)
            # Задаём дополнительное обязательное поле формы
            instance.author_id = request.user.id
            #  Сохраняем экземпляр формы
            instance.save()
            user_name = request.user.username
            #  Перенаправляем автора на страницу своего профайла
            return redirect('posts:profile', user_name)
        return render(request, 'posts/create_post.html', {'form': form})
    form = PostForm()
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    is_edit = True
    user_name = request.user.get_username()
    form = PostForm(request.POST or None, instance=post)
    if request.method == 'GET':
        #  Если редактирует не автор
        if user_name != post.author.username:
            # Перенаправляем на страницу просмотра поста
            return redirect('posts:post_detail', post.id)
    elif request.method == 'POST':
        if form.is_valid():
            form.save()
        return redirect('posts:post_detail', post.id)

    context = {
        'form': form,
        'is_edit': is_edit,
        'post': post,
    }
    return render(request, 'posts/create_post.html', context)
