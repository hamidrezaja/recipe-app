from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Tag
from recipe.serializers import TagSerializer


TAGS_URL=reverse("recipe:tag-list")

def detail_url(tag_id):
    return reverse("recipe:tag-detail",args=[tag_id])


def create_user(email="user@example.com",password="testpass123"):
    
    return get_user_model().objects.create_user(email=email,password=password)

class PublicTagsApiTest(TestCase):
    """Test unauthenticated API requests."""
    
    def setUp(self):
        self.client=APIClient()
        
    def test_auth_requierd(self):
        
        res=self.client.get(TAGS_URL)
        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)
        
class PriveteTagsApiTest(TestCase):
    
    def setUp(self):
        self.client=APIClient()
        self.user=create_user()
        self.client.force_authenticate(self.user)
        
    def test_retrieve_tags(self):
        
        Tag.objects.create(name="Test tag",user=self.user)
        Tag.objects.create(name="Test tag2",user=self.user)
        
        res= self.client.get(TAGS_URL)
        
        tags=Tag.objects.all().order_by("-name")
        serializer=TagSerializer(tags,many=True)
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(res.data,serializer.data)
        
    def test_tags_limited_to_user(self):
        
        other_user=create_user(email="otheruser@example.com")
        Tag.objects.create(name="test tag",user=other_user)
        tag= Tag.objects.create(name="test tag2",user=self.user)
        
        res=self.client.get(TAGS_URL)
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(len(res.data),1)
        self.assertEqual(res.data[0]["name"],tag.name)
        self.assertEqual(res.data[0]["id"],tag.id)
        
    def test_update_tag(self):
        
        tag=Tag.objects.create(name="After Dinner",user=self.user)
        
        payload={"name":"Dessert"}
        url=detail_url(tag.id)
        res=self.client.patch(url,payload)
        
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name,payload["name"])
        
    def test_delete_tag(self):
        
        tag=Tag.objects.create(name="Breakfast",user=self.user)
        
        url=detail_url(tag.id)
        res=self.client.delete(url)
        self.assertEqual(res.status_code,status.HTTP_204_NO_CONTENT)
        tags=Tag.objects.filter(user=self.user)
        self.assertFalse(tags.exists())