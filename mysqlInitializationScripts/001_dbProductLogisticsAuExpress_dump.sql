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
-- Table structure for table `dbProductLogisticsAuExpress`
--

DROP TABLE IF EXISTS `dbProductLogisticsAuExpress`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dbProductLogisticsAuExpress` (
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
) ENGINE=InnoDB AUTO_INCREMENT=43 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `dbProductLogisticsAuExpress`
--

LOCK TABLES `dbProductLogisticsAuExpress` WRITE;
/*!40000 ALTER TABLE `dbProductLogisticsAuExpress` DISABLE KEYS */;
INSERT INTO `dbProductLogisticsAuExpress` VALUES (1,'2024-01-21 11:44:29.841682','2024-01-21 11:44:29.841704',0,'纯奶粉-婴儿/成人罐装牛奶粉/羊奶粉',0,3,3,0,0.00,3,4.00,150.00,7.80,0.00,'Kg\r'),(2,'2024-01-21 11:44:29.857435','2024-01-21 11:44:29.857451',0,'纯奶粉袋装-成人袋装牛奶粉',0,6,6,0,0.00,6,4.00,150.00,7.80,0.00,'Kg\r'),(3,'2024-01-21 11:44:29.867604','2024-01-21 11:44:29.867619',0,'纯保健品类-乳铁蛋白粉 / Xenical 排油丸 / 月光宝盒花青素 / 婕斯 / 白藜芦醇 / NADASEA / EZZ (不承运 NMN) / BIOGENCY / SYNEXT / Kyani / Cellife / Concord 康道',0,1,1,0,0.00,1,4.00,150.00,7.80,0.00,'Kg\r'),(4,'2024-01-21 11:44:29.880219','2024-01-21 11:44:29.880229',0,'纯保健品类-Usana / Vierra / Syneregen / Fitline / Vida Glow / Nuskin 如新',1,2,2,1,0.00,10,4.00,150.00,7.80,0.00,'Kg\r'),(5,'2024-01-21 11:44:29.892336','2024-01-21 11:44:29.892345',0,'纯保健品类-普通保健品【特殊保健品除外】',1,6,8,6,0.00,10,4.00,150.00,7.80,0.00,'Kg\r'),(6,'2024-01-21 11:44:29.902706','2024-01-21 11:44:29.902715',0,'纯保健品类-麦卢卡蜂蜜 Manuka / 男女爱乐维',1,1,1,1,0.00,10,4.00,150.00,7.80,0.00,'Kg\r'),(7,'2024-01-21 11:44:29.913609','2024-01-21 11:44:29.913630',0,'纯食品类-婴儿食品 (米糊 / 米粉 / 果泥 / 米饼 / 泡芙 / 磨牙棒等)',1,15,15,6,0.00,10,4.00,150.00,7.80,0.00,'Kg\r'),(8,'2024-01-21 11:44:29.924197','2024-01-21 11:44:29.924207',0,'纯食品类其他食品-咖啡粉 / 茶包 / 巧克力 / 饼干 / 麦片 / 糖果 / 薯片 / 果干 / 坚果 / 蜂蜜 等 【套装套盒/T2/维生素软糖/麦卢卡蜂蜜除外】',1,6,8,6,0.00,10,4.00,150.00,7.80,0.00,'Kg\r'),(9,'2024-01-21 11:44:29.936161','2024-01-21 11:44:29.936170',0,'纯护肤类-护肤套装【每套≤$50】',0,1,1,0,0.00,1,4.00,150.00,7.80,0.00,'Kg\r'),(10,'2024-01-21 11:44:29.948048','2024-01-21 11:44:29.948066',0,'纯护肤类-Aesop 伊索 / Jurlique 茱莉蔻 / Nuskin 如新',0,1,1,0,0.00,1,4.00,150.00,7.80,0.00,'Kg\r'),(11,'2024-01-21 11:44:29.962756','2024-01-21 11:44:29.962787',0,'纯护肤类-面霜 / 洗面奶 / 爽肤水 / 精华 / 眼霜 / 防晒霜【单瓶≤$30】',1,3,3,2,0.00,10,4.00,150.00,7.80,0.00,'Kg\r'),(12,'2024-01-21 11:44:29.974968','2024-01-21 11:44:29.974991',0,'纯护肤类-面霜 / 洗面奶 / 爽肤水 / 精华 / 眼霜 / 防晒霜【单瓶≤$50】',1,1,1,1,0.00,10,4.00,150.00,7.80,0.00,'Kg\r'),(13,'2024-01-21 11:44:29.986216','2024-01-21 11:44:29.986239',0,'纯彩妆类-彩妆套装【每套≤$30】',0,1,1,0,0.00,1,4.00,150.00,7.80,0.00,'Kg\r'),(14,'2024-01-21 11:44:29.998912','2024-01-21 11:44:29.998935',0,'纯彩妆类-彩妆套装【每套≤$50】',0,1,1,0,0.00,1,4.00,150.00,7.80,0.00,'Kg\r'),(15,'2024-01-21 11:44:30.013404','2024-01-21 11:44:30.013431',0,'纯彩妆类-BB霜 / 眼影 / 眼线笔 / 粉饼 / 口红 / 睫毛膏等【单瓶≤$20】',1,2,3,1,0.00,10,4.00,150.00,7.80,0.00,'Kg\r'),(16,'2024-01-21 11:44:30.027720','2024-01-21 11:44:30.027755',0,'纯彩妆类-BB霜 / 眼影 / 眼线笔 / 粉饼 / 口红 / 睫毛膏等【单瓶≤$30】',1,3,3,1,0.00,10,4.00,150.00,7.80,0.00,'Kg\r'),(17,'2024-01-21 11:44:30.038849','2024-01-21 11:44:30.038870',0,'纯日用品类-护发油【单瓶≤$30】',1,2,2,1,0.00,10,4.00,150.00,7.80,0.00,'Kg\r'),(18,'2024-01-21 11:44:30.050266','2024-01-21 11:44:30.050289',0,'纯日用品类-护发油【单瓶≤$50】',1,1,1,1,0.00,10,4.00,150.00,7.80,0.00,'Kg\r'),(19,'2024-01-21 11:44:30.062918','2024-01-21 11:44:30.062940',0,'纯日用品类-绵羊油 / 普通牙刷 / 牙膏 / 木瓜膏',1,6,8,4,0.00,10,4.00,150.00,7.80,0.00,'Kg\r'),(20,'2024-01-21 11:44:30.074270','2024-01-21 11:44:30.074291',0,'纯日用品类-羊奶皂',1,12,12,4,0.00,10,4.00,150.00,7.80,0.00,'Kg\r'),(21,'2024-01-21 11:44:30.085441','2024-01-21 11:44:30.085462',0,'纯日用品类-沐浴露 / 洗发水 / 护发素 / 洗液 / 隐形眼镜清理液 等清洁用品',1,4,6,4,0.00,10,4.00,150.00,7.80,0.00,'Kg\r'),(22,'2024-01-21 11:44:30.099108','2024-01-21 11:44:30.099137',0,'纯日用品类-婴儿餐具 (水杯/碗/叉勺/吸管/围嘴/咬咬袋/ 盘子/分格盒/奶瓶/奶嘴等) 【保温杯除外】',1,2,5,4,0.00,10,4.00,150.00,7.80,0.00,'Kg\r'),(23,'2024-01-21 11:44:30.113147','2024-01-21 11:44:30.113170',0,'纯日用品类-水杯套装 / 保温杯套装 / 奶瓶套装 / 发油套装 等日用类套装 【每套$50 以内】',0,1,1,0,0.00,1,4.00,150.00,7.80,0.00,'Kg\r'),(24,'2024-01-21 11:44:30.127211','2024-01-21 11:44:30.127245',0,'纯日用品类-保温杯 / 马克杯 / 滤水壶 / 滤芯 / 成人水杯【T2 除外】',0,1,1,0,0.00,1,4.00,150.00,7.80,0.00,'Kg\r'),(25,'2024-01-21 11:44:30.142852','2024-01-21 11:44:30.142874',0,'纯日用品类-卫生巾独立袋装',0,6,6,0,0.00,6,4.00,150.00,7.80,0.00,'Kg\r'),(26,'2024-01-21 11:44:30.154235','2024-01-21 11:44:30.154257',0,'纯日用品类-电动牙刷 Oral B【价值不超$30，需要取出电池】',0,1,1,0,0.00,1,4.00,150.00,7.80,0.00,'Kg\r'),(27,'2024-01-21 11:44:30.166004','2024-01-21 11:44:30.166029',0,'药品类-外包装显示 AUST R 编码的非处方药(痔疮膏/脚 气膏/痛经片/打虫巧克力/小犀牛/Panadol 等)',1,3,3,2,0.00,10,4.00,150.00,7.80,0.00,'Kg\r'),(28,'2024-01-21 11:44:30.176967','2024-01-21 11:44:30.176987',0,'药品类-戒烟喷雾 1 支装 / 2 支装',0,2,2,0,0.00,2,4.00,150.00,7.80,0.00,'Kg\r'),(29,'2024-01-21 11:44:30.188985','2024-01-21 11:44:30.189008',0,'药品类-戒烟喷雾 3 支装',0,1,1,0,0.00,1,4.00,150.00,7.80,0.00,'Kg\r'),(30,'2024-01-21 11:44:30.204083','2024-01-21 11:44:30.204118',0,'药品类-戒烟糖【不承运 216 粒、432 粒、分阶段的，单件≤$20】',0,3,3,0,0.00,3,4.00,150.00,7.80,0.00,'Kg\r'),(31,'2024-01-21 11:44:30.218016','2024-01-21 11:44:30.218046',0,'药品类-戒烟糖【不承运 216 粒、432 粒、分阶段的，单件≤$50】',0,3,3,0,0.00,3,4.00,150.00,7.80,0.00,'Kg\r'),(32,'2024-01-21 11:44:30.231201','2024-01-21 11:44:30.231225',0,'玩具类-Lego / Building Blocks / Jelly Cat / 玩偶【单件≤$50】',0,1,1,0,0.00,1,4.00,150.00,7.80,0.00,'Kg\r'),(33,'2024-01-21 11:44:30.244782','2024-01-21 11:44:30.244811',0,'玩具类-Lego / Building Blocks / Jelly Cat / 玩偶【单件≤$100】',0,1,1,0,0.00,1,4.00,150.00,7.80,0.00,'Kg\r'),(34,'2024-01-21 11:44:30.326216','2024-01-21 11:44:30.326222',0,'玩具类-其他玩具【单件≤$20】',1,2,2,1,0.00,10,4.00,150.00,7.80,0.00,'Kg\r'),(35,'2024-01-21 11:44:30.334944','2024-01-21 11:44:30.334951',0,'玩具类-其他玩具【单件≤$30】',1,2,2,1,0.00,10,4.00,150.00,7.80,0.00,'Kg\r'),(36,'2024-01-21 11:44:30.342934','2024-01-21 11:44:30.342940',0,'文具类-SMIGGLE 书包',0,1,1,0,0.00,1,4.00,150.00,7.80,0.00,'Kg\r'),(37,'2024-01-21 11:44:30.350922','2024-01-21 11:44:30.350928',0,'文具类-笔 / 笔盒 / 笔袋 / 饭盒袋 / 记事本 / 文件夹 等',1,4,4,4,0.00,10,4.00,150.00,7.80,0.00,'Kg\r'),(38,'2024-01-21 11:44:30.359187','2024-01-21 11:44:30.359193',0,'衣服类-T 恤 / 裤 / 内衣裤 / 卫衣 / 外套 / 围巾 / 帽子 床单/ 被套 / 枕套 / 窗帘 【价值≤$50】',0,1,1,0,0.00,1,4.00,150.00,7.80,0.00,'Kg\r'),(39,'2024-01-21 11:44:30.367155','2024-01-21 11:44:30.367162',0,'特殊货物-被子/羊毛毯',0,1,1,0,20.00,1,4.00,150.00,7.80,0.00,'Kg\r'),(40,'2024-01-21 11:44:30.375707','2024-01-21 11:44:30.375713',0,'特殊货物-150AUD 内的鞋子，如 UGG 等，Nike / Adidas / AJ   $30 关税',0,1,1,0,30.00,1,4.00,150.00,12.00,0.00,'Kg\r'),(41,'2024-01-21 11:44:30.383602','2024-01-21 11:44:30.383609',0,'特殊货物-仅限葡萄酒，单瓶 ≤ 750ml ≤ 22 度 【单瓶≤ $20】',0,1,1,0,0.00,1,4.00,150.00,9.00,0.00,'Kg\r'),(42,'2024-01-21 11:44:30.391966','2024-01-21 11:44:30.391973',0,'葡萄酒【单瓶<$200】',0,2,2,0,30.00,2,10.00,500.00,9.00,0.00,'Kg');
/*!40000 ALTER TABLE `dbProductLogisticsAuExpress` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-01-31  9:21:28