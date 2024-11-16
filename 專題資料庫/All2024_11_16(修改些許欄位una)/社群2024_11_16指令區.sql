Create database new_community;/*社群資料庫*/
use new_community;
drop table community;
drop table news;
drop table post;
drop table users;
drop table comments;
drop table collect;
drop table score;
/*建立社群*/
CREATE TABLE community/*第二順位*/
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
Create table users /*第一順位*/
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
Create table post/*第三順位*/
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
Create table news/*第四順位*/
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
create table comments/*第五順位*/
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
CREATE TABLE collect/*第六順位*/
(
    pid VARCHAR(50),
    uid VARCHAR(20),
    PRIMARY KEY(pid, uid),
    FOREIGN KEY(pid) REFERENCES post(pid),
    FOREIGN KEY(uid) REFERENCES users(uid)
);
/*評分表*/
CREATE TABLE score/*第七順位*/
(
    pid VARCHAR(50),
    uid VARCHAR(20),
    rate_sc INT,
    PRIMARY KEY(pid, uid),
    FOREIGN KEY(pid) REFERENCES post(pid),
    FOREIGN KEY(uid) REFERENCES users(uid)
);

---------Trigger---------------------
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
SELECT uid, una,  usex, email, passwd, 
       DATE_FORMAT(birthday, '%Y/%m/%d') AS formatted_birthday
FROM users;
/*20241024*/
ALTER TABLE users DROP COLUMN uage;/*刪除uage欄位*/
ALTER TABLE users DROP COLUMN phone;/*刪除phone欄位*/
alter table users add column role Enum('user','admin');/*該欄位的類型為 Enum（列舉），其值只能是 'user' 或 'admin' 之一,一組預定義的值,只能取這兩個值*/

/*查看 外鍵*/
SHOW CREATE TABLE post;
SHOW CREATE TABLE comments;
SHOW CREATE TABLE collect;
SHOW CREATE TABLE score;
show create table community;


/*刪除外鍵*/
ALTER TABLE community DROP FOREIGN KEY community_uid_fk;
ALTER TABLE post DROP FOREIGN KEY post_uid_fk;
ALTER TABLE post DROP FOREIGN KEY post_ibfk_2;
ALTER TABLE comments DROP FOREIGN KEY comments_uid_fk;
ALTER TABLE comments DROP FOREIGN KEY comments_ibfk_2;
ALTER TABLE collect DROP FOREIGN KEY collect_uid_fk;
ALTER TABLE score DROP FOREIGN KEY score_uid_fk;


/*修改uid長度*/
ALTER TABLE community MODIFY crea_id VARCHAR(200); -- 假設你需要改的是這個欄位
ALTER TABLE post MODIFY uid VARCHAR(200);
ALTER TABLE comments MODIFY uid VARCHAR(200);
ALTER TABLE collect MODIFY uid VARCHAR(200);
ALTER TABLE score MODIFY uid VARCHAR(200);

/*確認修改*/
SHOW CREATE TABLE users;
SHOW CREATE TABLE community;
SHOW CREATE TABLE post;
SHOW CREATE TABLE comments;
SHOW CREATE TABLE collect;
SHOW CREATE TABLE score;

/*重新添加外鍵*/
ALTER TABLE community ADD CONSTRAINT community_uid_fk FOREIGN KEY (crea_id) REFERENCES users(uid);
ALTER TABLE post ADD CONSTRAINT post_uid_fk FOREIGN KEY (uid) REFERENCES users(uid);
ALTER TABLE comments ADD CONSTRAINT comments_uid_fk FOREIGN KEY (uid) REFERENCES users(uid);
ALTER TABLE collect ADD CONSTRAINT collect_uid_fk FOREIGN KEY (uid) REFERENCES users(uid);
ALTER TABLE score ADD CONSTRAINT score_uid_fk FOREIGN KEY (uid) REFERENCES users(uid);

/*20241113*/
ALTER TABLE post
ADD una varchar(20);/*新增una欄位*/


/*查詢外來建*/
SHOW CREATE TABLE post;

/*刪除外建*/
 DROP TRIGGER IF EXISTS test_trigger;
  DROP TRIGGER IF EXISTS community_post_count;
  
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

