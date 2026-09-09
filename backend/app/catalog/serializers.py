from rest_framework import serializers

from app.catalog.models import Category, Device


class CategorySerializer(serializers.ModelSerializer):
    specifications = serializers.SlugRelatedField(many=True,read_only=True,slug_field="name")

    class Meta:
        model = Category
        fields = ["id", "name", "specifications"]


class DeviceSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    image = serializers.ImageField(required=False)
    documentation = serializers.FileField(required=False)

    class Meta:
        model = Device
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get("request")

        if instance.image and request:
            data["image"] = request.build_absolute_uri(instance.image.url)
        if instance.documentation and request:
            data["documentation"] = request.build_absolute_uri(instance.documentation.url)

        return data