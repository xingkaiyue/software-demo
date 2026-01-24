import uuid
from . import models
from rest_framework import serializers, status, exceptions
from rest_framework.response import Response
from rest_framework.views import APIView
from account.models import UserInfo



class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model=models.UserInfo
        fields = ['username', 'password']




class Login(APIView):

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'code':1001,'error':'校验失败','detail':serializer.errors})

        instance=models.UserInfo.objects.filter(**serializer.validated_data).first()
        if not instance:
            return Response({'code':1001,'error':'用户名或密码错误','detail':serializer.errors})

        #生成token
        token=str(uuid.uuid4())
        instance.token=token
        instance.save()

        return Response({'code':1001,'token':token})



