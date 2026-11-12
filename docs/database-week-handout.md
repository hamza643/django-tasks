# Database & SQL Fundamentals — One Week

**For:** Hamza **Builds on:** your CLI and SRMS projects, both of which save data to JSON files **Time:** one week

## Why this week, right now

Your SRMS saves everything to a JSON file that your Repository class reads and rewrites completely, every time. That's fine for a few hundred students, but it breaks down as the data grows: every save rewrites the whole file, nothing stops two different records from disagreeing with each other, and finding one record means searching through all of them in Python.

A **database** solves these problems, and a real backend service talks to one instead of a file. Before you learn the web framework that will replace your main.py menu, you need to be able to ask a database for exactly the data you want, in the shape you want it.

By the end of this week you should be able to: - Explain what a database is, and why an application needs one - Explain the difference between a DBMS and an RDBMS - Understand tables, rows, columns, primary keys, and foreign keys - Write SQL queries that filter, sort, and aggregate data - Understand relationships between tables, and perform different kinds of joins - Write a basic subquery

## Setup

1.  Install **DB Browser for SQLite** — a free, visual tool for opening and querying .db files.

2.  Download the **Chinook** sample database: chinook.zip. Unzip it — you'll get chinook.db.

3.  Open chinook.db in DB Browser. Chinook is a sample music store: customers, employees, invoices, tracks, albums, artists, and playlists.

Every number and query in this handout was run against this exact file, so your results should match.

# PART 1 — What is a database, and why

## Concepts

**Data** is just facts: a name, a price, a date. **A database** is organised, searchable storage for data, built so many parts of a program (or many different programs) can read and change it safely at the same time.

**File storage vs. a database.** Your SRMS writes one JSON file. A database differs in three ways that matter: - **Partial access.** A database can hand you *just* the rows you asked for, without reading the whole dataset into memory first. - **Consistency rules.** A database can refuse to save a row that breaks a rule, for example a result for a student id that doesn't exist. Your Repository currently trusts the caller to get this right. - **Concurrent access.** Multiple programs, or multiple users of the same program, can read and write safely, without each one rewriting the whole file and clobbering someone else's change.

**DBMS vs. RDBMS.** A DBMS (Database Management System) is any system for managing data. An RDBMS (Relational DBMS) is a DBMS that organises data into **tables** with defined **relationships** between them — SQLite, PostgreSQL, MySQL, and SQL Server are all RDBMSs. "Relational" is the key word: it means the tables are connected on purpose, not just stored next to each other.

**Table, row, column.** A table is like a spreadsheet: a fixed set of **columns** (name, email, price), and any number of **rows** (one per customer, one per track). Each row is one record.

**Primary key.** The column, or combination of columns, that uniquely identifies a row in its table. No two rows share one, and it's never empty. In Chinook, CustomerId is the primary key of customers.

**Foreign key.** A column in one table that refers to the primary key of another. invoices.CustomerId is a foreign key pointing at customers.CustomerId — it's how one invoice is linked to the customer who made it.

## Exercise: explore Chinook

Open chinook.db in DB Browser, on the "Database Structure" tab, and answer: 1. How many tables are there? 2. Pick three tables. For each, name its primary key. 3. Find two foreign keys, and name which table and column each one points to. 4. Open the "Browse Data" tab for customers. How many rows are there?

# PART 2 — SQL basics

## Concepts

SELECT FirstName, LastName FROM customers; -- which columns

SELECT \* FROM customers WHERE Country = 'USA'; -- which rows

SELECT \* FROM customers ORDER BY LastName ASC; -- sort order

SELECT \* FROM customers LIMIT 10; -- only the first 10

SELECT DISTINCT Country FROM customers; -- unique values only

SELECT COUNT(\*) FROM customers; -- how many rows

SELECT FirstName AS first, LastName AS last FROM customers; -- rename a column

- SELECT names the columns you want back. SELECT \* means all of them.

- WHERE filters individual rows, before anything else happens.

- ORDER BY sorts the result. DESC reverses it.

- LIMIT caps how many rows come back.

- DISTINCT removes duplicate rows from the result.

- COUNT(\*) is an aggregate: it collapses many rows into one number.

