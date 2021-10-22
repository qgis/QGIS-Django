from django.urls import path

from wavefronts.views import (WavefrontCreateView,
                              WavefrontDetailView,
                              WavefrontDetailWithViewerView,
                              WavefrontUpdateView,
                              WavefrontListView,
                              WavefrontDeleteView,
                              WavefrontUnapprovedListView,
                              WavefrontRequireActionListView,
                              WavefrontReviewView,
                              WavefrontDownloadView,
                              wavefront_nav_content,
                              wavefront_obj_file)


urlpatterns = [
    #  Wavefront
    path('', WavefrontListView.as_view(), name='wavefront_list'),
    path('add/', WavefrontCreateView.as_view(), name='wavefront_create'),
    path('<int:pk>/', WavefrontDetailView.as_view(),
         name='wavefront_detail'),
    path('<int:pk>/viewer/', WavefrontDetailWithViewerView.as_view(),
         name='wavefront_viewer'),
    path('<int:pk>/update/', WavefrontUpdateView.as_view(),
         name='wavefront_update'),
    path('<int:pk>/delete/', WavefrontDeleteView.as_view(),
         name='wavefront_delete'),
    path('<int:pk>/review/', WavefrontReviewView.as_view(),
         name='wavefront_review'),
    path('<int:pk>/download/', WavefrontDownloadView.as_view(),
         name='wavefront_download'),
    path('<int:pk>/file/', wavefront_obj_file,
         name='wavefront_file'),

    path('unapproved/', WavefrontUnapprovedListView.as_view(),
         name='wavefront_unapproved'),
    path('require_action/', WavefrontRequireActionListView.as_view(),
         name='wavefront_require_action'),

    # JSON
    path('sidebarnav/', wavefront_nav_content, name="wavefront_nav_content"),
]