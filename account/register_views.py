from logging import exception

from django.contrib.auth.hashers import make_password
from django.shortcuts import render
from rest_framework import serializers, status, exceptions
from rest_framework.response import Response
from rest_framework.views import APIView

from account.models import UserInfo


class RegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)
    class Meta:
        model=UserInfo
        fields = ['username', 'password','confirm_password']
        extra_kwargs = {
            'id': {'read_only': True},
            'password': {'write_only': True}}

    def validate_password(self, value):
        return value

    def validate_confirm_password(self, value):
        password=self.initial_data.get('password')
        if password != value:
            raise exceptions.ValidationError("密码不一致")
        return value

class Register(APIView):
    def post(self, request):

        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data.pop('confirm_password')
            serializer.save()
            return Response({'code':1000,'data':'xxx'})
        return Response({'code':1001,'error':'注册失败','detail':serializer.errors})
# Create your views here.
