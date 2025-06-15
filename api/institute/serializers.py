from rest_framework import serializers

from api.institute.models import Institute


class InstituteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institute
        fields = ['id', 'name', 'created_at']
