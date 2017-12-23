# -*- coding: utf-8 -*-

from __future__ import unicode_literals

CURRENT_DBD_VERSION = '3.1'

SQL_DBD_PRE_INIT = """\
pragma foreign_keys = on;

--begin transaction;

--
-- Каталог схем для таблиц
--
create table dbd$schemas (
    id integer primary key autoincrement not null,
    name varchar not null, -- имя схемы
    fulltext_engine varchar default(null),
    version varchar default(null),
    description varchar default(null)
);
"""

SQL_DBD_DOMAINS_TABLE_INIT = """
--
-- Домены
--
create table dbd$domains (
    id  integer primary key autoincrement default(null),
    name varchar unique default(null),  -- имя домена
    description varchar default(null),  -- описание
    data_type_id integer not null,      -- идентификатор типа (dbd$data_types)
    length integer default(null),       -- длина
    char_length integer default(null),  -- длина в символах
    precision integer default(null),    -- точность
    scale integer default(null),        -- количество знаков после запятой
    width integer default(null),        -- ширина визуализации в символах
    align char default(null),           -- признак выравнивания
    show_null boolean default(null),    -- нужно показывать нулевое значение?
    show_lead_nulls boolean default(null),      -- следует ли показывать лидирующие нули?
    thousands_separator boolean default(null),  -- нужен ли разделитель тысяч?
    summable boolean default(null),             -- признак того, что поле является суммируемым
    case_sensitive boolean default(null)       -- признак необходимости регистронезависимого поиска для поля
--    ,uuid varchar unique not null COLLATE NOCASE, -- уникальный идентификатор домена
--    ,FOREIGN KEY(data_type_id) REFERENCES dbd$data_types(id)
);

create index "idx.FZX832TFV" on dbd$domains(data_type_id);
--create index "idx.4AF9IY0XR" on dbd$domains(uuid);
"""

SQL_DBD_TABLES_TABLE_INIT = """
--
-- Каталог таблиц
--
create table dbd$tables (
    id integer primary key autoincrement default(null),
    schema_id integer default(null),      -- идетификатор схемы (dbd$schemas)
    name varchar unique,                  -- имя таблицы
    description varchar default(null),    -- описание
    can_add boolean default(null),        -- разрешено ли добавление в таблицу
    can_edit boolean default(null),       -- разрешено ли редактирование  таблице?
    can_delete boolean default(null),     -- разрешено ли удаление в таблице
    temporal_mode varchar default(null),  -- временная таблица или нет? Если временная, то какого типа?
    means varchar default(null)          -- шаблон описания записи таблицы
--    ,uuid varchar unique not null COLLATE NOCASE  -- уникальный идентификатор таблицы
);

create index "idx.GCOFIBEBJ" on dbd$tables(name);
--create index "idx.2J02T9LQ7" on dbd$tables(uuid);
"""

