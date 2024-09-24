from io import BytesIO
import os
import tempfile
from PIL import Image
import numpy as np
from rest_framework import serializers
from video.models import Video
from moviepy.editor import VideoFileClip
from decimal import Decimal, InvalidOperation
from django.core.files.base import ContentFile
# from video.models import PostReview

class VideoSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source="user.username", read_only=True)
    user_profile_picture = serializers.CharField(
        source="user.profile_picture", read_only=True
    )
    user_bio=serializers.CharField(source="user.bio",read_only=True)
    
    # post_review_count=serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = [
            "id",
            "title",
            "video",
            "thumbnail",
            "preview",
            "user_bio",
            "user",
            "user_username",
            "user_profile_picture",
            "price",
            "description",
            "created_by",
            "updated_by",
            "deleted",
            "created_at",
            "updated_at",
            # "post_review_count",
            "status",
        ]

    def validate(self, data):
        errors = {}
        print("serializer", data)

        # Title validation
        # if "title" not in data or not data["title"] or data["title"] == "":
        #     errors["title"] = "Title is required."
        # elif len(data["title"].strip()) <= 50:
        #     errors["title"] = "Title must be more than 30 characters long."

        # Description validations
        # description = data.get("description")
        # if not description or data["description"] == "":
        #     errors["description"] = "Description is required."
        # elif len(description.strip()) < 100:
        #     errors["description"] = "Description must be at least 100 characters long."

        # Thumbnail validation (optional field)
        thumbnail = data.get("thumbnail")
        if thumbnail:
            ext = os.path.splitext(thumbnail.name)[-1].lower()
            if ext not in [".png", ".jpeg", ".jpg"]:
                errors["thumbnail"] = (
                    "Invalid file type. Only .png, .jpeg, and .jpg files are allowed for thumbnails."
                )
                
        price = data.get("price")
        if price is None or price == "":
            errors["price"] = "Price is required."
        else:
            try:
                # Attempt to convert price to a Decimal
                decimal_price = Decimal(price)
            except InvalidOperation:
                errors["price"] = (
                    "Price must be a valid number with up to two decimal places."
                )

            # Check if the price is greater than 0
            if decimal_price <= 0:
                errors["price"] = "Price must be greater than 0."

            # Ensure the price has two decimal places
            if decimal_price != decimal_price.quantize(Decimal("0.00")):
                errors["price"] = "Price must have up to two decimal places."


        # Video validation
        instance = getattr(self, 'instance', None)

        if not instance and 'video' not in data:
            errors['video'] = "Video file is required."
        elif 'video' in data:
            video = data.get('video')
            ext = os.path.splitext(video.name)[-1].lower()
            if ext not in [".wav", ".mp4"]:
                errors['video'] = "Invalid file type for video."
            if video.size > 400 * 1024 * 1024:  # 400MB
                errors['video'] = "Video file size should not exceed 400MB."

        # Preview validation
        preview = data.get("preview")
        if not preview:
            errors["preview"] = "Preview video is required."
        else:
            # Check the file extension
            ext_preview = os.path.splitext(preview.name)[-1].lower()
            if ext_preview not in [".mp4", ".wav"]:
                errors["preview"] = "Invalid file type. Only '.mp4' and '.wav' files are allowed for previews."
            # Check the file size
            if preview.size > 10 * 1024 * 1024:  # 100MB
                        errors["preview"] = "Preview file size should not exceed 10MB."
            
        # Price validation
        
        if errors:
            raise serializers.ValidationError(errors)

        return data

    def generate_thumbnail_from_video(self,video, thumbnail_time=1, thumbnail_size=(1500, 1500), frame_ratio=0.5):
        """
        Generate a thumbnail image from the first frame of the video.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            video_path = os.path.join(temp_dir, video.name)

            # Save the in-memory video file to a temporary location
            with open(video_path, 'wb') as temp_video_file:
                for chunk in video.chunks():
                    temp_video_file.write(chunk)

            try:
                # Load the video and get the frame at the specified time
                with VideoFileClip(video_path) as video_clip:
                    # Get the video dimensions
                    video_width, video_height = video_clip.size

                    # Calculate frame size based on the video size
                    frame_width = int(video_width * frame_ratio)
                    frame_height = int(video_height * frame_ratio)

                    # Get a frame at the specified time (in seconds)
                    frame = video_clip.get_frame(thumbnail_time)

                    # Convert the frame (numpy array) to an image
                    if frame.ndim == 3 and frame.shape[2] == 3:
                        frame_rgb = frame
                    elif frame.ndim == 3 and frame.shape[2] == 4:
                        frame_rgb = frame[:, :, :3]
                    else:
                        frame_rgb = np.stack([frame] * 3, axis=-1)

                    thumbnail_image = Image.fromarray(frame_rgb)

                    # Resize the image to the calculated frame size
                    thumbnail_image = thumbnail_image.resize((frame_width, frame_height), Image.LANCZOS)

                    # Resize the thumbnail to the desired thumbnail size
                    thumbnail_image.thumbnail(thumbnail_size, Image.LANCZOS)

                    # Save to a BytesIO object
                    thumbnail_io = BytesIO()
                    thumbnail_image.save(thumbnail_io, format='JPEG')
                    thumbnail_io.seek(0)

            except Exception as e:
                raise Exception(f"Failed to generate thumbnail: {str(e)}")

            # Return the thumbnail as ContentFile
            return ContentFile(thumbnail_io.read(), 'thumbnail.jpg')

    def create(self, validated_data):
        video = validated_data.get('video')
        if video and not validated_data.get('thumbnail'):
            validated_data['thumbnail'] = self.generate_thumbnail_from_video(video)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        video = validated_data.get('video')
        if video and (instance.video != video):  # Check if video has changed
            validated_data['thumbnail'] = self.generate_thumbnail_from_video(video)
        return super().update(instance, validated_data)
    
    # def get_post_review_count(self,obj):
        # id=obj.id
        # count=PostReview.objects.filter(post__id=id).count()
        # return count
        
        
# class PostReviewSerializer(serializers.ModelSerializer):
#     user_username = serializers.CharField(source='user.username', read_only=True)
#     post_title = serializers.CharField(source='post.title', read_only=True)  # Assuming the Post model has a title field
#     user_profile_picture=serializers.CharField(source='user.profile_picture', read_only=True)

#     class Meta:
#         model = PostReview
#         fields = [
#             'id',
#             'user',
#             'user_username',
#             "user_profile_picture",
#             'post',
#             'post_title',
#             'message',
#             'created_by',
#             'updated_by',
#             'deleted',
#             'created_at',
#             'updated_at'
#         ]
#         read_only_fields = ['created_at', 'updated_at']
        
        
#     # def validate(self, data):
#     #     message=data.get("message")
#     #     if len(message)<10:
#     #         return serializers.ValidationError("Comment length should be more than 10 chara")
        
    