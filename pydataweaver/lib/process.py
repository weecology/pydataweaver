from __future__ import print_function

from collections import OrderedDict

SELECT_FIELDS = """SELECT {trimmed_fields} """
FROM_TABLE = """FROM {payment_table_name} """


def rename_fields(dictionary_object, original, alias):
    """Rename field alias """
    dt = dictionary_object
    if not dt:
        return None
    for items in dt.keys():
        if original in dt[items]:
            dt[items] = [x if not x == original else alias for x in dt[items]]
    return dt


def make_sql(dataset):
    # 1. For spatial joins,
    # assume that the latitude and longitude fields are in the main file.
    # use ST_PointFromText ST_PointFromText('POINT(-71.064 42.28)', 4326);
    # 2. Refactoring to after raster joins are finalized

    main_table_path = dataset.main_file["path"]
    processed_tables = {main_table_path: {"name": "T1"}}
    as_processed_table = processed_tables

    if "lat_long" in dataset.main_file and dataset.main_file["lat_long"]:
        x_y = dataset.main_file["lat_long"]
        as_processed_table[main_table_path]["latitude"] = x_y[0]
        as_processed_table[main_table_path]["longitude"] = x_y[1]

    query_statement = ""
    all_fields = []
    gis_all_fields = []
    unique_f = set()
    rast_values = []

    if "fields" in dataset.main_file:
        if dataset.main_file["fields"]:
            all_fields += [
                as_processed_table[main_table_path]["name"] + "." + item_f.lower()
                for item_f in dataset.main_file["fields"]
            ]
            unique_f |= set(dataset.main_file["fields"])

    # process all tables that are to be joined
    # and the fields that are required

    for count, table2join in enumerate(dataset.join):
        # local fields
        make_local_temp = False
        local_raster_fields = set()
        local_vector_fields = set()
        local_tabular_fields = set()
        to_join = OrderedDict(table2join["join_ocn"])

        res_set = set(to_join.keys()) - {"common_field", table2join["table"]}
        join_with = res_set.pop()

        rast_alias = ""
        geom_alias = ""
        where_clause = ""
        left_join = ""
        left_join_on = ""
        original_tabular_fields = []

        vector_table, raster_table, tabular_table = None, None, None
        table_type = get_table_type(table2join, raster_table, tabular_table, vector_table)
        raster_table, tabular_table, vector_table = table_type

        # Create table alias using count
        as_tables = "as_" + str(count)  # Table references Table as T
        as_tables_dot = as_tables + "."

        # keep table information for lat and long name
        as_processed_table[table2join["table"]] = {"name": as_tables}

        # Get a list of fields from the table or create needed fields.
        # Rasters can have empty fields, `rast` should be added if not in field.
        # Vectors can have empty fields, geom should be included by default.

        local_fields_used = []
        if "fields_to_use" in table2join:
            local_fields_used = [field.lower() for field in table2join["fields_to_use"]]
            if vector_table:
                # Remove 'geom'
                # Rename the geom with respect to the DB and the table names
                # SELECT id, geom as geom_table_name FROM table_name
                local_vector_fields |= set(local_fields_used)
                local_vector_fields.discard("geom")
                # Add fields that do not use alias to all_fields
                all_fields += [
                    as_tables_dot + field_i
                    for field_i in list(local_vector_fields)
                    if field_i not in unique_f
                ]

                # keep sorted for uniformity
                all_fields = sorted(all_fields)

                geom_alias = "geom_{As_DB}_{Ta}".format(As_DB=table2join["database_name"],
                                                        Ta=table2join["table_name"])
                local_vector_fields.add(
                    "geom AS {geom_alias}".format(geom_alias=geom_alias))
                local_fields_used = sorted(list(local_vector_fields))
                # remove_fields += geom_alias
                # Update the join on dictionary with the new alias
                to_join = rename_fields(to_join, "geom", geom_alias)

            if raster_table:
                # Remove and rename 'rast' with respect to the DB and the table
                # names
                local_raster_fields |= set(local_fields_used)
                local_raster_fields.discard("rast")
                # Add fields that do not use alias to all_fields
                all_fields += [
                    as_tables_dot + field_i for field_i in list(local_raster_fields)
                ]
                # keep sorted for uniformity
                all_fields = sorted(all_fields)

                rast_alias = "rast_{As_DB}_{Ta}".format(As_DB=table2join["database_name"],
                                                        Ta=table2join["table_name"])
                local_raster_fields.add("rast AS {rast_alias}"
                                        "".format(rast_alias=rast_alias))
                local_fields_used = sorted(list(local_raster_fields))
                # all_fields += [as_tables_dot + rast_alias]

                # Update the join on dictionary with the new alias
                to_join = rename_fields(to_join, "rast", rast_alias)

            if tabular_table:
                local_tabular_fields |= set(local_fields_used)

                # Remove and rename the longitude and the latitude
                if "lat_long" not in table2join:
                    all_fields += [
                        as_tables_dot + field_i
                        for field_i in list(local_tabular_fields)
                        if field_i not in unique_f or "remove_duplicate" in table2join
                    ]
                    all_fields = sorted(all_fields)
                else:
                    make_local_temp = True
                    # ["latitude", "longitude"] [y,x]
                    y = table2join["lat_long"][0]
                    x = table2join["lat_long"][1]
                    as_DB = table2join["database_name"]
                    as_Ta = table2join["table_name"]

                    # Original will select longitute and latitude
                    # Using their original names
                    original_tabular_fields = sorted(list(local_tabular_fields))

                    local_tabular_fields.discard(y)
                    local_tabular_fields.discard(x)
                    lat_alias = "lat_{as_DB}_{as_Ta}".format(as_DB=as_DB, as_Ta=as_Ta)
                    long_alias = "long_{as_DB}_{as_Ta}".format(as_DB=as_DB, as_Ta=as_Ta)
                    all_fields += [
                        as_tables_dot + field_i
                        for field_i in list(local_tabular_fields)
                        if field_i not in unique_f or "remove_duplicate" in table2join
                    ]
                    all_fields = sorted(all_fields)
                    local_tabular_fields.add("{y} AS {lat_alias}".format(
                        y=y, lat_alias=lat_alias))
                    local_tabular_fields.add("{x} AS {long_alias}".format(
                        x=x, long_alias=long_alias))
                    as_processed_table[table2join["table"]]["latitude"] = lat_alias
                    as_processed_table[table2join["table"]]["longitude"] = long_alias

                    # add alias
                    gis_all_fields += [
                        as_tables_dot + lat_alias,
                        as_tables_dot + long_alias,
                    ]
                    gis_all_fields = sorted(gis_all_fields)
                    # Update the join on dictionary with the new alias
                    to_join = rename_fields(to_join, "rast", lat_alias)
                    to_join = rename_fields(to_join, "rast", long_alias)

                    # include where statement, use original fields
                    # Rows with no latitude and longitutde values are not considered
                    # If we consider them, we increase the time complexity
                    where_clause = ("\n\tWHERE {latitude} Not LIKE '%NULL%' "
                                    "\n\tAND {latitude} IS NOT NULL "
                                    "\n\tAND {longitude} Not LIKE '%NULL%' "
                                    "\n\tAND {longitude} IS NOT NULL "
                                    "".format(latitude=y, longitude=x))
                local_fields_used = sorted(list(local_tabular_fields))

        # Create `LEFT JOIN` and ON statements raster and vector data
        if raster_table or vector_table:
            left_join += ("\nLEFT OUTER JOIN "
                          "\n\t(SELECT {fields_used} "
                          "\n\tFROM {table_j}) AS {table_j_as} "
                          "".format(
                              fields_used=", ".join(str(e) for e in local_fields_used),
                              table_j=table2join["table"],
                              table_j_as=as_tables,
                          ))
            # on statement
            # look for the names of longitude and latitude for the particular join.
            # Get the table to be joined to,
            # set U =  to_join keys known-keys = {"common_field", values for this table}
            # To join with  = U | {"common_field", table2join["table"]}
            res_set = set(to_join.keys()) - {"common_field", table2join["table"]}
            join_with = res_set.pop()

            if join_with in as_processed_table:
                # ["latitude", "longitude"] [y,x]
                y = as_processed_table[join_with]["latitude"]
                x = as_processed_table[join_with]["longitude"]
            else:
                msg = ("The order of the tables in the script needs re-arranging.\n"
                       "Table {a} should be processed first before "
                       "{b}".format(a=join_with, b=table2join["table"]))
                print(msg)
                exit()
            T = as_processed_table[join_with]["name"]
            if raster_table:
                left_join_on += ("\nON ST_Intersects(" + as_tables_dot + rast_alias +
                                 ", ST_PointFromText(FORMAT('POINT(%s %s)',"
                                 " cast({T}.{x} as varchar), "
                                 "cast({T}.{y} as varchar)),"
                                 " 4326))\n".format(T=T, x=x, y=y))

                # now Add the ST_Value for this point , rast value

                rast_value = ("ST_Value(" + as_tables_dot + rast_alias +
                              ", 1, ST_PointFromText(FORMAT('POINT(%s %s)', "
                              "cast({T}.{longitude} as varchar), "
                              "cast({T}.{latitude} as varchar)), "
                              "4326)) as feature_{ras}".format(
                                  T=T, longitude=x, latitude=y, ras=rast_alias))
                # Add the value to final select statement
                rast_values.append(rast_value)
                gis_all_fields += [rast_value]
            if vector_table:
                geovalue = ("ST_PointFromText(FORMAT('POINT(%s %s)', "
                            "cast({T}.{longitude} as varchar), "
                            "cast({T}.{latitude} as varchar)),"
                            " 4326) ".format(T=T, longitude=x, latitude=y))

                left_join += (" \nON ST_Within({geovalue}, "
                              "{tablei_as}.{geomalias}) ".format(
                                  T=T,
                                  geovalue=geovalue,
                                  tablei_as=as_tables,
                                  geomalias=geom_alias,
                              ))
                # change the name of field to match the table
                new_geom_value = geovalue + " as feature_{geo}".format(geo=geom_alias)
                gis_all_fields += [new_geom_value]

        if tabular_table and make_local_temp:
            # Create `LEFT JOIN` statements from non pivot tables
            _all_fields = ", ".join(str(e) for e in local_fields_used)
            _local_fields = ", ".join(str(e) for e in original_tabular_fields)
            left_join += ("\nLEFT OUTER JOIN  "
                          "\n\t(SELECT  {all_flds} "
                          "\nFROM (SELECT  {original_fields} "
                          "\nFROM {table_j} "
                          "\n{where_stm}) temp) "
                          "{table_j_as} ".format(
                              all_flds=_all_fields,
                              original_fields=_local_fields,
                              table_j=table2join["table"],
                              where_stm=str(where_clause),
                              table_j_as=as_tables,
                          ))
        elif tabular_table:
            if "remove_duplicate" in table2join:
                new_modi_table = create_uniquevalue_query(
                    table_name=table2join["table"],
                    all_fields=local_fields_used,
                    duplicate=table2join["remove_duplicate"])
                left_join += ("\nLEFT OUTER JOIN \n" + new_modi_table + "\n) AS " +
                              as_tables)
            else:
                left_join += ("\nLEFT OUTER JOIN "
                              "\n\t(SELECT {fields_used} "
                              "\n\tFROM {table_i} {where_clause}) AS {tablei_as} "
                              "".format(
                                  fields_used=", ".join(
                                      str(e) for e in local_fields_used),
                                  table_i=table2join["table"],
                                  where_clause=str(where_clause),
                                  tablei_as=as_tables,
                              ))

        # Create "ON" statement
        on_condition = "\nON "
        if tabular_table:
            # Process "ON" statements, having either similar
            # or different field/column names
            on_common_stmt = []
            if to_join["common_field"]:
                for item_field in to_join["common_field"]:
                    on_common_stmt += [
                        "{table_i}.{common_name}={table_j}.{common_name}".format(
                            table_i=as_processed_table[dataset.main_file["path"]]["name"],
                            table_j=as_processed_table[table2join["table"]]["name"],
                            common_name=str(item_field),
                        )
                    ]

            # process non common fields
            temp_dict = to_join
            temp_dict.pop("common_field", True)

            # Two lists whose index each match the field to use
            # when creating the conditional statement
            # Use index of one to obtain the value of the other
            tab_field_index = list(temp_dict.keys())
            on_diff_stmt = []
            for num, items in enumerate(temp_dict[tab_field_index[0]]):
                new_on = "{tab_i}.{field_i}={tab_j}.{field_j}".format(
                    tab_i=as_processed_table[str(tab_field_index[0])]["name"],
                    # field_i=items,
                    field_i=temp_dict[tab_field_index[0]][num].lower(),
                    tab_j=as_processed_table[str(tab_field_index[1])]["name"],
                    field_j=temp_dict[tab_field_index[1]][num].lower(),
                )
                on_diff_stmt.append(new_on)

            all_on_stmts = on_diff_stmt + on_common_stmt

            on_condition += " AND ".join(str(etr) for etr in all_on_stmts)
            left_join_on += on_condition

        query_statement += left_join + left_join_on
        # Process the main file and create the query string
        # for all the required fields
        if "fields" in dataset.main_file:
            where_clause = ""
            if "lat_long" in dataset.main_file and dataset.main_file["lat_long"]:
                # ["latitude", "longitude"] [y,x]
                y = dataset.main_file["lat_long"][0]
                x = dataset.main_file["lat_long"][1]
                where_clause = ("WHERE CAST({latitude} AS TEXT) NOT LIKE '%NULL%' "
                                "AND {latitude} IS NOT NULL "
                                "AND CAST({longitude} AS TEXT) NOT LIKE '%NULL%' "
                                "AND {longitude} IS NOT NULL "
                                "".format(latitude=y, longitude=x))
                temp_fields = dataset.main_file["fields"]
                temp_fields_string = ", ".join(str(e) for e in temp_fields)
                pivot_query = (
                    "\nSELECT {all_flds} {local_spatials} "
                    "\nINTO {res} \n\n"
                    "\nFROM (SELECT  {temp_fields_s}  "
                    "\nFROM {main_table}  "
                    "\n{where_stm} ) "
                    "{table_m} ".format(
                        all_flds=", ".join(
                            str(e) + " AS " + e.replace(".", "_") for e in all_fields),
                        local_spatials="," + ", ".join(str(e) for e in gis_all_fields)
                        if gis_all_fields else "",
                        temp_fields_s=temp_fields_string,
                        main_table=dataset.main_file["path"],
                        res="{result_dbi}.{result_tablei}",
                        table_m=as_processed_table[main_table_path]["name"],
                        where_stm=where_clause,
                    ))
            else:
                pivot_query = (
                    "\nSELECT {all_fls} {local_spatials} "
                    "\ninto {res} \n\n"
                    "\nFROM {main_table} {where_stm} AS {table_m} "
                    "".format(
                        all_fls=", ".join(
                            str(e) + " AS " + e.replace(".", "_") for e in all_fields),
                        local_spatials="," + ", ".join(str(e) for e in gis_all_fields)
                        if gis_all_fields else "",
                        main_table=dataset.main_file["path"],
                        res="{result_dbi}.{result_tablei}",
                        where_stm=where_clause,
                        table_m=as_processed_table[main_table_path]["name"],
                    ))
    return pivot_query + query_statement


