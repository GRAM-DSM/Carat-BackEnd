# 김동현의 디렉토리

제가 개발한 코드를 업로드하는 공간입니다.   

## 폴더 구조

- carat_project <프로젝트 폴더>

- carat_user <app 폴더>
    - user API
- carat_carat <app 폴더>
    - caring API
    - recaring API
    - timeline API
    - carat API
- carat_profile <app 폴더>
    - profile API
    
## 설치 / 로컬 환경 구축

현재 폴더에서 

```py
./myvenv/Scripts/activate
```
으로 가상환경을 활성화 한 후, (윈도우 기준임)

```
pip install -r ./reqs/window.txt
```
으로 윈도우용 requirements.txt 을 불러와서 라이브러리들을 설치함.

```
code .\myvenv\Lib\site-packages\django\db\backends\mysql\base.py
```
으로 vscode를 사용하거나,
```
vim .\myvenv\Lib\site-packages\django\db\backends\mysql\base.py
```
으로 vim을 사용하던지 해서,

![여거](https://user-images.githubusercontent.com/48408417/90738232-49c3c900-e309-11ea-88ee-3d1306b094a4.png)
여기서,
```py
version = Database.version_info
if version < (1, 4, 0):
    raise ImproperlyConfigured('mysqlclient 1.4.0 or newer is required; you have %s.' % Database.__version__)

```
이부분을 
```
version = Database.version_info
if version < (1, 4, 0):
    pass
    # raise ImproperlyConfigured('mysqlclient 1.4.0 or newer is required; you have %s.' % Database.__version__)

```
으로 수정하면 완료.
