
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date
from datetime import datetime, timedelta

Base = declarative_base()


class Table(Base):
    __tablename__ = 'task'
    id = Column(Integer, primary_key=True)
    task = Column(String, default='default_value')
    deadline = Column(Date, default=datetime.today())

    def __repr__(self):
        return self.task


class ToDoList(Table):
    def __init__(self, db_file_name):
        self.engine = create_engine(f'sqlite:///{db_file_name}?check_same_thread=False')
        self.session = self.session_handler()
        self.table = Base.metadata.create_all(self.engine)
        self.weekdays = ['Monday', 'Tuesday', 'Wednesday',
                         'Thursday', 'Friday', 'Saturday', 'Sunday']

    def session_handler(self):
        sn_maker = sessionmaker(bind=self.engine)
        session = sn_maker()
        return session

    def add_task(self, task, date):
        new_row = Table(task=task,
                        deadline=datetime.strptime(date, '%Y-%m-%d').date())
        self.session.add(new_row)
        self.session.commit()

    def delete_task(self, task):
        rows = self.get_tasks()
        self.session.delete(rows[task])
        self.session.commit()

    def get_tasks(self):
        return self.session.query(Table).order_by(Table.deadline).all()

    def get_todays_tasks(self):
        today = datetime.today()
        rows = self.session.query(Table).filter(Table.deadline == today.date()).all()
        return rows

    def get_weeks_tasks(self, i):
        rows = self.session.query(Table).filter(Table.deadline == i).all()
        return rows

    def get_missed_tasks(self):
        today = datetime.today()
        rows = self.session.query(Table).filter(Table.deadline < today.date()).order_by(Table.deadline).all()
        return rows

    @staticmethod
    def print_menu():
        print("\n1) Today's tasks\n"
              "2) Week's tasks\n"
              "3) All tasks\n"
              "4) Missed tasks\n"
              "5) Add task\n"
              "6) Delete task\n"
              "0) Exit")

    def print_tasks(self, tasks, method):
        if method == 1:
            if len(tasks) == 0:
                print("Nothing to do!")
                self.handle_menu()
            else:
                print(f"Today {datetime.today().strftime('%e').strip()} {datetime.today().strftime('%b')}")
                for i in tasks:
                    print(f"{tasks.index(i) + 1}. {i.task}")
                self.handle_menu()
        elif method == 2:
            for i in tasks:
                rows = self.get_weeks_tasks(i)
                dl = [row.deadline for row in rows]
                if i not in dl:
                    print(f"\n{self.weekdays[i.weekday()]} {i.strftime('%e %b').strip()}\n"
                          f"Nothing to do!\n")
                else:
                    print(f"\n{self.weekdays[i.weekday()]} {i.strftime('%e %b').strip()}\n"
                          f"Nothing to do!")
                    for j in rows:
                        print(f"{rows.index(j) + 1}. {j.task}")
            self.handle_menu()
        elif method == 3:
            print("All tasks:")
            for i in tasks:
                dl = i.deadline
                d = dl.strftime('%e %b').strip()
                if len(i.task) == 0:
                    print(f'{tasks.index(i) + 1} Nothing to do! {d}')
                else:
                    print(f"{tasks.index(i) + 1}. {i.task}. {d}")
            self.handle_menu()
        elif method == 4:
            tasks = self.get_missed_tasks()
            print('\nMissed tasks:')
            for i in tasks:
                dl = i.deadline
                d = dl.strftime('%e %b').strip()
                if len(i.task) == 0:
                    print("Nothing is missed!\n")
                else:
                    print(f"{tasks.index(i) + 1}. {i.task}. {d}")
            self.handle_menu()
            pass

    def handle_menu(self):
        self.print_menu()
        choice = int(input())
        if choice == 1:
            tasks = self.get_todays_tasks()
            self.print_tasks(tasks, 1)
        elif choice == 2:
            today = datetime.today()
            tasks = [(today + timedelta(days=i)).date() for i in range(7)]
            # print(tasks)
            self.print_tasks(tasks, 2)
        elif choice == 3:
            tasks = self.get_tasks()
            self.print_tasks(tasks, 3)
        elif choice == 4:
            tasks = self.get_missed_tasks()
            self.print_tasks(tasks, 4)
        elif choice == 5:
            user_task = input("Enter task\n")
            date = input("Enter deadline\n")
            self.add_task(user_task, date)
            print("The task has been added!")
            self.handle_menu()
        elif choice == 6:
            tasks = self.get_tasks()
            print(f"Choose the number of the task you want to delete:")
            for i in tasks:
                print(f"{tasks.index(i) + 1}. {i.task}. {i.deadline.strftime('%e %b').strip()}")
            user_pick = int(input()) - 1
            self.delete_task(user_pick)
            print("The task has been deleted!")
            self.handle_menu()
        elif choice == 0:
            print("Bye!")


if __name__ == '__main__':
    tdl = ToDoList('todo.db')
    tdl.handle_menu()
