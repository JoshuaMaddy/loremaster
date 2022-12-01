import enum
from sqlalchemy import Column, ForeignKey, Integer, Enum, String, BINARY, Boolean, Float, Table, select
from sqlalchemy.orm import declarative_base, relationship, backref

from sqlalchemy.orm import Session as Ses

from .table_declaration_types import *

Base = declarative_base()

#Join tables
editable_editors = Table('editors', Base.metadata,
    Column('editable_id', ForeignKey('editable.id'), primary_key=True),
    Column('user_id', ForeignKey('user.id'), primary_key=True))

editable_images = Table('imagelist', Base.metadata,
    Column('character_id', ForeignKey('editable.id'), primary_key=True),
    Column('imagelistitem_id', ForeignKey('imagelistitem.id'), primary_key=True))

character_traits = Table('traits', Base.metadata,
    Column('character_id', ForeignKey('editable.id'), primary_key=True),
    Column('trait_id', ForeignKey('trait.id'), primary_key=True))

character_stats = Table('stats', Base.metadata,
    Column('character_id', ForeignKey('editable.id'), primary_key=True),
    Column('stat_id', ForeignKey('stat.id'), primary_key=True))

character_relationships = Table('relationships', Base.metadata,
    Column('character_id', ForeignKey('editable.id'), primary_key=True),
    Column('relationship_id', ForeignKey('relationship.id'), primary_key=True))

character_inventories = Table('inventories', Base.metadata,
    Column('character_id', ForeignKey('editable.id'), primary_key=True),
    Column('inventory_id', ForeignKey('inventory.editable_id'), primary_key=True))

familiar_traits = Table('f_traits', Base.metadata,
    Column('familiar_id', ForeignKey('editable.id'), primary_key=True),
    Column('trait_id', ForeignKey('trait.id'), primary_key=True))

familiar_stats = Table('f_stats', Base.metadata,
    Column('familiar_id', ForeignKey('editable.id'), primary_key=True),
    Column('stat_id', ForeignKey('stat.id'), primary_key=True))

familiar_relationships = Table('f_relationships', Base.metadata,
    Column('familiar_id', ForeignKey('editable.id'), primary_key=True),
    Column('relationship_id', ForeignKey('relationship.id'), primary_key=True))

familiar_inventories = Table('f_inventories', Base.metadata,
    Column('familiar_id', ForeignKey('editable.id'), primary_key=True),
    Column('inventory_id', ForeignKey('inventory.editable_id'), primary_key=True))

character_familiars = Table('familiars', Base.metadata,
    Column('character_id', ForeignKey('editable.id'), primary_key=True),
    Column('familiar_id', ForeignKey('familiar.editable_id'), primary_key=True))

guild_characters = Table("g_characters", Base.metadata,
    Column('guild_id', ForeignKey("editable.id"), primary_key=True),
    Column('character_id', ForeignKey('character.editable_id'), primary_key=True))

class Visibilites(enum.Enum):
    public = 1
    guild = 2
    private = 3

class User(Base):
    """
    User contains all information about a user for LoreMaster, including their ID, 
    name, email, password, and owned characters.

    Returns:
        User
    """

    __tablename__ = "user"

    id:int = Column(Integer, primary_key=True)

    name:str = Column(String, unique=True, nullable=False)
    first_name:str = Column(String, nullable=False)
    last_name:str = Column(String, nullable=False)
    email:str = Column(String, nullable=False)

    thumbnail_id:int = Column(Integer, ForeignKey('image.editable_id'))
    thumbnail:Image = relationship('Image', foreign_keys=[thumbnail_id])

    description:str =  Column(String)

    admin_status:bool = Column(Boolean, nullable=False)

    banned_status:bool = Column(Boolean, nullable=False)

    password:bytes = Column(BINARY, nullable=False)

    owns:list[Editable] = relationship('Editable', back_populates='owner')

    editor_perms:list[Editable] = relationship('Editable',
                        secondary = editable_editors,
                        back_populates = 'editors')

    def __init__(self, username:str, password:bytes=None, first_name:str=None, 
                last_name:str=None, email:str=None, admin_status:bool=None, banned_status:bool=None) -> None:
        """
        Args:
            username (str): string of username.
            password (bytes): encoded bytes from .auth.encrypt.
            first_name (str): string of first name.
            last_name (str): string of last name.
            email (str): string of email.
            admin_status (bool): boolean, true being admin.
            banned_status (bool): boolean, true being banned.
        """
        
        self.name = username
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.admin_status = admin_status
        self.banned_status = banned_status

        super().__init__()

    def __repr__(self) -> str:
        return f"User(name:{self.name}, id:{self.id})"

    def list_of_type(self, polymorphic_type:str, list_of_editbales:list[Editable]) -> list[Editable]:
        """
        Takes str of DB type to filter for user editables.

        Args:
            polymorphic_type (str): A DB type (eg, Character, Image, Item, etc.) 
            to filter for from all user editables.
            list_of_editbales (list[Editable]): list of editables to filter and return from.

        Returns:
            list[Editable]
        """

        editable_type:list[Editable] = []
        for editable in list_of_editbales:
            if editable.type == polymorphic_type:
                editable_type.append(editable)
        return editable_type
    
