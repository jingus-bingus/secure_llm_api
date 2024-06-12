from database import Database_Manager

def main():
    db_manager = Database_Manager()
    db_manager.create_tables()

if __name__ == '__main__':
    main()