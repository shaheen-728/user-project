import random

from ..extensions import app, g

from backend.app.users.users_models import Users, BotMetaDetails
from backend.app.users.utils import hash_password, create
from backend.app.users_proile_tags.tags_models import TagDomain, Domain

First_Names = [
               "Gyan", "Idhant", "Inesh", "Ishrat", "Ishank", "Jag", "Jagan",
               "Jash", "Kaamil", "Kahaan", "Kairav", "Kalap", "Kamal", "Ketan",
               "Kuval", "Laksh", "Lahar", "Layak", "Lomash", "Maaran", "Madan", "Mahir", "Manan", "Mehul", "Mohal",
               "Murali", "Naadir", "Nabhi", "Naksh", "Naval", "Nayan", "Neel",
               "Nihal", "Nimit", "Nirvan", "Paavan", "Pahal", "Parv", "Paresh", "Pavak", "Pran",
               "Pranay"
               ]
Last_Names = ["Acharya", "Agarwal", "Aggarwal", "Agrawal", "Ahuja", "Amble", "Anand", "Apte", "Arora", "Arya", "Atwal",
              "Babu", "Badal", "Badami",
              "Bahri", "Bajaj", "Bajwa", "Bakshi", "Bala", "Balakrishnan", "Balay", "Bali", "Banerjee", "Banik",
              "Bansal", "Basu", "Batra", "Bedi", "Bhagat", "Bhardwaj", "Bhargava", "Bhasin", "Bhatia", "Bhatt",
              "Bhattacharyya", "Bhavsar",
              "Biswas", " Bora", "Borra", "Buch", "Chahal", "Chakrabarti", "Chakraborty", "Chandra", "Chatterjee"
              ]


def create_testing_users(domain_id):
    first_name = random.choice(First_Names)
    last_name = random.choice(Last_Names)
    random_email_number = "".join(
        ["{}".format(random.randint(0, 9)) for num in range(0, 4)]
    )
    obj = {
        "password": "testing$123#%^",
        "first_name": first_name,
        "last_name": last_name,
        "country": "IN",
        "email": first_name + "." + last_name + random_email_number + "@gmail.com",
    }
    password_unhash = obj["password"]
    obj["password"] = hash_password(password_unhash)

    obj["is_active"] = True
    obj["user_type"] = "Automatic"
    user = Users(**obj)
    create(user)
    if domain_id is not None:
        all_tag_ids = g.session.query(TagDomain.tag_id).filter(TagDomain.domain_id == domain_id).all()
    else:
        domain_id = random.choice(g.session.query(Domain.id).all())
        all_tag_ids = g.session.query(TagDomain.tag_id).filter(TagDomain.domain_id == domain_id[0]).all()
    all_tag_ids = [ele[0] for ele in all_tag_ids]
    categories = random.sample(all_tag_ids, random.randint(min(3, len(all_tag_ids)), min(5, len(all_tag_ids))))
    accuracy = round(random.uniform(0.1, 0.3), 1)

    obj = {"user_id": user.id, "selected_categories": categories, "accuracy": accuracy}
    bot_user = BotMetaDetails(**obj)
    create(bot_user)

