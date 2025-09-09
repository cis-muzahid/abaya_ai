# designer/models.py
from django.db import models

class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()

class AbayaDesign(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    style = models.CharField(max_length=100)
    length = models.CharField(max_length=50)
    fabric = models.CharField(max_length=50)
    color = models.CharField(max_length=50)
    design_image = models.ImageField(upload_to='designs/')
    created_at = models.DateTimeField(auto_now_add=True)



class State(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"id: {self.id} | State: {self.name}"

class Topic(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='topics')
    topic_name = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    url = models.URLField()
    description = models.TextField()


    def __str__(self):
        return f"Topic: {self.topic_name} | State: {self.state.name}-{self.state.id}"
    

class License(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='licenses')
    profession = models.CharField(max_length=100)
    url = models.URLField()

    def __str__(self):
        return f"{self.profession} - {self.state.name}"

class County(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='counties')
    county_name = models.CharField(max_length=100)
    url = models.URLField()

    def __str__(self):
        return f"{self.county_name}, {self.state.name}-{self.state.id}"


class TopicSearchByRecord(models.Model):
    topic = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    url = models.URLField()
    description = models.TextField()

    def __str__(self):
        return f"Topic: {self.topic} | Title: {self.title}"


