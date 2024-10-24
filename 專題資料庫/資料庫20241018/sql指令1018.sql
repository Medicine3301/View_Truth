Create database new_community;/*社群資料庫*/
use new_community;
drop table community;
drop table news;
drop table post;
drop table users;
drop table comments;
drop table collect;

/*建立社群*/
CREATE TABLE community
(
  crea_id varchar(20), /*創建者*/
  cid varchar(20),
  cna varchar(50), /*社群名稱*/
  descr text, /*社群描述*/
  crea_na varchar(50), /*創建者名稱*/
  crea_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, /*創建日期*/
  last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, /*最後更新時間*/
  foreign key(crea_id) references users(uid), 
  primary key(cid) /*社群識別碼*/
);
ALTER TABLE community
MODIFY last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;
UPDATE community/*進行更新操作*/
SET descr = 'Updated description for testing.' -- 修改社群描述
WHERE cid = 'C001';
/*last_update 應該更新為最新的當前時間。*/
select * from community;
select * from users;
select * from news;
select * from post;
select * from comments ;
/*創建用戶表*/
Create table users
(
uid varchar(20),
una varchar(20),
uage int check(uage > 0 and uage<=70) , /*年齡範圍0~70*/
usex varchar(20),
phone varchar(15),
email varchar(30),
primary key(uid),
passwd varchar(100)
);
alter table users
  add constraint uk_users_email unique (email);
insert into users(uid,una,uage,usex,phone,email,passwd) values('u001','David',18,'男','0908577123','guozhiwei1205@gmail.com','123456');
/*因有此信箱,所以第二筆後無法使用同樣的信箱*/
insert into users(uid,una,uage,usex,phone,email,passwd) values('u002','David',20,'男','0908577112','takming122@gmail.com','123456');
insert into users(uid,una,uage,usex,phone,email,passwd) values('u003','Judy',21,'女','0908577156','813012@gs.takming.edu.tw','123456789');
/*因年齡超過70以上,所以無法新增上去到此資料庫*/
insert into users(uid,una,uage,usex,phone,email,passwd) values('u004','Eric',71,'男','0908577789','eric123@gmail.com','112345655');
delete from users
where uid='u003';
/*創建貼文表*/
Create table post
(
uid varchar(20),
pid varchar(50),
cid varchar(20),
title varchar(50),
content varchar(50),
crea_date timestamp default current_timestamp, 
primary key(pid),
comm_count int default 0,
foreign key(uid) references users(uid),
foreign key(cid) references community(cid)
);
 



/*創建新聞表*/
Create table news
(
newstitle varchar(20),/*新聞名稱*/
news_id varchar(50),/*新聞識別碼*/
journ varchar(30),/*新聞出處/來源/期刊*/
crea_date datetime,/*報導時間*/
newsclass varchar(10),/*新聞類別*/
count int,/*點擊次數*/
primary key(news_id)
);
/*留言表*/
create table comments
(
pid varchar(50),
comm_id varchar(50),
uid varchar(20),
title varchar(50),
content varchar(50),
nid varchar(50),
primary key (comm_id),
foreign key(pid) references post(pid),
foreign key (nid) references news(news_id)
);

/*收藏表*/
CREATE TABLE collect
(
    pid VARCHAR(50),
    uid VARCHAR(20),
    PRIMARY KEY(pid, uid),
    FOREIGN KEY(pid) REFERENCES post(pid),
    FOREIGN KEY(uid) REFERENCES users(uid)
);
/*評分表*/
CREATE TABLE score
(
    pid VARCHAR(50),
    uid VARCHAR(20),
    rate_sc INT,
    PRIMARY KEY(pid, uid),
    FOREIGN KEY(pid) REFERENCES post(pid),
    FOREIGN KEY(uid) REFERENCES users(uid)
);
/*更新每個貼文的留言數量*/
DELIMITER //

CREATE TRIGGER post_comment_count
AFTER INSERT ON comments
FOR EACH ROW
BEGIN
  IF NEW.pid IS NOT NULL THEN
    UPDATE post
    SET comm_count = comm_count + 1
    WHERE pid = NEW.pid;
  END IF;
END //

DELIMITER ;

/*更新新聞*/
DELIMITER //

CREATE TRIGGER new_comment_count
AFTER INSERT ON comments
FOR EACH ROW
BEGIN
  IF NEW.nid IS NOT NULL THEN
    UPDATE news
    SET count = count + 1
    WHERE news_id = NEW.nid;
  END IF;
END //

DELIMITER ;


