from django.urls import path,re_path
from .views import BookInfor,BookDetail

urlpatterns = [
    path('book/',BookInfor.as_view()),
    re_path('book/(\d+)',BookDetail.as_view(),),

]