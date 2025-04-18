-- MySQL dump 10.13  Distrib 8.0.41, for Win64 (x86_64)
--
-- Host: localhost    Database: new_community
-- ------------------------------------------------------
-- Server version	8.0.41

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
-- Table structure for table `post`
--

DROP TABLE IF EXISTS `post`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `post` (
  `uid` varchar(200) DEFAULT NULL,
  `pid` varchar(50) NOT NULL,
  `cid` varchar(20) DEFAULT NULL,
  `title` text,
  `content` text,
  `crea_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `comm_count` int DEFAULT '0',
  `una` varchar(20) DEFAULT NULL,
  `rate_sc` float DEFAULT NULL,
  `favorite` int DEFAULT '0',
  PRIMARY KEY (`pid`),
  KEY `uid` (`uid`),
  KEY `cid` (`cid`),
  CONSTRAINT `post_ibfk_1` FOREIGN KEY (`uid`) REFERENCES `users` (`uid`) ON DELETE CASCADE,
  CONSTRAINT `post_ibfk_2` FOREIGN KEY (`cid`) REFERENCES `community` (`cid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `post`
--

LOCK TABLES `post` WRITE;
/*!40000 ALTER TABLE `post` DISABLE KEYS */;
INSERT INTO `post` VALUES ('9dcc32d5-4726-4273-8937-3aa3709097cd','P1','C001','財經股票','測試1','2024-11-13 06:53:38',2,'123',3.5,1),('9dcc32d5-4726-4273-8937-3aa3709097cd','P10','C010','教育','在線學習的優勢與挑戰','2024-11-15 13:09:40',1,'123',3,0),('9dcc32d5-4726-4273-8937-3aa3709097cd','P12','C002','財經股票上升','測試2','2024-11-15 13:13:07',3,'123',0,0),('9dcc32d5-4726-4273-8937-3aa3709097cd','P13','C010','COVID','病毒','2024-11-15 13:19:26',1,'123',0,0),('f8b79c16-f589-41d4-84b3-8e73f6ccb307','P14','C004','財經股票','近期股市表現分析','2024-11-15 13:28:47',2,'acrhjh',0,0),('f8b79c16-f589-41d4-84b3-8e73f6ccb307','P16','C006','科技','AI 技術對未來的影響','2024-11-15 13:29:22',1,'acrhjh',0,0),('f8b79c16-f589-41d4-84b3-8e73f6ccb307','P17','C007','藝術','探索現代藝術的無限可能','2024-11-15 13:29:25',1,'acrhjh',0,0),('f8b79c16-f589-41d4-84b3-8e73f6ccb307','P18','C008','旅遊','分享夏日海島旅行的心得','2024-11-15 13:29:28',1,'acrhjh',0,0),('f8b79c16-f589-41d4-84b3-8e73f6ccb307','P19','C009','健康','健康飲食的十大原則','2024-11-15 13:29:30',1,'acrhjh',0,0),('f8b79c16-f589-41d4-84b3-8e73f6ccb307','P2','C002','運動!!','測試2','2024-11-13 06:52:09',2,'acrhjh',3,0),('f8b79c16-f589-41d4-84b3-8e73f6ccb307','P20','C010','教育','在線學習的優勢與挑戰','2024-11-15 13:29:32',1,'acrhjh',0,0),('f8b79c16-f589-41d4-84b3-8e73f6ccb307','P21','C010','教育','在線學習的優勢與挑戰','2024-11-15 13:29:35',1,'acrhjh',0,0),('f8b79c16-f589-41d4-84b3-8e73f6ccb307','P22','C010','教育1','在線學習的劣勢與挑戰','2024-11-15 13:29:37',1,'acrhjh',0,0),('f8b79c16-f589-41d4-84b3-8e73f6ccb307','P23','C010','教育2','在線學習的挑戰極限','2024-11-15 13:29:40',1,'acrhjh',0,0),('f8b79c16-f589-41d4-84b3-8e73f6ccb307','P24','C001','123','<p>12</p>','2024-12-27 06:42:21',0,'acrhjh',0,0),('f8b79c16-f589-41d4-84b3-8e73f6ccb307','P25','C001','123123','<p>123213123</p><p><br></p><h4><br></h4><p>1212312</p><p><br></p><p><br></p><p><span style=\"font-size:26px;\">123123123</span></p><p><br></p><h2><span style=\"font-size:26px;\">23123232323232323</span></h2><p>123123213</p>','2024-12-27 07:50:43',0,'acrhjh',0,0),('f8b79c16-f589-41d4-84b3-8e73f6ccb307','P26','C005','123','<p>123</p><p>123</p><p>123</p><p>1222222123</p><p>123123123123123123123</p><p><br></p><p><br></p><p><br></p>','2024-12-27 08:07:21',1,'acrhjh',0,0),('f8b79c16-f589-41d4-84b3-8e73f6ccb307','P27','C002','闢謠環節','<h1>測試用途</h1><p>有趣</p><p><br></p><p>跳行</p><p><br></p><p><br></p><p><br></p><p><br></p><p><strong><em>aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa</em></strong></p><p><strong><em>aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa</em></strong></p><p><br></p><p><strong><em><u class=\"ql-custom-strike\">1111111111111111111111111111111111111111111111111111111111</u></em></strong></p><div class=\"ql-code-block-container\" spellcheck=\"false\"><div class=\"ql-code-block\">&lt;div&gt;</div><div class=\"ql-code-block\">   &lt;h1&gt;代碼&lt;h1/&gt; </div><div class=\"ql-code-block\">&lt;/div&gt;</div></div><p><a class=\"ql-normal-link\" href=\"https://github.com/\">https://github.com/</a></p><p><br></p><p><span style=\"font-size:36px;\" class=\"ql-font-yahei\">哈哈</span></p><p><br></p><p><span style=\"font-size:18px;\" class=\"ql-font-kaiti\">哈哈</span></p><p><br></p><p><br></p><p><br></p>','2025-01-02 02:55:02',1,'acrhjh',0,0),('f8b79c16-f589-41d4-84b3-8e73f6ccb307','P28','C002','程式','<div class=\"ql-code-block-container\" spellcheck=\"false\"><div class=\"ql-code-block\">&lt;div&gt;123123&lt;/div&gt;</div><div class=\"ql-code-block\">import random as rd </div><div class=\"ql-code-block\">if a==b</div><div class=\"ql-code-block\">ddddd</div><div class=\"ql-code-block\">&lt;img src=\"\"/&gt;</div></div>','2025-01-02 02:57:33',0,'acrhjh',0,0),('f8b79c16-f589-41d4-84b3-8e73f6ccb307','P29','C002','123','<div class=\"ql-code-block-container\" spellcheck=\"false\"><div class=\"ql-code-block\">OKOKOKOKOKOKOKKOKOKOKOKOK</div></div>','2025-01-02 02:59:27',0,'acrhjh',0,0),('f8b79c16-f589-41d4-84b3-8e73f6ccb307','P3','C003','國內政治!!','測試3','2024-11-13 06:52:09',2,'acrhjh',0,0),('f8b79c16-f589-41d4-84b3-8e73f6ccb307','P30','C001','123123123','<p><span style=\"text-decoration: underline; color: #f1c40f;\"><strong>1231231233123</strong></span></p>','2025-03-05 05:26:39',0,'acrhjh',0,0),('f8b79c16-f589-41d4-84b3-8e73f6ccb307','P31','C002','123123123','<h1>123213213123</h1>\n<h4>12312312312312312312312312312312312312</h4>','2025-03-05 06:33:40',0,'acrhjh',0,0),('9dcc32d5-4726-4273-8937-3aa3709097cd','P4','C004','財經股票','近期股市表現分析','2024-11-15 13:06:48',1,'123',0,0),('9dcc32d5-4726-4273-8937-3aa3709097cd','P5','C005','運動','籃球世界盃賽事回顧','2024-11-15 13:07:42',1,'123',0,0),('9dcc32d5-4726-4273-8937-3aa3709097cd','P6','C006','科技','AI 技術對未來的影響','2024-11-15 13:09:02',1,'123',0,0),('9dcc32d5-4726-4273-8937-3aa3709097cd','P7','C007','藝術','探索現代藝術的無限可能','2024-11-15 13:09:12',1,'123',0,0),('9dcc32d5-4726-4273-8937-3aa3709097cd','P8','C008','旅遊','分享夏日海島旅行的心得','2024-11-15 13:09:23',1,'123',0,0),('9dcc32d5-4726-4273-8937-3aa3709097cd','P9','C009','健康','健康飲食的十大原則','2024-11-15 13:09:35',1,'123',0,0);
/*!40000 ALTER TABLE `post` ENABLE KEYS */;
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
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `community_post_count` AFTER INSERT ON `post` FOR EACH ROW -- 對於每一行插入的貼文
BEGIN -- 開始觸發器的主體
  UPDATE community -- 更新 community 表
  SET last_update = CURRENT_TIMESTAMP ,post_count=post_count+1-- 將社群的 last_update 欄位設為當前時間
  WHERE cid = NEW.cid; -- 以新增的貼文中的 cid 為條件進行更新
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

-- Dump completed on 2025-04-01 15:40:09