/*針對新聞的留言更新*/
DELIMITER //
CREATE TRIGGER new_comment_count-- 創建觸發器 new_comment_count，在 comments 表插入新紀錄後執行
AFTER INSERT ON comments -- 定義在 comments 表上插入操作後觸發
FOR EACH ROW
BEGIN
  UPDATE news -- 更新 news 表中對應的 news_id 新聞的留言數量
  SET count = count + 1 -- 將該新聞的點擊次數加 1
  WHERE news_id = NEW.nid; -- 以新增的留言中 nid 為條件
END //
-- 恢復終止符號為預設的分號；
DELIMITER ;

/*更新社群中的貼文數量*/
DELIMITER // -- 更改終止符號為 //

CREATE TRIGGER community_post_count -- 創建名為 community_post_count 的觸發器
AFTER INSERT ON post -- 定義在 post 表插入新貼文後觸發
FOR EACH ROW -- 對於每一行插入的貼文
BEGIN -- 開始觸發器的主體
  UPDATE community -- 更新 community 表
  SET last_update = CURRENT_TIMESTAMP -- 將社群的 last_update 欄位設為當前時間
  WHERE cid = NEW.cid; -- 以新增的貼文中的 cid 為條件進行更新
END // -- 結束觸發器的主體
DELIMITER ; -- 恢復終止符號為預設的分號


#測試post_comment_count
/*post數據*/
INSERT INTO post (uid, pid, cid, title, content)
VALUES ('u001', 'P001', 'C001', 'Test Post', 'This is a test post.');

/*確保用戶存在*/
SELECT * FROM users WHERE uid = 'u001';

/*確保社群存在*/
SELECT * FROM community WHERE cid = 'C001';

/*如無社群數據,必須新增數據*/
INSERT INTO community (cid, cna, descr, crea_id, crea_na)
VALUES ('C001', 'Test Community', 'This is a test community.', 'u001', 'User One');

/*重新插入post*/
INSERT INTO post (uid, pid, cid, title, content)
VALUES ('u001', 'P001', 'C001', 'Test Post', 'This is a test post.');

/*檢查初始的comm_count*/
SELECT comm_count FROM post WHERE pid = 'P001';
/*插入留言*/
INSERT INTO comments (pid, comm_id, uid, title, content, nid)
VALUES ('P001', 'CMT001', 'u001', 'Test Comment', 'This is a comment on the post.', NULL);
INSERT INTO comments (pid, comm_id, uid, title, content, nid)
VALUES ('P001', 'CMT002', 'u002', 'Second Test Comment', 'This is another comment.', NULL);
INSERT INTO comments (pid, comm_id, uid, title, content, nid)
VALUES ('P001', 'CMT003', 'u001', 'Third Test Comment', 'This is the third comment.', NULL);

#測試new_comment_count
/*確保news有新聞數據*/
SELECT * FROM news WHERE news_id = 'N001';

INSERT INTO news (news_id, newstitle, journ, crea_date, newsclass, count)
VALUES ('N001', 'Test News', 'Test Journal', NOW(), 'General', 0);
/*檢查初始的count*/
SELECT count FROM news WHERE news_id = 'N001';
/*插入留言*/
INSERT INTO comments (pid, comm_id, uid, title, content, nid)
VALUES (NULL, 'CMT004', 'u001', 'Test Comment for News', 'This is a comment on the news.', 'N001');
INSERT INTO comments (pid, comm_id, uid, title, content, nid)
VALUES (NULL, 'CMT005', 'u002', '中秋節活動', '在9/18開始', 'N001');
select * from comments;

/*測試community _post_count*/
/*確保有社群紀錄*/
SELECT * FROM community WHERE cid = 'C001';
/* 檢查初始的 last_update 值*/
SELECT last_update FROM community WHERE cid = 'C001';
/*插入一條新貼文*/
INSERT INTO post (uid, pid, cid, title, content)
VALUES ('u001', 'P002', 'C001', 'Test Post', 'This is a test post.');
INSERT INTO post (uid, pid, cid, title, content)
VALUES ('u001', 'P003', 'C001', 'NEW_Test Post', 'This is a test post.');
select * from post;
/*確認觸發器的定義*/
SHOW CREATE TRIGGER community_post_count;

/*確認觸發有哪些*/
SHOW TRIGGERS;
/*確認觸發器的存在*/
SHOW TRIGGERS LIKE 'community_post_count';
/*確認觸發器的正確性*/
SHOW CREATE TRIGGER community_post_count;

/*20241018*/

DROP TRIGGER IF EXISTS post_comment_count;
DROP TRIGGER IF EXISTS new_comment_count;

ALTER TABLE users
ADD birthday DATE;
select *from users;
/*呈現yyyy/mm/dd*/
SELECT uid, una,  usex, phone, email, passwd, 
       DATE_FORMAT(birthday, '%Y/%m/%d') AS formatted_birthday
FROM users;
