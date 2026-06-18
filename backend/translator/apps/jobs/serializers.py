from rest_framework import serializers
from .models import TranslationJob

class TranslationJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = TranslationJob
        fields = [
            'input_file', 'source_lang', 'target_lang', 'created_at',
        ]