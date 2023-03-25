-- DROP TABLE IF EXISTS auth_group CASCADE;
-- DROP TABLE IF EXISTS auth_group_permissions CASCADE;
-- DROP TABLE IF EXISTS auth_permission CASCADE;
-- DROP TABLE IF EXISTS auth_user CASCADE;
-- DROP TABLE IF EXISTS auth_user_groups CASCADE;
-- DROP TABLE IF EXISTS auth_user_user_permissions CASCADE;
-- DROP TABLE IF EXISTS django_admin_log CASCADE;
-- DROP TABLE IF EXISTS django_content_type CASCADE;
-- DROP TABLE IF EXISTS django_migrations CASCADE;
-- DROP TABLE IF EXISTS django_session CASCADE;
-- DROP TABLE IF EXISTS tree_structure_node CASCADE;


CREATE TABLE tree_structure_node(
	id				bigserial	NOT NULL,
	path			text		NOT NULL,
	project_id		uuid		NOT NULL,
	item_type		text		NOT NULL,
	item			text		NOT NULL,
	inner_order		int8		NOT NULL,
	attributes		jsonb,

	PRIMARY KEY(path, id)
);


CREATE UNIQUE INDEX node_id_project_id_item_type_item
	ON tree_structure_node(id, project_id, item_type, item);


CREATE INDEX node_project_id_item_type_item
	ON tree_structure_node(project_id, item_type, item);


-- SELECT * FROM tree_structure_node
-- 	ORDER BY path;
