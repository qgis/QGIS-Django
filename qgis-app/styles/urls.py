from django.urls import path

from styles.views import (StyleListView,
                          StyleCreateView,
                          StyleDetailView,
                          StyleDeleteView,
                          StyleUpdateView,
                          StyleUnapprovedListView,
                          StyleRequireActionListView,
                          StyleByTypeListView,
                          StyleDownloadView,
                          StyleReviewView,
                          style_nav_content,
                          style_type_list)

urlpatterns = [
    path('', StyleListView.as_view(), name='style_list'),
    path('add/', StyleCreateView.as_view(), name='style_create'),
    path('<int:pk>/', StyleDetailView.as_view(), name='style_detail'),
    path('<int:pk>/download/', StyleDownloadView.as_view(),
         name='style_download'),
    path('<int:pk>/delete/', StyleDeleteView.as_view(), name='style_delete'),
    path('<int:pk>/update/', StyleUpdateView.as_view(), name='style_update'),

    path('unapproved/', StyleUnapprovedListView.as_view(),
         name='style_unapproved'),
    path('require_action/', StyleRequireActionListView.as_view(),
         name='style_require_action'),
    path('types/<style_type>/', StyleByTypeListView.as_view(),
         name='style_by_type'),
    path('<int:pk>/review/', StyleReviewView.as_view(), name='style_review'),

    # JSON
    path('sidebarnav/', style_nav_content, name="style_nav_content"),
    path('sidebarnav_type/', style_type_list, name="style_nav_typelist"),
]
