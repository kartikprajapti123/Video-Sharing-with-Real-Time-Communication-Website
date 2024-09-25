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
    
    page_url=models.CharField(max_length=100,unique=True,help_text="Example:-terms_and_condtion.... and make sure to user undercorse '_' not spaces")
    page_name = models.CharField(
    max_length=100,
    unique=True,
    help_text="The name to show for user to click"
)
    content=CKEditor5Field(config_name='extends')
    
    deleted=models.IntegerField(default=0)
    
    
    def __str__(self) :
        return self.page_url
    
    class Meta:
        verbose_name="Create New Page"
    
    
