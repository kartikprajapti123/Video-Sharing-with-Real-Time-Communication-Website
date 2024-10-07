from django.db import models
from django_ckeditor_5.fields import CKEditor5Field

# Create your models here.
class Pages(models.Model):
    show_in_menu = models.BooleanField(
    default=False,
    help_text="Select to display this page in the menu bar."
)

    show_in_footer = models.BooleanField(
        default=False,
        help_text="Select to display this page in the footer."
    )
    
    page_url=models.CharField(max_length=100,unique=True,help_text="Example:-terms_and_condtion  for this url https://www.bmy.fan/pages/terms_and_condition and make suer to underscore '_' or dess '-' ")
    page_name = models.CharField(
    max_length=100,
    unique=True,
    help_text="exmaple:- terms and condition "
)
    content=CKEditor5Field(config_name='extends')
    
    deleted=models.IntegerField(default=0,help_text="This is for soft delete '1' for delete and '0' for not to delete  ")
    
    
    def __str__(self) :
        return self.page_url
    
    class Meta:
        verbose_name="Creator's Page"
    
    

class FanPages(models.Model):
    show_in_menu = models.BooleanField(
    default=False,
    help_text="Select to display this page in the menu bar."
)

    show_in_footer = models.BooleanField(
        default=False,
        help_text="Select to display this page in the footer."
    )
    
    page_url=models.CharField(max_length=100,unique=True,help_text="Example:-terms_and_condtion  for this url https://www.bmy.fan/pages/terms_and_condition and make suer to underscore '_' or dess '-' ")
    page_name = models.CharField(
    max_length=100,
    unique=True,
    help_text="exmaple:- terms and condition "
)
    content=CKEditor5Field(config_name='extends')
    
    deleted=models.IntegerField(default=0,help_text="This is for soft delete '1' for delete and '0' for not to delete  ")
    
    
    def __str__(self) :
        return self.page_url
    
    class Meta:
        verbose_name="Fan's Page"
    
    


class SimultaneouslyPages(models.Model):
    show_in_menu = models.BooleanField(
    default=False,
    help_text="Select to display this page in the menu bar."
)

    show_in_footer = models.BooleanField(
        default=False,
        help_text="Select to display this page in the footer."
    )
    
    page_url=models.CharField(max_length=100,unique=True,help_text="Example:-terms_and_condtion  for this url https://www.bmy.fan/pages/terms_and_condition and make suer to underscore '_' or dess '-' ")
    page_name = models.CharField(
    max_length=100,
    unique=True,
    help_text="exmaple:- terms and condition "
)
    content=CKEditor5Field(config_name='extends')
    
    deleted=models.IntegerField(default=0,help_text="This is for soft delete '1' for delete and '0' for not to delete  ")
    
    
    def __str__(self) :
        return self.page_url
    
    class Meta:
        verbose_name="Simultaneously_Pages (Pages for both creator's and fan's)"
        verbose_name_plural="Simultaneously_Pages (Pages for both creator's and fan's)"
        
    
    