- AS gives a column (or a whole query result) a different name in the output.

## Exercise

Write queries against Chinook for each of these. Run them in DB Browser and write down the actual result.

1.  All customers' first and last names.

2.  All albums.

3.  All artists.

4.  Customers from the USA, sorted by last name. (Check your answer: the first one alphabetically is Julia Barnett.)

5.  The first 5 customers, in any order.

6.  How many customers there are in total. (Check your answer: 59.)

7.  Every distinct country a customer is from.

# PART 3 — Relationships and design

## Concepts

Tables connect to each other in three shapes:

- **One-to-one**: one row in A matches exactly one row in B. Rare — usually you'd just merge the tables.

- **One-to-many**: one row in A can match many rows in B, but each row in B matches only one row in A. One customer has many invoices; each invoice belongs to one customer.

- **Many-to-many**: rows in A can match many rows in B, and the reverse is also true. One playlist has many tracks, and one track can be on many playlists. This needs a **join table** in between — Chinook's playlist_track table exists for exactly this reason, holding pairs of (PlaylistId, TrackId).

**Referential integrity** means a foreign key always points at a row that actually exists. A database can enforce this and refuse to save a bad reference; your JSON files cannot.

**Normalization**, briefly: splitting data into separate tables so each fact is stored in exactly one place. If a customer's country were repeated on every one of their invoices, correcting a typo would mean updating every invoice. Keeping it once, on the customer, and referencing the customer by id everywhere else, is the normalized approach — and it's exactly what your SRMS Result already does, referencing a student and a course by id rather than copying their details.

## Exercise

1.  In Chinook, find the one-to-many relationship between albums and tracks. Which column makes it one-to-many?

2.  Find the many-to-many relationship involving playlist_track. Name the two tables on either side.

3.  Draw an ER (Entity Relationship) diagram covering customers, invoices, invoice_items, and tracks. Use diagrams.net or draw it on paper. Show the primary key of each table and the foreign keys connecting them.

# PART 4 — JOINs

## Concepts

A join combines rows from two tables that are related by a key.

SELECT c.FirstName, c.LastName, i.InvoiceId, i.Total

FROM customers c

INNER JOIN invoices i ON c.CustomerId = i.CustomerId;

INNER JOIN keeps only the rows that match on both sides. A customer with no invoices would not appear at all.

LEFT JOIN keeps every row from the left table, filling in NULL where there's no match on the right. This is the join to reach for when you want to know about things that *might not* have a match.

Here's a real example from Chinook, where the difference matters:

-- INNER JOIN: only employees who have at least one customer

SELECT e.FirstName, e.LastName, COUNT(c.CustomerId) AS customers

FROM employees e

INNER JOIN customers c ON e.EmployeeId = c.SupportRepId

GROUP BY e.EmployeeId;

This returns only **3 employees**. Five employees in Chinook support zero customers, so an INNER JOIN makes them disappear entirely.

-- LEFT JOIN: every employee, with 0 where there's no match

SELECT e.FirstName, e.LastName, COUNT(c.CustomerId) AS customers

FROM employees e

LEFT JOIN customers c ON e.EmployeeId = c.SupportRepId

GROUP BY e.EmployeeId;

This returns all **8 employees**, five of them with a count of 0.

You'll also come across RIGHT JOIN (the mirror of LEFT JOIN, rare in practice), FULL OUTER JOIN (keeps unmatched rows from both sides), and CROSS JOIN (every row from A paired with every row from B — no matching condition at all). Know they exist; you won't need them this week.

## Exercise

1.  Join customers and invoices to show each customer's name next to each invoice total.

2.  Join tracks and albums to show each track's name next to its album title.

3.  Reproduce the employees example above with both an INNER JOIN and a LEFT JOIN, and confirm you get 3 rows and 8 rows respectively.

# PART 5 — Aggregation, GROUP BY, and HAVING

## Concepts

SELECT BillingCountry, SUM(Total) AS total_sales

FROM invoices

GROUP BY BillingCountry

ORDER BY total_sales DESC;

SUM, AVG, MIN, MAX, and COUNT are **aggregate functions**: they collapse many rows into one number. GROUP BY says which column defines each group — here, one group per country.

