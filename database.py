from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import USER, PASSWORD

# export PATH=$PATH:/usr/local/mysql/bin -> mysql -u root -p

engine = create_engine(
    f"mysql+pymysql://{USER}:{PASSWORD}@localhost/personal_assistant"
)

Base = declarative_base()  # Create base class of object


class Users(Base):
    __tablename__ = "users"  # name of table

    # Columns
    id = Column(Integer, primary_key=True, autoincrement=True, comment="Increment primary key")
    user_id = Column(Integer, unique=True, comment="User id in Telegram")
    name = Column(String(64), nullable=False, comment="User name")
    location = Column(String(64), nullable=False, comment="User location")

    def __str__(self) -> str:
        return "User(id：{}, user_id：{}, name：{} location：{})".format(self.id, self.user_id, self.name, self.location)

    def __repr__(self):
        return f"{self.name} from {self.location}"


def add_to_users(new_user):
    # Create session
    Session = sessionmaker(bind=engine)
    session = Session()
    users = Users(user_id=new_user.user_id, name=new_user.name, location=new_user.location)
    # Add to session
    session.add(users)
    # Commit to DB
    session.commit()
    session.close()


def get_location(user_id):
    connection = engine.connect()
    metadata = MetaData()

    users = Table('users', metadata, autoload=True, autoload_with=engine)
    sel = users.select().where(users.c.user_id == user_id)
    result = list(connection.execute(sel))

    return result[0][-1]


if __name__ == "__main__":
    Base.metadata.drop_all(engine)  # Delete table if it exist
    Base.metadata.create_all(engine)  # Create table
    from bot import NewUser
    bob = NewUser("Bob")
    bob.user_id, bob.location = 342342342, "lviv"
    add_to_users(bob)
    print(get_location(342342342))