SQL_DBD_TABLES_INIT = """
--
-- Поля таблиц
--
create table dbd$fields (
    id integer primary key autoincrement default(null),
    table_id integer not null,             -- идентификатор таблицы (dbd$tables)
--    position integer not null,             -- номер поля в таблице (для упорядочивания полей)
    name varchar not null,                 -- латинское имя поля (будет использовано в схеме Oracle)
    russian_short_name varchar not null,   -- русское имя поля для отображения пользователю в интерактивных режимах
    description varchar default(null),     -- описание
    domain_id integer not null,            -- идентификатор типа поля (dbd$domains)
    can_input boolean default(null),       -- разрешено ли пользователю вводить значение в поле?
    can_edit boolean default(null),        -- разрешено ли пользователю изменять значение в поле?
    show_in_grid boolean default(null),    -- следует ли отображать значение поля в браузере таблицы?
    show_in_details boolean default(null), -- следует ли отображать значение поля в полной информации о записи таблицы?
    is_mean boolean default(null),         -- является ли поле элементом описания записи таблицы?
    autocalculated boolean default(null),  -- признак того, что значение в поле вычисляется программным кодом
    required boolean default(null)        -- признак того, что поле дорлжно быть заполнено
--    ,uuid varchar unique not null COLLATE NOCASE, -- уникальный идентификатор поля
--    ,FOREIGN KEY(table_id) REFERENCES dbd$tables(id)
);

create index "idx.7UAKR6FT7" on dbd$fields(table_id);
--create index "idx.7HJ6KZXJF" on dbd$fields(position);
create index "idx.74RSETF9N" on dbd$fields(name);
create index "idx.6S0E8MWZV" on dbd$fields(domain_id);
--create index "idx.88KWRBHA7" on dbd$fields(uuid);

--
-- Спец. настройки описателя
--
create table dbd$settings (
    key varchar primary key not null,
    value varchar,
    valueb BLOB
);

--
-- Ограничения
--
create table dbd$constraints (
    id integer primary key autoincrement default (null),
    table_id integer not null,                           -- идентификатор таблицы (dbd$tables)
    name varchar default(null),                          -- имя ограничения
    constraint_type char default(null),                  -- вид ограничения
    reference integer default(null),        -- идентификатор таблицы (dbd$tables), на которую ссылается внешний ключ
    unique_key_id integer default(null),    -- (опционально) идентификатор ограничения (dbd$constraints) таблицы, на которую ссылается внешний ключ (*1*)
    has_value_edit boolean default(null),   -- признак наличия поля ввода ключа
    cascading_delete boolean default(null), -- признак каскадного удаления для внешнего ключа
    expression varchar default(null)       -- выражение для контрольного ограничения
--    ,uuid varchar unique not null COLLATE NOCASE, -- уникальный идентификатор ограничения
--    ,FOREIGN KEY(table_id) REFERENCES dbd$tables(id)
);

create index "idx.6F902GEQ3" on dbd$constraints(table_id);
create index "idx.6SRYJ35AJ" on dbd$constraints(name);
create index "idx.62HLW9WGB" on dbd$constraints(constraint_type);
create index "idx.5PQ7Q3E6J" on dbd$constraints(reference);
create index "idx.92GH38TZ4" on dbd$constraints(unique_key_id);
--create index "idx.6IOUMJINZ" on dbd$constraints(uuid);

--
-- Детали ограничений
--
create table dbd$constraint_details (
    id integer primary key autoincrement default(null),
    constraint_id integer not null,          -- идентификатор ограничения (dbd$constraints)
--    position integer not null,               -- номер элемента ограничения
    field_id integer default(null),  -- идентификатор поля (dbd$fields) в таблице, для которой определено ограничение
    FOREIGN KEY(field_id) REFERENCES dbd$fields(id),
    FOREIGN KEY(constraint_id) REFERENCES dbd$constraints(id)
);

create index "idx.5CYTJWVWR" on dbd$constraint_details(constraint_id);
--create index "idx.507FDQDMZ" on dbd$constraint_details(position);
create index "idx.4NG17JVD7" on dbd$constraint_details(field_id);

--
-- Индексы
--
create table dbd$indices (
    id integer primary key autoincrement default(null),
    table_id integer not null,                          -- идентификатор таблицы (dbd$tables)
    name varchar default(null),                         -- имя индекса
    local boolean default(0),                           -- показывает тип индекса: локальный или глобальный
    kind char default(null)                            -- вид индекса (простой/уникальный/полнотекстовый)
--    ,uuid varchar unique not null COLLATE NOCASE,         -- уникальный идентификатор индекса
--    ,FOREIGN KEY(table_id) REFERENCES dbd$tables(id)
);

create index "idx.12XXTJUYZ" on dbd$indices(table_id);
create index "idx.6G0KCWN0R" on dbd$indices(name);
--create index "idx.FQH338PQ7" on dbd$indices(uuid);

--
-- Детали индексов
--
create table dbd$index_details (
    id integer primary key autoincrement default(null),
    index_id integer not null,                          -- идентификатор индекса (dbd$indices)
--    position integer not null,                          -- порядковый номер элемента индекса
    field_id integer default(null),                     -- идентификатор поля (dbd$fields), участвующего в индексе
    expression varchar default(null),                   -- выражение для индекса
    descend boolean default(null),                       -- направление сортировки
    FOREIGN KEY(field_id) REFERENCES dbd$fields(id),
    FOREIGN KEY(index_id) REFERENCES dbd$indices(id)
);

create index "idx.H1KFOWTCB" on dbd$index_details(index_id);
create index "idx.BQA4HXWNF" on dbd$index_details(field_id);

--
-- Типы данных
--
create table dbd$data_types (
    id integer primary key autoincrement, -- идентификатор типа
    type_id varchar unique not null       -- имя типа
);

insert into dbd$data_types(type_id) values ('STRING');
insert into dbd$data_types(type_id) values ('SMALLINT');
insert into dbd$data_types(type_id) values ('INTEGER');
insert into dbd$data_types(type_id) values ('WORD');
insert into dbd$data_types(type_id) values ('BOOLEAN');
insert into dbd$data_types(type_id) values ('FLOAT');
insert into dbd$data_types(type_id) values ('CURRENCY');
insert into dbd$data_types(type_id) values ('BCD');
insert into dbd$data_types(type_id) values ('FMTBCD');
insert into dbd$data_types(type_id) values ('DATE');
insert into dbd$data_types(type_id) values ('TIME');
insert into dbd$data_types(type_id) values ('DATETIME');
insert into dbd$data_types(type_id) values ('TIMESTAMP');
insert into dbd$data_types(type_id) values ('BYTES');
insert into dbd$data_types(type_id) values ('VARBYTES');
insert into dbd$data_types(type_id) values ('BLOB');
insert into dbd$data_types(type_id) values ('MEMO');
insert into dbd$data_types(type_id) values ('GRAPHIC');
insert into dbd$data_types(type_id) values ('FMTMEMO');
insert into dbd$data_types(type_id) values ('FIXEDCHAR');
insert into dbd$data_types(type_id) values ('WIDESTRING');
insert into dbd$data_types(type_id) values ('LARGEINT');
insert into dbd$data_types(type_id) values ('COMP');
insert into dbd$data_types(type_id) values ('ARRAY');
insert into dbd$data_types(type_id) values ('FIXEDWIDECHAR');
insert into dbd$data_types(type_id) values ('WIDEMEMO');
insert into dbd$data_types(type_id) values ('CODE');
insert into dbd$data_types(type_id) values ('RECORDID');
insert into dbd$data_types(type_id) values ('SET');
insert into dbd$data_types(type_id) values ('PERIOD');
insert into dbd$data_types(type_id) values ('BYTE');
insert into dbd$settings(key, value) values ('dbd.version', '%(dbd_version)s');
""" % {'dbd_version': CURRENT_DBD_VERSION}

