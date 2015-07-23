/* Creates the table and columns */
/* Note: You will simplify your life by using all lowercase characters for column names */
/* Postgre expects lowercase and converts queries unless you "double-quote" them in your script */
/* Without the quotes on mixed-case column names, you get fatal 'column not found' errors */

CREATE TABLE cardinfo
(
  "ID" serial PRIMARY KEY,
  sport character varying(50) NOT NULL,
  "lastName" character varying NOT NULL,
  "firstName" character varying(50) NOT NULL,
  year smallint NOT NULL,
  team character varying(50) NOT NULL,
  company character varying(50) NOT NULL,
  "valueEst" money,
  "saleDate" date,
  "salePrice" money
)

/* No need for OIDS since we are using a serial column as the PK */
WITH (
  OIDS=FALSE
);

/* Ensures postgres is the table owner (shouldn't really be necessary) */
ALTER TABLE cardinfo
  OWNER TO postgres;
GRANT ALL ON TABLE cardinfo TO postgres;


/* -------------------------------------------------------------------- */


/* Creating roles is like creating users in older versions of Postgre */
/* My Python script roles start with 'py_' so I can track them */


/* Create a role with a password (encrypted by default), valid across entire database cluster*/
/* But you must grant permissions on a per-database or per-table level */
/* This allows scripts to run with different permissions in different locations*/
CREATE ROLE py_carddb WITH PASSWORD 'password';
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE cardinfo TO py_carddb;
/* You must ALSO explicitly grant the script permission to 'use' the serial sequence */
GRANT USAGE, SELECT ON SEQUENCE "cardinfo_ID_seq" TO py_carddb;


/* -------------------------------------------------------------------- */


/* 'Insert' syntax and test to insert the first row */
INSERT INTO cardinfo (sport, "lastName", "firstName", year, team, company)
	VALUES('Baseball', 'Smith', 'Bobby', 2015, 'Twins', 'Topps')
