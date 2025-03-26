DELIMITER //

CREATE TRIGGER delete_user_data
AFTER DELETE ON users
FOR EACH ROW
BEGIN
    -- 先刪除該用戶的留言
    DELETE FROM comment WHERE uid = OLD.uid;

    -- 再刪除該用戶的貼文（會連帶刪除 comment 表內相關留言）
    DELETE FROM post WHERE uid = OLD.uid;
END;
//

DELIMITER ;