SQL_DBD_VIEWS_INIT = """
create view dbd$view_fields as
select
--  dbd$schemas.name "schema",
--  dbd$fields.position "position",
  dbd$fields.id "id",
  dbd$fields.name "name",
  dbd$tables.name "table_id",
  dbd$fields.russian_short_name "russian_short_name",
  dbd$fields.description "description",
--  dbd$data_types.type_id "type_id",
  dbd$domains.name "domain_id",
--  dbd$domains.char_length,
--  dbd$domains.width "width",
--  dbd$domains.align "align",
--  dbd$domains.precision "precision",
--  dbd$domains.scale "scale",
--  dbd$domains.show_null "show_null",
--  dbd$domains.show_lead_nulls "show_lead_nulls",
--  dbd$domains.thousands_separator "thousands_separator",
--  dbd$domains.summable,
--  dbd$domains.case_sensitive "case_sensitive",
  CASE 
    WHEN dbd$fields.can_input=1 THEN 'True'
  END can_input,
  CASE 
    WHEN dbd$fields.can_edit=1 THEN 'True'
  END can_edit,
  CASE 
    WHEN dbd$fields.show_in_grid=1 THEN 'True'
  END show_in_grid,
  CASE 
    WHEN dbd$fields.show_in_details=1 THEN 'True'
  END show_in_details,
  CASE 
    WHEN dbd$fields.is_mean=1 THEN 'True'
  END is_mean,
  CASE 
    WHEN dbd$fields.autocalculated=1 THEN 'True'
  END autocalculated,
  CASE 
    WHEN dbd$fields.required=1 THEN 'True'
  END required
--  dbd$fields.can_input "can_input",
--  dbd$fields.can_edit "can_edit",
--  dbd$fields.show_in_grid "show_in_grid",
--  dbd$fields.show_in_details "show_in_details",
--  dbd$fields.is_mean "is_mean",
--  dbd$fields.autocalculated "autocalculated",
--  dbd$fields.required "required"
from dbd$fields
  inner join dbd$tables on dbd$fields.table_id = dbd$tables.id
  inner join dbd$domains on dbd$fields.domain_id = dbd$domains.id
  inner join dbd$data_types on dbd$domains.data_type_id = dbd$data_types.id
  Left Join dbd$schemas On dbd$tables.schema_id = dbd$schemas.id
order by
  dbd$tables.name;
--  dbd$fields.position;

create view dbd$view_domains as
select
  dbd$domains.id,
  dbd$domains.name,
  dbd$domains.description,
  dbd$data_types.type_id AS data_type_id,
  dbd$domains.length,
  dbd$domains.char_length,
  dbd$domains.width,
  dbd$domains.align,
  dbd$domains.precision,
  dbd$domains.scale,
  CASE 
    WHEN dbd$domains.show_null=1 THEN 'True'
  END show_null,
  CASE 
    WHEN dbd$domains.show_lead_nulls=1 THEN 'True'
  END show_lead_nulls,
  CASE 
    WHEN dbd$domains.thousands_separator=1 THEN 'True'
  END thousands_separator,
  CASE 
    WHEN dbd$domains.summable=1 THEN 'True'
  END summable,
  CASE 
    WHEN dbd$domains.case_sensitive=1 THEN 'True'
  END case_sensitive
from dbd$domains
  inner join dbd$data_types on dbd$domains.data_type_id = dbd$data_types.id
order by dbd$domains.id;

create view dbd$view_tables as
select
  dbd$tables.id "id",
  dbd$tables.schema_id "schema_id",
  dbd$tables.name "name",
  dbd$tables.description "description",
  CASE 
    WHEN dbd$tables.can_add=1 THEN 'True'
  END can_add,
  CASE 
    WHEN dbd$tables.can_edit=1 THEN 'True'
  END can_edit,
  CASE 
    WHEN dbd$tables.can_delete=1 THEN 'True'
  END can_delete,
  dbd$tables.temporal_mode "temporal_mode",
  dbd$tables.means "means"
from
  dbd$tables
order by
  dbd$tables.id;

create view dbd$view_constraints as
select
  dbd$fields.name "field_name",
  dbd$tables.name "table_id",
  dbd$constraints.id "id",
  dbd$constraints.name "name",
  dbd$constraints.constraint_type "constraint_type",
  "references".name "reference",
  dbd$constraints.unique_key_id "unique_key_id",
  CASE 
    WHEN dbd$constraints.has_value_edit=1 THEN 'True'
  END has_value_edit,
  CASE 
    WHEN dbd$constraints.cascading_delete=1 THEN 'True'
    WHEN dbd$constraints.cascading_delete=0 THEN 'False'
    WHEN dbd$constraints.cascading_delete is null THEN null
  END cascading_delete,
  dbd$constraints.expression "expression"
--  dbd$constraint_details.position "position",
from
  dbd$constraint_details
  inner join dbd$constraints on dbd$constraint_details.constraint_id = dbd$constraints.id
  inner join dbd$tables on dbd$constraints.table_id = dbd$tables.id
  left join dbd$tables "references" on dbd$constraints.reference = "references".id
  left join dbd$fields on dbd$constraint_details.field_id = dbd$fields.id
  Left Join dbd$schemas On dbd$tables.schema_id = dbd$schemas.id
order by
  constraint_id;
   -- position;

create view dbd$view_indices as
select
  dbd$fields.name "field_name",
  dbd$indices.id "id",
  dbd$indices.name "name",
  dbd$tables.name "table_id",
  CASE 
    WHEN dbd$indices.local=1 THEN 'True'
  END local,
  CASE 
    WHEN dbd$index_details.descend=1 THEN 'True'
  END descend,
  dbd$indices.kind "kind",
  dbd$index_details.expression "expression"
--  dbd$index_details.position,
--  dbd$fields.name as field_name,
--  dbd$index_details.expression,
--  dbd$index_details.descend
from
  dbd$index_details
  inner join dbd$indices on dbd$index_details.index_id = dbd$indices.id
  inner join dbd$tables on dbd$indices.table_id = dbd$tables.id
  left join dbd$fields on dbd$index_details.field_id = dbd$fields.id
  Left Join dbd$schemas On dbd$tables.schema_id = dbd$schemas.id
order by
  dbd$tables.name, dbd$indices.name;
   --dbd$index_details.position;
"""

SQL_DBD_TEMPORARY_TABLES_INIT = """
CREATE TEMPORARY TABLE temp (
    id INTEGER NOT NULL,
    name varchar NOT NULL
);
"""

COMMIT = """
commit;
"""

SQL_DBD_Init = SQL_DBD_PRE_INIT + SQL_DBD_DOMAINS_TABLE_INIT + \
    SQL_DBD_TABLES_TABLE_INIT + SQL_DBD_TABLES_INIT + \
    SQL_DBD_VIEWS_INIT + SQL_DBD_TEMPORARY_TABLES_INIT# + COMMIT
