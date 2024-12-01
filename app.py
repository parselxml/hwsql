import psycopg2

def create_db(conn):
    with conn.cursor() as cur:
        cur.execute('drop table if exists phone, client cascade;')
        cur.execute('''
        create table if not exists client(
            id serial primary key,
            first_name varchar(50) not null,
            last_name varchar(50) not null,
            email varchar(50) not null
        );
        
        create table if not exists phone(
            id serial primary key,
            client_id integer references client(id) on delete cascade,
            phone varchar(50) not null
        );
        ''')


def add_client(conn, first_name, last_name, email, phones=None):
    with conn.cursor() as cur:
        cur.execute('''
        insert into client(first_name, last_name, email)
        values (%s, %s, %s)
        returning id;
        ''', (first_name, last_name, email))
        client_id = cur.fetchone()[0]
        if phones:
            for phone in phones:
                add_phone(conn, client_id, phone)
        conn.commit()

def add_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute('''
        insert into phone(client_id, phone)
        values (%s, %s);
        ''', (client_id, phone))
        conn.commit()

def change_client(conn, client_id, first_name=None, last_name=None, email=None, phones=None):
    with conn.cursor() as cur:
        if first_name:
            cur.execute('update client set first_name=%s where id=%s', (first_name, client_id))
        if last_name:
            cur.execute('update client set last_name=%s where id=%s', (last_name, client_id))
        if email:
            cur.execute('update client set email=%s where id=%s', (email, client_id))
        if phones is not None:
            cur.execute('delete from phone where client_id=%s', (client_id,))
            for phone in phones:
                cur.execute('insert into phone (client_id, phone) values''(%s, %s)', (client_id, phone))


def delete_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute('''
        delete from phone
        where client_id=%s and phone=%s;
        ''', (client_id, phone))
        conn.commit()

def delete_client(conn, client_id):
    with conn.cursor() as cur:
        cur.execute('''
        delete from client
        where id=%s;
        ''', (client_id, ))
        conn.commit()

def find_client(conn, first_name=None, last_name=None, email=None, phone=None):
    with conn.cursor() as cur:
        query = '''
            select distinct c.id, c.first_name, c.last_name, c.email
            from client c
            left join phone p on c.id = p.client_id
            where true
        '''
        params = []

        if first_name:
            query += ' and c.first_name = %s'
            params.append(first_name)
        if last_name:
            query += ' and c.last_name = %s'
            params.append(last_name)
        if email:
            query += ' and c.email = %s'
            params.append(email)
        if phone:
            query += ' and p.phone = %s'
            params.append(phone)


        cur.execute(query, params)
        print(cur.fetchall())

with psycopg2.connect(database='netologydb', user='postgres', password='qw123qw') as conn:
    create_db(conn)

    add_client(conn, 'Иван', 'Иванов', 'ivanov@example.com', phones=['+79161234567', '+79162345678'])

    change_client(conn, 1, first_name='Александр', phones=['+79161111111'])

    find_client(conn, phone='+79161111111')

    delete_phone(conn, 1, '+79161111111')

    delete_client(conn, 1)