class Editable(Base):
    """
    Editable is the base class for the majority of database items, providing basic functions like
    visibility, owner, editors, name, description, and images.

    Returns:
        Editable
    """
    __tablename__ = "editable"

    id:int = Column(Integer, primary_key=True)

    visibility:Visibilites = Column(Enum(Visibilites))

    owner_id:int = Column(Integer, ForeignKey("user.id"))
    owner:User = relationship('User', back_populates='owns')

    editors:list[User] = relationship('User',
                        secondary = editable_editors,
                        back_populates = 'editor_perms')
    
    name:str = Column(String, nullable=False)
    description:str = Column(String)

    images:list[ImageListItem] = relationship('ImageListItem', secondary = editable_images, single_parent = True, cascade="all, delete-orphan")

    type:str = Column(String(15))

    __mapper_args__ = {
        'polymorphic_identity':'editable',
        'polymorphic_on':type
    }

    
    def __init__(self, owner:User, name:str) -> None:
        """
        Args:
            owner (User): Assigns the editable's owner as the User.
            name (str): String of name.
        """

        self.owner = owner
        self.name = name

        self.editors.append(self.owner)

        self.visibility = Visibilites.public

        super().__init__()

    id:int = Column(Integer, primary_key=True)

    def set_editors(self, sqlsession:Ses, editor_ids:list[int]) -> None:
        """
        Sets what users are able to edit the object.

        Args:
            sqlsession (Ses): Open SQLAlchmey session set to autocommit
            editor_ids (list[int]): Id's of users.
        """
        if editor_ids:
            for editor_id in editor_ids:
                editor:User = sqlsession.execute(select(User).where(User.id == editor_id)).scalar()

                if editor and not editor in self.editors:
                    self.editors.append(editor)

    def set_images(self, sqlsession:Ses, image_ids:list[int]) -> None:
        """
        Sets what images are associated with the object.

        Args:
            sqlsession (Ses): Open SQLAlchmey session set to autocommit
            image_ids (list[int]): Id's of images.
        """
        for index in range(len(image_ids)):
            image = sqlsession.execute(select(Image).where(Image.editable_id == image_ids[index])).scalar()
            if image:
                imageListItem:ImageListItem = ImageListItem(image=image, index=index)
                self.images.append(imageListItem)

    def set_visibility(self, sqlsession:Ses, visibility:Visibilites = None, vis_int:int = -1) -> None:
        """
        Sets the visibility of the object

        Args:
            sqlsession (Ses): Open SQLAlchmey session set to autocommit
            visibility (Visibilites): Visibility of the object.
            vis_int (int): Defaults visibility to public, user can set 1-3 for different types of visibility.
        """
        if not visibility == None: #if passed with a visibility value directly set that
            self.visibility = visibility
        elif int(vis_int) > -1: #else retrieve it by index
            self.visibility = Visibilites(int(vis_int))

