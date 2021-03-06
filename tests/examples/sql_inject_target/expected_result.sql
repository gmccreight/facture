insert into actors (
  id,
  first_name,
  last_name
)
-- facture_json: {"target_name": "actors", "position": "start"}
select
  -- facture_group_shawshank_redemption
  110,       -- id
  $build_id, -- job_run_id
  'Morgan',  -- first_name
  'Freeman'  -- last_name

union all

select
  -- facture_group_shawshank_redemption
  111,       -- id
  $build_id, -- job_run_id
  'Tim',     -- first_name
  'Robbins'  -- last_name
-- facture_json: {"target_name": "actors", "position": "end"}
;

insert into films (
  id,
  name,
  year
)
-- facture_json: {"target_name": "films", "position": "start"}
values
(
  -- facture_group_shawshank_redemption
  200,                    -- id
  'Shawshank Redemption', -- name
  '1994'                  -- year
)
-- facture_json: {"target_name": "films", "position": "end"}
;

insert into roles (
  id,
  actor_id,
  film_id
)
-- facture_json: {"target_name": "roles", "position": "start"}
values
(
  -- facture_group_shawshank_redemption
  1100, -- id
  110,  -- actor_id
  200   -- film_id
),

(
  -- facture_group_shawshank_redemption
  1101, -- id
  111,  -- actor_id
  200   -- film_id
)
-- facture_json: {"target_name": "roles", "position": "end"}
;
