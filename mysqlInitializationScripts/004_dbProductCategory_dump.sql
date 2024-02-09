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
-- Table structure for table `dbProductCategory`
--

DROP TABLE IF EXISTS `dbProductCategory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dbProductCategory` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `create_time` datetime(6) NOT NULL,
  `update_time` datetime(6) NOT NULL,
  `is_delete` tinyint(1) NOT NULL,
  `name` varchar(40) NOT NULL,
  `nameEN` varchar(40) NOT NULL,
  `logo` varchar(255) NOT NULL,
  `image` varchar(255) NOT NULL,
  `detail` longtext NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `dbProductCategory`
--

LOCK TABLES `dbProductCategory` WRITE;
/*!40000 ALTER TABLE `dbProductCategory` DISABLE KEYS */;
INSERT INTO `dbProductCategory` VALUES (1,'2024-01-21 11:45:04.528822','2024-01-21 11:45:04.528833',0,'婴幼儿奶粉','babyFormula','images/productCategory/babyFormula.png','images/productCategory/babyFormula.jpg','\r'),(2,'2024-01-21 11:45:04.535795','2024-01-21 11:45:04.535800',0,'成人奶粉','adultFormula','images/productCategory/adultFormula.png','images/productCategory/adultFormula.jpg','\r'),(3,'2024-01-21 11:45:04.543520','2024-01-21 11:45:04.543525',0,'保健品','health','images/productCategory/health.png','images/productCategory/health.jpg','\r'),(4,'2024-01-21 11:45:04.554175','2024-01-21 11:45:04.554196',0,'食品','food','images/productCategory/food.png','images/productCategory/food.jpg','\r'),(5,'2024-01-21 11:45:04.563819','2024-01-21 11:45:04.563836',0,'日用品','dailyCare','images/productCategory/dailyCare.png','images/productCategory/dailyCare.jpg','\r'),(6,'2024-01-21 11:45:04.570460','2024-01-21 11:45:04.570465',0,'护肤品','skinCare','images/productCategory/skinCare.png','images/productCategory/skinCare.jpg','\r'),(7,'2024-01-21 11:45:04.577337','2024-01-21 11:45:04.577342',0,'化妆品','cosmetics','images/productCategory/cosmetics.png','images/productCategory/cosmetics.jpg','\r'),(8,'2024-01-21 11:45:04.584156','2024-01-21 11:45:04.584162',0,'玩具','toy','images/productCategory/toy.png','images/productCategory/toy.jpg','\r'),(9,'2024-01-21 11:45:04.589437','2024-01-21 11:45:04.589442',0,'鞋子','shoes','images/productCategory/shoes.png','images/productCategory/shoes.jpg','');
/*!40000 ALTER TABLE `dbProductCategory` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-01-31  9:24:37
