DROP DATABASE CMall;
CREATE DATABASE CMall;

USE CMall;
-- 客户表
CREATE TABLE Customer (
	id CHAR (8) PRIMARY KEY,
	name CHAR (10),
	tel CHAR (11),
	pwd CHAR (128)
);

USE CMall;
-- 管理员表
CREATE TABLE Admin (
	id CHAR (8) PRIMARY KEY,
	pwd CHAR (128),
	privilege SMALLINT
);

USE CMall;
-- 收货地址表
CREATE TABLE ShipAddr (
	id INT  PRIMARY KEY AUTO_INCREMENT,
	cust_id CHAR (8),
	addr VARCHAR (100),
	FOREIGN KEY (cust_id) REFERENCES Customer (id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE INDEX cust_id_index ON ShipAddr (cust_id(8));

USE CMall;
-- 商品品牌表
CREATE TABLE Brand (
	id INT  PRIMARY KEY AUTO_INCREMENT,
	name CHAR (20)
);

USE CMall;
-- 商品类别表
CREATE TABLE Category (
	id INT  PRIMARY KEY AUTO_INCREMENT,
	name CHAR (20)
);

USE CMall;
-- 商品表
CREATE TABLE Goods (
	id INT  PRIMARY KEY AUTO_INCREMENT,
	name CHAR (30)
);


CREATE TABLE GoodsDetail (
	id INT  PRIMARY KEY,
	cate_id INT ,
	brand_id INT ,
	purchase_price DECIMAL (8, 2),
	sale_price DECIMAL (8, 2),
	stock INT ,
	sales_num INT ,
	description VARCHAR (500),
	FOREIGN KEY (id) REFERENCES Goods (id) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY (cate_id) REFERENCES Category (id) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY (brand_id) REFERENCES Brand (id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE INDEX cate_id_index ON GoodsDetail (cate_id);
CREATE INDEX brand_id_index ON GoodsDetail (brand_id);


USE CMall;
-- 商品图片表
CREATE TABLE Image (
	id INT  PRIMARY KEY AUTO_INCREMENT,
	url VARCHAR (100),
	goods_id INT ,
	FOREIGN KEY (goods_id) REFERENCES GoodsDetail (id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE INDEX goods_id_index ON Image (goods_id);

USE CMall;
-- 订单表
CREATE TABLE CustOrder (
	id INT  PRIMARY KEY AUTO_INCREMENT,
	create_time DATETIME,
	pay_time DATETIME,
	goods_id INT ,
	cust_id CHAR (8),
	admin_id CHAR (8),
	shipaddr_id INT ,
	-- status: 0 已创建 1 已付款 2 已发货 3 已签收 4 已评价
	status SMALLINT ,
	quantity SMALLINT ,
	cost DECIMAL (8, 2),
	FOREIGN KEY (goods_id) REFERENCES Goods (id) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY (cust_id) REFERENCES Customer (id) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY (admin_id) REFERENCES Admin (id) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY (shipaddr_id) REFERENCES ShipAddr (id) ON DELETE CASCADE ON UPDATE CASCADE,
	CHECK (status >= 0 AND status <= 4)
);

CREATE INDEX cust_id_index ON CustOrder (cust_id(8));
CREATE INDEX admin_id_index ON CustOrder (admin_id(8));
USE CMall;
CREATE INDEX status ON CustOrder (status);

USE CMall;
-- 客户评价表
CREATE TABLE Appraisal (
	id INT  PRIMARY KEY AUTO_INCREMENT,
	score SMALLINT,
	order_id INT ,
	create_time DATETIME,
	content VARCHAR (100),
	FOREIGN KEY (order_id) REFERENCES CustOrder (id) ON DELETE CASCADE ON UPDATE CASCADE,
	CHECK (score >= 1 AND score <= 5)
);

CREATE INDEX order_id_index ON Appraisal (order_id);

USE CMall;
-- 管理员盘点表
CREATE TABLE Inventory (
	id INT  PRIMARY KEY AUTO_INCREMENT,
	create_time DATETIME,
	goods_id INT ,
	admin_id CHAR (8),
	stock INT ,
	FOREIGN KEY (goods_id) REFERENCES Goods (id) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY (admin_id) REFERENCES Admin (id) ON DELETE CASCADE ON UPDATE CASCADE
);

USE CMall;
DELETE FROM Image WHERE 1;
DELETE FROM Goods WHERE 1;
DELETE FROM GoodsDetail WHERE 1;
INSERT INTO Admin VALUES ("admin", "pbkdf2:sha256:150000$ReEVRMsw$9b4d878541ab4090097fe16889dbd8c52375c05c6d48e02d71fee944c607a8ac", 100);
INSERT INTO Category (name) VALUES ("智能手机"), ("游戏本"), ("商务本");
INSERT INTO Brand (name) VALUES ("华为"), ("小米"), ("vivo"), ("oppo"), ("苹果");