class Location(Editable):
    __tablename__ = "location"

    editable_id:int = Column(Integer, ForeignKey("editable.id"), primary_key = True)

    parent_id:int = Column(Integer, ForeignKey(editable_id))

    children:list[Location] = relationship(
        "Location",
        backref=backref("parent", remote_side=editable_id),
        foreign_keys=[parent_id]
    )

    __mapper_args__ = {
        'polymorphic_identity':'location',
    }

    def __init__(self, owner: User, name: str) -> None:
        """
        Args:
            owner (User): Assigns the editable's owner as the User.
            name (str): String of name.
        """
        super().__init__(owner, name)

    def __repr__(self) -> str:
        return f"Location{{name:{self.name}, id:{self.editable_id}}}"

    def set_parent(self, sqlsession:Ses, parent_location_id:int) -> None:
        """
        Sets the location as a parent location

        Args:
            sqlsession (Ses): Open SQLAlchmey session set to autocommit
            parent_location_id (int): Int of parent location ID
        """
        
        parent_location = sqlsession.execute(select(Location).where(Location.editable_id == parent_location_id)).scalar()
        if parent_location:
            self.parent = parent_location

    def set_children(self, sqlsession:Ses, children_location_ids:list[int]) -> None:
        """
        Sets the location as a child location.

        Args:
            sqlsession (Ses): Open SQLAlchmey session set to autocommit
            children_location_id (int): Int of child location ID
        """
        for location_id in children_location_ids:
            child_location = sqlsession.execute(select(Location).where(Location.editable_id == location_id)).scalar()
            if child_location:
                self.children.append(child_location)

class Character(Editable):
    __tablename__ = "character"

    editable_id:int = Column(Integer, ForeignKey("editable.id"), primary_key = True)

    traits:list[Trait] = relationship('Trait', secondary = character_traits, single_parent = True, cascade="all, delete-orphan")
    stats:list[Stat] = relationship('Stat', secondary = character_stats, single_parent = True, cascade="all, delete-orphan")
    relationships:list[Relationship] = relationship('Relationship', secondary = character_relationships)
    inventories:list[Inventory] = relationship('Inventory', secondary = character_inventories)

    location_id:int = Column(Integer, ForeignKey("location.editable_id"))
    location:Location = relationship("Location", foreign_keys=[location_id], lazy='joined')
    
    guild_id:int = Column(Integer, ForeignKey("guild.editable_id"))
    guild:Guild = relationship('Guild', foreign_keys=[guild_id], lazy='joined')

    familiars:list[Familiar] = relationship('Familiar',
        secondary = character_familiars,
        back_populates = 'owners')

    __mapper_args__ = {
        'polymorphic_identity':'character',
    }

    def __init__(self, owner: User, name: str) -> None:
        """
        Args:
            owner (User): Assigns the editable's owner as the User.
            name (str): String of name.
        """
        super().__init__(owner, name)

    def __repr__(self) -> str:
        return f"Character{{name:{self.name}, id:{self.editable_id}}}"

    def set_stats(self, stats:list[dict]) -> None:
        """
        Sets the stats to the character.

        Args:
            stats (list[dict]): Gets list of stats
        """
        for stat in stats:
            new_stat:Stat = Stat(name=stat.get('stat_name'), short_description=stat.get('stat_description'))
            self.stats.append(new_stat)

    def set_traits(self, traits:list[dict]) -> None:
        """
        Sets the traits to the character.

        Args:
            traits (list[dict]): Gets list of traits.
        """
        for trait in traits:
            new_trait:Trait = Trait(name=trait.get('trait_name'), short_description=trait.get('trait_description'))
            self.traits.append(new_trait)

    def set_relationships(self, sqlsession:Ses, user:User, relationships:list[dict]) -> None:
        """
        Sets the relationships of the character.

        Args:
            sqlsession (Ses): Open SQLAlchmey session set to autocommit.
            user (User): Gets the user.
            relationships (list[dict]): Gets list of relationships.
        """
        for relationship in relationships:
            name:str = relationship.get('relationship_name')
            character_id:int = relationship.get('character_id')
            description:str = relationship.get('relationship_desc')

            if character_id != None:
                second_character:Character = sqlsession.execute(select(Character).where(Character.editable_id == character_id)).scalar()
                
                if second_character in user.editor_perms:
                    new_relationship:Relationship = Relationship(name=name, short_description=description)
                    new_relationship.character = second_character

                    self.relationships.append(new_relationship)

    def set_familiars(self, sqlsession:Ses, user:User, familiar_ids:list[int]) -> None:
        """
        Sets the familiars of the character.

        Args:
            sqlsession (Ses): Open SQLAlchmey session set to autocommit.
            user (User): Gets the user.
            familiar_ids (list[int]): Gets list of familiar's ids.
        """
        for familiar_id in familiar_ids:
            familiar:Familiar = sqlsession.execute(select(Familiar).where(Familiar.id == familiar_id)).scalar()

            if familiar and familiar in user.editor_perms:
                self.familiars.append(familiar)
    
    def set_location(self, sqlsession:Ses, user:User, location_id:int) -> None:
        """
        Sets the location of the character.

        Args:
            sqlsession (Ses): Open SQLAlchmey session set to autocommit.
            user (User): Gets the user.
            location_id (int): Gets the int of the location id.
        """
        self.location = sqlsession.execute(select(Location).where(Location.id == location_id)).scalar()
        self.location_id = location_id

    def set_guild(self, sqlsession:Ses, user:User, guild_id:int) -> None:
        """
        Sets the guild of the character.

        Args:
            sqlsession (Ses): Open SQLAlchmey session set to autocommit.
            user (User): Gets the user.
            guid_id (int): Gets the int of the guild id.
        """
        self.guild = sqlsession.execute(select(Guild).where(Guild.id == guild_id)).scalar()
        self.guild_id = guild_id