**The trap:** you cannot filter on an aggregate with WHERE, because WHERE runs *before* grouping happens, and the aggregate doesn't exist yet.

-- WRONG: fails, because COUNT(\*) doesn't exist until after grouping

SELECT AlbumId, COUNT(\*)

FROM tracks

WHERE COUNT(\*) \> 10

GROUP BY AlbumId;

-- RIGHT: HAVING filters groups, after they're built

SELECT AlbumId, COUNT(\*) AS track_count

FROM tracks

GROUP BY AlbumId

HAVING COUNT(\*) \> 10;

The real execution order is: FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY. That's why HAVING can use an aggregate and WHERE can't, and why ORDER BY can refer to a column you only named in SELECT.

## Exercise

1.  Total sales by country, highest first. (Check your answer: the USA is highest, at 523.06.)

2.  Average invoice amount, overall.

3.  Highest and lowest invoice totals.

4.  How many albums have more than 10 tracks. (Check your answer: 183.)

# PART 6 — Subqueries

## Concepts

A subquery is a query nested inside another one. You reach for one when you need a value *computed first*, before you can filter by it.

SELECT InvoiceId, CustomerId, Total

FROM invoices

WHERE Total \> (SELECT AVG(Total) FROM invoices);

The inner query runs first, producing one number (the average), and the outer query filters against it. This is the natural next step after HAVING — HAVING filters *groups* you've already built; a subquery lets you filter against a number that has to be calculated separately first.

## Exercise

1.  Find all invoices above the average invoice total. (Check your answer: 179 invoices.)

2.  Find the single most expensive track, by length in milliseconds. (Check your answer: "Occupation / Precipice", at 5,286,953 ms — about 88 minutes.)

3.  Find customers who have placed more than 5 invoices.

# THE ASSESSMENT

## Part A — Written (explain in your own words)

1.  What is a database, and why does an application need one instead of a file?

2.  What is the difference between a DBMS and an RDBMS?

3.  What is a primary key? What is a foreign key?

4.  What is the difference between WHERE and HAVING?

5.  What is the difference between INNER JOIN and LEFT JOIN? Give a real example from Chinook where the two would return a different number of rows.

6.  What is a subquery, and when would you reach for one instead of HAVING?

## Part B — Practical: 15 queries

Write 15 SQL queries against Chinook, covering everything from this week: - 5 basic SELECT queries (any combination of filtering, sorting, limiting) - 3 filtering queries using WHERE - 3 JOIN queries (at least one INNER JOIN and one LEFT JOIN) - 2 GROUP BY queries (at least one using HAVING) - 2 subqueries

## Deliverables

Submit: 1. Your SQL file (database_week_queries.sql), with a comment above each query saying what it does 2. Your ER diagram from Part 3 3. Screenshots from DB Browser showing three of your queries actually running, with results 4. A short reflection (half a page): what you found hardest this week, and one question you still have

## What a good submission looks like

| Area            | Full marks                                                                                     |
|-------------------------------------------|--------------------------------------------------------------------------------------------------------------------------|
| Written answers | Specific, in your own words, with an example from Chinook where relevant                       |
| Basic queries   | Correct results, using the right clause for the job                                            |
| Joins           | INNER and LEFT both used correctly, and you can explain why they'd return different row counts |
| Aggregation     | GROUP BY and HAVING used correctly, not WHERE on an aggregate                                  |
| Subqueries      | At least one genuinely needs the subquery, rather than being solvable with a plain WHERE       |
| ER diagram      | Matches the real foreign keys in the database                                                  |

## Review questions

- "Show me a query where INNER JOIN and LEFT JOIN would give you a different number of rows. Why?"

- "Why can't you put COUNT(\*) \> 10 in a WHERE clause?"

- "Walk me through the real order SQL runs your query in, not the order you typed it."

- "Your SRMS Result class stores a student id and a course code rather than copying their data in. How does that connect to normalization?"

## After this

Next is the Python bridge to backend: HTTP, async/await, pydantic, and the ORM — the layer that lets your Python code talk to a database like this one without writing raw SQL by hand. Then FastAPI, where your SRMS gets rebuilt as a real web API with a real database behind it.