/*查詢community*/
select * from community;
/*新增community*/
insert into community(`crea_id`,`cid`,`cna`,`descr`,`crea_na`) values('f8b79c16-f589-41d4-84b3-8e73f6ccb307','C006','運動','就是運動','acrhjh');
insert into community(`crea_id`,`cid`,`cna`,`descr`,`crea_na`) values('f8b79c16-f589-41d4-84b3-8e73f6ccb307','C007','財經','最新財經新聞','acrhjh');
insert into community(`crea_id`,`cid`,`cna`,`descr`,`crea_na`) values('f8b79c16-f589-41d4-84b3-8e73f6ccb307','C008','政治','政治內亂','acrhjh');
insert into community(`crea_id`,`cid`,`cna`,`descr`,`crea_na`) values('f8b79c16-f589-41d4-84b3-8e73f6ccb307','C009','外國新聞','林書豪','acrhjh');
insert into community(`crea_id`,`cid`,`cna`,`descr`,`crea_na`) values('f8b79c16-f589-41d4-84b3-8e73f6ccb307','C010','美食','台灣美食','acrhjh');
/*查詢comments*/
select * from comments;
ALTER TABLE comments
ADD una varchar(20);/*新增una欄位*/

/*查詢post*/
select * from post;
/*新增資料post*/
insert into post(`uid`,`pid`,`cid`,`title`,`content`,`una`) values('9dcc32d5-4726-4273-8937-3aa3709097cd','P1','C001','財經股票','測試1','acrhjh');
insert into post(`uid`,`pid`,`cid`,`title`,`content`,`una`) values('f8b79c16-f589-41d4-84b3-8e73f6ccb307','P2','C002','運動!!','測試2','acrhjh');
insert into post(`uid`,`pid`,`cid`,`title`,`content`,`una`) values('f8b79c16-f589-41d4-84b3-8e73f6ccb307','P3','C003','國內政治!!','測試3','acrhjh');
/*刪除貼文資料*/
delete from `post` 
where `pid`='P1';

/*查詢留言*/
select * from comments;
/*新增留言*/
insert into comments(`pid`,`comm_id`,`uid`,`title`,`content`,`una`) values('P1','RP1','9dcc32d5-4726-4273-8937-3aa3709097cd' ,'留言1','content1','123');
insert into comments(`pid`,`comm_id`,`uid`,`title`,`content`,`una`) values('P2','RP2','f8b79c16-f589-41d4-84b3-8e73f6ccb307' ,'德明財經科技大學','資管系','acrhjh');
insert into comments(`pid`,`comm_id`,`uid`,`title`,`content`,`una`) values('P3','RP3','9dcc32d5-4726-4273-8937-3aa3709097cd' ,'龍華科大','資訊工程學系','123');
/*刪除留言*/
delete from `comments` 
where `pid`='P0001';
/*查詢users*/
select* from users;
/*新增comments欄位*/

Alter table comments
ADD crea_date  timestamp default current_timestamp;
/***********************************************20241115*****************************************************************/
use new_community;
select * from comments;/*查詢留言*/
select * from post;/*查詢貼文*/
select * from community;/*查詢社群*/
select * from users;/*查詢用戶*/

/*查詢uid="9dcc32d5-4726-4273-8937-3aa3709097cd"的貼文*/
select *
from post
where uid="9dcc32d5-4726-4273-8937-3aa3709097cd" ;

/*新增資料uid="9dcc32d5-4726-4273-8937-3aa3709097cd"的貼文*/
insert into post(`uid`,`pid`,`cid`,`title`,`content`,`una`) values('9dcc32d5-4726-4273-8937-3aa3709097cd','P1','C001','財經股票','測試1','acrhjh');
insert into post(`uid`,`pid`,`cid`,`title`,`content`,`una`) values('9dcc32d5-4726-4273-8937-3aa3709097cd','P12','C002','財經股票上升','測試2','acrhjh');
insert into post(`uid`,`pid`,`cid`,`title`,`content`,`una`) values('9dcc32d5-4726-4273-8937-3aa3709097cd','P13','C010','COVID','病毒','acrhjh');
insert into post(`uid`,`pid`,`cid`,`title`,`content`,`una`) values('9dcc32d5-4726-4273-8937-3aa3709097cd','P10','C010','教育','在線學習的優勢與挑戰','acrhjh');
insert into post(`uid`,`pid`,`cid`,`title`,`content`,`una`) values('9dcc32d5-4726-4273-8937-3aa3709097cd','P4','C004','財經股票','近期股市表現分析','acrhjh');
insert into post(`uid`,`pid`,`cid`,`title`,`content`,`una`) values('9dcc32d5-4726-4273-8937-3aa3709097cd','P5','C005','運動','籃球世界盃賽事回顧','acrhjh');
insert into post(`uid`,`pid`,`cid`,`title`,`content`,`una`) values('9dcc32d5-4726-4273-8937-3aa3709097cd','P6','C006','科技','AI 技術對未來的影響','acrhjh');
insert into post(`uid`,`pid`,`cid`,`title`,`content`,`una`) values('9dcc32d5-4726-4273-8937-3aa3709097cd','P7','C007','藝術','探索現代藝術的無限可能','acrhjh');
insert into post(`uid`,`pid`,`cid`,`title`,`content`,`una`) values('9dcc32d5-4726-4273-8937-3aa3709097cd','P8','C008','旅遊','分享夏日海島旅行的心得','acrhjh');
insert into post(`uid`,`pid`,`cid`,`title`,`content`,`una`) values('9dcc32d5-4726-4273-8937-3aa3709097cd','P9','C009','健康','健康飲食的十大原則','acrhjh');

