from rest_framework import views
from rest_framework import generics
from rest_framework import authentication, permissions, status, reverse
from rest_framework.response import Response

from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import UserSerializer, CustomTokenObtainPairSerializer, CourseSerializer, ChildCourseSerializer
from .models import User,Course,ChildCourse

import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class SignUp(views.APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data,context={"request":request})
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data)

class Login(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

# easy way
# class ShowUserById(generics.RetrieveUpdateAPIView):
#     serializer_class = UserSerializer
#     queryset = User.objects.all()

class AdminNotification(views.APIView):
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request, *args, **kwargs):
        # filter not approved teachers
        queryset = User.objects.filter(status="teacher")
        serializer = UserSerializer(queryset,many=True,context={"request":request})
        return Response(serializer.data)

# this will show admin users by its id 
# admin can approve or reject user by sending patch request
class ShowUserById(generics.RetrieveUpdateAPIView): 
    permission_classes = [permissions.IsAdminUser]
    
    def get_object(self,pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExists:
            return Http404 
    
    def get(self,request,pk):
        user = self.get_object(pk)
        serializer = UserSerializer(user,many=False,context={"request":request})
        return Response(serializer.data)

    # Admin will send patch request to approve or reject a teacher
    def patch(self,request,pk,format=None):
        user = self.get_object(pk)
        serializer = UserSerializer(user,data=request.data,many=False,partial=True,context={"request":request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors,status.HTTP_400_BAD_REQUEST)

class Dashboard(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if request.user.is_superuser:
            logger.info("User is Admin.")
            queryset = Course.objects.all()
            # serializers.py
            serializer = CourseSerializer(queryset,many=True,context={"request":request})
            return Response(serializer.data)
        elif request.user.is_teacher:
            logger.info("User is Teacher")
            queryset = Course.objects.filter(teacher=request.user)
            serializer = CourseSerializer(queryset,many=True,context={"request":request})
            return Response(serializer.data)

        else:
            logger.info("User is Student")
            courses = Course.objects.all()
            serializer = CourseSerializer(courses,many=True,context={"request":request})
            return Response(serializer.data)

class CreateCourse(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChildCourseSerializer
    
class JoinAndLeaveCourse(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self,request,*args,**kwargs):
        queryset = ChildCourse.objects.all()
        serializer = ChildCourseSerializer(queryset,many=True,context={"request":request})
        return Response(serializer.data)
    
    def get_object(self,pk):
        try:
            course = ChildCourse.objects.get(pk=pk)
            return {"course":course,"response":Response(status=status.HTTP_200_OK)}
        except ChildCourse.DoesNotExists:
            return {"response":Response(status=status.HTTP_404_NOT_FOUND)}
    
    def post(self,request,*args,**kwargs):
        pk = kwargs.get("pk",None)
        res = self.get_object(pk)
        response = res.get("response",None)
        
        if response.status_code == status.HTTP_200_OK:
            course = res.get("course",None)
            
            if course is not None:
                # if student have not yet taken this course it will append
                # the student to student's list
                if request.user not in course.students.all():
                    course.students.add(request.user)
                else:
                    return Response({"error":"You have already  joined this course"},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error": "Something went wrong."},status=status.HTTP_400_BAD_REQUEST)
            return Response({"success": "You succesfully joined this course"},status=status.HTTP_201_CREATED)
    def delete(self,request,*args,**kwargs):
        pk = kwargs.get("pk",None)
        obj = self.get_object(pk)
        response = obj.get("response",None)
        
        if response.status_code == status.HTTP_200_OK:
            course = obj.get("course",None)
            
            if course is not None:
                # this will remove the student from list
                if request.user in course.students.all():
                    course.students.remove(request.user)
                else:
                    return Response({"error":"You have not yet joined this course"},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error": "Something went wrong."},status=status.HTTP_400_BAD_REQUEST)
            return Response({"success": "You succesfully left this course"},status=status.HTTP_200_OK)