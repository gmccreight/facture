-- Here is some commentary before that should remain preserved.

-- facture_json: {"target_name": "products", "position": "start"}
insert into products
(
  id,
  classified_code
)
values
 (
   110,            -- id
   'default name'  -- name
 ),
 (
   210,           -- id
   'better name'  -- name
 ),
-- facture_json: {"target_name": "products", "position": "end"}

-- Here is some commentary after that should remain preserved.