/*新增uid="9dcc32d5-4726-4273-8937-3aa3709097cd"的貼文留言*/
INSERT INTO comments(`pid`, `comm_id`, `uid`, `title`, `content`, `una`) 
VALUES ('P1', 'RP4', '9dcc32d5-4726-4273-8937-3aa3709097cd', '股票市場的波動', '這篇文章的分析很深入，值得一看。', 'acrhjh');
INSERT INTO comments(`pid`, `comm_id`, `uid`, `title`, `content`, `una`) 
VALUES ('P12', 'RP5', '9dcc32d5-4726-4273-8937-3aa3709097cd', '股票升勢', '是否會繼續上升呢？', 'acrhjh');
INSERT INTO comments(`pid`, `comm_id`, `uid`, `title`, `content`, `una`) 
VALUES ('P13', 'RP6', '9dcc32d5-4726-4273-8937-3aa3709097cd', '病毒疫情分析', '希望疫情能盡快結束，大家要保持警覺。', 'acrhjh');
INSERT INTO comments(`pid`, `comm_id`, `uid`, `title`, `content`, `una`) 
VALUES ('P10', 'RP7', '9dcc32d5-4726-4273-8937-3aa3709097cd', '在線學習的挑戰', '在線學習真的有很多挑戰，特別是集中注意力。', 'acrhjh');
INSERT INTO comments(`pid`, `comm_id`, `uid`, `title`, `content`, `una`) 
VALUES ('P4', 'RP8', '9dcc32d5-4726-4273-8937-3aa3709097cd', '股市分析', '最近股市的波動性很大，讓人不敢輕易投資。', 'acrhjh');
INSERT INTO comments(`pid`, `comm_id`, `uid`, `title`, `content`, `una`) 
VALUES ('P5', 'RP9', '9dcc32d5-4726-4273-8937-3aa3709097cd', '籃球世界盃', '這場比賽很精彩，尤其是最後一場決賽！', 'acrhjh');
INSERT INTO comments(`pid`, `comm_id`, `uid`, `title`, `content`, `una`) 
VALUES ('P6', 'RP10', '9dcc32d5-4726-4273-8937-3aa3709097cd', 'AI 未來影響', 'AI 在未來的發展潛力巨大，值得關注。', 'acrhjh');
INSERT INTO comments(`pid`, `comm_id`, `uid`, `title`, `content`, `una`) 
VALUES ('P7', 'RP11', '9dcc32d5-4726-4273-8937-3aa3709097cd', '現代藝術', '現代藝術真的是無窮無盡，總有新的驚喜。', 'acrhjh');
INSERT INTO comments(`pid`, `comm_id`, `uid`, `title`, `content`, `una`) 
VALUES ('P8', 'RP12', '9dcc32d5-4726-4273-8937-3aa3709097cd', '夏日旅行', '海島旅行真的很放鬆，尤其是享受陽光沙灘的時光。', 'acrhjh');
INSERT INTO comments(`pid`, `comm_id`, `uid`, `title`, `content`, `una`) 
VALUES ('P9', 'RP13', '9dcc32d5-4726-4273-8937-3aa3709097cd', '健康飲食', '健康飲食的原則真是生活的必需，保持飲食均衡。', 'acrhjh');

/*查詢uid="9dcc32d5-4726-4273-8937-3aa3709097cd"的貼文留言*/
select * 
from comments
where uid="9dcc32d5-4726-4273-8937-3aa3709097cd";

/*查詢uid="f8b79c16-f589-41d4-84b3-8e73f6ccb307"的貼文*/
select *
from post
where uid="f8b79c16-f589-41d4-84b3-8e73f6ccb307" ;

