import pytest

from pydataweaver.lib.process import create_inner_join
from pydataweaver.lib.process import create_sqlcolumn_string
from pydataweaver.lib.process import create_uniquevalue_query
from pydataweaver.lib.process import excel_column_name
from pydataweaver.lib.process import get_trimmed_columns
from pydataweaver.lib.process import process_duplicate_fields

process_duplicate_parameters = {
    # Fields used for create sample sql and expected query
    "1": [["zip"],
          ("SELECT a.user_id, a.account, a.zip, a.dt "
           "FROM payment as a INNER JOIN (SELECT b.zip FROM payment as b "
           "GROUP BY  b.zip HAVING (COUNT(b.zip) = 1)) AS b ON a.zip = b.zip")],
    "2": [["zip", "dt"],
          ("SELECT a.user_id, a.account, a.zip, a.dt FROM "
           "payment as a INNER JOIN (SELECT b.zip FROM payment as b "
           "GROUP BY  b.zip HAVING (COUNT(b.zip) = 1)) AS b ON a.zip = b.zip "
           "INNER JOIN (SELECT c.dt FROM payment as c GROUP BY  c.dt "
           "HAVING (COUNT(c.dt) = 1)) AS c ON a.dt = c.dt")],
    "3": [["zip", "dt", "account"],
          ("SELECT a.user_id, a.account, a.zip, a.dt "
           "FROM payment as a INNER JOIN (SELECT b.zip "
           "FROM payment as b GROUP BY  b.zip HAVING (COUNT(b.zip) = 1)) AS b "
           "ON a.zip = b.zip INNER JOIN (SELECT c.dt FROM payment as c "
           "GROUP BY  c.dt HAVING (COUNT(c.dt) = 1)) AS c ON a.dt = c.dt "
           "INNER JOIN (SELECT d.account FROM payment as d GROUP BY  d.account "
           "HAVING (COUNT(d.account) = 1)) AS d ON a.account = d.account")]
}
create_samplesql = [key for key, value in process_duplicate_parameters.items()]

inner_join_test = {
    # Inner join query values with the number of fields used as the key
    "1": ("INNER JOIN (SELECT a.account FROM emp_tabble as a "
          "GROUP BY  a.account HAVING (COUNT(a.account) = 1)) "
          "AS a ON a.account = a.account"),
    "2": ("INNER JOIN (SELECT b.account FROM emp_tabble as b "
          "GROUP BY  b.account HAVING (COUNT(b.account) = 1)) "
          "AS b ON a.account = b.account"),
    "30": ("INNER JOIN (SELECT ad.account FROM emp_tabble as ad "
           "GROUP BY  ad.account HAVING (COUNT(ad.account) = 1)) "
           "AS ad ON a.account = ad.account")
}
inner_join_parameters = [key for key, value in inner_join_test.items()]

trimmed_values_test = [
    # Tuple of (values to be excluded, expected)
    (["zip", "dt"], ["user_id", "account"]),
    (["zip"], ["user_id", "account", "dt"])
]


def test_create_fullunique_table_stat():
    expected_query = (
        "(SELECT temp_portal_species.species_id, temp_portal_species.genus, "
        "temp_portal_species.species, temp_portal_species.taxa FROM "
        "( SELECT a.species_id, a.genus, a.species, a.taxa "
        "FROM portal_species as a "
        "INNER JOIN (SELECT b.taxa FROM portal_species as b "
        "GROUP BY  b.taxa HAVING (COUNT(b.taxa) = 1)) AS b ON a.taxa = b.taxa "
        "INNER JOIN (SELECT c.species FROM portal_species as c "
        "GROUP BY  c.species HAVING (COUNT(c.species) = 1)) "
        "AS c ON a.species = c.species INNER JOIN "
        "(SELECT d.genus FROM portal_species as d "
        "GROUP BY  d.genus HAVING (COUNT(d.genus) = 1)) "
        "AS d ON a.genus = d.genus  ) temp_portal_species")
    fields_unique = ["taxa", "species", "genus"]
    all_fields = ["species_id", "genus", "species", "taxa"]
    tablename = "portal_species"
    output = create_uniquevalue_query(all_fields=all_fields,
                                      duplicate=fields_unique,
                                      table_name=tablename)
    assert expected_query.strip().replace("\n", "") == output.strip().replace("\n", "")


@pytest.mark.parametrize("test_id", inner_join_parameters)
def test_create_inner_join(test_id):
    field_name = "account"
    table_name = "emp_tabble"
    index = int(test_id)
    expected_value = inner_join_test[test_id]
    output = create_inner_join(field_name=field_name, index=index, table_name=table_name)
    assert expected_value == output.strip().replace("\n", "")


def test_convert_list_to_sqlcolumn_string():
    all_fields = ["user_id", "account", "zip", "dt"]
    assert "user_id, account, zip, dt" == create_sqlcolumn_string(all_fields, "")
    assert "user_id, account, zip, dt" == create_sqlcolumn_string(all_fields)
    expected = "ha.user_id, ha.account, ha.zip, ha.dt"
    assert expected == create_sqlcolumn_string(all_fields, "ha")


def test_excel_column_name():
    assert excel_column_name(704) == "aab"
    assert excel_column_name(27) == "aa"
    assert excel_column_name(702) == "zz"
    assert excel_column_name(56) == "bd"
    assert not excel_column_name(0)
    assert not excel_column_name(-2)


@pytest.mark.parametrize("excluded_values, expected_value", trimmed_values_test)
def test_get_trimmed_values(excluded_values, expected_value):
    all_fields = ["user_id", "account", "zip", "dt"]
    assert expected_value == get_trimmed_columns(all_fields, excluded_values)


@pytest.mark.parametrize("test_id", create_samplesql)
def test_process_duplicate_fields(test_id):
    """Test subquery to filter out duplicated values based on a column

    process_duplicate_fields excludes row values where the field has duplicates
    """
    all_fields = ["user_id", "account", "zip", "dt"]
    table_name = "payment"
    fields_unique = process_duplicate_parameters[test_id][0]
    expected_value = process_duplicate_parameters[test_id][1]
    output = process_duplicate_fields(all_fields=all_fields,
                                      remove_duplicates_fields=fields_unique,
                                      from_table=table_name)
    assert expected_value.strip() == output.strip().replace("\n", "")
