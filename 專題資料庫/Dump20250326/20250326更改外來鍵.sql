INSERT INTO users (`uid`, `una`) VALUES ('AAAAA', 'Eric');
INSERT INTO post (`uid`, `pid`, `content`) VALUES ('AAAAA', 'P32', 'Eric 的貼文');
INSERT INTO comments (`pid`, `comm_id`, `uid`, `content`) VALUES ('P32', 'RP29', 'AAAAA', 'Alice 的留言');

select* from post;
select * from comments;
select *from users;

DELETE FROM users WHERE uid = 'AAAAA';

/*修改 FOREIGN KEY，加上 ON DELETE CASCADE*/
ALTER TABLE post DROP FOREIGN KEY post_ibfk_1;
ALTER TABLE post 
ADD CONSTRAINT post_ibfk_1 
FOREIGN KEY (uid) REFERENCES users(uid) ON DELETE CASCADE;

/*對所有 pid 相關的表加上 ON DELETE CASCADE*/
ALTER TABLE comments
ADD CONSTRAINT comments_ibfk_1
FOREIGN KEY (pid) REFERENCES post (pid)
ON DELETE CASCADE;

/*刪除trigger*/
ALTER TABLE comments DROP FOREIGN KEY comments_ibfk_1;
/*更改外來鍵*/
ALTER TABLE comments 
ADD CONSTRAINT comments_ibfk_1 
FOREIGN KEY (pid) REFERENCES post(pid) ON DELETE CASCADE;

ALTER TABLE score DROP FOREIGN KEY score_ibfk_1;
ALTER TABLE score 
ADD CONSTRAINT score_ibfk_1 
FOREIGN KEY (pid) REFERENCES post(pid) ON DELETE CASCADE;

SHOW CREATE TABLE comments;
SHOW CREATE TABLE score;

DELETE FROM post WHERE pid = 'P32';
SELECT * FROM comments WHERE pid = 'P32';


