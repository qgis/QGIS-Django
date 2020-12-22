from django.urls import path

from models.views import (ModelCreateView,
                             ModelDetailView,
                             ModelUpdateView,
                             ModelListView,
                             ModelDeleteView,
                             ModelUnapprovedListView,
                             ModelRequireActionListView,
                             model_review,
                             model_download,
                             model_nav_content,)


urlpatterns = [
    #  Model
    path('', ModelListView.as_view(), name='model_list'),
    path('add/', ModelCreateView.as_view(), name='model_create'),
    path('<int:pk>/', ModelDetailView.as_view(),
         name='model_detail'),
    path('<int:pk>/update/', ModelUpdateView.as_view(),
         name='model_update'),
    path('<int:pk>/delete/', ModelDeleteView.as_view(),
         name='model_delete'),
    path('<int:pk>/review/', model_review, name='model_review'),
    path('<int:pk>/download/', model_download,
         name='model_download'),

    path('unapproved/', ModelUnapprovedListView.as_view(),
         name='model_unapproved'),
    path('require_action/', ModelRequireActionListView.as_view(),
         name='model_require_action'),

    # JSON
    path('sidebarnav/', model_nav_content, name="model_nav_content"),
]
