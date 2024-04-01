from django.db import models
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.dispatch import receiver

from .validators import validate_image_file_extension

def server_icon_upload_path(instance, filename):
    return f"server/{instance.id}/server_icons/{filename}"

def server_banner_upload_path(instance, filename):
    return f"server/{instance.id}/server_banner/{filename}"

def Catagory_icon_upload_path(instance, filename):
    return f"catagory/{instance.id}/catagory_icon/{filename}"

class Catagory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    icon = models.FileField(upload_to=Catagory_icon_upload_path, null=True, blank=True, validators=[validate_image_file_extension])


    def save(self, *args, **kwargs):
        if self.id:
            existing = get_object_or_404(Catagory, id=self.id)
            if existing.icon != self.icon:
                existing.icon.delete(save=False)

        super(Catagory, self).save(*args, **kwargs)

    @receiver(models.signals.pre_delete, sender="server.Catagory")
    def catagory_delete_files(sender, instance, **kwargs):
        for filed in instance._meta.fields:
            if filed.name == "icon":
                file = getattr(instance, filed.name)
                if file:
                    file.delete(save=False)

    def __str__(self):
        return str(self.name)

class Server(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='server_owner')
    catagory = models.ForeignKey(Catagory, on_delete=models.CASCADE, related_name='server_catagory')
    description = models.CharField(max_length = 250, blank=True, null=True)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='server_members')

    def __str__(self):
        return str(self.name)
    
class Channel(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='channel_owner')
    topic = models.CharField(max_length=250, blank=True, null=True)
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='channel_server')
    banner = models.ImageField(upload_to=server_banner_upload_path, null=True, blank=True, validators=[validate_image_file_extension])
    icon = models.ImageField(upload_to=server_icon_upload_path, null=True, blank=True, validators=[validate_image_file_extension])

    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        if self.id:
            existing = get_object_or_404(Catagory, id=self.id)
            if existing.icon != self.icon:
                existing.icon.delete(save=False)
            if existing.banner != self.banner:
                existing.banner.delete(save=False)

        super(Channel, self).save(*args, **kwargs)

    @receiver(models.signals.pre_delete, sender="server.Catagory")
    def catagory_delete_files(sender, instance, **kwargs):
        for field in instance._meta.fields:
            if field.name == "icon" or field.name == 'banner':
                file = getattr(instance, field.name)
                if file:
                    file.delete(save=False)

    def __str__(self):
        return self.name