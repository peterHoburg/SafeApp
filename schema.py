import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyConnectionField, SQLAlchemyObjectType
from database_handler import db_session, Users as UsersModel, Activities as ActivitiesModel, Contacts as ContactsModel, \
    UserActivities as UserActivitiesModel, UserContacts as UserContactsModel


class Users(SQLAlchemyObjectType):
    class Meta:
        model = UsersModel
        interfaces = (relay.Node,)


class Activities(SQLAlchemyObjectType):
    class Meta:
        model = ActivitiesModel
        interfaces = (relay.Node,)


class Contacts(SQLAlchemyObjectType):
    class Meta:
        model = ContactsModel
        interfaces = (relay.Node,)


class UserActivities(SQLAlchemyObjectType):
    class Meta:
        model = UserActivitiesModel
        interfaces = (relay.Node,)


class UserContacts(SQLAlchemyObjectType):
    class Meta:
        model = UserContactsModel
        interfaces = (relay.Node,)


class CreateUser(graphene.Mutation):
    class Input:
        user_id = graphene.Int()
        name = graphene.String()
        email = graphene.String()
        last = graphene.String()

    ok = graphene.Boolean()
    user = graphene.Field(Users)

    @classmethod
    def mutate(cls, _, args):
        user = UsersModel(email=args.get('email'), user_id=args.get('user_id'))
        db_session.add(user)
        db_session.commit()
        ok = True
        return CreateUser(user=user, ok=ok)


class UpdateUsername(graphene.Mutation):
    class Input:
        first = graphene.String()
        email = graphene.String()

    ok = graphene.Boolean()
    user = graphene.Field(Users)

    @classmethod
    def mutate(cls, _, args, context):
        query = Users.get_query(context)
        email = args.get('email')
        username = args.get('username')
        user = query.filter(UsersModel.email == email).first()
        user.username = username
        db_session.commit()
        ok = True
        return UpdateUsername(user=user, ok=ok)


class Query(graphene.ObjectType):
    node = relay.Node.Field()
    all_users = SQLAlchemyConnectionField(Users)
    all_activities = SQLAlchemyConnectionField(Activities)
    all_contacts = SQLAlchemyConnectionField(Contacts)
    # NOT SURE HOW THESE WORK
    find_user = graphene.Field(lambda: Users, user_id=graphene.Int())
    find_contacts = graphene.Field(lambda: Contacts, contact_id=graphene.Int())
    find_activity = graphene.Field(lambda: Activities, activity_id=graphene.Int())

    @staticmethod
    def resolve_find_user(args, context):
        query = Users.get_query(context)
        user_id = args.get('user_id')
        # you can also use and_ with filter() eg: filter(and_(param1, param2)).first()
        return query.filter(UsersModel.user_id == user_id).first()

    @staticmethod
    def resolve_find_contact(args, context):
        print(args)
        print(context)
        query = Contacts.get_query(context)
        contact_id = args.get('contact_id')
        return query.filter(ContactsModel.contact_id == contact_id).first()


class Mutations(graphene.ObjectType):
    create_user = CreateUser.Field()
    change_username = UpdateUsername.Field()


schema = graphene.Schema(query=Query, types=[Users, Activities, Contacts, UserContacts, UserActivities],
                         mutation=Mutations)
