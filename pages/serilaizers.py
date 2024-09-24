from pages.models import Pages
from rest_framework import serializers


class PagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pages
        fields = ["id", "page_url", "content", "show_in_menu",'deleted',"page_name",'show_in_footer']
