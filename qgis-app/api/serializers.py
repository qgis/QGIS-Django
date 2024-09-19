from base.validator import filesize_validator
from geopackages.models import Geopackage
from models.models import Model
from rest_framework import serializers
from styles.models import Style, StyleType
from layerdefinitions.models import LayerDefinition
from wavefronts.models import WAVEFRONTS_STORAGE_PATH, Wavefront
from sorl.thumbnail import get_thumbnail
from django.conf import settings
from os.path import exists, join
from django.templatetags.static import static
from wavefronts.validator import WavefrontValidator

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from styles.file_handler import read_xml_style, validator as style_validator
from layerdefinitions.file_handler import get_provider, get_url_datasource, validator as layer_validator
import tempfile

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

    def validate(self, attrs):
        """
        Validate a style file.
        We need to check if the uploaded file is a valid XML file.
        Then, we upload the file to a temporary file, validate it
        and check if the style type is defined.
        """
        attrs = super().validate(attrs)
        file = attrs.get("file")

        if not file:
            raise ValidationError(_("File is required."))

        if file.size == 0:
            raise ValidationError(_("Uploaded file is empty."))
        try:
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                for chunk in file.chunks():
                    temp_file.write(chunk)
                temp_file.flush()

                with open(temp_file.name, 'rb') as xml_file:
                    style = style_validator(xml_file)
                    xml_parse = read_xml_style(xml_file)
                    if xml_parse:
                        self.style_type, created = StyleType.objects.get_or_create(
                            symbol_type=xml_parse["type"],
                            defaults={
                                "name": xml_parse["type"].title(),
                                "description": "Automatically created from '"
                                "'an uploaded Style file",
                            }
                        )

                    if not style:
                        raise ValidationError(
                            _("Undefined style type. Please register your style type.")
                        )
        finally:
            import os
            if temp_file and os.path.exists(temp_file.name):
                os.remove(temp_file.name)

        return attrs

class LayerDefinitionSerializer(ResourceBaseSerializer):
    class Meta(ResourceBaseSerializer.Meta):
        model = LayerDefinition

    def get_resource_subtype(self, obj):
        return None

    def validate(self, attrs):
        """
        Validate a qlr file.
        We need to check if the uploaded file is a valid QLR file.
        Then, we upload the file to a temporary file and validate it
        """
        attrs = super().validate(attrs)
        file = attrs.get("file")

        if not file:
            raise ValidationError(_("File is required."))

        if file.size == 0:
            raise ValidationError(_("Uploaded file is empty."))
        try:
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                for chunk in file.chunks():
                    temp_file.write(chunk)
                temp_file.flush()

                with open(temp_file.name, 'rb') as qlr_file:
                    layer_validator(qlr_file)
                    self.url_datasource = get_url_datasource(qlr_file)
                    self.provider = get_provider(qlr_file)


        finally:
            import os
            if temp_file and os.path.exists(temp_file.name):
                os.remove(temp_file.name)

        return attrs

class WavefrontSerializer(ResourceBaseSerializer):
    class Meta(ResourceBaseSerializer.Meta):
        model = Wavefront

    def get_resource_subtype(self, obj):
        return None

    def validate(self, attrs):
        attrs = super().validate(attrs)
        file = attrs.get("file")
        if file and file.name.endswith('.zip'):
            valid_3dmodel = WavefrontValidator(file).validate_wavefront()
            self.new_filepath = join(WAVEFRONTS_STORAGE_PATH, valid_3dmodel)
        return attrs