-- MySQL dump 10.13  Distrib 8.1.0, for macos13.3 (arm64)
--
-- Host: localhost    Database: auking
-- ------------------------------------------------------
-- Server version	8.1.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `dbProductLogisticsEWE`
--

DROP TABLE IF EXISTS `dbProductLogisticsEWE`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dbProductLogisticsEWE` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `create_time` datetime(6) NOT NULL,
  `update_time` datetime(6) NOT NULL,
  `is_delete` tinyint(1) NOT NULL,
  `name` varchar(256) NOT NULL,
  `canBeMixed` smallint NOT NULL,
  `maxQtyperSkuperParcelStandAlone` int NOT NULL,
  `maxQtyperCategoryperParcelStandAlone` int NOT NULL,
  `maxQtyperParcelMixed` int NOT NULL,
  `extraTax` decimal(10,2) NOT NULL,
  `maxTotalQtyperParcel` int NOT NULL,
  `maxTotalWeightperParcel` decimal(10,2) NOT NULL,
  `maxTotalValueperParcel` decimal(10,2) NOT NULL,
  `price` decimal(10,2) NOT NULL,
  `gst` decimal(10,2) NOT NULL,
  `unit` varchar(20) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `dbProductLogisticsEWE`
--

LOCK TABLES `dbProductLogisticsEWE` WRITE;
/*!40000 ALTER TABLE `dbProductLogisticsEWE` DISABLE KEYS */;
INSERT INTO `dbProductLogisticsEWE` VALUES (1,'2024-01-21 11:44:44.811700','2024-01-21 11:44:44.811748',0,'罐装奶粉',0,3,3,0,0.00,3,4.50,150.00,7.80,0.00,'Kg\r'),(2,'2024-01-21 11:44:44.826014','2024-01-21 11:44:44.826044',0,'袋装奶粉',1,8,8,5,0.00,8,4.50,150.00,7.80,0.00,'Kg\r'),(3,'2024-01-21 11:44:44.840398','2024-01-21 11:44:44.840439',0,'袋装奶粉+食品/保健品',1,5,5,4,0.00,5,4.50,150.00,7.80,0.00,'Kg\r'),(4,'2024-01-21 11:44:44.853989','2024-01-21 11:44:44.854017',0,'保健品/食品',1,10,10,9,0.00,10,4.50,150.00,7.80,0.00,'Kg\r'),(5,'2024-01-21 11:44:44.868686','2024-01-21 11:44:44.868723',0,'洗护产品+保健品/食品',1,3,3,3,0.00,6,4.00,150.00,7.80,0.00,'Kg\r'),(6,'2024-01-21 11:44:44.883222','2024-01-21 11:44:44.883250',0,'洗护产品+保健品/食品+ 奶瓶，水杯，卫生巾，玩具，牙刷头，塑料餐具等杂货',1,3,3,3,0.00,6,4.00,150.00,7.80,0.00,'Kg\r'),(7,'2024-01-21 11:44:44.897145','2024-01-21 11:44:44.897172',0,'化妆品(单品不超过 $30，不含轻奢/奢侈品 牌，非礼盒)',1,3,3,3,0.00,3,4.00,150.00,7.80,0.00,'Kg\r'),(8,'2024-01-21 11:44:44.911045','2024-01-21 11:44:44.911085',0,'化妆品+洗护产品+保健 品/食品',1,2,2,2,0.00,6,4.00,150.00,7.80,0.00,'Kg\r'),(9,'2024-01-21 11:44:44.926453','2024-01-21 11:44:44.926509',0,'鞋类',0,1,1,0,0.00,1,4.00,150.00,7.80,0.00,'Kg\r'),(10,'2024-01-21 11:44:44.941275','2024-01-21 11:44:44.941306',0,'服装类(衣服，围巾等)',0,1,1,0,20.00,1,4.00,150.00,7.80,0.00,'Kg\r'),(11,'2024-01-21 11:44:44.954948','2024-01-21 11:44:44.954976',0,'被子',0,1,1,0,30.00,1,4.00,150.00,12.00,0.00,'Kg\r'),(12,'2024-01-21 11:44:44.967992','2024-01-21 11:44:44.968016',0,'酸奶桶 ',0,1,1,0,0.00,1,4.00,150.00,9.00,0.00,'Kg\r'),(13,'2024-01-21 11:44:44.981904','2024-01-21 11:44:44.981939',0,'葡萄酒【单瓶<$200】',0,2,2,0,30.00,2,10.00,500.00,9.00,0.00,'Kg\r'),(14,'2024-01-21 11:44:44.996556','2024-01-21 11:44:44.996590',0,'包 ',0,1,1,0,0.00,1,5.00,400.00,17.00,0.00,'Kg\r'),(15,'2024-01-21 11:44:45.011196','2024-01-21 11:44:45.011235',0,'首饰 ',0,2,2,0,0.00,2,5.00,400.00,17.00,0.00,'Kg\r'),(16,'2024-01-21 11:44:45.025728','2024-01-21 11:44:45.025758',0,'化妆品、洗护产品 ',0,5,5,0,0.00,5,5.00,400.00,17.00,0.00,'Kg\r'),(17,'2024-01-21 11:44:45.039459','2024-01-21 11:44:45.039488',0,'服饰 ',0,1,1,0,0.00,1,5.00,400.00,17.00,0.00,'Kg\r'),(18,'2024-01-21 11:44:45.052945','2024-01-21 11:44:45.052973',0,'鞋 ',0,1,1,0,0.00,1,5.00,400.00,17.00,0.00,'Kg\r'),(19,'2024-01-21 11:44:45.067548','2024-01-21 11:44:45.067571',0,'小家电 ',0,1,1,0,0.00,1,5.00,400.00,17.00,0.00,'Kg\r'),(20,'2024-01-21 11:44:45.080291','2024-01-21 11:44:45.080318',0,'眼镜',0,2,2,0,0.00,2,5.00,400.00,17.00,0.00,'Kg');
/*!40000 ALTER TABLE `dbProductLogisticsEWE` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-01-31  9:24:06
