from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import BookInfo


class BookInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model=BookInfo
        fields='__all__'


class BookInfor(APIView):
    #获取所有书籍
    def get(self,request):
        book_list=BookInfo.objects.all()
        serializer=BookInfoSerializer(book_list,many=True)
        return Response(serializer.data)
    def post(self,request):
        serializers=BookInfoSerializer(data=request.data)
        if serializers.is_valid():
            serializers.save()
            return Response({'code': 1000, 'data': '书籍添加成功'})
        return Response({'code': 1001, 'error': '书籍添加错误', 'detail': serializers.errors})

class BookDetail(APIView):
    #获取指定书籍信息
    def get(self, request, id):
        book=BookInfo.objects.get(pk=id)
        #序列化传参instance
        ser=BookInfoSerializer(instance=book,many=False)
        return Response(ser.data)
    #删除指定数据
    def delete(self,request,id):
        book=BookInfo.objects.get(pk=id)
        book.delete()
        return Response({'code': 1000, 'msg': '书籍删除成功'}, status=status.HTTP_200_OK)
    #修改指定书籍信息
    def put(self,request,id):
        book=BookInfo.objects.get(pk=id)
        #拿指定书籍，进行修改信息
        ser=BookInfoSerializer(instance=book,data=request.data)
        if ser.is_valid():
            BookInfo.objects.filter(pk=id).update(**ser.validated_data)
            return Response(ser.data)
        return Response(ser.errors)

