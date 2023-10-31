from dataclasses import dataclass

from simple_orm.db import QueryBuilderModel

from simple_orm.models import Model, ForeignKey

@dataclass
class Author(Model):
    name:str
    age:int


@dataclass
class Book(Model):
    title:str
    author:ForeignKey[Author]


def test_select_all_authors():
    sql = QueryBuilderModel.select(Author)
    assert "SELECT id, name, age FROM author" == sql


def test_select_author_by_id():
    sql = QueryBuilderModel.select(Author, id=1)
    assert "SELECT id, name, age FROM author WHERE id=?" == sql


def test_insert_author():
    author = Author(1, "Jhon", 25)

    sql = QueryBuilderModel.insert(author)
    assert (len(sql) == 1 and 
            "INSERT INTO author (id, name, age) VALUES (?, ?, ?);" in sql)


def test_update_author_all():
    author = Author(1, "Jhon", 25)

    sql = QueryBuilderModel.update(author)
    assert (len(sql) == 1 and
            "UPDATE author SET id=?, name=?, age=?;" in sql)


def test_update_author_by_id():
    author = Author(1, "Jhon", 25)

    sql = QueryBuilderModel.update(author, id=1)
    assert (len(sql) == 1 and
            "UPDATE author SET id=?, name=?, age=? WHERE id=?;" in sql)


# TODO def test_update_choosed_field(): ...

def test_delete_author_all():
    author = Author(1, "Jhon", 25)

    sql = QueryBuilderModel.delete(author)
    assert (len(sql) == 1 and
            "DELETE FROM author;" in sql)


def test_delete_author_by_id():
    author = Author(1, "Jhon", 25)

    sql = QueryBuilderModel.delete(author, id=1)
    assert (len(sql) == 1 and
            "DELETE FROM author WHERE id=?;" in sql)