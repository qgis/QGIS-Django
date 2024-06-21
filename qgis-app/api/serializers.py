from base.validator import filesize_validator
from geopackages.models import Geopackage
from models.models import Model
from rest_framework import serializers
from sorl_thumbnail_serializer.fields import HyperlinkedSorlImageField
from styles.models import Style
from layerdefinitions.models import LayerDefinition
from wavefronts.models import Wavefront
from sorl.thumbnail import get_thumbnail
from django.conf import settings
from os.path import exists
from django.templatetags.static import static

class ResourceBaseSerializer(serializers.ModelSerializer):
    creator = serializers.ReadOnlyField(source="get_creator_name")
    resource_type = serializers.SerializerMethodField()
    resource_subtype = serializers.SerializerMethodField()
    thumbnail_full = serializers.ImageField(source="thumbnail_image")
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        fields = [
            "resource_type",
            "resource_subtype",
            "uuid",
            "name",
            "creator",
            "upload_date",
            "download_count",
            "description",
            "file",
            "thumbnail",
            "thumbnail_full"
        ]

    def validate(self, attrs):
        file = attrs.get("file")
        filesize_validator(file)
        return attrs

    def get_resource_type(self, obj):
        if self.Meta.model.__name__ == "Wavefront":
            return "3DModel"
        return self.Meta.model.__name__

    def get_thumbnail(self, obj):
        request = self.context.get('request')
        try:
            if obj.thumbnail_image and exists(obj.thumbnail_image.path):
                thumbnail = get_thumbnail(obj.thumbnail_image, "128x128", crop="center")
                if request is not None:
                    return request.build_absolute_uri(thumbnail.url)
                return thumbnail.url
        except Exception as e:
            pass

        # Return a full URL to a default image if no thumbnail exists or if there's an error
        default_url = static("images/qgis-icon-32x32.png")
        if request is not None:
            return request.build_absolute_uri(default_url)
        return default_url


class GeopackageSerializer(ResourceBaseSerializer):
    class Meta(ResourceBaseSerializer.Meta):
        model = Geopackage

    def get_resource_subtype(self, obj):
        return None


class ModelSerializer(ResourceBaseSerializer):
    class Meta(ResourceBaseSerializer.Meta):
        model = Model

    def get_resource_subtype(self, obj):
        return None


class StyleSerializer(ResourceBaseSerializer):
    resource_subtype = serializers.ReadOnlyField(source="get_style_type")

    class Meta(ResourceBaseSerializer.Meta):
        model = Style

class LayerDefinitionSerializer(ResourceBaseSerializer):
    class Meta(ResourceBaseSerializer.Meta):
        model = LayerDefinition

    def get_resource_subtype(self, obj):
        return None


class WavefrontSerializer(ResourceBaseSerializer):
    class Meta(ResourceBaseSerializer.Meta):
        model = Wavefront

    def get_resource_subtype(self, obj):
        return None