class Familiar(Editable):
    __tablename__ = "familiar"

    editable_id:int = Column(Integer, ForeignKey("editable.id"), primary_key = True)

    traits:list[Trait] = relationship('Trait', secondary = familiar_traits, single_parent = True, cascade="all, delete-orphan")
    stats:list[Stat] = relationship('Stat', secondary = familiar_stats, single_parent = True, cascade="all, delete-orphan")
    relationships:list[Relationship] = relationship('Relationship', secondary = familiar_relationships)
    inventories:list[Inventory] = relationship('Inventory', secondary = familiar_inventories)

    location_id:int = Column(Integer, ForeignKey("location.editable_id"))
    location:Location = relationship("Location", foreign_keys=[location_id])

    guilds = None

    #character_owner_id:int = Column(Integer, ForeignKey("character.editable_id"))
    #character_owner:Character = relationship("Character", foreign_keys=[character_owner_id])

    owners:list[Character] = relationship('Character',
        secondary = character_familiars,
        back_populates = 'familiars')

    __mapper_args__ = {
        'polymorphic_identity':'familiar',
    }

    def __init__(self, owner: User, name: str) -> None:
        """
        Args:
            owner (User): Assigns the editable's owner as the User.
            name (str): String of name.
        """

        super().__init__(owner, name)

    def __repr__(self) -> str:
        return f"Familiar{{name:{self.name}, id:{self.editable_id}}}"

    def set_stats(self, stats:list[dict]) -> None:
        """
        Sets the stats to the familiar.

        Args:
            stats (list[dict]): Gets list of stats
        """
        for stat in stats:
            new_stat:Stat = Stat(name=stat.get('stat_name'), short_description=stat.get('stat_description'))
            self.stats.append(new_stat)

    def set_traits(self, traits:list[dict]) -> None:
        """
        Sets the traits to the familiar.

        Args:
            traits (list[dict]): Gets list of traits.
        """
        for trait in traits:
            new_trait:Trait = Trait(name=trait.get('trait_name'), short_description=trait.get('trait_description'))
            self.traits.append(new_trait)

    def set_relationships(self, sqlsession:Ses, user:User, relationships:list[dict]) -> None:
        """
        Sets the relationships of the familiar.

        Args:
            sqlsession (Ses): Open SQLAlchmey session set to autocommit.
            user (User): Gets the user.
            relationships (list[dict]): Gets list of relationships.
        """
        for relationship in relationships:
            name:str = relationship.get('relationship_name')
            character_id:int = relationship.get('character_id')
            description:str = relationship.get('relationship_desc')

            if character_id != None:
                second_character:Character = sqlsession.execute(select(Character).where(Character.editable_id == character_id)).scalar()
                
                if second_character in user.editor_perms:
                    new_relationship:Relationship = Relationship(name=name, short_description=description)
                    new_relationship.character = second_character

                    self.relationships.append(new_relationship)

    def set_owner(self, sqlsession:Ses, user:User, owner_id:int) -> None:
        """
        Sets the owner of the familiar.

        Args:
            sqlsession (Ses): Open SQLAlchmey session set to autocommit.
            user (User): Gets the user.
            owner_ids (int): Gets int of owners id.
        """
        character:Character = sqlsession.execute(select(Character).where(Character.id == owner_id)).scalar()

        if character and character in user.editor_perms:
            self.owners = [character]
    
    def set_location(self, sqlsession:Ses, location_id:int) -> None:
        """
        Sets the location of the familiar.

        Args:
            sqlsession (Ses): Open SQLAlchmey session set to autocommit.
            location_id (int): Gets the int of the location id.
        """
        self.location = sqlsession.execute(select(Location).where(Location.id == location_id)).scalar()
        self.location_id = location_id

