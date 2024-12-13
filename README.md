# Refactor ใหม่เกือบหมด

## ตั้งค่า database 0
0. เหมือนเดิมเลย ถ้าทำแล้วข้าม  
0.1 สร้าง connection ตาม lab 11 และ เข้าไปแก้ตัวแปรตามเครื่องตัวเองที่ settings ใน lotto ตามส่วนของโค้ดด้านล่าง
```bash
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'lotto',
        'USER': 'root',
        'PASSWORD': 'new_password',
        'PORT':'3306',
        'HOST': '127.0.0.1',
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}
```
1. ปรับเปลี่ยน database collation ให้เป็น utf8mb4_unicode_ci เพื่อให้สามารถรองรับภาษาไทยได้
2. import ไฟล์ lotto_all.csv ผ่าน Table data import wizard ***และเปลี่ยนประเภทข้อมูล lotto ให้เป็น text

## ตั้งค่า database ใหม่
1. ถ้าไม่อยากสร้าง db ใหม่ ให้ลบ table ทั้งหมดออกยกเว้นตัว lotto 
แล้ว makemigrations / migrate ใหม่ จะ reset ทั้งหมดได้เลย  ***อย่าสร้าง superuser ใหม่นะ และ signup user ใหม่
2. ใช้ โค้ดข้างล่าง insert ข้อมูล ถ้า insert อันแรกติด ให้สร้าง stored procedure จากข้อ 3 ก่อน แล้วใช้ postRound() เรียกโดยตรงจาก db สร้างได้เลย format เป็น ปี-เดือน-วัน

