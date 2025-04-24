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
-- Table structure for table `user_statistics`
--

DROP TABLE IF EXISTS `user_statistics`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_statistics` (
  `id` int NOT NULL AUTO_INCREMENT,
  `uid` varchar(200) NOT NULL,
  `post_count` int DEFAULT '0',
  `comment_count` int DEFAULT '0',
  `last_updated` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `status` enum('normal','banned','disabled') DEFAULT 'normal',
  `una` varchar(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `uid` (`uid`),
  CONSTRAINT `user_statistics_ibfk_1` FOREIGN KEY (`uid`) REFERENCES `users` (`uid`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_statistics`
--

LOCK TABLES `user_statistics` WRITE;
/*!40000 ALTER TABLE `user_statistics` DISABLE KEYS */;
INSERT INTO `user_statistics` VALUES (1,'f8b79c16-f589-41d4-84b3-8e73f6ccb307',14,12,'2025-04-23 07:30:08','normal','acrhjh'),(2,'0164413f-e3cf-4096-a759-960e83ce8acc',0,0,'2025-04-22 13:27:11','normal','1111111'),(3,'3c9f2870-ed7d-459f-82bb-cd41dcab695e',1,1,'2025-04-22 13:27:14','normal','admin1'),(4,'8911b1d5-ab4c-4c9c-858f-e576ccde85f1',0,0,'2025-04-22 13:27:13','normal','admin2'),(5,'6446e091-9770-4656-8427-0b4b281b07c1',0,0,'2025-04-22 13:25:45','normal','11111111'),(6,'8c1f6218-a7c2-492a-baae-ee223f6d24f7',0,0,'2025-04-22 13:19:43','normal','aaaaaaaa'),(7,'8a60195e-6188-4cad-9465-52bfe320f9d0',0,0,'2025-04-22 13:30:36','normal','nnnnnnnnnnn'),(8,'e0e77298-3bca-4d35-abd4-e40a7776017e',0,0,'2025-04-24 07:29:03','banned','OOOO'),(9,'6617914f-44db-4bab-9a52-1a573aed7cb3',0,0,'2025-04-23 07:26:18','banned','acrkkk'),(10,'8280f6f9-c056-4148-aee8-e22855b79f8e',0,0,'2025-04-23 07:26:18','banned','11111111111'),(11,'baa05a88-e042-4b76-ab7e-7372a4d39066',0,0,'2025-04-23 07:26:18','banned','acrkkk666');
/*!40000 ALTER TABLE `user_statistics` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-04-24 15:43:17
