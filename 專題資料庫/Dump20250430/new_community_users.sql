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
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `uid` varchar(200) NOT NULL,
  `una` varchar(20) DEFAULT NULL,
  `usex` varchar(20) DEFAULT NULL,
  `email` varchar(30) DEFAULT NULL,
  `passwd` varchar(100) DEFAULT NULL,
  `birthday` date DEFAULT NULL,
  `role` enum('user','admin') DEFAULT 'user',
  `reg_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`uid`),
  UNIQUE KEY `users_una_unique` (`una`),
  UNIQUE KEY `unique_key` (`email`),
  UNIQUE KEY `unique_una` (`una`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES ('0164413f-e3cf-4096-a759-960e83ce8acc','1111111','1','acr3214@gmail.com','$2b$12$dCDRMe76BbuDVYQEqVsnEu45hzLVrA0mUwyE3DpQ.8kN8xGw.FcT6','2024-10-09','user','2025-04-01 05:32:28'),('3c9f2870-ed7d-459f-82bb-cd41dcab695e','admin1','3','acr@ggg.ccc','$2b$12$6iEuMMhPSKFsz.E5ZLqBFOUT0KQ6CynT20FzLIkmjBZ0aPkteIZK2','2025-03-05','user','2025-03-31 06:41:59'),('73dab09d-4cf0-40cc-ac0d-dca657a8ef0d','Max','1','D11122215@gs.takming.edu.tw','$2b$12$EPwWe31q14nimEfELDlp0uA913Afbq6Krri2MXRRiFraCCSxm5MeS','2004-01-14','user','2025-04-28 04:56:19'),('8911b1d5-ab4c-4c9c-858f-e576ccde85f1','admin2','3','acr@jjj.ccc','$2b$12$csP6px/o.BgDbyxA6VN5XOsQYagHG5h7RkZuZr7yuX9ymBxO/Uyzq','2025-03-05','user','2025-03-31 06:45:04'),('9dcc32d5-4726-4273-8937-3aa3709097cd','123','1','aaaaa@bbb.mm','$2b$12$R4RzD.rc3JRxokAnRRshSeymNO86qHV.utdXSUQ5j4utpnHBozaw.','2007-10-10','user','2025-01-02 03:07:07'),('f1701c74-b5cf-4be2-a687-93454748d7ac','123456','1','AAA@CCC.VVVV','$2b$12$2P1i.Og3y4gUxB7CK/rqi.KeBfKznOR8XAEYjAnmjNk0dmx4TKgbK','2020-01-08','user','2025-01-02 03:07:07'),('f8b79c16-f589-41d4-84b3-8e73f6ccb307','acrhjh','1','aaddd@bb.ccC','$2b$12$9QBrsjqzjkMtKTLIpJi.x.L.HOe960Eh6Qd5p6A332SS3b0gZ3mia','2014-10-16','admin','2025-01-02 03:07:07');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-04-30 16:07:39