```bash
INSERT INTO `lotto`.`app_round`
(`date`)
VALUES
("2024–10-01”);

INSERT INTO `lotto`.`app_room`
(`id`, `is_open`, `shares`)
VALUES
(1, True, 0),
(2, True, 0),
(3, True, 0),
(4, True, 0),
(5, True, 0);
```
3. สร้าง stored procedure ที่ใช้ทั้งหมด ไม่ต้องลบของเก่า ใน code มี drop ให้ ***run ผ่าน sql ตรง ๆ ไม่ต้องกดสร้าง stored procedure
```bash
USE `lotto`;
DROP procedure IF EXISTS `getPendingLottos`;
DROP procedure IF EXISTS `getSuccessfulLottos`;
DROP procedure IF EXISTS `getSharesSumLotto`;
DROP procedure IF EXISTS `getSharesSumRoom`;
DROP procedure IF EXISTS `getShareOwn`;
DROP procedure IF EXISTS `getBoughtLottos`;
DROP procedure IF EXISTS `postBoughtLottos`;
DROP procedure IF EXISTS `getLottosRoom`;
DROP procedure IF EXISTS `getTotalPrize`;
DROP procedure IF EXISTS `getUsersRoom`;

DELIMITER $$
USE `lotto`$$

CREATE PROCEDURE `getPendingLottos`(
	IN round_id int,
    IN room_in int
)
BEGIN
	select lotto, sum(share) as count 
    from app_transaction
    where (status = "รอการยืนยันการชำระเงิน" or status = "การชำระเงินไม่สำเร็จ")
    and round_bought_id = round_id
    group by lotto, room_id
    having room_id = room_in
    order by count desc;
END$$

CREATE PROCEDURE `getSuccessfulLottos`(
	IN round_id int,
    IN room_in int
)
BEGIN
    select lotto, sum(share) as count 
    from app_transaction
    where status = "คำสั่งซื้อสำเร็จ"
    and round_bought_id = round_id
    group by lotto, room_id
    having room_id = room_in
    order by count desc;
END$$

CREATE PROCEDURE `getSharesSumLotto`(
	IN lotto_num VARCHAR(3)
)
BEGIN
	select sum(share) as count
    from app_transaction
    where lotto = lotto_num 
    and round_bought_id = (select id from app_round order by id DESC limit 1);
END$$

CREATE PROCEDURE `getSharesSumRoom`(
	IN round_id int,
    IN room_in int
)
BEGIN
	select sum(share) as count
    from app_transaction
    where room_id = room_in 
    and round_bought_id = round_id;
END$$

CREATE PROCEDURE `getShareOwn` (
	IN uid INT,
    IN round_id INT,
    IN room_in INT
)
BEGIN
	select sum(share)
    from app_transaction
    where user_id = uid and round_bought_id = round_id and room_id = room_in;
END$$

CREATE PROCEDURE `getBoughtLottos` (
	IN uid INT,
    IN round_id INT,
    IN room_in INT
)
BEGIN
	select lotto
    from app_transaction
    where user_id = uid and round_bought_id = round_id and room_id = room_in;
END$$

CREATE PROCEDURE `postBoughtLottos` (
	IN lotto_num VARCHAR(6),
    IN room_in INT
)
BEGIN
	INSERT INTO `lotto`.`app_lottobought` (`lotto`, `prize`, `room_id`, `round_bought_id`)
    VALUES (lotto_num, 0, room_in, (select id from app_round order by id DESC limit 1));
END$$

CREATE PROCEDURE `postLottoPrize` (
	IN lotto_num varchar(6),
    IN prize_in INT
)
BEGIN
	UPDATE `lotto`.`app_lottobought` 
    SET `prize` = prize_in WHERE (`lotto` = lotto_num);
END$$

CREATE PROCEDURE `getLottosRoom` (
	IN round_id INT,
    IN room_in INT
)
BEGIN
	select distinct lotto 
    from app_transaction
    where round_bought_id = round_id and room_id = room_in;
END$$

CREATE PROCEDURE `getTotalPrize` (
	IN round_id INT,
    IN room_in INT
)
BEGIN
	select sum(prize)
    from app_lottobought
    where round_bought_id = round_id and room_id = room_in;
END$$

CREATE PROCEDURE `getUsersRoom` (
	IN round_id INT,
    IN room_in INT
)
BEGIN
	select distinct user_id
    from app_transaction
    where round_bought_id = round_id and room_id = room_in;
END$$

DELIMITER ;


```
4. อันนี้ใช้อยู่มั้ย ถ้าใช้ก็เอาไปสร้างด้วย แต่ไม่ได้เปลี่ยน ก็ถ้ามีอยู่เหมือนเดิมก็ทิ้งไว้เหมือนเดิม
```bash
CREATE PROCEDURE `getLottoStats` (
	IN lotto_number VARCHAR(6)
)
BEGIN
	SELECT 
		CASE
            WHEN type = 'prize_1st' THEN 'รางวัลที่ 1'
            WHEN type = 'nearby_1st' THEN 'รางวัลข้างเคียงรางวัลที่ 1'
			WHEN type = 'prize_2nd' THEN 'รางวัลที่ 2'
			WHEN type = 'prize_3rd' THEN 'รางวัลที่ 3'
			WHEN type = 'prize_4th' THEN 'รางวัลที่ 4'
			WHEN type = 'prize_5th' THEN 'รางวัลที่ 5'
            WHEN type = 'prize_2digits' THEN 'รางวัลเลขท้าย 2 ตัว'
            WHEN type = 'prize_pre_3digit' THEN 'รางวัลเลขหน้า 3 ตัว'
			WHEN type = 'prize_sub_3digits' THEN 'รางวัลเลขท้าย 3 ตัว'
			ELSE type
        END AS type, 
		COUNT(*) AS count
	FROM 
		lotto
	WHERE 
		lotto = lotto_number
	GROUP BY 
		type;
END
```

