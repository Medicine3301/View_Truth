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
-- Table structure for table `user_activity`
--

DROP TABLE IF EXISTS `user_activity`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_activity` (
  `id` int NOT NULL AUTO_INCREMENT,
  `uid` varchar(200) DEFAULT NULL,
  `activity_type` enum('login','logout','post','comment') NOT NULL,
  `activity_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `uid` (`uid`),
  CONSTRAINT `user_activity_ibfk_1` FOREIGN KEY (`uid`) REFERENCES `users` (`uid`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_activity`
--

LOCK TABLES `user_activity` WRITE;
/*!40000 ALTER TABLE `user_activity` DISABLE KEYS */;
INSERT INTO `user_activity` VALUES (1,'f8b79c16-f589-41d4-84b3-8e73f6ccb307','post','2025-04-02 07:55:04'),(2,'f8b79c16-f589-41d4-84b3-8e73f6ccb307','comment','2025-04-02 07:55:31'),(3,'3c9f2870-ed7d-459f-82bb-cd41dcab695e','post','2025-04-02 07:59:44'),(4,'3c9f2870-ed7d-459f-82bb-cd41dcab695e','comment','2025-04-02 08:00:20'),(5,'f8b79c16-f589-41d4-84b3-8e73f6ccb307','comment','2025-04-24 08:43:22'),(6,'f8b79c16-f589-41d4-84b3-8e73f6ccb307','comment','2025-04-24 08:43:27'),(7,'f8b79c16-f589-41d4-84b3-8e73f6ccb307','comment','2025-04-24 08:51:09'),(8,'f8b79c16-f589-41d4-84b3-8e73f6ccb307','comment','2025-04-24 08:58:10'),(9,'f8b79c16-f589-41d4-84b3-8e73f6ccb307','comment','2025-04-24 08:58:22'),(10,'f8b79c16-f589-41d4-84b3-8e73f6ccb307','comment','2025-04-24 09:23:28'),(11,'f8b79c16-f589-41d4-84b3-8e73f6ccb307','comment','2025-04-24 09:23:36'),(12,'f8b79c16-f589-41d4-84b3-8e73f6ccb307','comment','2025-04-24 09:34:33'),(13,'f8b79c16-f589-41d4-84b3-8e73f6ccb307','comment','2025-04-24 09:34:38'),(14,'f8b79c16-f589-41d4-84b3-8e73f6ccb307','comment','2025-04-24 09:34:44'),(15,'f8b79c16-f589-41d4-84b3-8e73f6ccb307','comment','2025-04-24 09:40:41'),(16,'f8b79c16-f589-41d4-84b3-8e73f6ccb307','comment','2025-04-24 09:40:47'),(17,'f8b79c16-f589-41d4-84b3-8e73f6ccb307','comment','2025-04-24 09:45:07'),(18,'f8b79c16-f589-41d4-84b3-8e73f6ccb307','comment','2025-04-24 09:45:51'),(19,'f8b79c16-f589-41d4-84b3-8e73f6ccb307','comment','2025-04-24 09:46:24');
/*!40000 ALTER TABLE `user_activity` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-05-07 13:44:48
