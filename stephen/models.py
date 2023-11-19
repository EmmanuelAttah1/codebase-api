from django.db import models
from django.contrib.auth.models import User


class Project(models.Model):
    name = models.CharField(max_length=100)
    created_by = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)

    def __str__(self):
        return self.name
    
    
class ProjectFile(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=300)

    def __str__(self):
        return self.name
    
class FileChunk(models.Model):
    file = models.ForeignKey(ProjectFile, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    chunk = models.TextField(blank=True)
    doc = models.TextField(blank=True)
    chunk_range = models.CharField(max_length=100, default="")

    def __str__(self):
        return f"{self.file.name} -- {self.name} "