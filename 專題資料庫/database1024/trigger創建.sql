use new_community;
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


DELIMITER //

CREATE TRIGGER community_post_count
AFTER INSERT ON post
FOR EACH ROW
BEGIN
  UPDATE community
  SET last_update = CURRENT_TIMESTAMP
  WHERE cid = NEW.cid;
END //

DELIMITER ;