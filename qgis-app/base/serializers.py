from rest_framework import serializers
from sorl_thumbnail_serializer.fields import HyperlinkedSorlImageField

from base.validator import filesize_validator


class ResourceBaseSerializer(serializers.HyperlinkedModelSerializer):
    creator = serializers.ReadOnlyField(source='get_creator_name')

    class Meta:
        fields = ['url',
                  'id',
                  'name',
                  'creator',
                  'upload_date',
                  'download_count',
                  'description',
                  'file',
                  'thumbnail_image']

    def validate(self, attrs):
        file = attrs.get('file')
        filesize_validator(file)
        return attrs


class ResourceThumbnailBaseSerializer(ResourceBaseSerializer):

    class Meta:
        fields = ResourceBaseSerializer.Meta.fields + ['thumbnail']

    # A thumbnail image, sorl options and read-only
    thumbnail = HyperlinkedSorlImageField(
        '128x128',
        options={"crop": "center"},
        source='thumbnail_image',
        read_only=True
    )
