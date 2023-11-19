from rest_framework import serializers

from .models import FileChunk

from django.contrib.auth import get_user_model


User = get_user_model()

class ChunkSeializer(serializers.ModelSerializer):
    class Meta:
        model = FileChunk
        fields = ['chunk','doc','id','chunk_range','name']


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        user = User.objects.filter(username=username).first()

        if user is None:
            raise serializers.ValidationError("User does not exist.")

        if not user.check_password(password):
            raise serializers.ValidationError("Incorrect password.")

        data['user'] = user
        return data
