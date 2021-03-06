from django.shortcuts import render, redirect, get_object_or_404
from IPython import embed
from .models import Article, Comment, HashTag
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
# from accounts.models import User
from django.contrib.auth import get_user_model
from django.contrib import messages
from .forms import ArticleForm, CommentForm
from IPython import embed
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden

# Create your views here.
def index(request):
    articles = Article.objects.order_by('-id')
    context = {
        'articles' : articles
    }
    return render(request, 'articles/index.html',context)

# def new(request):
#     return render(request,'articles/new.html')


@login_required
def create(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
        # POST 요청 --> 검증 및 저장
            article_form = ArticleForm(request.POST, request.FILES)
            # embed()
            if article_form.is_valid():
            # 검증에 성공하면 저장하고,
                # title = article_form.cleaned_data.get('title')
                # content = article_form.cleaned_data.get('content')
                # article = Article(title=title, content=content)
                article = article_form.save(commit=False)
                article.user = request.user
                # 해시태그 저장 및 연결 작업
                article.save()
                for word in article.content.split():
                    if word[0] == '#':
                        hashtag,created = HashTag.objects.get_or_create(content=word[1:])
                        article.hashtags.add(hashtag)
                return redirect('articles:detail', article.pk)
            # else :
                # 다시 폼으로 돌아가 --> 중복되서 제거 !
        else:
        # GET 요청 -> Form
            article_form = ArticleForm()
        # GET -> 비어있는 Form context
        # POST -> 검증 실패시 에러메세지와 입력값 채워진 Form context
        context = {
            'article_form': article_form
        }
        return render(request, 'articles/form.html', context)
    else:
        messages.success(request, '로그인 후 이용해주세요')
        return redirect('accounts:login')

def detail(request,article_pk):
    # article = Article.objects.get(pk=article_pk)
    article = get_object_or_404(Article, pk=article_pk)
    comments = article.comment_set.all()
    comment_form = CommentForm()
    context = {
        'article':article,
        'comments' : comments,
        'comment_form' :comment_form
    }
    return render(request,'articles/detail.html',context)


@require_POST
def delete(request,article_pk):
    article = Article.objects.get(pk=article_pk)
    if article.user == request.user:
    # if request.method == 'POST':
        article.delete()
        messages.success(request, '글이 삭제되었습니다.')
        return redirect('articles:index')
    else:
        messages.warning(request, '글을 삭제할수 없습니다.')
        raise HttpResponseForbidden

    # else:
    #     return redirect('articles:detail',article.pk)


# def edit(request,article_pk):
#     article = Article.objects.get(pk=article_pk)
#     context = {
#         'article':article
#     }
#     return render(request,'articles/edit.html',context)

def update(request,article_pk):
    article = Article.objects.get(pk=article_pk)
    if article.user == request.user:
        if request.method =='POST':
            article_form = ArticleForm(request.POST, instance=article)
            if article_form.is_valid():
                article = article_form.save()
                article.hashtags.clear()
                for word in article.content.split():
                    if word[0] == '#':
                        hashtag,created = HashTag.objects.get_or_create(content=word[1:])
                        article.hashtags.add(hashtag)
                return redirect('articles:detail',article_pk)
        else:
            article_form = ArticleForm(instance=article)
        context = {
            'article_form' : article_form
        }
        return render(request,'articles/form.html',context)
    else:
        return HttpResponseForbidden

@login_required
@require_POST
def comment_create(request,article_pk):
    if request.user.is_authenticated:
        article = get_object_or_404(Article, pk=article_pk)
        # 1. modelform에 사용자 입력값 넣고
        comment_form = CommentForm(request.POST)
        # 2. 검증하고,
        if comment_form.is_valid():
        # 3. 맞으면 저장.
            # 3.1. 사용자 입력값으로 comment instance 생성 (저장은 x)
            comment = comment_form.save(commit=False)
            # 3-2. FK 넣고 저장
            comment.article = article
            comment.user = request.user
            comment.save()
            messages.success(request, '댓글이 생성되었습니다.')
        # 4. return redirect
        else:
            messages.success(request, '댓글 형식이 맞지 않습니다.')
        return redirect('articles:detail', article_pk)
    else:
        return HttpResponse('Unauthorized',status=401)

@require_POST
def comment_delete(request,article_pk,comment_pk):
    comment = Comment.objects.get(pk=comment_pk)
    if comment.user == request.user:
        comment.delete()
        messages.success(request, '댓글이 삭제되었습니다.')
        return redirect('articles:detail',article_pk)
    else:
        messages.warning(request, '남의댓글을 삭제할수 없습니다.')
    return HttpResponseForbidden

@login_required
def like(request, article_pk):
    if request.is_ajax():
        article = get_object_or_404(Article,pk=article_pk)
        user = request.user
        is_liked = True
        if user not in article.like_users.all():
            article.like_users.add(user)
            is_liked = True
        else:
            article.like_users.remove(user)
            is_liked = False
        return JsonResponse({'is_liked':is_liked,'like_count':article.like_users.count()})
    else:
        return HttpResponseForbidden

def hashtag(request, tag):
    hashtag = get_object_or_404(HashTag,content=tag)
    context = {
        'hashtag': hashtag
    }
    return render(request,'articles/hashtag.html',context)