class Guild(Editable):
    __tablename__ = "guild"

    editable_id:int = Column(Integer, ForeignKey("editable.id"), primary_key = True)

    character_id:int = Column(Integer, ForeignKey("character.editable_id"))
    leader:Character = relationship("Character", foreign_keys=[character_id])

    __mapper_args__ = {
        'polymorphic_identity':'guild',
    }

    guild_members:list[Character] = relationship('Character', secondary = guild_characters)

    def __init__(self, owner: User, name: str) -> None:
        """
        Args:
            owner (User): Assigns the editable's owner as the User.
            name (str): String of name.
        """
        super().__init__(owner, name)

    def __repr__(self) -> str:
        return f"Guild{{name:{self.name}, id:{self.editable_id}}}"

    def set_leader(self, sqlsession:Ses, user:User, leader_id:int) -> None:
        """
        Sets the leader of the guild.

        Args:
            sqlsession (Ses): Open SQLAlchmey session set to autocommit.
            user (User): Gets the user.
            leader_id (int): Gets the int of the leader's id.
        """
        character:Character = sqlsession.execute(select(Character).where(Character.editable_id == leader_id)).scalar()

        if character and character in user.editor_perms:
            self.leader = character
            print(self.leader)

    def set_members(self, sqlsession:Ses, member_ids:list[int]) -> None:
        """
        Sets the members of the guild.

        Args:
            sqlsession (Ses): Open SQLAlchmey session set to autocommit.
            members_id (list[int]): Gets the list of the members's id.
        """
        for character_id in member_ids:
            member = sqlsession.execute(select(Character).where(Character.editable_id == character_id)).scalar()
            if member:
                self.guild_members.append(member)

class Trait(Base):
    __tablename__ = "trait"

    id:int = Column(Integer, primary_key=True)

    name:str = Column(String(50), nullable=False)

    short_description:str = Column(String(50), nullable=True)

    thumbnail_id:int = Column(Integer, ForeignKey('image.editable_id'))
    thumbnail:Image = relationship('Image')

    def __init__(self, name: str, short_description:str=None) -> None:
        """
        Args:
            name (str): String of name.
            short_description (str): String of the description
        """
        self.name = name
        self.short_description = short_description

    def __repr__(self) -> str:
        return f"Trait(name:{{{self.name}}})"

class Relationship(Base):
    __tablename__ = "relationship"

    id:int = Column(Integer, primary_key=True)

    name:str = Column(String(50), nullable=False)

    short_description:str = Column(String(50), nullable=True)

    thumbnail_id:int = Column(Integer, ForeignKey('image.editable_id'))
    thumbnail:Image = relationship('Image')

    character_id:int = Column(Integer, ForeignKey('character.editable_id'))
    character:Character = relationship('Character')

    def __init__(self, name: str, short_description:str=None) -> None:
        """
        Args:
            name (str): String of name.
            short_description (str): String of the description
        """
        self.name = name
        self.short_description = short_description

    def __repr__(self) -> str:
        return f"Relationship(name:{{{self.name}}})"

