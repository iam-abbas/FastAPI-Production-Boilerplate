from faker import Faker

fake = Faker()


def create_fake_user():
    username = fake.user_name()
    password = fake.password(length=12)
    email = fake.email()
    return {
        "username": username,
        "password": password,
        "email": email,
    }