def create_sqlcolumn_string(fields, pre_field_name=None):
    """Convert fields to sql table_name.field_name form"""
    if not pre_field_name:
        table_name = ""
    else:
        table_name = pre_field_name + "."
    return ", ".join([table_name + field for field in fields])


def create_inner_join(field_name, index, table_name):
    """Use the field name and index to create and inner join statement"""
    if not (field_name and index and table_name):
        return None
    default_string = ("\nINNER JOIN\n "
                      "(\nSELECT {g}.{dt} FROM {table_name} as {g} "
                      "GROUP BY  {g}.{dt} HAVING (COUNT({g}.{dt}) = 1)\n) "
                      "AS {g} \nON a.{dt} = {g}.{dt} ")
    g = excel_column_name(index)
    return default_string.format(g=g, dt=field_name, table_name=table_name)


def create_uniquevalue_query(table_name, all_fields, duplicate):
    """Create a query to remove all duplicates values present for the given columns

    output is referenced as temp_'tablename'
    """
    inner_subquery = process_duplicate_fields(all_fields=all_fields,
                                              remove_duplicates_fields=duplicate,
                                              from_table=table_name)

    table_alias = table_name.replace(".", "")
    field_str = create_sqlcolumn_string(fields=all_fields,
                                        pre_field_name="temp_" + table_alias)
    select_stmt = SELECT_FIELDS.format(trimmed_fields=field_str)
    query = " (" + select_stmt + "FROM ( \n" + inner_subquery + " ) temp_" + table_alias
    return query