class Stat(Base):
    __tablename__ = "stat"

    id:int = Column(Integer, primary_key=True)
    name:str = Column(String(50), nullable=False)

    short_description:str = Column(String(50), nullable=True)

    def __init__(self, name: str, short_description:str=None) -> None:
        """
        Args:
            name (str): String of name.
            short_description (str): String of the description
        """
        self.name = name
        self.short_description = short_description
    
    def __repr__(self) -> str:
        return f"Stat(name:{{{self.name}}})"

class Item(Editable):
    __tablename__ = "item"

    editable_id:int = Column(Integer, ForeignKey("editable.id"), primary_key = True)

    __mapper_args__ = {
        'polymorphic_identity':'item',
    }

    def __init__(self, owner: User, name: str) -> None:
        """
        Args:
            owner (User): Assigns the editable's owner as the User.
            name (str): String of name.
        """
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
        """
        Args:
            item (Item): Gets the item.
            count (float): Sets a count for the number of items.
            index (float): Sets an index for inventory slot.
        """
        self.item = item
        self.count = count
        self.index = index

    def __repr__(self) -> str:
        return f"ItemListItem(item:{{{self.item.name}}}, index:{{{self.index}}}, count:{{{self.count}}})"

class Inventory(Editable):
    __tablename__ = "inventory"

    editable_id:int = Column(Integer, ForeignKey("editable.id"), primary_key = True)

    items:list[ItemListItem] = relationship('ItemListItem', back_populates="inventory")

    __mapper_args__ = {
        'polymorphic_identity':'inventory',
    }

    def __init__(self, owner:User, name:str) -> None:
        """
        Args:
            owner (User): Assigns the editable's owner as the User.
            name (str): String of name.
        """
        super().__init__(owner, name)
    
    def __repr__(self) -> str:
        return f"Inventory(name:{{{self.name}}})"

    def set_items(self, sqlsession:Ses, item_ids:list[int], item_counts:list[int]) -> None:
        """
        Sets items to the inventory

        Args:
            sqlsession (Ses):
            item_ids (list[int]): Gets a list of the item's ids.
            item_counts (list[int]): Gets the int for amount of each item.
        """
        self.items = []
        for index in range(len(item_ids)):
            item:Item = sqlsession.execute(select(Item).where(Item.id == item_ids[index])).scalars().first()
            if item:
                new_itemLI:ItemListItem = ItemListItem(item=item, count=item_counts[index], index=index) 

                self.items.append(new_itemLI)

class Image(Editable):
    __tablename__ = "image"

    editable_id:int = Column(Integer, ForeignKey("editable.id"), primary_key = True)

    image_url:str = Column(String)
    image_path:str = Column(String)

    __mapper_args__ = {
        'polymorphic_identity':'image',
    }

    def __init__(self, owner: User, name: str, image_path:str = None, image_url:str = None) -> None:
        """
        Args:
            owner (User): Assigns the editable's owner as the User.
            name (str): String of name.
            image_path (str): String of image path.
            image_url (str): String of image url.
        """
        self.image_path = image_path
        self.image_url = image_url
        super().__init__(owner, name)

    def __repr__(self) -> str:
        return f"Image(name:{{{self.name}}}, path:{{{self.image_path}}}, url:{{{self.image_url}}})"

class ImageListItem(Base):
    __tablename__ = "imagelistitem"

    id:int = Column(Integer, primary_key=True)

    editable_id:int = Column(Integer, ForeignKey("editable.id"))
    editable:Editable = relationship('Editable', back_populates='images', foreign_keys=[editable_id])
    
    image_id:int = Column(Integer, ForeignKey('editable.id'))
    image:Image = relationship('Image', foreign_keys=[image_id])

    index = Column(Integer, nullable=False)

    def __init__(self, image:Image, index:int=-1) -> None:
        """
        Args:
            image (Image): Gets image of image.
            index (int): Sets the index to -1:
        """
        self.image = image
        self.index = index
    
    def __repr__(self) -> str:
        return f"ImageListItem(image_id:{{{self.image_id}}}, index:{{{self.index}}})"

class Description(Base):
    __tablename__ = "description"

    id:int = Column(Integer, primary_key=True)
    text:str = Column(String)
    type:str = Column(String(10))

    def __init__(self, text:str, type:str) -> None:
        """
        Args:
            text (str): Gets string of text.
            type (str): Gets string of type.
        """
        self.text = text
        self.type = type
        super().__init__()