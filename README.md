# ตรวจหวย

ใส่เลขหวยพร้อมค้นหาสถิติการปรากฎตัวจากทั้งหมด 411 งวด*  
*รางวัลเลขหน้า 3 ตัวและรางวัลที่ 2 จะมีจำนวนงวดทั้งหมดน้อยกว่า เนื่องจากเกิดขึ้นที่หลัง

## ตั้งค่า database
0. สร้าง connection ตาม lab 11 และ เข้าไปแก้ตัวแปรตามเครื่องตัวเองที่ settings ใน lotto ตามส่วนของโค้ดด้านล่าง
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
3. สร้าง stored procedure ด้วยโค้ดข้างล่าง

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
```bash
CREATE PROCEDURE `getPendingLottos` (
    IN room int(1)
)
BEGIN
	select lotto, sum(share) as count 
    from app_transaction
    where (status = "รอการยืนยันการชำระเงิน" or status = "การชำระเงินไม่สำเร็จ") and is_active =True
    group by lotto, room
    having room = room
    order by count desc;
END
```
```bash
CREATE PROCEDURE `getSuccessfulLottos` (
    IN room int(1)
)
BEGIN
    select lotto, sum(share) as count 
    from app_transaction
    where status = "คำสั่งซื้อสำเร็จ" and is_active =True
    group by lotto, room
    having room = room
    order by count desc;
END
```
```bash
CREATE PROCEDURE `transRoomSum` (
	IN room_in int(1)
)
BEGIN
	select sum(share) as count
    from app_transaction
    where room = room_in and is_active = True;
END
```
```bash
CREATE PROCEDURE `transLottoSum` (
	IN lotto_num int(3)
)
BEGIN
	select sum(share) as count
    from app_transaction
    where lotto = lotto_num and is_active = True;
END
```

## information: lotto_data
มี raw ไฟล์ผลรางวัลอยู่ และไฟล์ restructure.py ที่ใช้สร้าง lotto_all.csv โดยมีโครงสร้างคือ date, lotto, type เพื่อให้สามารถนับได้สะดวก
