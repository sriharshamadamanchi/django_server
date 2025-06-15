from django.contrib.auth import authenticate, login, get_user_model, logout
from django.db.models import Q
from rest_framework import permissions
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

User = get_user_model()


class LoginAPIView(APIView):
    def post(self, request):
        identifier = request.data.get("username")  # can be username or email
        password = request.data.get("password")

        if not identifier or not password:
            return Response({"error": "Username and password required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_obj = User.objects.get(Q(username=identifier) | Q(email=identifier))
        except User.DoesNotExist:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        user = authenticate(username=user_obj.username, password=password)
        if user:
            login(request, user)
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                "message": "Login successful",
                "token": token.key,
                "user": {
                    "id": user.id,
                    "username": user.username,
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # Delete the user's token to log out
        try:
            request.user.auth_token.delete()
        except:
            return Response({"error": "Token not found"}, status=status.HTTP_400_BAD_REQUEST)

        logout(request)  # optional: logs out the session if used
        return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
