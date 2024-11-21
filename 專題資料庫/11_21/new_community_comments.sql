-- MySQL dump 10.13  Distrib 8.0.40, for Win64 (x86_64)
--
-- Host: localhost    Database: new_community
-- ------------------------------------------------------
-- Server version	8.0.40

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `comments`
--

DROP TABLE IF EXISTS `comments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `comments` (
  `pid` varchar(50) DEFAULT NULL,
  `comm_id` varchar(50) NOT NULL,
  `uid` varchar(200) DEFAULT NULL,
  `title` varchar(50) DEFAULT NULL,
  `content` varchar(50) DEFAULT NULL,
  `nid` varchar(50) DEFAULT NULL,
  `una` varchar(20) DEFAULT NULL,
  `crea_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`comm_id`),
  KEY `pid` (`pid`),
  KEY `nid` (`nid`),
  CONSTRAINT `comments_ibfk_1` FOREIGN KEY (`pid`) REFERENCES `post` (`pid`),
  CONSTRAINT `comments_ibfk_2` FOREIGN KEY (`nid`) REFERENCES `news` (`news_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `comments`
--

LOCK TABLES `comments` WRITE;
/*!40000 ALTER TABLE `comments` DISABLE KEYS */;
INSERT INTO `comments` VALUES ('P1','RP1','9dcc32d5-4726-4273-8937-3aa3709097cd','留言1','content1',NULL,'123','2024-11-13 07:49:29'),('P6','RP10','9dcc32d5-4726-4273-8937-3aa3709097cd','AI 未來影響','AI 在未來的發展潛力巨大，值得關注。',NULL,'123','2024-11-15 13:43:12'),('P7','RP11','9dcc32d5-4726-4273-8937-3aa3709097cd','現代藝術','現代藝術真的是無窮無盡，總有新的驚喜。',NULL,'123','2024-11-15 13:43:12'),('P8','RP12','9dcc32d5-4726-4273-8937-3aa3709097cd','夏日旅行','海島旅行真的很放鬆，尤其是享受陽光沙灘的時光。',NULL,'123','2024-11-15 13:43:12'),('P9','RP13','9dcc32d5-4726-4273-8937-3aa3709097cd','健康飲食','健康飲食的原則真是生活的必需，保持飲食均衡。',NULL,'123','2024-11-15 13:43:12'),('P14','RP14','f8b79c16-f589-41d4-84b3-8e73f6ccb307','股市分析','股市的變動性越來越大，值得持續關注。',NULL,'acrhjh','2024-11-15 13:54:41'),('P14','RP15','f8b79c16-f589-41d4-84b3-8e73f6ccb307','籃球賽事回顧','這場比賽激烈精彩，特別是最後的逆轉！',NULL,'acrhjh','2024-11-15 14:00:56'),('P16','RP16','f8b79c16-f589-41d4-84b3-8e73f6ccb307','AI 技術','AI 的未來發展會大大改變我們的生活，值得期待。',NULL,'acrhjh','2024-11-15 14:01:02'),('P17','RP17','f8b79c16-f589-41d4-84b3-8e73f6ccb307','現代藝術','現代藝術的創新和挑戰，讓人目不暇接。',NULL,'acrhjh','2024-11-15 14:01:08'),('P18','RP18','f8b79c16-f589-41d4-84b3-8e73f6ccb307','夏日旅行','夏日海島的海風和沙灘是最放鬆的享受。',NULL,'acrhjh','2024-11-15 14:01:15'),('P19','RP19','f8b79c16-f589-41d4-84b3-8e73f6ccb307','健康飲食原則','健康飲食對保持身體健康至關重要。',NULL,'acrhjh','2024-11-15 14:01:28'),('P2','RP2','f8b79c16-f589-41d4-84b3-8e73f6ccb307','德明財經科技大學','資管系',NULL,'acrhjh','2024-11-13 07:49:29'),('P20','RP20','f8b79c16-f589-41d4-84b3-8e73f6ccb307','在線學習的挑戰','在線學習確實有很多挑戰，特別是在自我管理方面。',NULL,'acrhjh','2024-11-15 14:01:34'),('P21','RP21','f8b79c16-f589-41d4-84b3-8e73f6ccb307','在線學習的優勢','在線學習方便靈活，讓我們可以隨時隨地學習。',NULL,'acrhjh','2024-11-15 14:01:40'),('P22','RP22','f8b79c16-f589-41d4-84b3-8e73f6ccb307','在線學習的劣勢','在線學習的最大問題是缺乏面對面互動，學習效果會受影響。',NULL,'acrhjh','2024-11-15 14:01:48'),('P23','RP23','f8b79c16-f589-41d4-84b3-8e73f6ccb307','在線學習的挑戰','在線學習的挑戰在於如何保持專注和積極參與。',NULL,'acrhjh','2024-11-15 14:01:54'),('P2','RP24','f8b79c16-f589-41d4-84b3-8e73f6ccb307','運動測試','這篇測試文章不錯，可以再加一些細節。',NULL,'acrhjh','2024-11-15 14:02:00'),('P3','RP25','f8b79c16-f589-41d4-84b3-8e73f6ccb307','國內政治','政治動態十分複雜，特別是最近的政策變動。',NULL,'acrhjh','2024-11-15 14:02:07'),('P3','RP3','9dcc32d5-4726-4273-8937-3aa3709097cd','龍華科大','資訊工程學系',NULL,'123','2024-11-13 07:49:29'),('P1','RP4','9dcc32d5-4726-4273-8937-3aa3709097cd','股票市場的波動','這篇文章的分析很深入，值得一看。',NULL,'123','2024-11-15 13:43:12'),('P12','RP5','9dcc32d5-4726-4273-8937-3aa3709097cd','股票升勢','是否會繼續上升呢？',NULL,'123','2024-11-15 13:43:12'),('P13','RP6','9dcc32d5-4726-4273-8937-3aa3709097cd','病毒疫情分析','希望疫情能盡快結束，大家要保持警覺。',NULL,'123','2024-11-15 13:43:12'),('P10','RP7','9dcc32d5-4726-4273-8937-3aa3709097cd','在線學習的挑戰','在線學習真的有很多挑戰，特別是集中注意力。',NULL,'123','2024-11-15 13:43:12'),('P4','RP8','9dcc32d5-4726-4273-8937-3aa3709097cd','股市分析','最近股市的波動性很大，讓人不敢輕易投資。',NULL,'123','2024-11-15 13:43:12'),('P5','RP9','9dcc32d5-4726-4273-8937-3aa3709097cd','籃球世界盃','這場比賽很精彩，尤其是最後一場決賽！',NULL,'123','2024-11-15 13:43:12');
/*!40000 ALTER TABLE `comments` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `post_comment_count` AFTER INSERT ON `comments` FOR EACH ROW BEGIN
  IF NEW.pid IS NOT NULL THEN
    UPDATE post
    SET comm_count = comm_count + 1
    WHERE pid = NEW.pid;
  END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `new_comment_count` AFTER INSERT ON `comments` FOR EACH ROW BEGIN
  UPDATE news -- 更新 news 表中對應的 news_id 新聞的留言數量
  SET count = count + 1 -- 將該新聞的點擊次數加 1
  WHERE news_id = NEW.nid; -- 以新增的留言中 nid 為條件
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-11-21 14:15:36
