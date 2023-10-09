

CREATE TABLE "Attribute" (
	name TEXT NOT NULL, 
	dims TEXT, 
	shape TEXT, 
	value TEXT, 
	default_value TEXT, 
	doc TEXT NOT NULL, 
	required BOOLEAN, 
	dtype TEXT, 
	PRIMARY KEY (name, dims, shape, value, default_value, doc, required, dtype)
);

CREATE TABLE "CompoundDtype" (
	name TEXT NOT NULL, 
	doc TEXT NOT NULL, 
	dtype TEXT NOT NULL, 
	PRIMARY KEY (name, doc, dtype)
);

CREATE TABLE "Dataset" (
	neurodata_type_def TEXT, 
	neurodata_type_inc TEXT, 
	name TEXT, 
	default_name TEXT, 
	dims TEXT, 
	shape TEXT, 
	value TEXT, 
	default_value TEXT, 
	doc TEXT NOT NULL, 
	quantity TEXT, 
	linkable BOOLEAN, 
	attributes TEXT, 
	dtype TEXT, 
	PRIMARY KEY (neurodata_type_def, neurodata_type_inc, name, default_name, dims, shape, value, default_value, doc, quantity, linkable, attributes, dtype)
);

CREATE TABLE "Datasets" (
	datasets TEXT, 
	PRIMARY KEY (datasets)
);

CREATE TABLE "Group" (
	neurodata_type_def TEXT, 
	neurodata_type_inc TEXT, 
	name TEXT, 
	default_name TEXT, 
	doc TEXT NOT NULL, 
	quantity TEXT, 
	linkable BOOLEAN, 
	attributes TEXT, 
	datasets TEXT, 
	groups TEXT, 
	links TEXT, 
	PRIMARY KEY (neurodata_type_def, neurodata_type_inc, name, default_name, doc, quantity, linkable, attributes, datasets, groups, links)
);

CREATE TABLE "Groups" (
	groups TEXT, 
	PRIMARY KEY (groups)
);

CREATE TABLE "Link" (
	name TEXT, 
	doc TEXT NOT NULL, 
	target_type TEXT NOT NULL, 
	quantity TEXT, 
	PRIMARY KEY (name, doc, target_type, quantity)
);

CREATE TABLE "Namespace" (
	doc TEXT NOT NULL, 
	name TEXT NOT NULL, 
	full_name TEXT, 
	version TEXT NOT NULL, 
	date DATETIME, 
	author TEXT NOT NULL, 
	contact TEXT NOT NULL, 
	schema_ TEXT, 
	PRIMARY KEY (doc, name, full_name, version, date, author, contact, schema_)
);

CREATE TABLE "Namespaces" (
	namespaces TEXT, 
	PRIMARY KEY (namespaces)
);

CREATE TABLE "ReferenceDtype" (
	target_type TEXT NOT NULL, 
	reftype VARCHAR(9), 
	PRIMARY KEY (target_type, reftype)
);

CREATE TABLE "Schema" (
	source TEXT, 
	namespace TEXT, 
	title TEXT, 
	neurodata_types TEXT, 
	doc TEXT, 
	PRIMARY KEY (source, namespace, title, neurodata_types, doc)
);