## คำอธิบาย stored procedure 
คร่าว ๆ มีบางอันที่ไม่ได้ใช้แล้ว แต่เก็บไว้ก่อนเผื่อดึงมาใช้อีก
1. สำหรับทั่วไป เรียกดูในหน้า buy lotto
```bash
CREATE PROCEDURE `getPendingLottos`(
	IN round_id int,
    IN room_in int
)
BEGIN
	select lotto, sum(share) as count 
    from app_transaction
    where (status = "รอการยืนยันการชำระเงิน" or status = "การชำระเงินไม่สำเร็จ")
    and round_bought_id = round_id
    group by lotto, room_id
    having room_id = room_in
    order by count desc;
END
```
2. สำหรับทั่วไป เรียกดูในหน้า buy lotto
```bash
CREATE PROCEDURE `getSuccessfulLottos`(
	IN round_id int,
    IN room_in int
)
BEGIN
    select lotto, sum(share) as count 
    from app_transaction
    where status = "คำสั่งซื้อสำเร็จ"
    and round_bought_id = round_id
    group by lotto, room_id
    having room_id = room_in
    order by count desc;
END
```
3. ดูว่า lotto นี้รอบนี้ซื้อไปเท่าไหร่แล้ว
```bash
CREATE PROCEDURE `getSharesSumLotto`(
	IN lotto_num VARCHAR(3)
)
BEGIN
	select sum(share) as count
    from app_transaction
    where lotto = lotto_num 
    and round_bought_id = (select id from app_round order by id DESC limit 1);
END
```
4. ดูว่าห้องนี้ รอบนี้ซื้อไปเท่าไหร่แล้ว
```bash
CREATE PROCEDURE `getSharesSumRoom`(
	IN round_id int,
    IN room_in int
)
BEGIN
	select sum(share) as count
    from app_transaction
    where room_id = room_in 
    and round_bought_id = round_id;
END
```
5. ดูว่ารอบนี้ ห้องนี้ ซื้อไปเท่าไหร่แล้ว
```bash
CREATE PROCEDURE `getShareOwn` (
	IN uid INT,
    IN round_id INT,
    IN room_in INT
)
BEGIN
	select sum(share)
    from app_transaction
    where user_id = uid and round_bought_id = round_id and room_id = room_in;
END
```
6. ดูว่าห้องนี้ ซื้อเลขไรไปบ้าง
```bash
CREATE PROCEDURE `getBoughtLottos` (
	IN uid INT,
    IN round_id INT,
    IN room_in INT
)
BEGIN
	select lotto
    from app_transaction
    where user_id = uid and round_bought_id = round_id and room_id = room_in;
END
```
7. ใส่ Lotto Bought 
```bash
CREATE PROCEDURE `postBoughtLottos` (
	IN lotto_num VARCHAR(6),
    IN room_in INT
)
BEGIN
	INSERT INTO `lotto`.`app_lottobought` (`lotto`, `prize`, `room_id`, `round_bought_id`)
    VALUES (lotto_num, 0, room_in, (select id from app_round order by id DESC limit 1));
END
```
8. ดูว่าห้องนี้มี lotto อะไรบ้าง
```bash
CREATE PROCEDURE `getLottosRoom` (
	IN round_id INT,
    IN room_in INT
)
BEGIN
	select distinct lotto 
    from app_transaction
    where round_bought_id = round_id and room_id = room_in;
END
```
9. เงินรางวัลในห้องนั้น
```bash
CREATE PROCEDURE `getTotalPrize` (
	IN round_id INT,
    IN room_in INT
)
BEGIN
	select sum(prize)
    from app_lottobought
    where round_bought_id = round_id and room_id = room_in;
END
```
10. user_id ทั้งหมดในห้องนั้น
```bash
CREATE PROCEDURE `getUsersRoom` (
	IN round_id INT,
    IN room_in INT
)
BEGIN
	select distinct user_id
    from app_transaction
    where round_bought_id = round_id and room_id = room_in;
END
```
11. ซื้อมาแล้ว ใส่รางวัล
```bash
CREATE PROCEDURE `postLottoPrize` (
	IN lotto_num varchar(6),
    IN prize_in INT
)
BEGIN
	UPDATE `lotto`.`app_lottobought` 
    SET `prize` = prize_in WHERE (`lotto` = lotto_num);
END
```
12. get stat ตามประเภท
```bash
CREATE PROCEDURE `getLottoStatsTable`(
	IN lotto_mode TEXT
)
BEGIN
    SELECT lotto, COUNT(*) AS count
    FROM lotto_all
    WHERE type = lotto_mode
    GROUP BY lotto
    ORDER BY count desc;
END
```


## information: lotto_data
มี raw ไฟล์ผลรางวัลอยู่ และไฟล์ restructure.py ที่ใช้สร้าง lotto_all.csv โดยมีโครงสร้างคือ date, lotto, type เพื่อให้สามารถนับได้สะดวก
