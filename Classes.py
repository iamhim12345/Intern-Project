"""
This is the initial module of all the classes present.
"""
import logging
import datetime
import psycopg2

logging.basicConfig(filename='classes.log', level=logging.INFO,
                    format='%(asctime)s:%(message)s')


# bookDB = {
#     'Pride': [1, 1],
#     'Crime and Punishment': [2, 1],
#     '1984': [3, 1]
# }
# book_genres = ('horror', 'drama', 'history')  # tuple of genres
conn =  psycopg2.connect(host='localhost',dbname='library',user='postgres',
                         password ='vamsi',port=5432)
DBconfig = {
    'host': 'localhost',
    'dbname': 'library',
    'user': 'postgres',
    'password': 'vamsi',                    
    'port': 5432
}
cur = conn.cursor()

sqlstr = 'select * from public.books order by book_id'

cur.execute(sqlstr)


records = cur.fetchall()

def tuple_to_dict(lst):
    result_dict = {}
    for tup in lst:
        key = tup[0]
        value = list(tup[1:])
        result_dict[key] = value
    return result_dict


bookDB = tuple_to_dict(records)
global bookDB_lst 
bookDB_lst =[]
bookDB_lst = list(bookDB.values())


class User:
    """
    This is the parent class of the Librarian and Student classes.
    """
    def __init__(self, name, password):
        self.name = name
        self.password = password
        logging.info('User created: %s', self.name)

    def introduce(self):
        logging.info('Hello, I am %s', self.name)

    def search_book(self, book_name):
        found = False
        for i in range(len(bookDB_lst)):
            if book_name == bookDB_lst[i][0]:
                found = True

        return found
    def avail_book(self,book_name):
        for i in range(len(bookDB_lst)):
            if (bookDB_lst[i][0] == book_name):
                if(bookDB_lst[i][1] == 1):
                    return True
                else:
                    return False
    def get_book_info(name):
        conn = psycopg2.connect(host='localhost',dbname='library',user='postgres',
                         password ='vamsi',port=5432)
        cur_2 = conn.cursor()
        sqlquery = 'select * from public.books inner join public.book_info on books.book_id = book_info.book_id where books.book_name = %s'
        insert_value = (name)
        try:
            book_called = cur_2.execute(sqlquery,insert_value)
            conn.commit()
            print("the book is " + book_called)
        except Exception as e:
            conn.rollback()
            print(f"Error: {e}")
        cur_2.close()
        conn.close()


    

    

class Librarian(User):
    """
    This is a child class Librarian of the User class.
    """
    # pylint: disable=useless-super-delegation
    def __init__(self, name, password):
        super().__init__(name, password)   

    def add_book(self,name,id):
        conn = psycopg2.connect(host='localhost',dbname='library',user='postgres',
                         password ='vamsi',port=5432)
        curr_1 = conn.cursor()
        query_1 = """
        insert into public.books(book_id,book_name,availability) values (%s,%s,%s); 
        """
        query_2 = "insert into public.book_info(book_id,author,genre) values (%s,%s,%s );"
        name = input("give book name ")
        id = (len(bookDB_lst) + 1)
        insert_values = (id,name,1)          #for multiple insertions use list of tuples
        
       
        
        
        try:
            curr_1.execute(query_1,insert_values)
            print("Book added successfully.")   
            
            conn.commit()
        except Exception as e:
            print("rooling back")
            conn.rollback()
            print(str(e))
        finally:
             curr_1.close()
             conn.close()
       

class Student(User):
    """
    This is a child class Student of the User class.
    """
    def __init__(self, name, password, student_id):
        super().__init__(name, password)
        self.student_id = student_id

    def borrow_book(self, book_name):
        
        if self.search_book(book_name):
            if self.avail_book(book_name):
                for i in range(len(bookDB_lst)):
                    if bookDB_lst[i][0] == book_name:
                        bookDB_lst[i][1] = 0
                borrowed_date = datetime.datetime.now()
                logging.info('Borrowed book %s at %s', book_name, str(borrowed_date))
                print('Book is available')
                print('Book is borrowed ' + str(borrowed_date))
            else:
                print('Book is not available')
        else:
            print('Book is not of library')

    def return_book(self, book_name):
        if self.search_book(book_name):
            if not self.avail_book(book_name):
                for i in range(len(bookDB_lst)):
                    if bookDB_lst[i][0] == book_name:
                        bookDB_lst[i][1] = 0
                return_date = datetime.datetime.now()
                logging.info('Returned book %s at %s', book_name, str(return_date))
                print('Returned book at ' + str(return_date))
            else:
                print('Book was not borrowed')
        else:
            print('Book is not in the library')



conn.commit()

cur.close()
conn.close()

