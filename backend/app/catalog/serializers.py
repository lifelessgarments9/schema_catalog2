from rest_framework import serializers

from app.catalog.models import Category, Device


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class DeviceSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    image = serializers.SerializerMethodField()
    documentation = serializers.SerializerMethodField()

    class Meta:
        model = Device
        fields = "__all__"

    def get_image(self, obj):
        request = self.context.get("request")
        if obj.image:
            return request.build_absolute_uri(obj.image.url)

        return None

    def get_documentation(self, obj):
        request = self.context.get("request")
        if obj.documentation:
            return request.build_absolute_uri(obj.documentation.url)

        return None