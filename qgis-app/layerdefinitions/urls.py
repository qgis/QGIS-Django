from django.urls import path
from layerdefinitions.views import (
    LayerDefinitionCreateView,
    LayerDefinitionDeleteView,
    LayerDefinitionDetailView,
    LayerDefinitionDownloadView,
    LayerDefinitionListView,
    LayerDefinitionRequireActionListView,
    LayerDefinitionReviewView,
    LayerDefinitionUnapprovedListView,
    LayerDefinitionUpdateView,
    layerdefinition_nav_content,
)

urlpatterns = [
    #  GeoPackage
    path("", LayerDefinitionListView.as_view(), name="layerdefinition_list"),
    path("add/", LayerDefinitionCreateView.as_view(), name="layerdefinition_create"),
    path(
        "<int:pk>/", LayerDefinitionDetailView.as_view(), name="layerdefinition_detail"
    ),
    path(
        "<int:pk>/update/",
        LayerDefinitionUpdateView.as_view(),
        name="layerdefinition_update",
    ),
    path(
        "<int:pk>/delete/",
        LayerDefinitionDeleteView.as_view(),
        name="layerdefinition_delete",
    ),
    path(
        "<int:pk>/review/",
        LayerDefinitionReviewView.as_view(),
        name="layerdefinition_review",
    ),
    path(
        "<int:pk>/download/",
        LayerDefinitionDownloadView.as_view(),
        name="layerdefinition_download",
    ),
    path(
        "unapproved/",
        LayerDefinitionUnapprovedListView.as_view(),
        name="layerdefinition_unapproved",
    ),
    path(
        "require_action/",
        LayerDefinitionRequireActionListView.as_view(),
        name="layerdefinition_require_action",
    ),
    # JSON
    path(
        "sidebarnav/", layerdefinition_nav_content, name="layerdefinition_nav_content"
    ),
]
