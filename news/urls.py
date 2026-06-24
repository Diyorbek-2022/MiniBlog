from django.urls import path, include  # include qo‘shildi
from .views import (
    NewsListView, post_detail, PostCreateView, PostUpdateView,
    PostDeleteView, IndexTemplateView, pageNotFound, AddCommentView,
    ContactView, CategoryListView, SearchListView
)

urlpatterns = [
    path('', IndexTemplateView.as_view(), name="home"),
    path('blog/', NewsListView.as_view(), name='post_list'),
    path('blog/<int:year>/<int:month>/<int:day>/<slug:post>/', post_detail, name="post_detail"),

    # CRUD uchun nomlarni bir xil qilish (post_create ishlatilgan)
    path('blog/create/', PostCreateView.as_view(), name="post_create"),  # 'post_new' emas
    path('blog/<int:pk>/edit/', PostUpdateView.as_view(), name="post_edit"),
    path('blog/<int:pk>/delete/', PostDeleteView.as_view(), name="post_delete"),
    path('blog/<int:pk>/comment/', AddCommentView.as_view(), name='add_comment'),

    # Contact (qo‘shildi)
    path('contact/', ContactView.as_view(), name='contact'),

    # Kategoriya va qidiruv
    path('category/<slug:cat_slug>/', CategoryListView.as_view(), name='category'),
    path('search/', SearchListView.as_view(), name='search'),

    # Django authentication (login/logout uchun)
    path('accounts/', include('django.contrib.auth.urls')),  # login, logout, password reset va h.k.
]

handler404 = pageNotFound