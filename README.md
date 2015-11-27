![Plyse, ask gently, ask properly](https://github.com/sebastiandev/plyse/raw/master/logo.png)

**Plyse** is a query parser inspired on the lucene and gmail sintax, fully extensible and configurable, that lets you focus on making the backend find what the user wants without worring about parsing user queries, defining sintax and query trees.

**Plyse** is based on [pyParsing](http://pyparsing.wikispaces.com/), it comes with a default sintax and lets you configure and extend it. It also comes with a default formatter for the output of the parsed query, and of course it lets you extend it to fit your needs. Every query is converted into a binary tree of operands and operators that is easy to iterate and do whatever you need to to with a user query.
