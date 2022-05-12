from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User, Course, ChildCourse



class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Adding custom token
        token["user"] = user.email, user.name, user.status

        return token

class UserSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="show-user")
    class Meta:
        model = User
        fields = '__all__' #["url","name","status","email","password"]

    def create(self, validated_data):
        user = User(
            email=validated_data["email"], name=validated_data["name"], status=validated_data["status"])
        user.set_password(validated_data["password"])
        if validated_data["status"] == "teacher":
            user.is_teacher = True
        elif validated_data["status"] == "student":
            user.is_student = True
            
        user.save()

        return user
    
    def update(self,instance,validated_data):
        approved = validated_data.get("is_approved",instance.is_approved)
        rejected = validated_data.get("is_rejected",instance.is_rejected)
        if approved and rejected:
            raise serializers.ValidationError({"error":"You cannot approve and reject at one time"})
        else:
            instance.is_approved = validated_data.get("is_approved",instance.is_approved)
            instance.is_rejected = validated_data.get("is_rejected",instance.is_rejected)
            instance.save()
        return instance

class ChildCourseSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="course-detail")
    class Meta:
        model = ChildCourse
        fields = ["url","name"]
        
    def to_internal_value(self,data):
        useful_data = {}
        name = data.get("name",None)
        if name is None:
            raise serializers.ValidationError({"error": "You must provide with course name"})
        else:
            useful_data["name"] = name
            return super().to_internal_value(useful_data)
    
    def create(self,validated_data):
        user = self.context["request"].user
        
        if user.is_teacher and user.is_approved:
            child_course = ChildCourse(name=validated_data["name"])
            child_course.save()
            
            course,created = Course.objects.get_or_create(teacher=user)
            course.courses.add(child_course)
            course.save()
            return child_course

        elif user.is_teacher and not user.is_approved:
            raise serializers.ValidationError({"error":"You do not yet approved by Admin."})
        else:
            raise serializers.ValidationError({"error":"You cannot create course."})

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'
        depth = 1
        
    def to_representation(self,instance):
        ret = super().to_representation(instance)
        
        user = self.context["request"].user
        
        # for admins dashboard
        if user.is_superuser:
            return ret
        
        # for teachers dashboard
        elif user.is_teacher:
            courses = [course for course in instance.courses.all()]
            ret.pop("id")
            ret.pop("teacher")
            ret["courses"] = [(course.name,course.students.all().count()) for course in courses]
            return ret
        
        # for students dashboard
        else:
            ret.pop("id")
            ret["teacher"] = instance.teacher.name
            
            # this will store course names and students count
            courses = {}
            for idx,course in enumerate(instance.courses.all()):
                if user in course.students.all():
                    courses[user.student.values()[idx]["name"]] = course.students.all().count()
            ret["courses"] = courses
            return ret
