from api.permissions import IsHasAccessOrReadOnly
from rest_framework import generics, mixins, permissions
from drf_multiple_model.views import ObjectMultipleModelAPIView

from geopackages.models import Geopackage
from models.models import Model

from api.serializers import GeopackageSerializer, ModelSerializer


class ResourceAPIList(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, *args, **kwargs):
        geopackage = Geopackage.approved_objects.all()
        model = Model.approved_objects.all()

        context = {
            "request": request,
        }

        geopackage_serializer = GeopackageSerializer(
            geopackage, many=True, context=context
        )
        model_serializer = ModelSerializer(
            model, many=True, context=context
        )

        response = (
            geopackage_serializer.data + model_serializer.data
        )
        return Response(response)




# class ResourceAPIDetail(generics.RetrieveUpdateAPIView):
#     permission_classes = [permissions.IsAuthenticatedOrReadOnly,
#                           IsHasAccessOrReadOnly]
#     http_method_names = ['get', 'put']
#
#     def get_queryset(self):
#         """Return detail """
#         qs = self.model.approved_objects.all()
#         return qs
#
#     def perform_update(self, serializer):
#         serializer.save(approved=False, require_action=False)

#
# class ReasourceAPIDownload(generics.ListAPIView):
#     def get(self, request, pk, format=None):
#         object = self.model.approved_objects.get(id=pk)
#         object.increase_download_counter()
#         object.save()
#         # zip the resource and license.txt
#         zipfile = zipped_with_license(object.file.file.name, object.name)
#
#         response = HttpResponse(
#             zipfile.getvalue(), content_type="application/x-zip-compressed")
#         response['Content-Disposition'] = 'attachment; filename=%s.zip' % (
#             slugify(object.name, allow_unicode=True)
#         )
#         return response