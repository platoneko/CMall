CREATE DATABASE CMall;

USE CMall;

INSERT INTO Goods (goodsName, cateID, brandID, purchasePrice, salePrice, stock, salesNum, description) VALUES ("小米10 Pro", 3, 2, 3000.00, 4999.00, 999, 0, "向往的生活同款 / 骁龙865处理器 / 1亿像素8K电影相机，50倍数字变焦，10倍混合光学变焦 / 双模5G / 新一代LPDDR5内存 / 50W极速闪充+30W无线闪充+10W无线反充 / 对称式立体声 / 90Hz刷新率+180Hz采样率 / UFS 3.0高速存储 / 全面适配WiFi 6 / 超强VC液冷散热 / 4500mAh大电量 / 多功能NFC");
INSERT INTO Image (imageUrl, goodsID) VALUES ("/images/goods/2.jpg", 1);
INSERT INTO Brand (brandName) VALUES ("华为"), ("小米"), ("vivo"), ("oppo"), ("苹果");

-- 客户表
CREATE TABLE Customer (
	custID CHAR (8) PRIMARY KEY,
	custName CHAR (10),
	tel CHAR (11),
	pwd CHAR (128)
);

-- 管理员表
CREATE TABLE Admin (
	adminID CHAR (8) PRIMARY KEY,
	pwd CHAR (128),
	privilege SMALLINT
);

-- 收货地址表
CREATE TABLE ShipAddr (
	addrID INT  PRIMARY KEY AUTO_INCREMENT,
	custID CHAR (8),
	addr VARCHAR (100),
	FOREIGN KEY (custID) REFERENCES Customer (custID) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE INDEX custIDindex ON ShipAddr (custID(8));

-- 商品品牌表
CREATE TABLE Brand (
	brandID INT  PRIMARY KEY AUTO_INCREMENT,
	brandName CHAR (20)
);

-- 商品类别表
CREATE TABLE Category (
	cateID INT  PRIMARY KEY AUTO_INCREMENT,
	cateName CHAR (20)
);

-- 商品表
CREATE TABLE Goods (
	goodsID INT  PRIMARY KEY AUTO_INCREMENT,
	goodsName CHAR (30),
	cateID INT ,
	brandID INT ,
	purchasePrice DECIMAL (8, 2),
	salePrice DECIMAL (8, 2),
	stock INT ,
	salesNum INT ,
	description VARCHAR (500),
	FOREIGN KEY (cateID) REFERENCES Category (cateID) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY (brandID) REFERENCES Brand (brandID) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE INDEX cateIDindex ON Goods (cateID);
CREATE INDEX brandIDindex ON Goods (brandID);

-- 商品图片表
CREATE TABLE Image (
	imageID INT  PRIMARY KEY AUTO_INCREMENT,
	imageUrl VARCHAR (100),
	goodsID INT ,
	FOREIGN KEY (goodsID) REFERENCES Goods (goodsID) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE INDEX goodsIDindex ON Image (goodsID);

-- 订单表
CREATE TABLE CustOrder (
	orderID INT  PRIMARY KEY AUTO_INCREMENT,
	createTime DATETIME,
	payTime DATETIME,
	goodsID INT ,
	custID CHAR (8),
	adminID CHAR (8),
	shipAddrID INT ,
	-- orderStatus: 0 已创建 1 已付款 2 已发货 3 已签收 4 已评价
	orderStatus SMALLINT,
	quantity SMALLINT ,
	payAmount DECIMAL (8, 2),
	FOREIGN KEY (goodsID) REFERENCES Goods (goodsID) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY (custID) REFERENCES Customer (custID) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY (adminID) REFERENCES Admin (adminID) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY (shipAddrID) REFERENCES ShipAddr (addrID) ON DELETE CASCADE ON UPDATE CASCADE,
	CHECK (orderStatus >= 0 AND orderStatus <= 4)
);

CREATE INDEX custIDindex ON CustOrder (custID(8));
CREATE INDEX adminIDindex ON CustOrder (adminID(8));

-- 客户评价表
CREATE TABLE Appraisal (
	apprID INT  PRIMARY KEY AUTO_INCREMENT,
	score SMALLINT,
	orderID INT ,
	createDate DATETIME,
	description VARCHAR (100),
	FOREIGN KEY (orderID) REFERENCES CustOrder (orderID) ON DELETE CASCADE ON UPDATE CASCADE,
	CHECK (score >= 1 AND score <= 5)
);

CREATE INDEX orderIDindex ON Appraisal (orderID);

-- 管理员盘点表
CREATE TABLE Inventory (
	inventID INT  PRIMARY KEY AUTO_INCREMENT,
	createDate DATETIME,
	goodsID INT ,
	adminID CHAR (8),
	stock INT ,
	FOREIGN KEY (goodsID) REFERENCES Goods (goodsID) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY (adminID) REFERENCES Admin (adminID) ON DELETE CASCADE ON UPDATE CASCADE
);
