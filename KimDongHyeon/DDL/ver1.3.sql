-- 장고가 복합키를 지원하지 않기에, DB 구조를 변경
-- on delete cascade 를 FK 마다 추가
-- recarings 에서 id (auto field) 추가

DROP DATABASE if exists carat;
CREATE DATABASE carat;
USE carat;
CREATE TABLE users 
(
	email 			VARCHAR(80) 	NOT NULL,
    hashed_password VARCHAR(120) 	NOT NULL,
    created_at 		TIMESTAMP 		NOT NULL 	DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (email)
);
CREATE TABLE carings 
(
	id 				INT 			AUTO_INCREMENT,
    user_email 		VARCHAR(80) 	NOT NULL,
    caring 			VARCHAR(300) 	NOT NULL,
    image 			VARCHAR(400) 	NOT	NULL,
    carat_count 	INT 			NOT NULL,
    recaring_count 	INT 			NOT NULL,
    created_at 		TIMESTAMP 		NOT NULL 	DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT carings_user_email_fkey FOREIGN KEY (user_email) REFERENCES users(email) on delete cascade
);
CREATE TABLE recarings
(
	id					INT 		AUTO_INCREMENT,	
	user_email 		VARCHAR(80) 	NOT NULL,
    caring_id 		INT 			NOT NULL,
	created_at 		TIMESTAMP 		NOT NULL 	DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT recarings_carat_user_email_fkey FOREIGN KEY (user_email) REFERENCES users(email) on delete cascade,
    CONSTRAINT recarings_caring_id_fkey FOREIGN KEY (caring_id) REFERENCES carings(id) on delete cascade 
);
CREATE TABLE profiles
(
	user_email 		VARCHAR(80) 	NOT NULL,
    name 			VARCHAR(80) 	NOT NULL,
    profile_image 	VARCHAR(120) 	NOT NULL,
    cover_image		VARCHAR(120) 	NOT NULL,
    about_me        VARCHAR(100)    NOT NULL,
    CONSTRAINT profiles_user_email_fkey FOREIGN KEY (user_email) REFERENCES users(email) on delete cascade
);
CREATE TABLE carat_list 
(
	id					INT 		AUTO_INCREMENT,	
	carat_user_email 	VARCHAR(80),
    caring_id 			INT 		NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT follow_list_carat_user_email_fkey FOREIGN KEY (carat_user_email) REFERENCES users(email) on delete cascade,
    CONSTRAINT follow_list_caring_id_fkey FOREIGN KEY (caring_id) REFERENCES carings(id) on delete cascade
);
CREATE TABLE follow_list
(
	id						INT 		AUTO_INCREMENT,
	follow_user_email 		VARCHAR(80),
    followed_user_email 	VARCHAR(80),
    PRIMARY KEY (id),
    CONSTRAINT follow_list_follow_user_email_fkey FOREIGN KEY (follow_user_email) REFERENCES users(email) on delete cascade,
    CONSTRAINT follow_list_followed_user_email_fkey FOREIGN KEY (followed_user_email) REFERENCES users(email) on delete cascade 
);
