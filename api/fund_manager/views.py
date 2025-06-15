from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from api.institute.models import Institute
from api.institute.serializers import InstituteSerializer


class InstituteViewSet(viewsets.ModelViewSet):
    queryset = Institute.objects.all()
    serializer_class = InstituteSerializer
    permission_classes = [IsAdminUser]  # Only admin users can access this endpoint
