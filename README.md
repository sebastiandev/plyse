![Plyse, ask gently, ask properly](https://github.com/sebastiandev/plyse/raw/master/logo.png)  [![Build Status](https://travis-ci.org/sebastiandev/plyse.svg?branch=master)](https://travis-ci.org/sebastiandev/plyse)


**Plyse** is a query parser inspired on the lucene and gmail syntax, fully extensible and configurable, that lets you focus on making the backend find what the user wants without worring about parsing user queries, defining syntax and query trees.

**Plyse** is based on [pyParsing](http://pyparsing.wikispaces.com/), it comes with a default syntax and lets you configure and extend it. There is also a default formatter for the output of the parsed query, and of course it lets you extend it to fit your needs. Every query is converted into a binary tree of operands and operators that is easy to iterate and do whatever you need to to with a user query.


## Install
```shell
sudo pip install plyse
```

## Getting started
**Plyse** ships with defaults so you can start using it in your project immediatly. For the simplest approach, all you need to know is QueryParser and Query. So for the lazy ones:

```python
from plyse import QueryParser, GrammarFactory

parser = QueryParser(GrammarFactory.build_default())
query = parser.parse("hello world")
```



For the curious ones, first we will explain the basic terminology:

- **Gramar**: Usually you want to allow the user to search for data on you application. Sometimes plain text search is not enough and you want to give the user more control and flexibility. So you need to define a grammar which is basically a set of rules that defines the syntax for the user queries. Like gmail's search for example, that lets you do `'in:inbox'` or `'from:foo@gmail.com'`, etc. Here **in** and **from** are the fields where the user search will take place, the colon (**:**) delimits the field to be search and the value that field should contain. Of course you could define different types of field values or operators to make more complex queries. 

- **Term**: Is what a user query is made of, 'from:foo@gmail.com' is a term, defined by a field **from** and its value **foo@gmail.com**. Since fields sort of represent you model's data attributes, you probably have different kind of types. Like text, ints, maybe email, etc; So a Term definition consists on representing those types as possible values for the field. You could think of it as something like: `Field: <integer> | <email> | <string> | <quotes string>`.  Remember that, behind the scenes, these are pyparsing expressions that define matching patterns, so everything can be think of as a huge regular expression.

- **Keyword**: Fields are not fixed, meaning the user can write whatever he wants as a field name, is up to you to let him know what can be put there and handle it. If you need to define certain keywords that have specific behaviour like performing some kind of logic or computacion than just a simple search on an attribute, then defining **Keyword** is what you need, since they are identified as something different than a Term (where the search would be performed on an attribute). Usually **Keywords** have a fixed set of values as well, that mean something particular to your business model. You could think of it as something like: `Keyword: value1 | value2` 

- **Operator**: A logical operator like *AND*, *OR*, *NOT*

- **Operand**: Items where the operators operate on, for example: 'this' OR 'that'. *This* and *that* are the operands of the **OR** operator.

To sum up, if we have a grammar that lets us search for users by their name, you could come up with this query:

` name: 'Peter' or name:'Mary' `
There you have an **OR** operator with 2 *operands* made up by *terms*. Simple right?


## Parsing queries
**QueryParser** is built with a grammar that you can get from **GrammarFactory**. From there all you need to do is call **parse** with the input query string. It will return a **Query** object representing the parsed query. Query gives you access to all the terms from the query, as well as a tree representation of it. 

You will probably want to do something with the user query, like translating it to your data base query language, and thats the case where the tree is useful, you can traverse it to translate each term to the desired query language. Thats the nice thing, users use only one way for querying your app, no matter what you have on your backend, and you dont need to implement hundreds of methods for each posible query. You work with a query tree and translate that to whatever backend you have. The complexity of the queries is up to you, to how deep or complex queries you allow the user to do and how rich you grammar and translating capabilities are.

```python
from plyse import QueryParser, GrammarFactory

parser = QueryParser(GrammarFactory.build_default())
query = parser.parse("name:Peter" or "name:Mary")
```

You can also combine queries, say you want to concatenate two user queries, or you have stored a query that works as a general filter from where user queries are applied to, etc.

Query provides two methods: *stack* and *combine*.

- **Stack**, works like an aggregation, a filter of filters. You can think of it as a select from (select from ...). Or simply as an And concatenation.
- **Combine**, on the other hand opens up the possibility for matches, works as an Or concatenation.

```python
age_query = parser.parse("age:>18")

new_query = query.stack(age_query)  # We are bulding a bigger query, filtering all people named 'peter' or 'mary', older than 18
```

Later on you can check all the stacked or combined queries that make up your new query and get them individually if you need so.

```python
new_query.query_from_stack(level=0)  # returns the query with name filters
new_query.query_from_stack(level=1)  # returns the query with age filter
```

> Query objects are immutable, so every method that modfies the object returns a new instance.

## Traversing query trees
A query tree is a composition of **TreeNodes**, which defines the basic interface for nodes. A node can be of type **Operator** or **Operand**. Query trees are binary trees (almost true except for 'Not' operator which has only one input/child) so every node is an **Operator** that has childs/inputs and every leaf is an **Operand** which is a representation of a query **Term**. You can traverse the tree by asking for the node's children, checking if is a leaf.
You can also ask for all the leafs of a particular node.

```python
print query.terms()

# {field: 'name', field_type:'attribute', 'val': 'peter', val_type: 'partial_string'}
# {field: 'name', field_type:'attribute', 'val': 'mary', val_type: 'partial_string'}

print query.query_as_tree

# [TreeNode] 'OR' operator with 2 children

print query.query_as_tree.inputs[0]
# {'field': 'name',  'field_type': 'attribute',  'val': 'peter',  'val_type': 'partial_string'}

print query.query_as_tree.inputs[1]
# {'field': 'name',  'field_type': 'attribute',  'val': 'mary',  'val_type': 'partial_string'}
```
**Operators** have some extra methods you can query to find out if it supports left and right operands, the name of the Operator and so on. **Operands** can be treated as dicts.

**TreeNode** have methods for traversing and querying for nodes and leafs:

```python
print query.query_as_tree.is_leaf
# False
print len(query.query_as_tree.leafs)
# 2
```

## Gammars and custom setups
A grammar is a set of rules that make up your query syntax. Those rules involve defining the types of values that the query expression will accept, they way they are supposed to be expressed and how they are combined to build up the grammar.

A user query is a combination of terms. Terms can be simple text or can define exactly where the desired value has to be searched, like in a particular field or attribute. 

The very baisc example would allow the user to enter some text and use that to search for some particular fields or attributes of your model that contains it. So we need a value type that represents a word. **Plyse** provides SimpleWord, PartialString, QuotedString and Phrase. We will use **PartialString**

Lets start wit a Term that supports a PartialString as the only possible value. So, If the user enters more than one Term how are we supposed to interpret that? It means the result has to meet both conditions? Only one of them? Thats what Operators are for, and you can decide which one can be implícit so the user doesnt need to write it, if we use Or as implícit then:

**"Hello word"** would be a query with 2 terms and one Operator, an implicit *Or*.

So if we build our Grammar with that definition of Term and the Or operator and parse the input string *"hello world"*,  code and output would look like:

```python
from plyse import PartialString, Field, Term, Operator, GrammarFactory

term = Term(field=Field(), values=[PartialString()])
operators = [Operator(name='or', symbols=['or'], implicit=True)]

grammar = GrammarFactory.build(term, None, operators)
grammar.parse("hello word")

# ([([(['hello'], {}), 'OR', (['world'], {})], {})], {})
```

Lets go through each line:

```python 
term = Term(field=Field(), values=[PartialString()])
```

Creating a Term requires specifing the type for the field, and the possible values for the field. **Plyse** has only one definition for fields (*Field*) that is represented as a combination of characters, dash and points. Meaning that anycombination o chars, dash and points followed by a colon will be treated as a field name. What ever comes next would be interpreted as the value of that field. And theres where the value array comes in, it defines all the possible types that are going to be identified as values. For now we only support **PartialString** which means that the allowed input will be any combination of chars, and is going to be tagged as **partial_string**. If you want the user to be able to search for an exact expression you can use QuotedString, which allows all combination of chars, but surrounded by quotes, and tags the value as **exact_string**.

```python 
operators = [Operator(name='or', symbols=['or'], implicit=True)]
```

This line builds the operator array, with only the definition of the Or operator. *name* is... well the name. *symbols* defines what can be used as the operator, and lets you define for example *'|'* so that would also be interpreted as an **Or**. *Implicit* means that if two words/terms are defined with no operator in the middle, then an **Or** is assumed.

```python 
grammar.parse("hello word")
```

This line just parses the input, looking to match with the Term definition. Here no field was specified, just plain text, so the field type is tagged as **default** for each term, and the value will be *hello* for the first one, and *world* for the second one. When configuring the grammar and the Field object, you can specify an array to be used as the default value when no field name whas specified. In that case instead of been tagged as **default**, the field_type will be an array with the specified fieldnames.

That was easy, althougth the output doesn't look so nice. 

That is because pyParsing output is pretty ugly or raw. You always need to format and adapt it to you needs. **Plyse** has a default parser called **TermParser**, since the higher order element of a query is a **Term**. This class defines a parse method for each supported value type. The idea is that each part of a query Term gets represented by a dict, so if you look for: `"age: 25"` the **Grammar** will find a **field** *(age)* and a **value** *(25)*. Each one will be parsed independently, and finally the Grammar builds up the Term which gets parsed as well. The final output, using the term parser and query parser becomes:

```python
from plyse import GrammarFactory, QuerParser, Query

parser = QueryParser(GrammarFactory.build_default())
query = parser.parse("age:25")

print query.terms()
# {field:age, field_type:attribute, value:25, value_type:integer}
```

Thats much better and now you can do different things based on the **value_type** and **field_type** of each term.

So in our example previous would build the **PartialString** type passing the *TermParser.partial_string_parse* method. And so the code and output would now loo like:

```python
from plyse import PartialString, Field, Term, TermParser, Operator, GrammarFactory, QuerParser, Query

term_parser = TermParser()
term = Term(field=Field(), values=[PartialString(term_parser.partial_string_parse)])
operators = [Operator(name='or', symbols=['or'], implicit=True)]

grammar = GrammarFactory.build(term, term_parser, operators)
parser = QueryParser(grammar)
query = parser.parse("hello world")

print query.terms()
# {field:default, field_type:attribute, value:hello, value_type:partial_string}
# {field:default, field_type:attribute, value:world, value_type:partial_string}
```
You can always create new types for the Term values to be used in the Grammar, and you can extend TermParser as well if you need to add parse methods for the new values or change they way they are represented.

## Configuring the Grammar
Grammars can be built manually like in the previous example or through a yaml file. In this file you need to specify the Operators you want to use, with the symbols that identify them, as well as if they are implícit. The order here is important since it defines the precedence.

For terms, you need to define the class used for the field, and the parse method. For the possible term values you need to define the class path, parse method and precedence for each type. Precedence is important because it defines which type is check first when parsing the query, so be careful if you change the defaults. 

For example, giving more precedence to string than integer will  cause integers to never match, since strings are alphanumeric, they will always pick up the numbers as strings. The same considerations apply to special values like integer range, they need to have a higher precedence than simple types.

Finally to build the Term parser you have to define the class path, and optional aliases to be used for specific fields, and values to be used as default attribute fields when no field was specify in the query. So in our example, `"hello world"` didn't specify a field, so default is applied. If you define default values to the TermParser, like `[name, description]`. Then instead of 'default' you would get a list with those values.

Here's how the default configuration for the grammar looks like:
```yaml
grammar:

  term_parser:
    class: plyse.term_parser.TermParser
    integer_as_string: False
    default_fields: []
    aliases: {}

  operators:
    not:
      implicit: False
      symbols:
        - 'not'
        - '-'
        - '!'
    and:
      implicit: False
      symbols:
        - 'and'
        - '+'
    or:
      implicit: True
      symbols:
        - 'or'

  keywords:
    is:
      - important
      - critical

  term:
    field:
      class: plyse.expressions.primitives.Field
      precedence: 10
      parse_method: field_parse

    values:
      - class: plyse.expressions.primitives.PartialString
        precedence: 3
        parse_method: partial_string_parse

      - class: plyse.expressions.primitives.QuotedString
        precedence: 2
        parse_method: quoted_string_parse

      - class: plyse.expressions.primitives.Integer
        precedence: 4
        parse_method: integer_parse

      - class: plyse.expressions.primitives.IntegerRange
        precedence: 5
        range_parse_method: range_parse
        item_parse_method: integer_parse
```

## Extending the Grammar
Plyse ships with a set of default types that should cover the basic needs pretty well:

- PartialString
- QuotedString
- Phrase
- Integer
- IntegerRange
- IntegerComparison
- Field
- MultiField

The grammar can be manipulated programatically, removing or adding types used for the terms:
```python
from plyse import GrammarFactory, IntegerComparison, QueryParser, Query

grammar = GrammarFactory.build_default()
grammar.value_types

# [{'precedence': 10, 'type': 'integer_range'},
#  {'precedence': 6, 'type': 'integer'},
#  {'precedence': 3, 'type': 'partial_string'},
#  {'precedence': 2, 'type': 'quoted_string'}]

grammar.remove_type('integer_range')
grammar.add_value_type(IntegerComparison(grammar.term_parser.integer_comparison_parse))

parser = QueryParser(grammar)
q = qp.parse("age:>18")

print q.terms()

#[{'field': 'age',
#  'field_type': 'attribute',
#  'val': 18,
#  'val_type': 'greater_than'}]
```

For more examples take a look at the different tests covering the funcionality of each module [here](https://github.com/sebastiandev/plyse/tree/master/plyse/tests)
