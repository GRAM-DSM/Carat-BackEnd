from django.db import models


class Users(models.Model):
    email = models.CharField(primary_key=True, max_length=80)
    hashed_password = models.CharField(max_length=120)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'users'


class Carings(models.Model):
    user_email = models.ForeignKey('Users', models.DO_NOTHING, db_column='user_email')
    caring = models.CharField(max_length=300)
    image = models.CharField(max_length=400)
    carat_count = models.IntegerField()
    recaring_count = models.IntegerField()
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'carings'


class CaratList(models.Model):
    carat_user_email = models.OneToOneField('Users', models.DO_NOTHING, db_column='carat_user_email', primary_key=True)
    caring = models.ForeignKey('Carings', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'carat_list'
        unique_together = (('carat_user_email', 'caring'),)


class Profiles(models.Model):
    user_email = models.ForeignKey('Users', models.DO_NOTHING, db_column='user_email')
    name = models.CharField(max_length=80)
    profile_image = models.CharField(max_length=120)
    cover_image = models.CharField(max_length=120)
    about_me = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'profiles'


class FollowList(models.Model):
    follow_user_email = models.OneToOneField('Users', models.DO_NOTHING, db_column='follow_user_email', primary_key=True)
    followed_user_email = models.ForeignKey('Profiles', models.DO_NOTHING, db_column='followed_user_email')

    class Meta:
        managed = False
        db_table = 'follow_list'
        unique_together = (('follow_user_email', 'followed_user_email'),)


class Recarings(models.Model):
    user_email = models.ForeignKey('Users', models.DO_NOTHING, db_column='user_email')
    caring = models.ForeignKey('Carings', models.DO_NOTHING)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'recarings'


##
# class CaratList(models.Model):
#     carat_user_email = models.OneToOneField('Users', models.DO_NOTHING, db_column='carat_user_email', primary_key=True)
#     caring = models.ForeignKey('Carings', models.DO_NOTHING)
#
#     class Meta:
#         managed = False
#         db_table = 'carat_list'
#         unique_together = (('carat_user_email', 'caring'),)
#
#
# class Carings(models.Model):
#     user_email = models.ForeignKey('Users', models.DO_NOTHING, db_column='user_email')
#     caring = models.CharField(max_length=300)
#     image = models.CharField(max_length=400)
#     carat_count = models.IntegerField()
#     recaring_count = models.IntegerField()
#     created_at = models.DateTimeField()
#
#     class Meta:
#         managed = False
#         db_table = 'carings'
#
# cclass FollowList(models.Model):
#     follow_user_email = models.OneToOneField('Users', models.DO_NOTHING, db_column='follow_user_email', primary_key=True)
#     followed_user_email = models.ForeignKey('Users', models.DO_NOTHING, db_column='followed_user_email')
#
#     class Meta:
#         managed = False
#         db_table = 'follow_list'
#         unique_together = (('follow_user_email', 'followed_user_email'),)
#
#
# class Profiles(models.Model):
#     user_email = models.ForeignKey('Users', models.DO_NOTHING, db_column='user_email')
#     name = models.CharField(max_length=80)
#     profile_image = models.CharField(max_length=120)
#     cover_image = models.CharField(max_length=120)
#     about_me = models.CharField(max_length=100)
#
#     class Meta:
#         managed = False
#         db_table = 'profiles'
#
# class Recarings(models.Model):
#     user_email = models.ForeignKey('Users', models.DO_NOTHING, db_column='user_email')
#     caring = models.ForeignKey(Carings, models.DO_NOTHING)
#     created_at = models.DateTimeField()
#
#     class Meta:
#         managed = False
#         db_table = 'recarings'
#
# class Users(models.Model):
#     email = models.CharField(primary_key=True, max_length=80)
#     hashed_password = models.CharField(max_length=120)
#     created_at = models.DateTimeField()
#
#     class Meta:
#         managed = False
#         db_table = 'users'
