from contextlib import nullcontext
from sqlalchemy import Column, ForeignKey, Integer, String, BINARY, Boolean, Float, Table
from sqlalchemy.orm import declarative_base, relationship, backref

from .table_declaration_types import *

Base = declarative_base()

#Join tables
editable_editors = Table('editors', Base.metadata,
    Column('editable_id', ForeignKey('editable.id'), primary_key=True),
    Column('user_id', ForeignKey('user.id'), primary_key=True))

character_traits = Table('traits', Base.metadata,
    Column('character_id', ForeignKey('character.editable_id'), primary_key=True),
    Column('trait_id', ForeignKey('trait.id'), primary_key=True))

character_stats = Table('stats', Base.metadata,
    Column('character_id', ForeignKey('character.editable_id'), primary_key=True),
    Column('stat_id', ForeignKey('stat.id'), primary_key=True))

character_relationships = Table('relationships', Base.metadata,
    Column('character_id', ForeignKey('character.editable_id'), primary_key=True),
    Column('relationship_id', ForeignKey('relationship.id'), primary_key=True))

character_inventories = Table('inventories', Base.metadata,
    Column('character_id', ForeignKey('character.editable_id'), primary_key=True),
    Column('inventory_id', ForeignKey('inventory.editable_id'), primary_key=True))

character_familiars = Table('familiars', Base.metadata,
    Column('character_id', ForeignKey('character.editable_id'), primary_key=True),
    Column('familiar_id', ForeignKey('familiar.editable2_id'), primary_key=True))

class User(Base):
    __tablename__ = "user"

    id:int = Column(Integer, primary_key=True)

    name:str = Column(String, unique=True, nullable=False)
    first_name:str = Column(String, nullable=False)
    last_name:str = Column(String, nullable=False)
    email:str = Column(String, nullable=False)

    thumbnail_id:int = Column(Integer, ForeignKey('image.editable_id'))
    thumbnail:Image = relationship('Image', foreign_keys=[thumbnail_id])

    description_id:int = Column(Integer, ForeignKey('description.id'))
    description:Description = relationship('Description', foreign_keys=[description_id])

    admin_status:bool = Column(Boolean, nullable=False)

    password:bytes = Column(BINARY, nullable=False)

    owns:list[Editable] = relationship('Editable', back_populates='owner')

    editor_perms:list[Editable] = relationship('Editable',
                        secondary = editable_editors,
                        back_populates = 'editors')

    def __init__(self, username:str, password:bytes=None, first_name:str=None, 
                last_name:str=None, email:str=None, admin_status:bool=None) -> None:
        self.name = username
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.admin_status = admin_status

        super().__init__()

    def __repr__(self) -> str:
        return f"User(name:{self.name}, id:{self.id})"
    
class Editable(Base):
    __tablename__ = "editable"

    id:int = Column(Integer, primary_key=True)

    owner_id:int = Column(Integer, ForeignKey("user.id"))
    owner:User = relationship('User', back_populates='owns',)

    editors:list[User] = relationship('User',
                        secondary = editable_editors,
                        back_populates = 'editor_perms')
    
    name:str = Column(String, nullable=False)
    description:str = Column(String)

    images:list[ImageListItem] = relationship('ImageListItem', back_populates='editable')

    type:str = Column(String(15))

    __mapper_args__ = {
        'polymorphic_identity':'editable',
        'polymorphic_on':type
    }

    
    def __init__(self, owner:User, name:str) -> None:
        self.owner = owner
        self.name = name

        self.editors.append(self.owner)

        super().__init__()

    id:int = Column(Integer, primary_key=True)

