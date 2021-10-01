CREATE TABLE IF NOT EXISTS User_table(
	id_user integer(20) primary key,
	name_user varchar(40),
	)

CREATE TABLE Marital_Status(
    id_status serial primary key,
    marital_status varchar
)

CREATE TABLE IF NOT EXISTS User_request(
    request_id serial NOT NULL,
    id_user integer references User_table(id_user) ON DELETE CASCADE,
    age integer not null,
    sex integer CHECK
        ( sex>=0 and sex<=2),
    city varchar not null,
    marital_status integer references Marital_Status(id_status),
    CONSTRAINT User_request_pk PRIMARY KEY (request_id, id_user)
);

CREATE TABLE IF NOT EXISTS Search_users(
    id_search serial NOT NULL,
    search_user_id integer NOT NULL,
    to_id_user integer references User_table(id_user) ON DELETE CASCADE,
    age integer not null,
    sex integer not null,
    city varchar not null,
    marital_status integer references Marital_Status(id_status),
    CONSTRAINT User_request_pk PRIMARY KEY (id_search, search_user_id)
);

