from django.db import models


class Users(models.Model):
    email = models.CharField(primary_key=True, max_length=80)
    hashed_password = models.CharField(max_length=120)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'users'


class Carings(models.Model):
    user_email = models.ForeignKey(Users, on_delete=models.CASCADE, db_column='user_email')
    caring = models.CharField(max_length=300)
    image = models.CharField(max_length=400)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'carings'


class CaratList(models.Model):
    carat_user_email = models.ForeignKey(Users, on_delete=models.CASCADE, db_column='carat_user_email')
    caring = models.ForeignKey(Carings, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'carat_list'
        unique_together = (('carat_user_email', 'caring'),)


class Profiles(models.Model):
    user_email = models.OneToOneField(Users, on_delete=models.CASCADE, db_column='user_email', primary_key=True)
    name = models.CharField(max_length=80)
    profile_image = models.CharField(max_length=120)
    cover_image = models.CharField(max_length=120)
    about_me = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'profiles'


class FollowList(models.Model):
    follow_user_email = models.ForeignKey(Users, on_delete=models.CASCADE, db_column='follow_user_email',
                                          related_name='related_primary')
    followed_user_email = models.ForeignKey(Users, on_delete=models.CASCADE, db_column='followed_user_email',
                                            related_name='related_secondary')

    class Meta:
        managed = False
        db_table = 'follow_list'
        unique_together = (('follow_user_email', 'followed_user_email'),)


class Recarings(models.Model):
    id = models.CharField(primary_key=True, max_length=10)
    user_email = models.ForeignKey('Users', on_delete=models.CASCADE, db_column='user_email')
    caring = models.ForeignKey(Carings, on_delete=models.CASCADE)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'recarings'


"""
화가나는 장고의 모델

0. 좋은 자료 http://recordingbetter.com/django/2017/06/02/Django-Model
1. 장고는 pk(기본키)가 릴레이션(한 테이블)에 없을 경우, 직접 자동(auto)으로 pk인 id를 만든다. (장고는 pk 1개는 필수다.)
2. pk(기본키)를 참조하는 fk(외래키)는 외래키이면서 기본키가 될 수 없다.
3. 2번에도 예외가 있으니, 바로 OneToOneField 다. 일대일로 기본키를 공유하는 느낌 https://brunch.co.kr/@ddangdol/10
4. 장고의 정참조와 역참조라는 것이 있다. https://velog.io/@jcinsh/Project-%EC%A0%95%EC%B0%B8%EC%A1%B0%EC%97%AD%EC%B0%B8%EC%A1%B0-selectrelated-prefetchrelated
5. 장고는 fk(외래키)가 2개이상이 안되나 보다. https://stackoverrun.com/ko/q/89313
6. 5번을 해결해주는 방법이 있는데, fk(외래키)의 related_name 을 같은 fk(외래키)끼리 다르게 해주면 된다.
7. 근데 Recarings 를 보면, fk(외래키)가 2개여도, 참조하는 테이블이 다르면 6번을 할 필요없이 잘 돌아간다;;
8. on_delete=models.CASCADE 를 장고 모델의 필드 괄호 안에 넣어주면, 부모가 삭제되면 자식도 같이 삭제되는, 종속 관계가 된다.
9. 장고 쿼리셋(query set) 내맘대로 조종하기 : https://brownbears.tistory.com/426
10. 장고 imageField 를 쓰지않고 파일을 저장할 수 있다! default_storage : https://stackoverflow.com/questions/26274021/simply-save-file-to-folder-in-django

"""
