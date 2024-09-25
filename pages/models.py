from django.db import models
from django_ckeditor_5.fields import CKEditor5Field

# Create your models here.
class Pages(models.Model):
    show_in_menu=models.BooleanField(default=False)
    show_in_footer=models.BooleanField(default=False)
    
    page_url=models.CharField(max_length=100,unique=True)
    page_name=models.CharField(max_length=100,unique=True)
    
    content=CKEditor5Field(config_name='extends')
    
    deleted=models.IntegerField(default=0)
    
    
    def __str__(self) :
        return self.page_url
    
    class Meta:
        verbose_name="Create New Page"
    
    
