from rest_framework import viewsets, permissions, status
from rest_framework.response import Response

from api.fund_manager.models import FundManager
from api.fund_manager.serializers import FundManagerSerializer


class FundManagerViewSet(viewsets.ModelViewSet):
    queryset = FundManager.objects.all()
    serializer_class = FundManagerSerializer
    permission_classes = [permissions.IsAdminUser]  # restrict all CRUD to admin only

    def create(self, request, *args, **kwargs):
        user = request.data.get("user")
        if FundManager.objects.filter(user_id=user).exists():
            return Response({"error": "This user is already a FundManager."}, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)
