# from base.serializers import (ResourceBaseSerializer,
#                               ResourceThumbnailBaseSerializer)
#
# from geopackages.models import Geopackage
#
#
# class GeopackageSerializer(ResourceBaseSerializer):
#     class Meta(ResourceBaseSerializer.Meta):
#         model = Geopackage
#
#
# class GeopackageThumbnailSerializer(ResourceThumbnailBaseSerializer):
#     class Meta(ResourceThumbnailBaseSerializer.Meta):
#         model = Geopackage

# =============================================================================
from rest_framework import serializers
from sorl_thumbnail_serializer.fields import HyperlinkedSorlImageField

from base.validator import filesize_validator

from geopackages.models import Geopackage
from models.models import Model


class ResourceBaseSerializer(serializers.ModelSerializer):
    creator = serializers.ReadOnlyField(source='get_creator_name')

    # A thumbnail image, sorl options and read-only
    thumbnail = HyperlinkedSorlImageField(
        '128x128',
        options={"crop": "center"},
        source='thumbnail_image',
        read_only=True
    )

    class Meta:
        fields = ['id',
                  'name',
                  'creator',
                  'upload_date',
                  'download_count',
                  'description',
                  'file',
                  'thumbnail_image',
                  'thumbnail']

    def validate(self, attrs):
        file = attrs.get('file')
        filesize_validator(file)
        return attrs


class GeopackageSerializer(ResourceBaseSerializer):
    class Meta(ResourceBaseSerializer.Meta):
        model = Geopackage


class ModelSerializer(ResourceBaseSerializer):
    class Meta(ResourceBaseSerializer.Meta):
        model = Model