/*新增uid="f8b79c16-f589-41d4-84b3-8e73f6ccb307"的貼文*/
INSERT INTO post(`uid`, `pid`, `cid`, `title`, `content`, `una`) VALUES('f8b79c16-f589-41d4-84b3-8e73f6ccb307', 'P14', 'C004', '財經股票', '近期股市表現分析', 'acrhjh')
INSERT INTO post(`uid`, `pid`, `cid`, `title`, `content`, `una`) VALUES('f8b79c16-f589-41d4-84b3-8e73f6ccb307', 'P15', 'C005', '運動', '籃球世界盃賽事回顧', 'acrhjh')
INSERT INTO post(`uid`, `pid`, `cid`, `title`, `content`, `una`) VALUES('f8b79c16-f589-41d4-84b3-8e73f6ccb307', 'P16', 'C006', '科技', 'AI 技術對未來的影響', 'acrhjh')
INSERT INTO post(`uid`, `pid`, `cid`, `title`, `content`, `una`) VALUES('f8b79c16-f589-41d4-84b3-8e73f6ccb307', 'P17', 'C007', '藝術', '探索現代藝術的無限可能', 'acrhjh')
INSERT INTO post(`uid`, `pid`, `cid`, `title`, `content`, `una`) VALUES('f8b79c16-f589-41d4-84b3-8e73f6ccb307', 'P18', 'C008', '旅遊', '分享夏日海島旅行的心得', 'acrhjh')
INSERT INTO post(`uid`, `pid`, `cid`, `title`, `content`, `una`) VALUES('f8b79c16-f589-41d4-84b3-8e73f6ccb307', 'P19', 'C009', '健康', '健康飲食的十大原則', 'acrhjh')
INSERT INTO post(`uid`, `pid`, `cid`, `title`, `content`, `una`) VALUES('f8b79c16-f589-41d4-84b3-8e73f6ccb307', 'P20', 'C010', '教育', '在線學習的優勢與挑戰', 'acrhjh')
INSERT INTO post(`uid`, `pid`, `cid`, `title`, `content`, `una`) VALUES('f8b79c16-f589-41d4-84b3-8e73f6ccb307', 'P21', 'C010', '教育', '在線學習的優勢與挑戰', 'acrhjh')
INSERT INTO post(`uid`, `pid`, `cid`, `title`, `content`, `una`) VALUES('f8b79c16-f589-41d4-84b3-8e73f6ccb307', 'P22', 'C010', '教育1', '在線學習的劣勢與挑戰', 'acrhjh')
INSERT INTO post(`uid`, `pid`, `cid`, `title`, `content`, `una`) VALUES('f8b79c16-f589-41d4-84b3-8e73f6ccb307', 'P23', 'C010', '教育2', '在線學習的挑戰極限', 'acrhjh')
INSERT INTO post(`uid`, `pid`, `cid`, `title`, `content`, `una`) VALUES('f8b79c16-f589-41d4-84b3-8e73f6ccb307', 'P2', 'C002', '運動!!', '測試2', 'acrhjh')
INSERT INTO post(`uid`, `pid`, `cid`, `title`, `content`, `una`) VALUES('f8b79c16-f589-41d4-84b3-8e73f6ccb307', 'P3', 'C003', '國內政治!!', '測試3', 'acrhjh')

/*查詢uid="f8b79c16-f589-41d4-84b3-8e73f6ccb307"的留言*/
select * 
from comments
where uid="f8b79c16-f589-41d4-84b3-8e73f6ccb307";

