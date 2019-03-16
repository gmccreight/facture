insert into products (
  name,
  id
)
values
-- facture_json: {"target_name": "products", "position": "start"}

-- facture_group_testgroup1
(
  'default name', -- name
  110             -- id
),

-- facture_group_testgroup2
(
  'better name', -- name
  210            -- id
)

-- facture_json: {"target_name": "products", "position": "end"}
;

insert into places (
  name
)
values
('San Francisco')
;