class Location(Editable):
    __tablename__ = "location"

    editable_id:int = Column(Integer, ForeignKey("editable.id"), primary_key = True)

    parent_id:int = Column(Integer, ForeignKey(editable_id))

    parent:list[Location]
    children:list[Location] = relationship(
        "Location",
        cascade="all, delete-orphan",
        backref=backref("parent", remote_side=editable_id),
        foreign_keys=[parent_id]
    )

    __mapper_args__ = {
        'polymorphic_identity':'location',
    }

    def __init__(self, owner: User, name: str) -> None:
        super().__init__(owner, name)

    def __repr__(self) -> str:
        return f"Location{{name:{self.name}, id:{self.editable_id}}}"

class Character(Editable):
    __tablename__ = "character"

    editable_id:int = Column(Integer, ForeignKey("editable.id"), primary_key = True)

    traits:list[Trait] = relationship('Trait', secondary = character_traits)
    stats:list[Stat] = relationship('Stat', secondary = character_stats)
    relationships:list[Relationship] = relationship('Relationship', secondary = character_relationships)
    inventories:list[Inventory] = relationship('Inventory', secondary = character_inventories)

    location_id:int = Column(Integer, ForeignKey("location.editable_id"))
    location:Location = relationship("Location", foreign_keys=[location_id])

    guilds = None

    familiars:list[Familiar] = relationship('Familiar',
                        secondary = character_familiars,
                        back_populates = 'character_owners')

    __mapper_args__ = {
        'polymorphic_identity':'character',
    }

    def __init__(self, owner: User, name: str) -> None:
        super().__init__(owner, name)

    def __repr__(self) -> str:
        return f"Character{{name:{self.name}, id:{self.editable_id}}}"

class Familiar(Character):
    __tablename__ = "familiar"

    editable2_id:int = Column(Integer, ForeignKey("editable.id"), primary_key = True, autoincrement=True)

    character_owner_id:int = Column(Integer, ForeignKey("character.editable_id"))
    character_owner:Character = relationship("Character", foreign_keys=[character_owner_id])

    character_owners:list[Character] = relationship('Character',
                        secondary = character_familiars,
                        back_populates = 'familiars')

    __mapper_args__ = {
        'polymorphic_identity':'familiar',
    }

    def __init__(self, owner: User, name: str) -> None:
        super().__init__(owner, name)

    def __repr__(self) -> str:
        return f"Familiar{{name:{self.name}, id:{self.editable_id}}}"

class Guild(Editable):
    __tablename__ = "guild"

    editable_id:int = Column(Integer, ForeignKey("editable.id"), primary_key = True)

    location_id:int = Column(Integer, ForeignKey("location.editable_id"))
    location:Location = relationship("Location", foreign_keys=[location_id])

    character_id:int = Column(Integer, ForeignKey("character.editable_id"))
    leader:Character = relationship("Character", foreign_keys=[character_id])

    __mapper_args__ = {
        'polymorphic_identity':'guild',
    }

    guild_members = None

    def __init__(self, owner: User, name: str) -> None:
        super().__init__(owner, name)

    def __repr__(self) -> str:
        return f"Guild{{name:{self.name}, id:{self.editable_id}}}"

class Trait(Base):
    __tablename__ = "trait"

    id:int = Column(Integer, primary_key=True)

    name:str = Column(String(50), nullable=False)

    short_description:str = Column(String(50), nullable=True)

    description_id:int = Column(Integer, ForeignKey('description.id'))
    description:str = relationship('Description')

    thumbnail_id:int = Column(Integer, ForeignKey('image.editable_id'))
    thumbnail:Image = relationship('Image')

    def __init__(self, name: str) -> None:
        self.name = name

    def __repr__(self) -> str:
        return f"Trait(name:{{{self.name}}})"

class Relationship(Base):
    __tablename__ = "relationship"

    id:int = Column(Integer, primary_key=True)

    name:str = Column(String(50), nullable=False)

    description_id:int = Column(Integer, ForeignKey('description.id'))
    description:Description = relationship('Description')

    short_description:str = Column(String(50), nullable=True)

    thumbnail_id:int = Column(Integer, ForeignKey('image.editable_id'))
    thumbnail:Image = relationship('Image')

    def __init__(self, name: str) -> None:
        self.name = name

    def __repr__(self) -> str:
        return f"Relationship(name:{{{self.name}}})"

