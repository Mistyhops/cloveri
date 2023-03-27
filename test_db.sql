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
