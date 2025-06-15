from django.contrib.auth.models import User
from rest_framework import serializers

from api.fund_manager.models import FundManager
from api.institute.models import Institute


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class FundManagerSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    institute = serializers.PrimaryKeyRelatedField(queryset=Institute.objects.all())

    class Meta:
        model = FundManager
        fields = ['id', 'user', 'institute']
