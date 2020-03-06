insert into products (
  id
)
-- facture_json: {"target_name": "products", "position": "start"}
values
(
  -- facture_group_basic_workflow_grouping
  1100  -- id
),

(
  -- facture_group_basic_workflow_grouping
  1101  -- id
)
-- facture_json: {"target_name": "products", "position": "end"}
;

insert into workflows (
  id,
  name,
  query,
  created_by
)
-- facture_json: {"target_name": "workflows", "position": "start"}
values
(
  -- facture_group_basic_workflow_grouping
  200,                                                              -- id
  'Tracking Dwight',                                                -- name
  'select * from orders where product_id = 1100 and user_id = 111', -- query
  110                                                               -- created_by
),

(
  -- facture_group_basic_workflow_grouping
  201,                              -- id
  'Fetch all orders',               -- name
  'select * from orders where 1=1', -- query
  111                               -- created_by
)
-- facture_json: {"target_name": "workflows", "position": "end"}
;

insert into users (
  id,
  first_name,
  last_name
)
-- facture_json: {"target_name": "users", "position": "start"}
values
(
  -- facture_group_basic_workflow_grouping
  110,       -- id
  'Michael', -- first_name
  'Scott'    -- last_name
),

(
  -- facture_group_basic_workflow_grouping
  111,       -- id
  'Dwight',  -- first_name
  'Schrute'  -- last_name
)
-- facture_json: {"target_name": "users", "position": "end"}
;
