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
-- Table structure for table `community`
--

DROP TABLE IF EXISTS `community`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `community` (
  `crea_id` varchar(200) DEFAULT NULL,
  `cid` varchar(20) NOT NULL,
  `cna` varchar(50) DEFAULT NULL,
  `descr` text,
  `crea_na` varchar(50) DEFAULT NULL,
  `crea_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `last_update` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `post_count` int DEFAULT '0',
  PRIMARY KEY (`cid`),
  KEY `crea_id` (`crea_id`),
  CONSTRAINT `community_ibfk_1` FOREIGN KEY (`crea_id`) REFERENCES `users` (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `community`
--

LOCK TABLES `community` WRITE;
/*!40000 ALTER TABLE `community` DISABLE KEYS */;
INSERT INTO `community` VALUES ('f8b79c16-f589-41d4-84b3-8e73f6ccb307','C001','八卦','就是八卦','acrhjh','2024-11-13 04:42:41','2024-11-21 06:11:23',1),('f8b79c16-f589-41d4-84b3-8e73f6ccb307','C002','闢謠','就是闢謠','acrhjh','2024-11-13 04:42:41','2024-11-21 06:11:58',2),('f8b79c16-f589-41d4-84b3-8e73f6ccb307','C003','感情','就是感情','acrhjh','2024-11-13 04:42:41','2024-11-21 06:12:19',1),('f8b79c16-f589-41d4-84b3-8e73f6ccb307','C004','新聞','就是新聞','acrhjh','2024-11-13 04:42:41','2024-11-21 06:12:37',2),('f8b79c16-f589-41d4-84b3-8e73f6ccb307','C005','股票','就是股票','acrhjh','2024-11-13 04:42:41','2024-11-21 06:12:57',1),('f8b79c16-f589-41d4-84b3-8e73f6ccb307','C006','運動','就是運動','acrhjh','2024-11-13 06:16:03','2024-11-21 06:13:32',2),('f8b79c16-f589-41d4-84b3-8e73f6ccb307','C007','財經','最新財經新聞','acrhjh','2024-11-13 06:28:38','2024-11-21 06:13:53',2),('f8b79c16-f589-41d4-84b3-8e73f6ccb307','C008','政治','政治內亂','acrhjh','2024-11-13 06:28:38','2024-11-21 06:14:25',2),('f8b79c16-f589-41d4-84b3-8e73f6ccb307','C009','外國新聞','林書豪','acrhjh','2024-11-13 06:28:38','2024-11-21 06:14:46',2),('f8b79c16-f589-41d4-84b3-8e73f6ccb307','C010','美食','台灣美食','acrhjh','2024-11-13 06:28:38','2024-11-21 06:15:16',6);
/*!40000 ALTER TABLE `community` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-11-21 14:15:36