def excel_column_name(n):
    """Convert a number to Excel-style column name.

    eg., 704 = aab 27 = aa 56 = bd
    """
    if n < 1:
        return None
    name = ""
    while n > 0:
        n, r = divmod(n - 1, 26)  # Return the tuple (x//y, x%y).
        name = chr(r + ord("A")) + name
    return name.lower()


def get_table_type(table_info, raster_table, tabular_table, vector_table):
    """Determine the type of table from.

    Data type can be raster, vector otherwise default to tabular"""
    if table_info["table_type"] == "vector":
        vector_table = True
    elif table_info["table_type"] == "raster":
        raster_table = True
    elif table_info["table_type"] == "tabular":
        tabular_table = True
    elif not table_info["table_type"]:
        tabular_table = True
    return raster_table, tabular_table, vector_table


def get_trimmed_columns(all_fields, exclude_column):
    """Return column keeping order"""
    include_column = set(all_fields) - set(exclude_column)
    return [column for column in all_fields if column in include_column]


def process_duplicate_fields(all_fields, remove_duplicates_fields, from_table=None):
    """Create subquery to filter out duplicated values based on a column

    For considered fields in a table T,
    select column values that have no duplicates and inner join results
    with T.
    Values "a" and "b" are reserved for the initial sub queries "AS tables"
    """
    sample_sql = "as a "

    outer_fields_a = create_sqlcolumn_string(fields=all_fields, pre_field_name="a")
    outer_base_sql = SELECT_FIELDS.format(trimmed_fields=outer_fields_a)
    outer_base_sql += FROM_TABLE + sample_sql
    outer_base_sql = outer_base_sql.format(payment_table_name=from_table)
    inner_fields = create_sqlcolumn_string(fields=remove_duplicates_fields[:1],
                                           pre_field_name="b")
    inner_select = SELECT_FIELDS.format(trimmed_fields=inner_fields)

    # Add inner joins for other fields that need duplicates removed
    for index, value in enumerate(remove_duplicates_fields, 2):
        # "a" and "b" are used for the base sub query hence we start from 3 = "c"
        outer_base_sql += create_inner_join(field_name=value,
                                            index=index,
                                            table_name=from_table)
    return outer_base_sql


def create_trim_statment():
    """Select fields from table statement"""
    return SELECT_FIELDS + FROM_TABLE