class Stat(Base):
    __tablename__ = "stat"

    id:int = Column(Integer, primary_key=True)
    name:str = Column(String(50), nullable=False)

    short_description:str = Column(String(50), nullable=True)

    description_id:int = Column(Integer, ForeignKey('description.id'))
    description:str = relationship('Description')

    def __init__(self, name: str) -> None:
        self.name = name
    
    def __repr__(self) -> str:
        return f"Stat(name:{{{self.name}}})"

class Item(Editable):
    __tablename__ = "item"

    editable_id:int = Column(Integer, ForeignKey("editable.id"), primary_key = True)

    __mapper_args__ = {
        'polymorphic_identity':'item',
    }

    def __init__(self, owner: User, name: str) -> None:
        super().__init__(owner, name)

    def __repr__(self) -> str:
        return f"Item(name:{{{self.name}}})"

class ItemListItem(Base):
    __tablename__ = "itemlistitem"

    id:int = Column(Integer, primary_key=True)

    inventory_id:int = Column(Integer, ForeignKey("inventory.editable_id"))
    inventory:Inventory = relationship('Inventory', back_populates="items")

    item_id:int = Column(Integer, ForeignKey("item.editable_id"))
    item:Item = relationship('Item')

    count:float = Column(Float, nullable=False)
    index:int = Column(Integer, nullable=False)

    def __init__(self, item:Item, count:float=1, index:float=-1) -> None:
        self.item = item
        self.count = count
        self.index = index

    def __repr__(self) -> str:
        return f"ItemListItem(item:{{{self.item.name}}}, index:{{{self.index}}}, count:{{{self.count}}})"

class Inventory(Editable):
    __tablename__ = "inventory"

    editable_id:int = Column(Integer, ForeignKey("editable.id"), primary_key = True)

    items:ItemListItem = relationship('ItemListItem', back_populates="inventory")

    __mapper_args__ = {
        'polymorphic_identity':'inventory',
    }

    def __init__(self, owner: User, name: str) -> None:
        super().__init__(owner, name)
    
    def __repr__(self) -> str:
        return f"Inventory(name:{{{self.name}}})"

class Image(Editable):
    __tablename__ = "image"

    editable_id:int = Column(Integer, ForeignKey("editable.id"), primary_key = True)

    image_url:str = Column(String)
    image_path:str = Column(String)

    __mapper_args__ = {
        'polymorphic_identity':'image',
    }

    def __init__(self, owner: User, name: str, image_path:str = None, image_url:str = None) -> None:
        self.image_path = image_path
        self.image_url = image_url
        super().__init__(owner, name)

    def __repr__(self) -> str:
        return f"Image(name:{{{self.name}}}, path:{{{self.image_path}}}, url:{{{self.image_url}}})"

class ImageListItem(Base):
    __tablename__ = "imagelistitem"

    id:int = Column(Integer, primary_key=True)

    editable_id:int = Column(Integer, ForeignKey("editable.id"))
    editable:Editable = relationship('Editable', back_populates="images", foreign_keys=[editable_id])

    image_id:int = Column(Integer, ForeignKey("image.editable_id"))
    image:Image = relationship('Image', foreign_keys=[image_id])

    index = Column(Integer, nullable=False)

    def __init__(self, image:Image, index:int=-1) -> None:
        self.image = image
        self.index = index
    
    def __repr__(self) -> str:
        return f"ImageListItem(editable name:{{{self.editable.name}}}, name{{{self.image.name}}}, index:{{{self.index}}})"

class Description(Base):
    __tablename__ = "description"

    id:int = Column(Integer, primary_key=True)
    text:str = Column(String)
    type:str = Column(String(10))

    def __init__(self, text:str, type:str) -> None:
        self.text = text
        self.type = type
        super().__init__()