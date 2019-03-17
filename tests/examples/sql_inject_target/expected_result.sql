insert into actors (
  id,
  first_name,
  last_name
)
values
-- facture_json: {"target_name": "actors", "position": "start"}

-- facture_group_shawshank_redemption
(
  'Morgan',  -- first_name
  'Freeman', -- last_name
  110        -- id
),

-- facture_group_shawshank_redemption
(
  'Tim',     -- first_name
  'Robbins', -- last_name
  111        -- id
)

-- facture_json: {"target_name": "actors", "position": "end"}
;

insert into films (
  id,
  name,
  year
)
values
-- facture_json: {"target_name": "films", "position": "start"}

-- facture_group_shawshank_redemption
(
  'Shawshank Redemption', -- name
  '1994',                 -- year
  200                     -- id
)

-- facture_json: {"target_name": "films", "position": "end"}
;

insert into roles (
  id,
  actor_id,
  film_id
)
values
-- facture_json: {"target_name": "roles", "position": "start"}

-- facture_group_shawshank_redemption
(
  110,  -- actor_id
  200,  -- film_id
  1100  -- id
),

-- facture_group_shawshank_redemption
(
  111,  -- actor_id
  200,  -- film_id
  1101  -- id
)

-- facture_json: {"target_name": "roles", "position": "end"}
;
