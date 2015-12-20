/* Creates the table and columns */
/* Note: You will simplify your life by using all lowercase characters for column names */
/* Postgre expects lowercase and converts queries unless you "double-quote" them in your script */
/* Without the quotes on mixed-case column names, you get fatal 'column not found' errors */

/* My 'cards' database has two schemas, 'public' which is a default, and 'testing' */
/* This enables me to clone the 'public' table(s) into 'testing' to test commands etc. */
/* You can ignore or delete the 'public.' prefixes if you don't want to have multiple schemas */

CREATE TABLE public.cardinfo
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
ALTER TABLE public.cardinfo
  OWNER TO postgres;
GRANT ALL ON TABLE public.cardinfo TO postgres;


/* -------------------------------------------------------------------- */


/* Creating roles is like creating users in older versions of Postgre */
/* My Python script roles start with 'py_' so I can track them */


/* Create a user with a password that this app uses to connect to and alter the database */
/* You must grant permissions on a database, schema, and table level */
CREATE USER py_carddb WITH PASSWORD 'password';
GRANT CONNECT ON DATABASE cards to py_carddb;
GRANT USAGE ON SCHEMA public TO py_carddb;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE public.cardinfo TO py_carddb;
/* You must ALSO explicitly grant the script permission to 'use' the serial sequence (PK) */
GRANT USAGE, SELECT ON SEQUENCE "cardinfo_ID_seq" TO py_carddb;


/* -------------------------------------------------------------------- */


/* 'Insert' syntax and test to insert the first row */
INSERT INTO public.cardinfo (sport, "lastName", "firstName", year, team, company)
	VALUES('Baseball', 'Smith', 'Bobby', 1984, 'Twins', 'Topps')
