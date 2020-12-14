from django.urls import path

from modelers.views import (ModelerCreateView,
                             ModelerDetailView,
                             ModelerUpdateView,
                             ModelerListView,
                             ModelerDeleteView,
                             ModelerUnapprovedListView,
                             ModelerRequireActionListView,
                             modeler_review,
                             modeler_download,
                             modeler_nav_content,)


urlpatterns = [
    #  Model
    path('', ModelerListView.as_view(), name='modeler_list'),
    path('add/', ModelerCreateView.as_view(), name='modeler_create'),
    path('<int:pk>/', ModelerDetailView.as_view(),
         name='modeler_detail'),
    path('<int:pk>/update/', ModelerUpdateView.as_view(),
         name='modeler_update'),
    path('<int:pk>/delete/', ModelerDeleteView.as_view(),
         name='modeler_delete'),
    path('<int:pk>/review/', modeler_review, name='modeler_review'),
    path('<int:pk>/download/', modeler_download,
         name='modeler_download'),

    path('unapproved/', ModelerUnapprovedListView.as_view(),
         name='modeler_unapproved'),
    path('require_action/', ModelerRequireActionListView.as_view(),
         name='modeler_require_action'),

    # JSON
    path('sidebarnav/', modeler_nav_content, name="modeler_nav_content"),
]
