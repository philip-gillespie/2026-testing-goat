from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from lists.models import Item, List


# Create your views here.
def home_page(request: HttpRequest) -> HttpResponse:
    return render(request, "home.html")


def new_list(request: HttpRequest) -> HttpResponse:
    nulist = List.objects.create()
    Item.objects.create(text=request.POST["item_text"], list=nulist)
    return redirect(f"/lists/{nulist.id}/")


def view_list(request: HttpRequest, list_id: int) -> HttpResponse:
    our_list = List.objects.get(id=list_id)
    items = Item.objects.filter(list=our_list)
    return render(request, "list.html", {"list": our_list})


def add_item(request: HttpRequest, list_id: int) -> HttpResponse:
    our_list = List.objects.get(id=list_id)
    Item.objects.create(text=request.POST["item_text"], list=our_list)
    return redirect(f"/lists/{our_list.id}/")