/*新增uid="f8b79c16-f589-41d4-84b3-8e73f6ccb307"的貼文留言*/
INSERT INTO comments(`pid`, `comm_id`, `uid`, `title`, `content`, `una`) 
VALUES ('P14', 'RP14', 'f8b79c16-f589-41d4-84b3-8e73f6ccb307', '股市分析', '股市的變動性越來越大，值得持續關注。', 'acrhjh');
INSERT INTO comments(`pid`, `comm_id`, `uid`, `title`, `content`, `una`) 
VALUES ('P14', 'RP15', 'f8b79c16-f589-41d4-84b3-8e73f6ccb307', '籃球賽事回顧', '這場比賽激烈精彩，特別是最後的逆轉！', 'acrhjh');
INSERT INTO comments(`pid`, `comm_id`, `uid`, `title`, `content`, `una`) 
VALUES ('P16', 'RP16', 'f8b79c16-f589-41d4-84b3-8e73f6ccb307', 'AI 技術', 'AI 的未來發展會大大改變我們的生活，值得期待。', 'acrhjh');
INSERT INTO comments(`pid`, `comm_id`, `uid`, `title`, `content`, `una`) 
VALUES ('P17', 'RP17', 'f8b79c16-f589-41d4-84b3-8e73f6ccb307', '現代藝術', '現代藝術的創新和挑戰，讓人目不暇接。', 'acrhjh');
INSERT INTO comments(`pid`, `comm_id`, `uid`, `title`, `content`, `una`) 
VALUES ('P18', 'RP18', 'f8b79c16-f589-41d4-84b3-8e73f6ccb307', '夏日旅行', '夏日海島的海風和沙灘是最放鬆的享受。', 'acrhjh');
INSERT INTO comments(`pid`, `comm_id`, `uid`, `title`, `content`, `una`) 
VALUES ('P19', 'RP19', 'f8b79c16-f589-41d4-84b3-8e73f6ccb307', '健康飲食原則', '健康飲食對保持身體健康至關重要。', 'acrhjh');
INSERT INTO comments(`pid`, `comm_id`, `uid`, `title`, `content`, `una`) 
VALUES ('P20', 'RP20', 'f8b79c16-f589-41d4-84b3-8e73f6ccb307', '在線學習的挑戰', '在線學習確實有很多挑戰，特別是在自我管理方面。', 'acrhjh');
INSERT INTO comments(`pid`, `comm_id`, `uid`, `title`, `content`, `una`) 
VALUES ('P21', 'RP21', 'f8b79c16-f589-41d4-84b3-8e73f6ccb307', '在線學習的優勢', '在線學習方便靈活，讓我們可以隨時隨地學習。', 'acrhjh');
INSERT INTO comments(`pid`, `comm_id`, `uid`, `title`, `content`, `una`) 
VALUES ('P22', 'RP22', 'f8b79c16-f589-41d4-84b3-8e73f6ccb307', '在線學習的劣勢', '在線學習的最大問題是缺乏面對面互動，學習效果會受影響。', 'acrhjh');
INSERT INTO comments(`pid`, `comm_id`, `uid`, `title`, `content`, `una`) 
VALUES ('P23', 'RP23', 'f8b79c16-f589-41d4-84b3-8e73f6ccb307', '在線學習的挑戰', '在線學習的挑戰在於如何保持專注和積極參與。', 'acrhjh');
INSERT INTO comments(`pid`, `comm_id`, `uid`, `title`, `content`, `una`) 
VALUES ('P2', 'RP24', 'f8b79c16-f589-41d4-84b3-8e73f6ccb307', '運動測試', '這篇測試文章不錯，可以再加一些細節。', 'acrhjh');
INSERT INTO comments(`pid`, `comm_id`, `uid`, `title`, `content`, `una`) 
VALUES ('P3', 'RP25', 'f8b79c16-f589-41d4-84b3-8e73f6ccb307', '國內政治', '政治動態十分複雜，特別是最近的政策變動。', 'acrhjh');
/************************************************2024_11_16修改*********************************************/
use new_community;
select * from comments;/*查詢留言*/
select * from post;/*查詢貼文*/
select * from community;/*查詢社群*/
select * from users;/*查詢用戶*/
/*查詢uid="9dcc32d5-4726-4273-8937-3aa3709097cd"的貼文*/
select *
from post
where uid="9dcc32d5-4726-4273-8937-3aa3709097cd" ;
/*查詢uid="9dcc32d5-4726-4273-8937-3aa3709097cd"的留言*/
select *
from comments
where uid="9dcc32d5-4726-4273-8937-3aa3709097cd" ;
/*更改 post  uid="9dcc32d5-4726-4273-8937-3aa3709097cd"的una*/
update post
set una="123"
where uid="9dcc32d5-4726-4273-8937-3aa3709097cd";


/*使用臨時禁用安全更新模式--->批量更新需要基於特定條件更新多行*/
/*使用臨時禁用指令 SET SQL_SAFE_UPDATES = 0; 是為了允許一些特殊操作，例如更新無索引條件的數據、批量更新或刪除數據。這應僅用於已確認條件正確的情況，並在完成後立即恢復安全模式。*/
SET SQL_SAFE_UPDATES = 0;
/*重新啟用安全更新模式的指令。當啟用安全更新模式後，MySQL 會對 UPDATE 和 DELETE 指令施加以下限制，避免潛在的批量數據修改或刪除風險*/
SET SQL_SAFE_UPDATES = 1;
/*更改 comments uid="9dcc32d5-4726-4273-8937-3aa3709097cd"的una*/
update comments
set una="123"
where uid="9dcc32d5-4726-4273-8937-3aa3709097cd";



