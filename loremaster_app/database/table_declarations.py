from sqlalchemy import Column, ForeignKey, Integer, String, BINARY, Boolean, Float
from sqlalchemy.orm import declarative_base, relationship, backref

from .table_declaration_types import *

Base = declarative_base()

class User(Base):
    __tablename__ = "user"

    id:int = Column(Integer, primary_key=True)

    name:str = Column(String, unique=True, nullable=False)
    first_name:str = Column(String, nullable=False)
    last_name:str = Column(String, nullable=False)
    email:str = Column(String, nullable=False)

    thumbnail_id:int = Column(Integer, ForeignKey('image.editable_id'))
    thumbnail:Image = relationship('Image', foreign_keys=[thumbnail_id])

    admin_status:bool = Column(Boolean, nullable=False)

    password:bytes = Column(BINARY, nullable=False)

    owns:list[Editable] = relationship('Editable', back_populates='owner')

    editor_perms:list[Editor] = relationship('Editor', back_populates='editor')

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

    editors:list[Editor] = relationship('Editor', back_populates='editable')
    
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

        self.editors.append(Editor(self.owner))

        super().__init__()

    id:int = Column(Integer, primary_key=True)

class Editor(Base):
    __tablename__ = "editor"

    id:int = Column(Integer, primary_key=True)

    editable_id:int = Column(Integer, ForeignKey("editable.id"))
    editable:Editable = relationship('Editable', back_populates="editors")

    editor_id:int = Column(Integer, ForeignKey("user.id"))
    editor:User = relationship('User', back_populates="editor_perms")

    def __init__(self, editor:User) -> None:
        self.editor = editor

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

    traits:TraitListItem = relationship("TraitListItem", back_populates="character")
    stats:StatListItem = relationship("StatListItem", back_populates="character")
    relationships:RelationshipListItem = relationship("RelationshipListItem", back_populates="character")
    inventories:InventoryListItem = relationship("InventoryListItem", back_populates="character")

    location_id:int = Column(Integer, ForeignKey("location.editable_id"))
    location:Location = relationship("Location", foreign_keys=[location_id])

    guilds = None

    __mapper_args__ = {
        'polymorphic_identity':'character',
    }

    def __init__(self, owner: User, name: str) -> None:
        super().__init__(owner, name)

    def __repr__(self) -> str:
        return f"Character{{name:{self.name}, id:{self.editable_id}}}"

class Familiar(Character):
    __tablename__ = "familiar"

    character_id:int = Column(Integer, ForeignKey("editable.id"), primary_key = True)

    character_owner_id:int = Column(Integer, ForeignKey("character.editable_id"))
    character_owner:Character = relationship("Character", foreign_keys=[character_owner_id])

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

    description_id:int = Column(Integer, ForeignKey('description.id'))
    description:str = relationship('Description')

    thumbnail_id:int = Column(Integer, ForeignKey('image.editable_id'))
    thumbnail:Image = relationship('Image')

    def __init__(self, name: str) -> None:
        self.name = name

    def __repr__(self) -> str:
        return f"Trait(name:{{{self.name}}})"

class TraitListItem(Base):
    __tablename__ = "traitlistitem"

    id:int = Column(Integer, primary_key=True)

    character_id:int = Column(Integer, ForeignKey("character.editable_id"))
    character:Character = relationship('Character', back_populates="traits")

    trait_id:int = Column(Integer, ForeignKey("trait.id"))
    trait:Trait = relationship('Trait')

    def __init__(self, trait:Trait) -> None:
        self.trait = trait

    def __repr__(self) -> str:
        return f"TraitListItem(character:{{{self.character.name}}}, name:{{{self.name}}})"

class Relationship(Base):
    __tablename__ = "relationship"

    id:int = Column(Integer, primary_key=True)

    name:str = Column(String(50), nullable=False)

    description_id:int = Column(Integer, ForeignKey('description.id'))
    description:Description = relationship('Description')

    thumbnail_id:int = Column(Integer, ForeignKey('image.editable_id'))
    thumbnail:Image = relationship('Image')

    def __init__(self, name: str) -> None:
        self.name = name

    def __repr__(self) -> str:
        return f"Relationship(name:{{{self.name}}})"

class RelationshipListItem(Base):
    __tablename__ = "relationshiplistitem"

    id:int = Column(Integer, primary_key=True)

    character_id:int = Column(Integer, ForeignKey("character.editable_id"))
    character:Character = relationship('Character', back_populates="relationships")

    relationship_id:int = Column(Integer, ForeignKey("relationship.id"))
    relationship:Relationship = relationship('Relationship')

    def __init__(self, relationship:Relationship) -> None:
        self.relationship = relationship
    
    def __repr__(self) -> str:
        return f"RelationshipListItem(character:{{{self.character.name}}}, name:{{{self.name}}})"

class Stat(Base):
    __tablename__ = "stat"

    id:int = Column(Integer, primary_key=True)
    name:str = Column(String(50), nullable=False)

    description_id:int = Column(Integer, ForeignKey('description.id'))
    description:str = relationship('Description')

    def __init__(self, name: str) -> None:
        self.name = name
    
    def __repr__(self) -> str:
        return f"Stat(name:{{{self.name}}})"

class StatListItem(Base):
    __tablename__ = "statlistitem"

    id:int = Column(Integer, primary_key=True)

    character_id:int = Column(Integer, ForeignKey("character.editable_id"))
    character:Character = relationship('Character', back_populates="stats")

    stat_id:int = Column(Integer, ForeignKey("stat.id"))
    stat:Stat = relationship('Stat')

    def __init__(self, stat:Stat) -> None:
        self.stat = stat

    def __repr__(self) -> str:
        return f"StatListItem(character:{{{self.character.name}}}, name:{{{self.name}}})"

class Item(Editable):
    __tablename__ = "item"

    editable_id:int = Column(Integer, ForeignKey("editable.id"), primary_key = True)

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

    def __init__(self, owner: User, name: str) -> None:
        super().__init__(owner, name)
    
    def __repr__(self) -> str:
        return f"Inventory(name:{{{self.name}}})"

class InventoryListItem(Base):
    __tablename__ = "inventorylistitem"

    id:int = Column(Integer, primary_key=True)

    character_id:int = Column(Integer, ForeignKey("character.editable_id"))
    character:Character = relationship('Character', back_populates="inventories")

    inventory_id:int = Column(Integer, ForeignKey("inventory.editable_id"))
    inventory:Inventory = relationship('Inventory')

    def __init__(self, inventory:Inventory) -> None:
        self.inventory = inventory

    def __repr__(self) -> str:
        return f"InventoryListItem(character:{{{self.character.name}}}, name{{{self.inventory.name}}})"

class Image(Editable):
    __tablename__ = "image"

    editable_id:int = Column(Integer, ForeignKey("editable.id"), primary_key = True)

    image_url:str = Column(String)
    image_path:str = Column(String)

    def __init__(self, owner: User, name: str) -> None:
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