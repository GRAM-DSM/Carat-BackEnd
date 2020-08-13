from django.db import models


class Users(models.Model):
    email = models.CharField(primary_key=True, max_length=80)
    hashed_password = models.CharField(max_length=120)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'users'


class Profiles(models.Model):
    user_email = models.OneToOneField('Users', models.DO_NOTHING, db_column='user_email', primary_key=True)
    name = models.CharField(max_length=80)
    profile_image = models.ImageField(upload_to="images/profile")
    cover_image = models.ImageField(upload_to="images/profile")
    # profile_image = models.CharField(max_length=120)
    # cover_image = models.CharField(max_length=120)
    about_me = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'profiles'


class FollowList(models.Model):
    follow_user_email = models.OneToOneField('Users', models.DO_NOTHING, db_column='follow_user_email')
    followed_user_email = models.ForeignKey('Profiles', models.DO_NOTHING, db_column='followed_user_email')

    class Meta:
        managed = False
        db_table = 'follow_list'
        unique_together = (('follow_user_email', 'followed_user_email'),)
