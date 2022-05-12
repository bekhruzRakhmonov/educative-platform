from django.contrib import admin
from .models import User,Course,ChildCourse

class UserAdmin(admin.ModelAdmin):
    list_display = ('email','name','status',)

class CourseAdmin(admin.ModelAdmin):
    list_display = ('teacher',)

class ChildCourseAdmin(admin.ModelAdmin):
    list_display = ('name','created_at','is_active',)

admin.site.register(User,UserAdmin)
admin.site.register(Course,CourseAdmin)
admin.site.register(ChildCourse,ChildCourseAdmin)