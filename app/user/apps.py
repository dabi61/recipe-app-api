from django.apps import AppConfig

#Kế thừa AppConfig 
class UserConfig(AppConfig):
    #Tự động tăng
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user'
