from pages.models import Pages,FanPages,SimultaneouslyPages
from rest_framework import serializers


class PagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pages
        fields = ["id", "page_url", "content", "show_in_menu",'deleted',"page_name",'show_in_footer']



class FanPagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = FanPages
        fields = ["id", "page_url", "content", "show_in_menu",'deleted',"page_name",'show_in_footer']


class SimultaneouslyPagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimultaneouslyPages
        fields = ["id", "page_url", "content", "show_in_menu",'deleted',"page_name",'show_in_footer']

