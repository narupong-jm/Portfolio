-- Open our database called 'buffet_restaurant.db'
.open buffet_restaurant.db

/*Create table
  - customers
  - option_menu
  - menu
  - member
  - detail_option */
CREATE TABLE IF NOT EXISTS customers (
  id int,
  name text,
  ages int,
  city text,
  mem_level int,
  opt_name text
); 
-- Insert data into table
INSERT INTO customers VALUES 
  (1, "Johnny", 25, "London", 3, "standard" ),
  (2, "Cassy", 19, "New York", 3, "standard"),
  (3, "Tim", 42, "Los angeles", 1, "platinum"),
  (4, "Romanov", 30, "Los angeles", 2, "gold"),
  (5, "Charles", 60, "New York", 1, "premium");

CREATE TABLE IF NOT EXISTS option_menu (
  opt_id int,
  opt_name text,
  opt_price int
);

INSERT INTO option_menu VALUES 
  (1, "standard", 599),
  (2, "premium", 799),
  (3, "gold", 999),
  (4, "platinum", 1999);

CREATE TABLE IF NOT EXISTS menu (
  menu_id text,
  menu_name text
);

INSERT INTO menu VALUES 
  (1, "black pork collar"),
  (2, "bacon"),
  (3, "australian beef"),
  (4, "oyster"),
  (5, "wagyu beef"),
  (6, "river prawn"),
  (7, "new zealand mussels"),
  (8, "river prawn with cheese"),
  (9, "premium wagyu beef hoba yaki"),
  (10, "sashimi set");

CREATE TABLE IF NOT EXISTS member (
  mem_level int,
  mem_name text,
  discount text
);

INSERT INTO member VALUES
  (1, "family", "15%"),
  (2, "cloesd friend", "10%"),
  (3, "friend", "5%");

CREATE TABLE IF NOT EXISTS detail_option (
  opt_name text,
  menu_id int
);

INSERT INTO detail_option VALUES 
  ("standard", 1),
  ("standard", 2),
  ("premium", 1),
  ("premium", 2),
  ("premium", 3),
  ("premium", 4),
  ("gold", 1),
  ("gold", 2),
  ("gold", 3),
  ("gold", 4),
  ("gold", 5),
  ("gold", 6),
  ("gold", 7),
  ("platinum", 1),
  ("platinum", 2),
  ("platinum", 3),
  ("platinum", 4),
  ("platinum", 5),
  ("platinum", 6),
  ("platinum", 7),
  ("platinum", 8),
  ("platinum", 9),
  ("platinum", 10);

-- List table in db
.table

-- change how we display data in terminal/ shell
.mode column

-- query-1
-- Focused on customer in New York or London and show discount
-- sub query
SELECT sub1.name, sub1.city, sub2.mem_level, sub2.discount
FROM (SELECT * FROM customers
      WHERE city IN ("London", "New York")) AS sub1
JOIN (SELECT * FROM member) AS sub2
ON sub1.mem_level = sub2.mem_level;

-- query-2
-- focused on customer that choose standard option, show price and menu
-- sub query
SELECT sub1.name, sub1.opt_name, sub2.opt_price, sub4.menu_name
FROM (SELECT * FROM customers
      WHERE opt_name = "standard") AS sub1
JOIN (SELECT * FROM option_menu) AS sub2
ON sub1.opt_name = sub2.opt_name
JOIN (SELECT * FROM detail_option
      WHERE opt_name = "standard") AS sub3
ON sub2.opt_name = sub3.opt_name
JOIN (SELECT * FROM menu) AS sub4
ON sub3.menu_id = sub4.menu_id;
-- common table expression
WITH sub1 AS (
  SELECT * FROM customers
  WHERE opt_name = "standard"
), sub2 AS (SELECT * FROM option_menu
), sub3 AS (
  SELECT * FROM detail_option
  WHERE opt_name = "standard"
), sub4 AS (SELECT * FROM menu
)

SELECT 
  sub1.name, 
  sub1.opt_name, 
  sub2.opt_price, 
  sub4.menu_name
FROM sub1
JOIN sub2
ON sub1.opt_name = sub2.opt_name
JOIN sub3
ON sub2.opt_name = sub3.opt_name
JOIN sub4
ON sub3.menu_id = sub4.menu_id;

-- query-3
-- foused on count menu in each option and show price
SELECT 
  a1.opt_name AS optionName, 
  a2.opt_price AS price, 
  COUNT(a1.opt_name)
FROM detail_option AS a1
JOIN option_menu AS a2
ON a1.opt_name = a2.opt_name
GROUP BY a1.opt_name
ORDER BY a2.opt_price DESC
