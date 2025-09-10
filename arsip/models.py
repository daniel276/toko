from django.contrib.auth.models import User
from django.db import models
from django.conf import settings

# Create your models here.

class Arsip(models.Model):

    class Meta:
        ordering = ['nota_date'] # TODO CHANGE THIS TOO ASCENDING LATER

    userUploader = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='userUploader')
    uploadDateTime = models.DateTimeField(auto_now=True)
    nota_previous_id = models.ForeignKey('Arsip', on_delete=models.CASCADE, null=True, blank=True, related_name='previous_id')
    nota_receipt_id = models.CharField(max_length=10, null=True, blank=True)
    nota_cust_name = models.CharField(max_length=100)
    nota_date = models.DateField(name="nota_date")
    nota_image_file = models.ImageField(upload_to="nota_image_file/", null=True, blank=True)
    nota_notes = models.TextField(max_length=400, null=True, blank=True)
    ganti_nota = models.BooleanField(default=False)
    nota_sudah_diambil = models.BooleanField(default=False)
    nota_sudah_diambil_dateTime = models.DateTimeField(blank=True, null=True)
    nota_sudah_diambil_signer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.nota_cust_name


