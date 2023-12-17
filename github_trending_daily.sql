SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for github_trending_daily
-- ----------------------------
DROP TABLE IF EXISTS `github_trending_daily`;
CREATE TABLE `github_trending_daily` (
  `id` int(10) NOT NULL AUTO_INCREMENT COMMENT 'id',
  `name` varchar(255) DEFAULT NULL COMMENT '作者 / 项目名',
  `url` varchar(255) DEFAULT NULL COMMENT '项目地址',
  `about` varchar(255) DEFAULT NULL COMMENT '项目介绍',
  `language` varchar(255) DEFAULT NULL COMMENT '项目编程语言',
  `star` int(10) DEFAULT NULL COMMENT '项目star数',
  `fork` int(10) DEFAULT NULL COMMENT '项目fork数',
  `date` varchar(20) DEFAULT NULL COMMENT '热榜日期',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

SET FOREIGN_KEY_CHECKS = 1;
