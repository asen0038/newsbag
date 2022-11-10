from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.http.response import HttpResponseServerError
from django.shortcuts import render, redirect, get_object_or_404
from newsbag_app.forms import Register, LibraryForm
from newsbag_app.models import *
from newsdataapi import NewsDataApiClient

from newsbag_app.utils.ArticleClass import ArticleClass
from newsbag_app.utils.summarizer import summarize
from newsbag_app.utils.nlp_scm import constructMatrix
from newsbag_app.utils.math_utils import threshold

logged_in = False


# TODO: Make a feature that uses google API to take in a search phrase and group and summarize news articles based on
#  their topic
def landing(request, category="world"):
    global logged_in
    if request.user.is_authenticated:
        logged_in = True

    if category == "logout":
        category = "world"

    apikey = "pub_58060ec39f6c03c32ea52fe263f9580b8efa"
    api = NewsDataApiClient(apikey=apikey)
    response = None
    if category == "search":
        query = request.GET.get('query')
        response = api.news_api(q=query, language="en")
    else:
        response = api.news_api(category=category, language="en")
    articles = response["results"]

    corpus = []
    titles = []
    imagePaths = []
    sources = []
    urls = []
    for article in articles:
        if article["content"] is not None:
            corpus.append(article["content"])

            if article["title"] is not None:
                titles.append(article["title"])
            else:
                titles.append("No Title")

            if article["image_url"] is not None:
                imagePaths.append(article["image_url"])
            else:
                imagePaths.append("https://i.ibb.co/7V0Zxcs/default.jpg")

            if article["source_id"] is not None:
                sources.append(article["source_id"])
                if article["link"] is not None:
                    sources.append(article["source_id"])
                    urls.append(article["link"])
                else:
                    sources.append("Source unavailable")
                    urls.append("...")
            else:
                sources.append("Source unavailable")
                urls.append("...")

    new_corpus = []
    for doc in corpus:
        sum_text = summarize(doc)
        new_corpus.append(sum_text)

    i = 0
    articles = []
    while i < len(new_corpus):
        a = ArticleClass(titles[i], new_corpus[i], imagePaths[i], sources[i], urls[i])
        articles.append(a)
        i = i + 1

    libraries = None
    if request.user.is_authenticated:
        libraries = Library.objects.filter(user=request.user)

    if request.method == "POST":
        libid = request.POST.get('cid')
        new_article = Article(title=request.POST.get('title'),
                              content=request.POST.get('content'),
                              image_path=request.POST.get('image_path'),
                              source_name=request.POST.get('source_name'),
                              source_link=request.POST.get('source_link'))
        new_article.save()
        library = get_object_or_404(Library, id=libid)
        libart = LibArt(library=library, article=new_article)
        libart.save()

    return render(request, 'newsbag_app/landing.html',
                  {'logged_in': logged_in, 'articles': articles, 'libraries': libraries})


def signup(request, id):
    global logged_in
    form = Register(request.POST)
    error = ""
    if form.is_valid():
        user = form.save()
        user.refresh_from_db()
        user.save()
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)
        login(request, user)
        logged_in = True
        return redirect("/collection/{}".format(user.id))
    else:
        form = Register()
        error = form.errors
    return render(request, 'newsbag_app/signup.html', {'form': form, "error": error, 'logged_in': logged_in})


def loginUser(request, id):
    global logged_in
    error = ""
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            login(request, user)
            logged_in = True
            return redirect("/collection/{}".format(user.id))
        else:
            error = "Invalid username or password."

    form = AuthenticationForm()
    return render(request, 'newsbag_app/login.html', {'form': form, "error": error, 'logged_in': logged_in})


def logoutUser(request, id):
    logout(request)
    global logged_in
    logged_in = False
    return redirect('/world')


def collection(request, id):
    global logged_in
    if request.method == "POST":
        c = request.POST.get('cid')
        library = get_object_or_404(Library, id=c)
        pairs = LibArt.objects.filter(library=library)
        for pair in pairs:
            if pair.article.links == 1:
                article = get_object_or_404(Article, id=pair.article.id)
                pair.delete()
                article.delete()
            else:
                pair.delete()
        library.delete()

    libraries = Library.objects.filter(user=request.user)
    return render(request, 'newsbag_app/collection.html', {'logged_in': logged_in, 'libraries': libraries})


def addNewLibrary(request):
    form = LibraryForm(request.POST or None)
    if form.is_valid():
        form.instance.user = request.user
        form.save()
        return redirect("/collection/{}".format(request.user.id))
    return render(request, 'newsbag_app/create.html', {'form': form})


def visitLibrary(request, id):
    if request.method == "POST":
        artid = request.POST.get('cid')
        article = get_object_or_404(Article, id=artid)
        pair = LibArt.objects.filter(article=article)
        for p in pair:
            p.delete()
        article.delete()

    library = get_object_or_404(Library, id=id)
    pairs = LibArt.objects.filter(library=library)
    articles = []
    for i in pairs:
        articles.append(i.article)

    one = False
    if len(articles) == 1:
        one = True

    return render(request, 'newsbag_app/library.html',
                  {'logged_in': logged_in, 'library': library, 'articles': articles, 'one': one})


def compare(request, lid, aid):
    left = []
    right = []
    library = get_object_or_404(Library, id=lid)
    article_compare = get_object_or_404(Article, id=aid)
    left.append(article_compare)
    pairs = LibArt.objects.filter(library=library)
    corpus = [article_compare.content]
    all_arts = [article_compare]
    for i in pairs:
        if i.article.id != article_compare.id:
            corpus.append(i.article.content)
            all_arts.append(i.article)

    result = constructMatrix(corpus)
    articles = result[0]
    matrix = result[1]
    scores = []
    index = 1
    while index < len(articles):
        score = matrix.inner_product(articles[0], articles[index], normalized=(True, True))
        scores.append(score.item())
        index = index + 1

    threshold_value = threshold(scores)
    c = 1
    while c < len(articles):
        score = matrix.inner_product(articles[0], articles[c], normalized=(True, True))
        if score < threshold_value:
            right.append(all_arts[c])
        else:
            left.append(all_arts[c])
        c = c + 1

    return render(request, 'newsbag_app/compare.html', {'library': library, 'left': left, 'right': right})
