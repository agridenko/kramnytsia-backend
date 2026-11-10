from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import RegisterSerializer
from .throttles import LoginRateThrottle


class RegisterView(generics.CreateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                },
                "message": "Користувач успішно зареєстрований"
            },
            status=status.HTTP_201_CREATED
        )


class CustomTokenObtainPairView(TokenObtainPairView):
    throttle_classes = [LoginRateThrottle]
