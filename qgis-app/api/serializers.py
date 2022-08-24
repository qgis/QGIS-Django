from base.validator import filesize_validator
from geopackages.models import Geopackage
from models.models import Model
from rest_framework import serializers
from sorl_thumbnail_serializer.fields import HyperlinkedSorlImageField
from styles.models import Style


class ResourceBaseSerializer(serializers.ModelSerializer):
    creator = serializers.ReadOnlyField(source="get_creator_name")
    resource_type = serializers.SerializerMethodField()
    resource_subtype = serializers.SerializerMethodField()

    # A thumbnail image, sorl options and read-only
    thumbnail = HyperlinkedSorlImageField(
        "128x128", options={"crop": "center"}, source="thumbnail_image", read_only=True
    )

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
        ]

    def validate(self, attrs):
        file = attrs.get("file")
        filesize_validator(file)
        return attrs

    def get_resource_type(self, obj):
        return self.Meta.model.__name__


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
